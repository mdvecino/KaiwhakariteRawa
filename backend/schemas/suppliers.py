from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class SupplierBase(BaseModel):
    name: str
    supplier_code: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    abn: Optional[str] = None
    tax_id: Optional[str] = None
    payment_terms: Optional[str] = None
    credit_limit: Optional[int] = None
    notes: Optional[str] = None
    rating: Optional[int] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    abn: Optional[str] = None
    tax_id: Optional[str] = None
    payment_terms: Optional[str] = None
    credit_limit: Optional[int] = None
    notes: Optional[str] = None
    rating: Optional[int] = None
    is_active: Optional[bool] = None


class SupplierResponse(SupplierBase):
    id: int
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class SupplierList(BaseModel):
    suppliers: List[SupplierResponse]
    total: int
    page: int
    per_page: int 