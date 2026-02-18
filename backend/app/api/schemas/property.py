from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date
from enum import Enum

class PropertyTypeEnum(str, Enum):
    """Property types"""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    AGRICULTURAL = "agricultural"

class TransactionTypeEnum(str, Enum):
    """Transaction types"""
    SALE = "sale"
    RENT = "rent"

class PropertyPriceResponse(BaseModel):
    """Single property price data point"""
    id: int
    omi_zone_code: str
    municipality_name: Optional[str] = None
    year: int
    semester: int
    reference_date: date
    property_type: PropertyTypeEnum
    transaction_type: TransactionTypeEnum
    property_state: Optional[str] = None
    min_price: Optional[float] = Field(None, description="Minimum price per sqm (€)")
    max_price: Optional[float] = Field(None, description="Maximum price per sqm (€)")
    avg_price: float = Field(..., description="Average price per sqm (€)")
    rental_yield: Optional[float] = Field(None, description="Rental yield percentage")
    price_change_yoy: Optional[float] = Field(None, description="Year-over-year price change (%)")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "omi_zone_code": "B1",
                "municipality_name": "Milano",
                "year": 2024,
                "semester": 1,
                "reference_date": "2024-06-30",
                "property_type": "residential",
                "transaction_type": "sale",
                "property_state": "Normale",
                "min_price": 4500.0,
                "max_price": 6000.0,
                "avg_price": 5250.0,
                "rental_yield": 3.2,
                "price_change_yoy": 2.5
            }
        }

class PropertyPriceHistoryResponse(BaseModel):
    """Historical property price data"""
    omi_zone_code: str
    municipality_name: str
    property_type: PropertyTypeEnum
    transaction_type: TransactionTypeEnum
    history: List[PropertyPriceResponse]
    
    class Config:
        json_schema_extra = {
            "example": {
                "omi_zone_code": "B1",
                "municipality_name": "Milano",
                "property_type": "residential",
                "transaction_type": "sale",
                "history": [
                    {
                        "year": 2023,
                        "semester": 2,
                        "avg_price": 5120.0,
                        "price_change_yoy": 1.8
                    },
                    {
                        "year": 2024,
                        "semester": 1,
                        "avg_price": 5250.0,
                        "price_change_yoy": 2.5
                    }
                ]
            }
        }

class PropertyStatistics(BaseModel):
    """Aggregated property statistics for a location"""
    location_name: str
    location_type: str = Field(..., description="municipality or omi_zone")
    current_avg_price: Optional[float] = Field(None, description="Current average price per sqm (€)")
    price_range: Optional[Dict[str, float]] = Field(None, description="Min and max prices")
    avg_rental_yield: Optional[float] = Field(None, description="Average rental yield (%)")
    price_trend_1year: Optional[float] = Field(None, description="1-year price change (%)")
    price_trend_3year: Optional[float] = Field(None, description="3-year price change (%)")
    transaction_volume: Optional[int] = Field(None, description="Number of data points")
    
    class Config:
        json_schema_extra = {
            "example": {
                "location_name": "Milano - Centro Storico",
                "location_type": "omi_zone",
                "current_avg_price": 5250.0,
                "price_range": {
                    "min": 4500.0,
                    "max": 6000.0
                },
                "avg_rental_yield": 3.2,
                "price_trend_1year": 2.5,
                "price_trend_3year": 8.3,
                "transaction_volume": 12
            }
        }
