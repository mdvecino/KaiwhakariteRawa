from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.suppliers import Supplier
from ..schemas.suppliers import SupplierCreate, SupplierUpdate
from datetime import datetime
from ..services import BaseService


class SupplierService(BaseService[Supplier]):
    """Service class for supplier management operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, Supplier)
        self.db = db
    
    def create_supplier(self, supplier_data: SupplierCreate, user_id: int) -> Supplier:
        """Create a new supplier with auto-generated supplier_code if not provided"""
        # Auto-generate supplier_code if not provided
        code = supplier_data.supplier_code
        if not code:
            # Find the max existing code number
            last_supplier = self.db.query(Supplier).order_by(Supplier.id.desc()).first()
            last_code = getattr(last_supplier, "supplier_code", None) if last_supplier else None
            if last_code and isinstance(last_code, str) and last_code.startswith('SUP-'):
                try:
                    last_num = int(last_code.split('-')[1])
                except Exception:
                    last_num = 0
            else:
                last_num = 0
            code = f"SUP-{last_num + 1:03d}"
        db_supplier = Supplier(
            **supplier_data.dict(exclude={"supplier_code"}),
            supplier_code=code,
            created_by_id=user_id
        )
        self.db.add(db_supplier)
        self.db.commit()
        self.db.refresh(db_supplier)
        return db_supplier
    
    def get_supplier_by_id(self, supplier_id: int) -> Optional[Supplier]:
        """Get supplier by ID"""
        return self.get_by_id(supplier_id)
    
    def get_suppliers(self, skip: int = 0, limit: int = 100) -> List[Supplier]:
        """Get all active suppliers with pagination"""
        return self.db.query(Supplier).filter(
            Supplier.is_active.is_(True)
        ).offset(skip).limit(limit).all()
    
    def update_supplier(self, supplier_id: int, supplier_data: SupplierUpdate) -> Optional[Supplier]:
        """Update supplier information"""
        supplier = self.get_supplier_by_id(supplier_id)
        if not supplier:
            return None
        
        # Update fields
        update_data = supplier_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(supplier, field, value)
        setattr(supplier, 'updated_at', datetime.utcnow())
        self.db.commit()
        self.db.refresh(supplier)
        return supplier
    
    def delete_supplier(self, supplier_id: int) -> bool:
        """Soft delete a supplier"""
        supplier = self.get_supplier_by_id(supplier_id)
        if not supplier:
            return False
        
        setattr(supplier, 'is_active', False)
        setattr(supplier, 'updated_at', datetime.utcnow())
        self.db.commit()
        return True 