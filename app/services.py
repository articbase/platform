from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .models import InventoryItem, Order, OrderLine
from .schemas import InventoryItemCreate, OrderCreate, OrderRead, OrderUpdate
from .telemetry import (
    record_inventory_conflict,
    record_inventory_item_created,
    record_order_created,
    record_order_failed,
    tracer,
)


class InventoryConflictError(ValueError):
    pass


class OrderValidationError(ValueError):
    pass


class OrderNotFoundError(ValueError):
    pass


def create_inventory_item(session: Session, payload: InventoryItemCreate) -> InventoryItem:
    with tracer.start_as_current_span("inventory.create") as span:
        span.set_attribute("inventory.sku", payload.sku)

        existing_item = session.scalar(select(InventoryItem).where(InventoryItem.sku == payload.sku))
        if existing_item is not None:
            record_inventory_conflict(payload.sku)
            raise InventoryConflictError(f"Inventory item '{payload.sku}' already exists.")

        item = InventoryItem(
            sku=payload.sku,
            name=payload.name,
            stock=payload.stock,
            unit_price_cents=payload.unit_price_cents,
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        record_inventory_item_created(item.sku)
        return item


def list_inventory_items(session: Session) -> list[InventoryItem]:
    return list(session.scalars(select(InventoryItem).order_by(InventoryItem.sku)))


def create_order(session: Session, payload: OrderCreate) -> Order:
    with tracer.start_as_current_span("orders.create") as span:
        span.set_attribute("order.customer_id", payload.customer_id)
        span.set_attribute("order.line_count", len(payload.lines))

        skus = [line.sku for line in payload.lines]
        with session.begin():
            items = list(session.scalars(select(InventoryItem).where(InventoryItem.sku.in_(skus))))
            items_by_sku = {item.sku: item for item in items}
            missing_skus = sorted(set(skus) - set(items_by_sku))

            if missing_skus:
                missing_list = ", ".join(missing_skus)
                record_order_failed(reason="unknown_sku")
                raise OrderValidationError(f"Unknown SKU(s): {missing_list}.")

            order = Order(customer_id=payload.customer_id, status="created")
            session.add(order)
            session.flush()

            total_amount_cents = 0
            for line in payload.lines:
                item = items_by_sku[line.sku]
                if item.stock < line.quantity:
                    record_order_failed(reason="insufficient_stock")
                    raise OrderValidationError(
                        f"Insufficient stock for SKU '{line.sku}': requested {line.quantity}, available {item.stock}."
                    )

                item.stock -= line.quantity
                line_total_cents = item.unit_price_cents * line.quantity
                total_amount_cents += line_total_cents

                session.add(
                    OrderLine(
                        order_id=order.id,
                        inventory_item_id=item.id,
                        quantity=line.quantity,
                        unit_price_cents=item.unit_price_cents,
                        line_total_cents=line_total_cents,
                    )
                )

            order.total_amount_cents = total_amount_cents

        persisted_order = session.scalar(
            select(Order)
            .options(selectinload(Order.lines).selectinload(OrderLine.item))
            .where(Order.id == order.id)
        )
        if persisted_order is None:
            raise RuntimeError("Order creation completed, but the order could not be reloaded.")

        record_order_created(
            order_id=persisted_order.id,
            line_count=len(persisted_order.lines),
            total_amount_cents=persisted_order.total_amount_cents,
        )
        span.set_attribute("order.id", persisted_order.id)
        span.set_attribute("order.total_amount_cents", persisted_order.total_amount_cents)
        return persisted_order


def get_order(session: Session, order_id: int) -> Order | None:
    return session.scalar(
        select(Order)
        .options(selectinload(Order.lines).selectinload(OrderLine.item))
        .where(Order.id == order_id)
    )


def update_order(session: Session, order_id: int, payload: OrderUpdate) -> Order:
    with tracer.start_as_current_span("orders.update") as span:
        span.set_attribute("order.id", order_id)
        span.set_attribute("order.customer_id", payload.customer_id)
        span.set_attribute("order.line_count", len(payload.lines))

        skus = [line.sku for line in payload.lines]
        with session.begin():
            order = get_order(session, order_id)
            if order is None:
                raise OrderNotFoundError(f"Order '{order_id}' does not exist.")

            for existing_line in order.lines:
                existing_line.item.stock += existing_line.quantity

            items = list(session.scalars(select(InventoryItem).where(InventoryItem.sku.in_(skus))))
            items_by_sku = {item.sku: item for item in items}
            missing_skus = sorted(set(skus) - set(items_by_sku))

            if missing_skus:
                missing_list = ", ".join(missing_skus)
                raise OrderValidationError(f"Unknown SKU(s): {missing_list}.")

            order.customer_id = payload.customer_id
            order.status = payload.status
            order.lines.clear()
            session.flush()

            total_amount_cents = 0
            for line in payload.lines:
                item = items_by_sku[line.sku]
                if item.stock < line.quantity:
                    raise OrderValidationError(
                        f"Insufficient stock for SKU '{line.sku}': requested {line.quantity}, available {item.stock}."
                    )

                item.stock -= line.quantity
                line_total_cents = item.unit_price_cents * line.quantity
                total_amount_cents += line_total_cents
                order.lines.append(
                    OrderLine(
                        item=item,
                        quantity=line.quantity,
                        unit_price_cents=item.unit_price_cents,
                        line_total_cents=line_total_cents,
                    )
                )

            order.total_amount_cents = total_amount_cents
            session.flush()

        persisted_order = get_order(session, order_id)
        if persisted_order is None:
            raise RuntimeError("Order update completed, but the order could not be reloaded.")

        span.set_attribute("order.total_amount_cents", persisted_order.total_amount_cents)
        return persisted_order


def delete_order(session: Session, order_id: int) -> None:
    with tracer.start_as_current_span("orders.delete") as span:
        span.set_attribute("order.id", order_id)

        with session.begin():
            order = get_order(session, order_id)
            if order is None:
                raise OrderNotFoundError(f"Order '{order_id}' does not exist.")

            for line in order.lines:
                line.item.stock += line.quantity

            session.delete(order)


def list_orders(session: Session) -> list[Order]:
    return list(
        session.scalars(
            select(Order)
            .options(selectinload(Order.lines).selectinload(OrderLine.item))
            .order_by(Order.id.desc())
        )
    )


def order_to_read_model(order: Order) -> OrderRead:
    return OrderRead(
        id=order.id,
        customer_id=order.customer_id,
        status=order.status,
        total_amount_cents=order.total_amount_cents,
        created_at=order.created_at,
        lines=[
            {
                "sku": line.item.sku,
                "name": line.item.name,
                "quantity": line.quantity,
                "unit_price_cents": line.unit_price_cents,
                "line_total_cents": line.line_total_cents,
            }
            for line in order.lines
        ],
    )
