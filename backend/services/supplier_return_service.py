from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
import json

from ..models.supplier_return import SupplierReturn
from ..models.suppliers import Supplier
from ..models.inventory import InventoryItem
from ..models.users import User
from ..schemas.supplier_returns import (
    SupplierReturnCreate, 
    SupplierReturnUpdate,
    ReturnStatus,
    SupplierReturnStats
)
from ..services import BaseService


class SupplierReturnService(BaseService[SupplierReturn]):
    """Service class for supplier return operations"""
    def __init__(self, db: Session):
        super().__init__(db, SupplierReturn)
        self.db = db
    
    @staticmethod
    def generate_return_id() -> str:
        """Generate a unique return ID"""
        return f"RET-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    @staticmethod
    def create_return(db: Session, return_data: SupplierReturnCreate, created_by_id: int) -> SupplierReturn:
        """Create a new supplier return"""
        # Generate unique return ID
        return_id = SupplierReturnService.generate_return_id()
        
        # Create return object
        db_return = SupplierReturn(
            return_id=return_id,
            supplier_id=return_data.supplier_id,
            item_id=return_data.item_id,
            quantity=return_data.quantity,
            reason=return_data.reason,
            return_date=return_data.return_date,
            status=ReturnStatus.pending,
            reference=return_data.reference,
            notes=return_data.notes,
            condition=return_data.condition,
            attachments=return_data.attachments,
            created_by_id=created_by_id
        )
        
        db.add(db_return)
        db.commit()
        db.refresh(db_return)
        
        return db_return
    
    @staticmethod
    def get_return_by_id(db: Session, return_id: int) -> Optional[SupplierReturn]:
        """Get a supplier return by ID"""
        return db.query(SupplierReturn).filter(SupplierReturn.id == return_id).first()
    
    @staticmethod
    def get_return_by_return_id(db: Session, return_id: str) -> Optional[SupplierReturn]:
        """Get a supplier return by return_id"""
        return db.query(SupplierReturn).filter(SupplierReturn.return_id == return_id).first()
    
    @staticmethod
    def get_returns(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        supplier_id: Optional[int] = None,
        item_id: Optional[int] = None,
        status: Optional[ReturnStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[SupplierReturn]:
        """Get supplier returns with filtering and pagination"""
        query = db.query(SupplierReturn)
        
        # Apply filters
        if supplier_id:
            query = query.filter(SupplierReturn.supplier_id == supplier_id)
        if item_id:
            query = query.filter(SupplierReturn.item_id == item_id)
        if status:
            query = query.filter(SupplierReturn.status == status)
        if start_date:
            query = query.filter(SupplierReturn.return_date >= start_date)
        if end_date:
            query = query.filter(SupplierReturn.return_date <= end_date)
        
        return query.order_by(desc(SupplierReturn.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_return(
        db: Session, 
        return_id: int, 
        update_data: SupplierReturnUpdate,
        updated_by_id: int
    ) -> Optional[SupplierReturn]:
        """Update a supplier return"""
        db_return = db.query(SupplierReturn).filter(SupplierReturn.id == return_id).first()
        if not db_return:
            return None
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_return, field, value)
        
        # Update timestamp
        db_return.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_return)
        
        return db_return
    
    @staticmethod
    def approve_return(
        db: Session, 
        return_id: int, 
        approved_by_id: int,
        notes: Optional[str] = None
    ) -> Optional[SupplierReturn]:
        """Approve a supplier return"""
        db_return = db.query(SupplierReturn).filter(SupplierReturn.id == return_id).first()
        if not db_return:
            return None
        
        if db_return.status != ReturnStatus.pending:
            raise ValueError("Only pending returns can be approved")
        
        db_return.status = ReturnStatus.approved
        db_return.approved_by_id = approved_by_id
        db_return.notes = notes if notes else db_return.notes
        db_return.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_return)
        
        return db_return
    
    @staticmethod
    def reject_return(
        db: Session, 
        return_id: int, 
        rejected_by_id: int,
        reason: str
    ) -> Optional[SupplierReturn]:
        """Reject a supplier return"""
        db_return = db.query(SupplierReturn).filter(SupplierReturn.id == return_id).first()
        if not db_return:
            return None
        
        if db_return.status != ReturnStatus.pending:
            raise ValueError("Only pending returns can be rejected")
        
        db_return.status = ReturnStatus.rejected
        db_return.approved_by_id = rejected_by_id
        db_return.notes = f"Rejected: {reason}" if db_return.notes else f"Rejected: {reason}"
        db_return.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_return)
        
        return db_return
    
    @staticmethod
    def complete_return(
        db: Session, 
        return_id: int, 
        completed_by_id: int,
        notes: Optional[str] = None
    ) -> Optional[SupplierReturn]:
        """Complete a supplier return (mark as returned to supplier)"""
        db_return = db.query(SupplierReturn).filter(SupplierReturn.id == return_id).first()
        if not db_return:
            return None
        
        if db_return.status != ReturnStatus.approved:
            raise ValueError("Only approved returns can be completed")
        
        db_return.status = ReturnStatus.completed
        db_return.approved_by_id = completed_by_id
        db_return.notes = notes if notes else db_return.notes
        db_return.updated_at = datetime.utcnow()
        
        # Update inventory quantity (reduce stock)
        item = db.query(InventoryItem).filter(InventoryItem.id == db_return.item_id).first()
        if item:
            item.quantity = max(0, item.quantity - db_return.quantity)
            item.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_return)
        
        return db_return
    
    @staticmethod
    def delete_return(db: Session, return_id: int) -> bool:
        """Delete a supplier return (only if pending)"""
        db_return = db.query(SupplierReturn).filter(SupplierReturn.id == return_id).first()
        if not db_return:
            return False
        
        if db_return.status != ReturnStatus.pending:
            raise ValueError("Only pending returns can be deleted")
        
        db.delete(db_return)
        db.commit()
        
        return True
    
    @staticmethod
    def get_return_stats(
        db: Session,
        supplier_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> SupplierReturnStats:
        """Get supplier return statistics"""
        query = db.query(SupplierReturn)
        
        # Apply filters
        if supplier_id:
            query = query.filter(SupplierReturn.supplier_id == supplier_id)
        if start_date:
            query = query.filter(SupplierReturn.return_date >= start_date)
        if end_date:
            query = query.filter(SupplierReturn.return_date <= end_date)
        
        # Get counts by status
        total_returns = query.count()
        pending_returns = query.filter(SupplierReturn.status == ReturnStatus.pending).count()
        approved_returns = query.filter(SupplierReturn.status == ReturnStatus.approved).count()
        rejected_returns = query.filter(SupplierReturn.status == ReturnStatus.rejected).count()
        completed_returns = query.filter(SupplierReturn.status == ReturnStatus.completed).count()
        
        # Calculate total value
        total_value = 0.0
        if total_returns > 0:
            value_query = query.join(InventoryItem).with_entities(
                func.sum(SupplierReturn.quantity * InventoryItem.unit_price)
            )
            result = value_query.scalar()
            total_value = float(result) if result else 0.0
        
        # Calculate average processing time
        avg_processing_time = None
        completed_query = query.filter(SupplierReturn.status == ReturnStatus.completed)
        if completed_query.count() > 0:
            processing_times = []
            for ret in completed_query.all():
                if ret.approved_at and ret.created_at:
                    processing_time = (ret.approved_at - ret.created_at).days
                    processing_times.append(processing_time)
            
            if processing_times:
                avg_processing_time = sum(processing_times) / len(processing_times)
        
        return SupplierReturnStats(
            total_returns=total_returns,
            pending_returns=pending_returns,
            approved_returns=approved_returns,
            rejected_returns=rejected_returns,
            completed_returns=completed_returns,
            total_value=total_value,
            average_processing_time=avg_processing_time
        ) 