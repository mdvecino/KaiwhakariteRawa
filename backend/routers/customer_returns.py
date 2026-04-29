from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from ..models.customer_return import CustomerReturn, CustomerReturnStatusEnum
from ..models.customers import Customer
from ..models.inventory import InventoryItem
from ..models.users import User
from ..schemas.customer_returns import (
    CustomerReturnCreate, 
    CustomerReturnUpdate, 
    CustomerReturnResponse,
    CustomerReturnList,
    CustomerReturnStats
)
from ..db import get_db
from ..auth.dependencies import get_current_user

router = APIRouter(prefix="/customer-returns", tags=["customer-returns"])

def generate_return_id():
    """Generate a unique return ID"""
    return f"CR{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

@router.get("/", response_model=CustomerReturnList)
def list_customer_returns(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List customer returns with optional filtering"""
    query = db.query(CustomerReturn).options(
        joinedload(CustomerReturn.customer),
        joinedload(CustomerReturn.item),
        joinedload(CustomerReturn.processed_by),
        joinedload(CustomerReturn.created_by)
    )
    
    if status:
        query = query.filter(CustomerReturn.status == status)
    if customer_id:
        query = query.filter(CustomerReturn.customer_id == customer_id)
    
    total = query.count()
    returns = query.offset(skip).limit(limit).all()
    
    # Convert to response format with related data
    return_data = []
    for ret in returns:
        return_dict = {
            "id": ret.id,
            "return_id": ret.return_id,
            "customer_id": ret.customer_id,
            "item_id": ret.item_id,
            "quantity": ret.quantity,
            "reason": ret.reason,
            "return_date": ret.return_date,
            "status": ret.status,
            "processed_by_id": ret.processed_by_id,
            "reference": ret.reference,
            "notes": ret.notes,
            "condition": ret.condition,
            "restocking": ret.restocking,
            "refund_amount": ret.refund_amount,
            "refund_processed": ret.refund_processed,
            "attachments": ret.attachments,
            "created_at": ret.created_at,
            "updated_at": ret.updated_at,
            "customer_name": ret.customer.name if ret.customer else None,
            "customer_email": ret.customer.email if ret.customer else None,
            "item_name": ret.item.name if ret.item else None,
            "processed_by_name": ret.processed_by.name if ret.processed_by else None
        }
        return_data.append(CustomerReturnResponse(**return_dict))
    
    return CustomerReturnList(
        returns=return_data,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        total_pages=(total + limit - 1) // limit
    )

@router.get("/{return_id}", response_model=CustomerReturnResponse)
def get_customer_return(return_id: str, db: Session = Depends(get_db)):
    """Get a specific customer return by return_id"""
    return_obj = db.query(CustomerReturn).options(
        joinedload(CustomerReturn.customer),
        joinedload(CustomerReturn.item),
        joinedload(CustomerReturn.processed_by),
        joinedload(CustomerReturn.created_by)
    ).filter(CustomerReturn.return_id == return_id).first()
    
    if not return_obj:
        raise HTTPException(status_code=404, detail="Customer return not found")
    
    return_dict = {
        "id": return_obj.id,
        "return_id": return_obj.return_id,
        "customer_id": return_obj.customer_id,
        "item_id": return_obj.item_id,
        "quantity": return_obj.quantity,
        "reason": return_obj.reason,
        "return_date": return_obj.return_date,
        "status": return_obj.status,
        "processed_by_id": return_obj.processed_by_id,
        "reference": return_obj.reference,
        "notes": return_obj.notes,
        "condition": return_obj.condition,
        "restocking": return_obj.restocking,
        "refund_amount": return_obj.refund_amount,
        "refund_processed": return_obj.refund_processed,
        "attachments": return_obj.attachments,
        "created_at": return_obj.created_at,
        "updated_at": return_obj.updated_at,
        "customer_name": return_obj.customer.name if return_obj.customer else None,
        "customer_email": return_obj.customer.email if return_obj.customer else None,
        "item_name": return_obj.item.name if return_obj.item else None,
        "processed_by_name": return_obj.processed_by.name if return_obj.processed_by else None
    }
    
    return CustomerReturnResponse(**return_dict)

@router.post("/", response_model=CustomerReturnResponse)
def create_customer_return(
    return_data: CustomerReturnCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new customer return"""
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == return_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Verify item exists
    item = db.query(InventoryItem).filter(InventoryItem.id == return_data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    # Create return object
    db_return = CustomerReturn(
        return_id=generate_return_id(),
        created_by_id=current_user.id,
        **return_data.dict()
    )
    
    db.add(db_return)
    db.commit()
    db.refresh(db_return)
    
    # Return with related data
    return_dict = {
        "id": db_return.id,
        "return_id": db_return.return_id,
        "customer_id": db_return.customer_id,
        "item_id": db_return.item_id,
        "quantity": db_return.quantity,
        "reason": db_return.reason,
        "return_date": db_return.return_date,
        "status": db_return.status,
        "processed_by_id": db_return.processed_by_id,
        "reference": db_return.reference,
        "notes": db_return.notes,
        "condition": db_return.condition,
        "restocking": db_return.restocking,
        "refund_amount": db_return.refund_amount,
        "refund_processed": db_return.refund_processed,
        "attachments": db_return.attachments,
        "created_at": db_return.created_at,
        "updated_at": db_return.updated_at,
        "customer_name": customer.name,
        "customer_email": customer.email,
        "item_name": item.name,
        "processed_by_name": None
    }
    
    return CustomerReturnResponse(**return_dict)

@router.put("/{return_id}", response_model=CustomerReturnResponse)
def update_customer_return(
    return_id: str,
    return_data: CustomerReturnUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a customer return"""
    db_return = db.query(CustomerReturn).filter(CustomerReturn.return_id == return_id).first()
    if not db_return:
        raise HTTPException(status_code=404, detail="Customer return not found")
    
    # Update fields
    update_data = return_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_return, key, value)
    
    db_return.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_return)
    
    # Return with related data
    return get_customer_return(return_id, db)

@router.delete("/{return_id}")
def delete_customer_return(
    return_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a customer return"""
    db_return = db.query(CustomerReturn).filter(CustomerReturn.return_id == return_id).first()
    if not db_return:
        raise HTTPException(status_code=404, detail="Customer return not found")
    
    db.delete(db_return)
    db.commit()
    return {"message": "Customer return deleted successfully"}

@router.get("/stats/overview", response_model=CustomerReturnStats)
def get_customer_return_stats(db: Session = Depends(get_db)):
    """Get customer return statistics"""
    total_returns = db.query(CustomerReturn).count()
    pending_returns = db.query(CustomerReturn).filter(CustomerReturn.status == CustomerReturnStatusEnum.pending).count()
    approved_returns = db.query(CustomerReturn).filter(CustomerReturn.status == CustomerReturnStatusEnum.approved).count()
    rejected_returns = db.query(CustomerReturn).filter(CustomerReturn.status == CustomerReturnStatusEnum.rejected).count()
    completed_returns = db.query(CustomerReturn).filter(CustomerReturn.status == CustomerReturnStatusEnum.completed).count()
    
    total_refund_amount = db.query(func.sum(CustomerReturn.refund_amount)).filter(
        CustomerReturn.refund_amount.isnot(None)
    ).scalar() or 0.0
    
    # Calculate average processing time for completed returns
    completed_returns_data = db.query(CustomerReturn).filter(
        CustomerReturn.status == CustomerReturnStatusEnum.completed
    ).all()
    
    if completed_returns_data:
        total_days = 0
        for ret in completed_returns_data:
            if ret.created_at and ret.updated_at:
                days = (ret.updated_at - ret.created_at).days
                total_days += days
        average_processing_time = total_days / len(completed_returns_data)
    else:
        average_processing_time = None
    
    return CustomerReturnStats(
        total_returns=total_returns,
        pending_returns=pending_returns,
        approved_returns=approved_returns,
        rejected_returns=rejected_returns,
        completed_returns=completed_returns,
        total_refund_amount=total_refund_amount,
        average_processing_time=average_processing_time
    ) 