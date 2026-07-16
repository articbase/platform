from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


def create_client(tmp_path: Path) -> TestClient:
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    return TestClient(create_app(database_url))


def test_healthcheck(tmp_path: Path) -> None:
    client = create_client(tmp_path)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_telemetry_is_enabled_without_external_collector(tmp_path: Path) -> None:
    client = TestClient(create_app(f"sqlite:///{tmp_path / 'telemetry.db'}", service_name="test-service"))

    telemetry = client.app.state.telemetry

    assert telemetry["enabled"] is True
    assert telemetry["service_name"] == "test-service"
    assert telemetry["trace_export_enabled"] is False
    assert telemetry["metric_export_enabled"] is False


def test_order_creation_updates_inventory(tmp_path: Path) -> None:
    client = create_client(tmp_path)

    item_response = client.post(
        "/inventory-items",
        json={
            "sku": "SKU-1",
            "name": "Keyboard",
            "stock": 10,
            "unit_price_cents": 2999,
        },
    )
    assert item_response.status_code == 201

    order_response = client.post(
        "/orders",
        json={
            "customer_id": "customer-123",
            "lines": [{"sku": "SKU-1", "quantity": 2}],
        },
    )

    assert order_response.status_code == 201
    assert order_response.json()["total_amount_cents"] == 5998

    inventory_response = client.get("/inventory-items")
    assert inventory_response.status_code == 200
    assert inventory_response.json()[0]["stock"] == 8


def test_order_rolls_back_when_stock_is_insufficient(tmp_path: Path) -> None:
    client = create_client(tmp_path)

    item_response = client.post(
        "/inventory-items",
        json={
            "sku": "SKU-2",
            "name": "Mouse",
            "stock": 1,
            "unit_price_cents": 1599,
        },
    )
    assert item_response.status_code == 201

    order_response = client.post(
        "/orders",
        json={
            "customer_id": "customer-456",
            "lines": [{"sku": "SKU-2", "quantity": 3}],
        },
    )

    assert order_response.status_code == 400
    assert "Insufficient stock" in order_response.json()["detail"]

    inventory_response = client.get("/inventory-items")
    assert inventory_response.status_code == 200
    assert inventory_response.json()[0]["stock"] == 1

    orders_response = client.get("/orders")
    assert orders_response.status_code == 200
    assert orders_response.json() == []


def test_order_update_rebalances_inventory(tmp_path: Path) -> None:
    client = create_client(tmp_path)

    for item in (
        {"sku": "SKU-1", "name": "Keyboard", "stock": 10, "unit_price_cents": 2999},
        {"sku": "SKU-2", "name": "Mouse", "stock": 5, "unit_price_cents": 1599},
    ):
        response = client.post("/inventory-items", json=item)
        assert response.status_code == 201

    order_response = client.post(
        "/orders",
        json={
            "customer_id": "customer-123",
            "lines": [{"sku": "SKU-1", "quantity": 2}],
        },
    )
    assert order_response.status_code == 201

    update_response = client.put(
        "/orders/1",
        json={
            "customer_id": "customer-789",
            "status": "packed",
            "lines": [
                {"sku": "SKU-1", "quantity": 1},
                {"sku": "SKU-2", "quantity": 2},
            ],
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["customer_id"] == "customer-789"
    assert update_response.json()["status"] == "packed"
    assert update_response.json()["total_amount_cents"] == 6197

    inventory_response = client.get("/inventory-items")
    assert inventory_response.status_code == 200
    assert inventory_response.json() == [
        {"sku": "SKU-1", "name": "Keyboard", "stock": 9, "unit_price_cents": 2999},
        {"sku": "SKU-2", "name": "Mouse", "stock": 3, "unit_price_cents": 1599},
    ]


def test_order_delete_restores_inventory(tmp_path: Path) -> None:
    client = create_client(tmp_path)

    item_response = client.post(
        "/inventory-items",
        json={
            "sku": "SKU-3",
            "name": "Headset",
            "stock": 4,
            "unit_price_cents": 4999,
        },
    )
    assert item_response.status_code == 201

    order_response = client.post(
        "/orders",
        json={
            "customer_id": "customer-999",
            "lines": [{"sku": "SKU-3", "quantity": 3}],
        },
    )
    assert order_response.status_code == 201

    delete_response = client.delete("/orders/1")

    assert delete_response.status_code == 204

    inventory_response = client.get("/inventory-items")
    assert inventory_response.status_code == 200
    assert inventory_response.json()[0]["stock"] == 4

    orders_response = client.get("/orders")
    assert orders_response.status_code == 200
    assert orders_response.json() == []


def test_order_management_page_is_available(tmp_path: Path) -> None:
    client = create_client(tmp_path)

    response = client.get("/orders/manage")

    assert response.status_code == 200
    assert "Order Manager" in response.text
