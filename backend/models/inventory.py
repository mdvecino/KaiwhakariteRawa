from sqlalchemy import (
    Column, String, Integer, Float, Text, Boolean, ForeignKey, Enum,
    Date, DateTime, UniqueConstraint
)
from sqlalchemy.orm import relationship
import enum
from ..models.base import BaseModel
from datetime import datetime


class ItemStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    maintenance = "maintenance"
    retired = "retired"


class ItemCategory(str, enum.Enum):
    # Māori cultural categories
    taonga = "taonga"
    raranga = "raranga"
    whakairo = "whakairo"
    rongoa = "rongoa"
    kai = "kai"
    kakahu = "kakahu"
    
    # General inventory categories
    technology = "technology"
    furniture = "furniture"
    equipment = "equipment"
    supplies = "supplies"
    cultural = "cultural"
    tools = "tools"
    decor = "decor"
    fashion = "fashion"
    appliances = "appliances"
    stationery = "stationery"
    sports = "sports"
    outdoor = "outdoor"
    toys = "toys"
    books = "books"
    other = "other"


class UnitOfMeasure(str, enum.Enum):
    # General units
    piece = "piece"
    pcs = "pcs"
    pair = "pair"
    bundle = "bundle"
    set = "set"
    box = "box"
    pack = "pack"
    kilogram = "kilogram"
    kg = "kg"
    litre = "litre"
    metre = "metre"
    other = "other"


class StorageArea(str, enum.Enum):
    # Māori cultural storage areas
    marae = "marae"
    workshop = "workshop"
    archive = "archive"
    storage_room = "storage_room"
    display_area = "display_area"
    
    # General storage areas
    shelf_a = "shelf_a"
    shelf_b = "shelf_b"
    shelf_c = "shelf_c"
    warehouse = "warehouse"
    office = "office"
    other = "other"


class ItemOrigin(str, enum.Enum):
    gifted_by_iwi = "gifted_by_iwi"
    found_in_rohe = "found_in_rohe"
    crafted_locally = "crafted_locally"
    purchased = "purchased"
    inherited = "inherited"
    other = "other"


class MaterialType(str, enum.Enum):
    POUNAMU = "pounamu"
    HARAREKE = "harakeke"
    WOOD = "wood"
    BONE = "bone"
    SHELL = "shell"
    STONE = "stone"
    FEATHER = "feather"
    OTHER = "other"


class StorageRequirement(str, enum.Enum):
    HUMIDITY_CONTROLLED = "humidity_controlled"
    NO_DIRECT_SUNLIGHT = "no_direct_sunlight"
    COOL_TEMPERATURE = "cool_temperature"
    DRY_ENVIRONMENT = "dry_environment"
    VENTILATED = "ventilated"
    OTHER = "other"


class ItemTag(str, enum.Enum):
    TAPU = "tapu"
    DISPLAY_ONLY = "display_only"
    LOANABLE = "loanable"
    SACRED = "sacred"
    FRAGILE = "fragile"
    OTHER = "other"


class TransactionType(str, enum.Enum):
    # Stock In / Goods Receipt
    stock_in = "stock_in"  # Adding new inventory from suppliers or purchases
    
    # Stock Out / Goods Issue  
    stock_out = "stock_out"  # Removing inventory for sales, production, or internal use
    
    # Stock Transfer
    transfer = "transfer"  # Moving inventory from one location to another
    
    # Stock Adjustment
    adjustment = "adjustment"  # Manually changing inventory quantities to fix discrepancies
    
    # Stock Return (Return In)
    customer_return = "customer_return"  # Returning goods from customers back into inventory
    
    # Purchase Return (Return Out)
    return_to_supplier = "return_to_supplier"  # Sending purchased goods back to suppliers
    
    # Stock Reservation / Allocation
    reservation = "reservation"  # Reserving inventory for specific customer, order, or purpose
    release = "release"  # Releasing reserved inventory
    
    # Stock Write-Off / Disposal
    write_off = "write_off"  # Removing unusable, damaged, or expired items from inventory
    
    # Stock Take / Physical Count
    stock_take = "stock_take"  # Physical inventory count to verify actual stock on hand
    
    # Production Issue / Material Issue
    production_issue = "production_issue"  # Issuing raw materials to production or manufacturing
    
    # Production Receipt
    production_receipt = "production_receipt"  # Adding finished goods into inventory after manufacturing
    
    # Consignment In
    consignment_in = "consignment_in"  # Stock received from supplier but not yet owned (not paid for)
    
    # Consignment Out
    consignment_out = "consignment_out"  # Stock sent to reseller/distributor but still owned by you
    
    # Cycle Count
    cycle_count = "cycle_count"  # Regular partial stock count for selected items
    
    # Legacy types (keeping for backward compatibility)
    audit = "audit"
    repack = "repack"
    loaned = "loaned"
    borrowed = "borrowed"


