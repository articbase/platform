from __future__ import annotations

import logging
from time import perf_counter

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session

from .database import create_session_factory, create_sqlalchemy_engine, get_database_url, get_session, init_db
from .logging import configure_application_logging
from .order_management_ui import render_order_management_page
from .schemas import InventoryItemCreate, InventoryItemRead, OrderCreate, OrderRead, OrderUpdate
from .services import (
    InventoryConflictError,
    OrderNotFoundError,
    OrderValidationError,
    create_inventory_item,
    create_order,
    delete_order,
    get_order,
    list_inventory_items,
    list_orders,
    order_to_read_model,
    update_order,
)
from .telemetry import configure_telemetry


def create_app(
    database_url: str | None = None,
    *,
    service_name: str | None = None,
    enable_telemetry: bool | None = None,
) -> FastAPI:
    app = FastAPI(title="Python OLTP App", version="0.1.0")
    logger = configure_application_logging()

    engine = create_sqlalchemy_engine(database_url or get_database_url())
    init_db(engine)
    app.state.session_factory = create_session_factory(engine)
    app.state.telemetry = configure_telemetry(
        app,
        engine,
        service_name=service_name,
        enabled=enable_telemetry,
    )

    @app.middleware("http")
    async def log_requests(request, call_next):  # type: ignore[no-untyped-def]
        started_at = perf_counter()
        response = await call_next(request)
        duration_ms = (perf_counter() - started_at) * 1000
        logger.info(
            "request method=%s path=%s status=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/inventory-items", response_model=InventoryItemRead, status_code=status.HTTP_201_CREATED)
    def add_inventory_item(
        payload: InventoryItemCreate,
        session: Session = Depends(get_session),
    ) -> InventoryItemRead:
        try:
            item = create_inventory_item(session, payload)
        except InventoryConflictError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

        return InventoryItemRead.model_validate(item)

    @app.get("/inventory-items", response_model=list[InventoryItemRead])
    def get_inventory_items(session: Session = Depends(get_session)) -> list[InventoryItemRead]:
        return [InventoryItemRead.model_validate(item) for item in list_inventory_items(session)]

    @app.post("/orders", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
    def add_order(payload: OrderCreate, session: Session = Depends(get_session)) -> OrderRead:
        try:
            order = create_order(session, payload)
        except OrderValidationError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

        return order_to_read_model(order)

    @app.get("/orders", response_model=list[OrderRead])
    def get_orders(session: Session = Depends(get_session)) -> list[OrderRead]:
        return [order_to_read_model(order) for order in list_orders(session)]

    @app.get("/orders/manage", response_class=HTMLResponse)
    def manage_orders_page() -> HTMLResponse:
        return HTMLResponse(render_order_management_page())

    @app.get("/orders/{order_id}", response_model=OrderRead)
    def get_order_by_id(order_id: int, session: Session = Depends(get_session)) -> OrderRead:
        order = get_order(session, order_id)
        if order is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order '{order_id}' does not exist.")

        return order_to_read_model(order)

    @app.put("/orders/{order_id}", response_model=OrderRead)
    def update_order_by_id(
        order_id: int,
        payload: OrderUpdate,
        session: Session = Depends(get_session),
    ) -> OrderRead:
        try:
            order = update_order(session, order_id, payload)
        except OrderNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        except OrderValidationError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

        return order_to_read_model(order)

    @app.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_order_by_id(order_id: int, session: Session = Depends(get_session)) -> Response:
        try:
            delete_order(session, order_id)
        except OrderNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app


app = create_app()
