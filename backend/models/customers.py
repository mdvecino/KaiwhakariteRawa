from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from .base import Base

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    phone = Column(String(30), nullable=True)
    address = Column(String(200), nullable=True)
    iwi = Column(String(100), nullable=True)  # Māori tribe/affiliation
    whakapapa = Column(String(500), nullable=True)  # Genealogy/lineage
    tikanga_notes = Column(String(500), nullable=True)  # Cultural protocols
    kaupapa_notes = Column(String(500), nullable=True)  # Purpose/intent
    region = Column(String(100), nullable=True)  # Geographic region
    bank_name = Column(String(100), nullable=True)
    account_name = Column(String(100), nullable=True)
    account_number = Column(String(50), nullable=True)
    branch = Column(String(50), nullable=True)
    swift_bic = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    returns = relationship('CustomerReturn', back_populates='customer') 