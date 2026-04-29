from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class CustomerReturnStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    completed = "completed"
    cancelled = "cancelled"


class CustomerReturnCondition(str, Enum):
    new = "new"
    like_new = "like_new"
    good = "good"
    fair = "fair"
    poor = "poor"
    damaged = "damaged"
    defective = "defective"


class CustomerReturnBase(BaseModel):
    """Base schema for customer returns"""
    customer_id: int = Field(..., description="ID of the customer")
    item_id: int = Field(..., description="ID of the inventory item")
    quantity: int = Field(..., gt=0, description="Quantity to return")
    reason: str = Field(..., min_length=1, max_length=500, description="Reason for return")
    return_date: date = Field(..., description="Date of return")
    reference: Optional[str] = Field(None, max_length=100, description="Reference number or PO")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    condition: CustomerReturnCondition = Field(..., description="Condition of returned items")
    restocking: bool = Field(False, description="Whether items will be restocked")
    refund_amount: Optional[float] = Field(None, ge=0, description="Refund amount")
    refund_processed: bool = Field(False, description="Whether refund has been processed")
    attachments: Optional[str] = Field(None, description="JSON array of attachment URLs")


class CustomerReturnCreate(CustomerReturnBase):
    """Schema for creating a new customer return"""
    pass


class CustomerReturnUpdate(BaseModel):
    """Schema for updating a customer return"""
    customer_id: Optional[int] = None
    item_id: Optional[int] = None
    quantity: Optional[int] = Field(None, gt=0)
    reason: Optional[str] = Field(None, min_length=1, max_length=500)
    return_date: Optional[date] = None
    status: Optional[CustomerReturnStatus] = None
    processed_by_id: Optional[int] = None
    reference: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)
    condition: Optional[CustomerReturnCondition] = None
    restocking: Optional[bool] = None
    refund_amount: Optional[float] = Field(None, ge=0)
    refund_processed: Optional[bool] = None
    attachments: Optional[str] = None


class CustomerReturnResponse(CustomerReturnBase):
    """Schema for customer return responses"""
    id: int
    return_id: str
    status: CustomerReturnStatus
    processed_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    item_name: Optional[str] = None
    processed_by_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class CustomerReturnList(BaseModel):
    """Schema for listing customer returns"""
    returns: List[CustomerReturnResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class CustomerReturnStats(BaseModel):
    """Schema for customer return statistics"""
    total_returns: int
    pending_returns: int
    approved_returns: int
    rejected_returns: int
    completed_returns: int
    total_refund_amount: float
    average_processing_time: Optional[float] = None  # in days 