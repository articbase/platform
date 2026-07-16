from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InventoryItemCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    stock: int = Field(ge=0)
    unit_price_cents: int = Field(gt=0)


class InventoryItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sku: str
    name: str
    stock: int
    unit_price_cents: int


class OrderLineCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    customer_id: str = Field(min_length=1, max_length=128)
    lines: list[OrderLineCreate] = Field(min_length=1)


class OrderUpdate(BaseModel):
    customer_id: str = Field(min_length=1, max_length=128)
    status: str = Field(min_length=1, max_length=32)
    lines: list[OrderLineCreate] = Field(min_length=1)


class OrderLineRead(BaseModel):
    sku: str
    name: str
    quantity: int
    unit_price_cents: int
    line_total_cents: int


class OrderRead(BaseModel):
    id: int
    customer_id: str
    status: str
    total_amount_cents: int
    created_at: datetime
    lines: list[OrderLineRead]
