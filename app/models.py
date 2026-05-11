
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class LineItem(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "sku": "SKU-001",
            "description": "Software license",
            "quantity": 2,
            "unit_price": "100.00",
            "category": "software"
        }
    })

    sku: str = Field(min_length=1)
    description: Optional[str] = None
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(gt=0)
    category: str = "default"


class InvoiceTaxRequest(BaseModel):
    invoice_id: str = Field(min_length=1)
    region: str = Field(min_length=1)
    currency: str = "USD"
    line_items: List[LineItem] = Field(min_length=1)
