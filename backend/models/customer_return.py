from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, Text, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from .base import BaseModel
from .customers import Customer
import enum
import datetime

class CustomerReturnStatusEnum(str, enum.Enum):
    pending = 'pending'
    approved = 'approved'
    rejected = 'rejected'
    completed = 'completed'
    cancelled = 'cancelled'

class CustomerReturnConditionEnum(str, enum.Enum):
    new = 'new'
    like_new = 'like_new'
    good = 'good'
    fair = 'fair'
    poor = 'poor'
    damaged = 'damaged'
    defective = 'defective'

class CustomerReturn(BaseModel):
    __tablename__ = 'customer_returns'

    return_id = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=False)
    return_date = Column(Date, default=datetime.date.today, nullable=False)
    status = Column(Enum(CustomerReturnStatusEnum), default=CustomerReturnStatusEnum.pending, nullable=False)
    processed_by_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    reference = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    condition = Column(Enum(CustomerReturnConditionEnum), nullable=False)
    restocking = Column(Boolean, default=False, nullable=False)
    refund_amount = Column(Float, nullable=True)
    refund_processed = Column(Boolean, default=False, nullable=False)
    attachments = Column(String(255), nullable=True)
    created_by_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    customer = relationship('Customer', back_populates='returns')
    item = relationship('InventoryItem', back_populates='customer_returns')
    processed_by = relationship('User', foreign_keys=[processed_by_id], cascade='all, delete')
    created_by = relationship('User', foreign_keys=[created_by_id], cascade='all, delete') 