from __future__ import annotations

import os
from threading import Lock
from typing import Any

from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from sqlalchemy import Engine

DEFAULT_SERVICE_NAME = "python-oltp-app"

_provider_lock = Lock()
_providers_initialized = False
_instrumented_engines: set[int] = set()

tracer = trace.get_tracer("app.business")
meter = metrics.get_meter("app.business")
orders_created_counter = meter.create_counter("orders.created", description="Number of successfully created orders.")
orders_failed_counter = meter.create_counter("orders.failed", description="Number of failed order creation attempts.")
inventory_items_created_counter = meter.create_counter(
    "inventory_items.created",
    description="Number of inventory items created.",
)
inventory_conflicts_counter = meter.create_counter(
    "inventory_items.conflicts",
    description="Number of rejected inventory item creates caused by duplicate SKUs.",
)
order_total_histogram = meter.create_histogram(
    "orders.total_amount_cents",
    unit="cents",
    description="Distribution of successfully created order totals.",
)


def _is_enabled(explicit_value: bool | None) -> bool:
    if explicit_value is not None:
        return explicit_value
    return os.getenv("OTEL_ENABLED", "true").lower() not in {"0", "false", "no"}


def _service_name(explicit_value: str | None) -> str:
    return explicit_value or os.getenv("OTEL_SERVICE_NAME", DEFAULT_SERVICE_NAME)


def _base_otlp_endpoint() -> str | None:
    return os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")


def _signal_endpoint(signal: str) -> str | None:
    env_name = f"OTEL_EXPORTER_OTLP_{signal.upper()}_ENDPOINT"
    if explicit_signal_endpoint := os.getenv(env_name):
        return explicit_signal_endpoint

    if base_endpoint := _base_otlp_endpoint():
        return f"{base_endpoint.rstrip('/')}/v1/{signal}"

    return None


def _metric_export_interval_millis() -> int:
    return int(os.getenv("OTEL_METRIC_EXPORT_INTERVAL", "5000"))


def _ensure_providers(service_name: str, trace_endpoint: str | None, metric_endpoint: str | None) -> None:
    global _providers_initialized

    if _providers_initialized:
        return

    with _provider_lock:
        if _providers_initialized:
            return

        resource = Resource.create({"service.name": service_name})

        tracer_provider = TracerProvider(resource=resource)
        if trace_endpoint is not None:
            tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=trace_endpoint)))
        trace.set_tracer_provider(tracer_provider)

        metric_readers: list[PeriodicExportingMetricReader] = []
        if metric_endpoint is not None:
            metric_readers.append(
                PeriodicExportingMetricReader(
                    OTLPMetricExporter(endpoint=metric_endpoint),
                    export_interval_millis=_metric_export_interval_millis(),
                )
            )
        metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=metric_readers))

        _providers_initialized = True


def configure_telemetry(
    app: FastAPI,
    engine: Engine,
    *,
    service_name: str | None = None,
    enabled: bool | None = None,
) -> dict[str, Any]:
    telemetry_enabled = _is_enabled(enabled)
    resolved_service_name = _service_name(service_name)
    trace_endpoint = _signal_endpoint("traces")
    metric_endpoint = _signal_endpoint("metrics")

    telemetry_state = {
        "enabled": telemetry_enabled,
        "service_name": resolved_service_name,
        "trace_export_enabled": trace_endpoint is not None,
        "metric_export_enabled": metric_endpoint is not None,
    }

    if not telemetry_enabled:
        app.state.telemetry = telemetry_state
        return telemetry_state

    _ensure_providers(resolved_service_name, trace_endpoint, metric_endpoint)

    if not getattr(app.state, "telemetry_instrumented", False):
        FastAPIInstrumentor.instrument_app(app)
        app.state.telemetry_instrumented = True

    engine_id = id(engine)
    if engine_id not in _instrumented_engines:
        SQLAlchemyInstrumentor().instrument(engine=engine)
        _instrumented_engines.add(engine_id)

    app.state.telemetry = telemetry_state
    return telemetry_state


def record_inventory_item_created(item_sku: str) -> None:
    inventory_items_created_counter.add(1, {"inventory.sku": item_sku})


def record_inventory_conflict(item_sku: str) -> None:
    inventory_conflicts_counter.add(1, {"inventory.sku": item_sku})


def record_order_created(*, order_id: int, line_count: int, total_amount_cents: int) -> None:
    attributes = {
        "order.id": order_id,
        "order.line_count": line_count,
    }
    orders_created_counter.add(1, attributes)
    order_total_histogram.record(total_amount_cents, attributes)


def record_order_failed(*, reason: str) -> None:
    orders_failed_counter.add(1, {"order.failure_reason": reason})
