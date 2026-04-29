from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel
from .suppliers import Supplier
import enum
import datetime

class ReturnStatusEnum(str, enum.Enum):
    pending = 'pending'
    approved = 'approved'
    rejected = 'rejected'
    completed = 'completed'
    cancelled = 'cancelled'

class ConditionEnum(str, enum.Enum):
    new = 'new'
    like_new = 'like_new'
    good = 'good'
    fair = 'fair'
    poor = 'poor'
    damaged = 'damaged'
    defective = 'defective'

class SupplierReturn(BaseModel):
    __tablename__ = 'supplier_returns'

    return_id = Column(String(50), unique=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=False)
    return_date = Column(Date, default=datetime.date.today, nullable=False)
    status = Column(Enum(ReturnStatusEnum), default=ReturnStatusEnum.pending, nullable=False)
    approved_by_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    reference = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    condition = Column(Enum(ConditionEnum), nullable=False)
    attachments = Column(String(255), nullable=True)
    created_by_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    supplier = relationship('Supplier', back_populates='returns')
    item = relationship('InventoryItem', back_populates='returns')
    approved_by = relationship('User', foreign_keys=[approved_by_id], cascade='all, delete')
    created_by = relationship('User', foreign_keys=[created_by_id], cascade='all, delete') 