class InventoryItem(BaseModel):
    """Inventory item model with Māori cultural integration"""
    __tablename__ = "inventory_items"
    __table_args__ = (
        UniqueConstraint('sku', 'location', name='uix_sku_location'),
        {'extend_existing': True}
    )
    
    # Basic inventory fields
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    sku = Column(String(50), index=True)
    barcode = Column(String(100), unique=True, index=True)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100), nullable=True)
    custom_category = Column(String(100), nullable=True)  # User-defined category for Māori items
    
    # Quantity and measurement
    quantity = Column(Integer, default=0)
    unit_of_measure = Column(
        Enum(UnitOfMeasure), nullable=False, default=UnitOfMeasure.piece
    )
    min_quantity = Column(Integer, default=0)
    max_quantity = Column(Integer, nullable=True)
    
    # Financial
    unit_price = Column(Float, nullable=True)
    total_value = Column(Float, nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    
    # Location and storage
    location = Column(String(100), nullable=True)
    storage_conditions = Column(Text, nullable=True)
    storage_requirements = Column(
        String(500), nullable=True
    )  # JSON array of requirements
    
    # Dates
    purchase_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    
    # Tracking
    batch_number = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True)
    status = Column(Enum(ItemStatus), default=ItemStatus.active)
    condition_notes = Column(Text, nullable=True)
    maintenance_schedule = Column(Text, nullable=True)
    
    # Māori cultural fields
    iwi = Column(String(100), nullable=True)  # Tribal affiliation
    tapu_status = Column(Boolean, default=False)  # Sacred status
    korero = Column(Text, nullable=True)  # Cultural narrative/story
    whakapapa = Column(Text, nullable=True)  # Genealogy/lineage
    tikanga_notes = Column(Text, nullable=True)  # Cultural protocols
    item_origin = Column(
        Enum(ItemOrigin), nullable=True
    )  # Origin/provenance
    material_used = Column(
        String(500), nullable=True
    )  # JSON array of materials
    cultural_notes = Column(
        Text, nullable=True
    )  # Additional cultural information
    
    # Media and documents
    image_url = Column(String(500), nullable=True)
    documents = Column(Text, nullable=True)  # JSON array of document URLs
    
    # Tags and alerts
    item_tags = Column(String(500), nullable=True)  # JSON array of tags
    is_sacred = Column(Boolean, default=False)  # Alert for sacred items
    loanable = Column(Boolean, default=True)  # Whether item can be loaned
    stock_alert = Column(Boolean, default=True)  # Enable/disable low stock alerts for this item
    
    # Auto-generated fields
    auto_sku = Column(
        String(100), nullable=True
    )  # Auto-generated SKU based on category + origin
    
    # Relationships
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_by = relationship("User", back_populates="inventory_items", cascade="all, delete")
    supplier = relationship("Supplier", back_populates="items")
    returns = relationship("SupplierReturn", back_populates="item")
    customer_returns = relationship("CustomerReturn", back_populates="item")
    messages = relationship("Message", back_populates="related_item")
    # Additional Māori cultural fields
    custom_category = Column(String(100), nullable=True)  # User-defined category for Māori items
    maori_name = Column(String(200), nullable=True)  # Traditional Māori name
    cultural_significance = Column(Text, nullable=True)  # Cultural significance description
    kaitiaki = Column(String(100), nullable=True)  # Custodian/guardian
    item_condition = Column(String(100), nullable=True)  # Physical condition
    related_event = Column(String(100), nullable=True)  # Related cultural events
    
    # Extended Māori-specific fields
    hapu = Column(String(100), nullable=True)  # Sub-tribe affiliation
    rohe = Column(String(100), nullable=True)  # Traditional territory
    whakatoki = Column(Text, nullable=True)  # Proverbs or sayings related to the item
    karakia = Column(Text, nullable=True)  # Prayers or incantations associated with the item
    mauri = Column(String(100), nullable=True)  # Life force or essence of the item
    tipuna = Column(String(200), nullable=True)  # Ancestors associated with the item
    whenua = Column(String(100), nullable=True)  # Land or place of origin
    age_estimate = Column(String(50), nullable=True)  # Estimated age of the item
    craftsperson = Column(String(100), nullable=True)  # Person who created the item
    acquisition_method = Column(String(100), nullable=True)  # How the item was acquired


class InventoryTransaction(BaseModel):
    __tablename__ = "inventory_transactions"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(Integer, nullable=False)
    related_party = Column(
        String(200), nullable=True
    )  # Supplier, customer, etc.
    reference = Column(
        String(100), nullable=True
    )  # PO, SO, etc.
    notes = Column(Text, nullable=True)
    from_location = Column(String(100), nullable=True)  # For transfer (already string, keep as is)
    to_location = Column(String(100), nullable=True)    # For transfer (already string, keep as is)
    
    # Additional fields for enhanced transaction tracking
    unit_price = Column(Float, nullable=True)  # Price per unit at time of transaction
    total_value = Column(Float, nullable=True)  # Total value of transaction
    batch_number = Column(String(100), nullable=True)  # For batch tracking
    expiry_date = Column(Date, nullable=True)  # For expiry tracking
    condition = Column(String(100), nullable=True)  # Item condition at time of transaction
    
    # Approval and authorization
    approved_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approval_notes = Column(Text, nullable=True)
    
    # Reservation and allocation details
    reservation_expiry = Column(DateTime, nullable=True)  # When reservation expires
    allocated_for = Column(String(200), nullable=True)  # Purpose of allocation
    
    # Production and manufacturing details
    production_order = Column(String(100), nullable=True)  # Production order number
    work_center = Column(String(100), nullable=True)  # Manufacturing work center
    
    # Consignment details
    consignment_terms = Column(Text, nullable=True)  # Terms of consignment agreement
    ownership_status = Column(String(50), nullable=True)  # owned, consigned_in, consigned_out
    
    # Cycle count and stock take details
    count_method = Column(String(50), nullable=True)  # manual, barcode, rfid
    variance_reason = Column(Text, nullable=True)  # Reason for stock variance
    
    # Timestamps
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    transaction_date = Column(DateTime, nullable=True)  # Actual transaction date (may differ from created_at)

    # Relationships
    item = relationship("InventoryItem", backref="transactions")
    created_by = relationship("User", foreign_keys=[created_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id]) 