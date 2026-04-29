from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from ..models.inventory import (
    ItemStatus, ItemCategory, UnitOfMeasure, StorageArea, ItemOrigin,
    TransactionType
)


class InventoryItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    sku: str
    barcode: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    quantity: int = 0
    unit_of_measure: UnitOfMeasure = UnitOfMeasure.piece
    min_quantity: int = 0
    max_quantity: Optional[int] = None
    unit_price: Optional[float] = None
    total_value: Optional[float] = None
    location: Optional[str] = None
    storage_conditions: Optional[str] = None
    storage_requirements: Optional[str] = None  # JSON array
    purchase_date: Optional[date] = None
    expiry_date: Optional[date] = None
    batch_number: Optional[str] = None
    serial_number: Optional[str] = None
    status: ItemStatus = ItemStatus.active
    condition_notes: Optional[str] = None
    maintenance_schedule: Optional[str] = None
    
    # Māori cultural fields
    iwi: Optional[str] = None
    tapu_status: bool = False
    korero: Optional[str] = None
    whakapapa: Optional[str] = None
    tikanga_notes: Optional[str] = None
    item_origin: Optional[ItemOrigin] = None
    material_used: Optional[str] = None  # JSON array
    cultural_notes: Optional[str] = None
    custom_category: Optional[str] = None
    maori_name: Optional[str] = None
    cultural_significance: Optional[str] = None
    kaitiaki: Optional[str] = None
    item_condition: Optional[str] = None
    related_event: Optional[str] = None
    
    # Extended Māori-specific fields
    hapu: Optional[str] = None
    rohe: Optional[str] = None
    whakatoki: Optional[str] = None
    karakia: Optional[str] = None
    mauri: Optional[str] = None
    tipuna: Optional[str] = None
    whenua: Optional[str] = None
    age_estimate: Optional[str] = None
    craftsperson: Optional[str] = None
    acquisition_method: Optional[str] = None
    
    # Media and documents
    image_url: Optional[str] = None
    documents: Optional[str] = None  # JSON array
    
    # Tags and alerts
    item_tags: Optional[str] = None  # JSON array
    is_sacred: bool = False
    loanable: bool = True
    stock_alert: bool = True
    
    # Auto-generated fields
    auto_sku: Optional[str] = None


class InventoryItemCreate(InventoryItemBase):
    supplier_id: Optional[int] = None
    stock_alert: bool = True


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    quantity: Optional[int] = None
    unit_of_measure: Optional[UnitOfMeasure] = None
    min_quantity: Optional[int] = None
    max_quantity: Optional[int] = None
    unit_price: Optional[float] = None
    total_value: Optional[float] = None
    supplier_id: Optional[int] = None
    location: Optional[str] = None
    storage_conditions: Optional[str] = None
    storage_requirements: Optional[str] = None
    purchase_date: Optional[date] = None
    expiry_date: Optional[date] = None
    batch_number: Optional[str] = None
    serial_number: Optional[str] = None
    status: Optional[ItemStatus] = None
    condition_notes: Optional[str] = None
    maintenance_schedule: Optional[str] = None
    iwi: Optional[str] = None
    tapu_status: Optional[bool] = None
    korero: Optional[str] = None
    whakapapa: Optional[str] = None
    tikanga_notes: Optional[str] = None
    item_origin: Optional[ItemOrigin] = None
    material_used: Optional[str] = None
    cultural_notes: Optional[str] = None
    image_url: Optional[str] = None
    documents: Optional[str] = None
    item_tags: Optional[str] = None
    is_sacred: Optional[bool] = None
    loanable: Optional[bool] = None
    stock_alert: Optional[bool] = None
    auto_sku: Optional[str] = None
    custom_category: Optional[str] = None
    maori_name: Optional[str] = None
    cultural_significance: Optional[str] = None
    kaitiaki: Optional[str] = None
    item_condition: Optional[str] = None
    related_event: Optional[str] = None
    
    # Extended Māori-specific fields
    hapu: Optional[str] = None
    rohe: Optional[str] = None
    whakatoki: Optional[str] = None
    karakia: Optional[str] = None
    mauri: Optional[str] = None
    tipuna: Optional[str] = None
    whenua: Optional[str] = None
    age_estimate: Optional[str] = None
    craftsperson: Optional[str] = None
    acquisition_method: Optional[str] = None


class InventoryItemResponse(InventoryItemBase):
    id: int
    supplier_id: Optional[int] = None
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    barcode: Optional[str] = None
    stock_alert: bool = True
    
    class Config:
        from_attributes = True


class InventoryItemList(BaseModel):
    items: List[InventoryItemResponse]
    total: int
    page: int
    per_page: int


class InventoryTransactionBase(BaseModel):
    item_id: int
    transaction_type: TransactionType
    quantity: int
    related_party: Optional[str] = None
    reference: Optional[str] = None
    notes: Optional[str] = None
    from_location: Optional[str] = None  # Location is now a string
    to_location: Optional[str] = None    # Location is now a string


class InventoryTransactionCreate(BaseModel):
    transaction_type: TransactionType
    quantity: int
    related_party: Optional[str] = None
    reference: Optional[str] = None
    notes: Optional[str] = None
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    
    # Enhanced transaction fields
    unit_price: Optional[float] = None
    total_value: Optional[float] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    condition: Optional[str] = None
    
    # Approval fields
    approved_by_id: Optional[int] = None
    approval_notes: Optional[str] = None
    
    # Reservation and allocation fields
    reservation_expiry: Optional[datetime] = None
    allocated_for: Optional[str] = None
    
    # Production fields
    production_order: Optional[str] = None
    work_center: Optional[str] = None
    
    # Consignment fields
    consignment_terms: Optional[str] = None
    ownership_status: Optional[str] = None
    
    # Stock take and cycle count fields
    count_method: Optional[str] = None
    variance_reason: Optional[str] = None
    
    # Transaction date
    transaction_date: Optional[datetime] = None
    
    # Legacy fields for backward compatibility
    transfer_reason: Optional[str] = None
    approved_by: Optional[str] = None
    performed_by: Optional[str] = None
    date_time: Optional[str] = None


class InventoryTransactionResponse(InventoryTransactionBase):
    id: int
    created_by_id: int
    created_at: datetime
    quantity_before: Optional[int] = None
    quantity_after: Optional[int] = None
    
    # Enhanced response fields
    unit_price: Optional[float] = None
    total_value: Optional[float] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    condition: Optional[str] = None
    
    # Approval fields
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None
    
    # Reservation and allocation fields
    reservation_expiry: Optional[datetime] = None
    allocated_for: Optional[str] = None
    
    # Production fields
    production_order: Optional[str] = None
    work_center: Optional[str] = None
    
    # Consignment fields
    consignment_terms: Optional[str] = None
    ownership_status: Optional[str] = None
    
    # Stock take and cycle count fields
    count_method: Optional[str] = None
    variance_reason: Optional[str] = None
    
    # Transaction date
    transaction_date: Optional[datetime] = None
    
    # User information
    created_by_name: Optional[str] = None
    approved_by_name: Optional[str] = None
    
    class Config:
        from_attributes = True 