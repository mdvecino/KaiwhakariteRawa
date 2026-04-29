from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from ..models.base import BaseModel


class Supplier(BaseModel):
    """Supplier model for vendor management"""
    __tablename__ = "suppliers"
    
    name = Column(String(200), nullable=False)
    supplier_code = Column(String(50), unique=True, nullable=False)
    contact_person = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    website = Column(String(200), nullable=True)
    
    # Business details
    abn = Column(String(50), nullable=True)  # Australian Business Number
    tax_id = Column(String(50), nullable=True)
    payment_terms = Column(String(100), nullable=True)
    credit_limit = Column(Integer, nullable=True)
    
    # Status and notes
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5 rating
    
    # Relationships
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_by = relationship("User", back_populates="suppliers", cascade="all, delete")
    items = relationship("InventoryItem", back_populates="supplier")
    returns = relationship("SupplierReturn", back_populates="supplier") 