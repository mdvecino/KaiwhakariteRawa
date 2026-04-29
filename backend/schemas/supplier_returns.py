from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class ReturnStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    completed = "completed"
    cancelled = "cancelled"


class ReturnCondition(str, Enum):
    new = "new"
    like_new = "like_new"
    good = "good"
    fair = "fair"
    poor = "poor"
    damaged = "damaged"
    defective = "defective"


class SupplierReturnBase(BaseModel):
    """Base schema for supplier returns"""
    supplier_id: int = Field(..., description="ID of the supplier")
    item_id: int = Field(..., description="ID of the inventory item")
    quantity: int = Field(..., gt=0, description="Quantity to return")
    reason: str = Field(..., min_length=1, max_length=500, description="Reason for return")
    return_date: date = Field(..., description="Date of return")
    reference: Optional[str] = Field(None, max_length=100, description="Reference number or PO")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    condition: ReturnCondition = Field(..., description="Condition of returned items")
    attachments: Optional[str] = Field(None, description="JSON array of attachment URLs")


class SupplierReturnCreate(SupplierReturnBase):
    """Schema for creating a new supplier return"""
    pass


class SupplierReturnUpdate(BaseModel):
    """Schema for updating a supplier return"""
    supplier_id: Optional[int] = None
    item_id: Optional[int] = None
    quantity: Optional[int] = Field(None, gt=0)
    reason: Optional[str] = Field(None, min_length=1, max_length=500)
    return_date: Optional[date] = None
    status: Optional[ReturnStatus] = None
    approved_by_id: Optional[int] = None
    reference: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)
    condition: Optional[ReturnCondition] = None
    attachments: Optional[str] = None


class SupplierReturnResponse(SupplierReturnBase):
    """Schema for supplier return responses"""
    id: int
    return_id: str
    status: ReturnStatus
    approved_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    supplier_name: Optional[str] = None
    item_name: Optional[str] = None
    approved_by_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class SupplierReturnList(BaseModel):
    """Schema for listing supplier returns"""
    returns: List[SupplierReturnResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class SupplierReturnStats(BaseModel):
    """Schema for supplier return statistics"""
    total_returns: int
    pending_returns: int
    approved_returns: int
    rejected_returns: int
    completed_returns: int
    total_value: float
    average_processing_time: Optional[float] = None  # in days 