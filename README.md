# Python App with OpenTelemetry

This repository now contains a small FastAPI application with an OLTP-oriented relational data model and OpenTelemetry wiring for traces and metrics.

## OpenTelemetry support

The app now includes:

- FastAPI request instrumentation
- SQLAlchemy database instrumentation
- custom business spans for inventory and order creation
- custom counters and histograms for order and inventory activity
- OTLP HTTP exporter support for traces and metrics

To export telemetry to an OpenTelemetry collector, set:

```bash
export OTEL_SERVICE_NAME=python-oltp-app
export OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
```

If no OTLP endpoint is configured, the app still creates telemetry signals but does not ship them anywhere.

You can disable instrumentation entirely with:

```bash
export OTEL_ENABLED=false
```

## Local observability stack

This repository includes a simple local stack with:

- **OpenTelemetry Collector** for OTLP ingest and routing
- **Tempo** for traces
- **Prometheus** for metrics
- **Alertmanager** for alert routing
- **Loki** for logs
- **Promtail** for shipping app log files to Loki
- **Grafana** for visualization

Start the stack:

```bash
docker compose up -d
```

That command now starts the observability stack **and** the FastAPI app in Docker. The app is available at `http://127.0.0.1:8000`.

If you want to run the app outside Docker instead, start only the observability services and run Uvicorn locally:

```bash
docker compose up -d otel-collector tempo prometheus alertmanager loki promtail grafana
```

Then run the app with telemetry export pointed at the collector:

```bash
source .venv/bin/activate
export OTEL_SERVICE_NAME=python-oltp-app
export OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
uvicorn app.main:app --reload
```

Open the UIs:

| Service | URL | Notes |
| --- | --- | --- |
| Grafana | `http://127.0.0.1:3000` | Login `admin` / `admin` |
| Prometheus | `http://127.0.0.1:9090` | Scrapes metrics from the collector |
| Alertmanager | `http://127.0.0.1:9093` | Receives alerts from Prometheus |
| Tempo | `http://127.0.0.1:3200` | Trace backend API |
| Loki | `http://127.0.0.1:3100` | Log backend API |
| App | `http://127.0.0.1:8000` | FastAPI app running in Docker |

Once the app receives traffic, Grafana will have:

- a **Prometheus** datasource for metrics
- a **Tempo** datasource for traces
- a **Loki** datasource for logs
- an **Alertmanager** datasource for active alerts
- a provisioned dashboard named **Python OLTP App Overview**
- a provisioned dashboard named **Python API Endpoint Status** with list views for services and endpoints

The app also writes request logs to `logs/app.log`, and Promtail ships that file into Loki.

The Dockerized app stores its SQLite database under `./data/oltp.db` on the host so order and inventory data persist across container restarts.

To generate sample telemetry:

```bash
curl -X POST http://127.0.0.1:8000/inventory-items \
  -H "Content-Type: application/json" \
  -d '{"sku":"SKU-1","name":"Keyboard","stock":10,"unit_price_cents":2999}'

curl -X POST http://127.0.0.1:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"customer-123","lines":[{"sku":"SKU-1","quantity":2}]}'
```

Useful Prometheus queries:

```text
orders_created_total
orders_failed_total
inventory_items_created_total
inventory_items_conflicts_total
```

Prometheus also loads alerting rules from `observability/prometheus-alerts.yml` and sends them to Alertmanager. The starter rules cover:

- observability services that stop responding to Prometheus scrapes
- API endpoints that return `5xx` responses for at least 2 minutes

The dashboard is available in Grafana under the **Observability** folder.

The app also exposes an order management page at `http://127.0.0.1:8000/orders/manage` for viewing, editing, updating, and deleting existing orders from the browser.

Stop the stack:

```bash
docker compose down
```

## OLTP behavior

The app is still designed for short, transactional writes:

- inventory items are stored in relational tables
- order creation runs inside a single database transaction
- stock deductions and order line inserts succeed or fail together
- SQLite is configured with WAL mode locally to improve concurrent read/write behavior

For production, point `DATABASE_URL` at PostgreSQL or another SQLAlchemy-compatible transactional database and configure your OpenTelemetry collector endpoint.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Basic healthcheck |
| `POST` | `/inventory-items` | Create an inventory record |
| `GET` | `/inventory-items` | List inventory |
| `POST` | `/orders` | Create an order transactionally |
| `GET` | `/orders` | List orders |
| `GET` | `/orders/manage` | Browser UI for managing existing orders |
| `GET` | `/orders/{id}` | Fetch a single order |
| `PUT` | `/orders/{id}` | Update an order and rebalance inventory |
| `DELETE` | `/orders/{id}` | Delete an order and restore inventory |

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

The application uses `sqlite:///./oltp.db` by default.

## Run the app in Docker only

```bash
docker compose up -d --build app
```

## Example requests

Create inventory:

```bash
curl -X POST http://127.0.0.1:8000/inventory-items \
  -H "Content-Type: application/json" \
  -d '{"sku":"SKU-1","name":"Keyboard","stock":10,"unit_price_cents":2999}'
```

Create an order:

```bash
curl -X POST http://127.0.0.1:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"customer-123","lines":[{"sku":"SKU-1","quantity":2}]}'
```

## Run tests

```bash
pytest
```
