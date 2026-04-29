from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..db import get_db
from ..auth.dependencies import get_current_user
from ..models.users import User
from ..services.supplier_return_service import SupplierReturnService
from ..schemas.supplier_returns import (
    SupplierReturnCreate,
    SupplierReturnUpdate,
    SupplierReturnResponse,
    SupplierReturnList,
    SupplierReturnStats,
    ReturnStatus
)
from ..models.supplier_return import SupplierReturn
from ..models.suppliers import Supplier
from ..models.inventory import InventoryItem

router = APIRouter(prefix="/api/supplier-returns", tags=["supplier-returns"])


@router.post("/", response_model=SupplierReturnResponse, status_code=status.HTTP_201_CREATED)
def create_supplier_return(
    return_data: SupplierReturnCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new supplier return"""
    try:
        return_obj = SupplierReturnService.create_return(
            db=db,
            return_data=return_data,
            created_by_id=current_user.id
        )
        
        # Get related data for response
        supplier = db.query(Supplier).filter(Supplier.id == return_obj.supplier_id).first()
        item = db.query(InventoryItem).filter(InventoryItem.id == return_obj.item_id).first()
        
        return SupplierReturnResponse(
            id=return_obj.id,
            return_id=return_obj.return_id,
            supplier_id=return_obj.supplier_id,
            item_id=return_obj.item_id,
            quantity=return_obj.quantity,
            reason=return_obj.reason,
            return_date=return_obj.return_date,
            status=return_obj.status,
            reference=return_obj.reference,
            notes=return_obj.notes,
            condition=return_obj.condition,
            attachments=return_obj.attachments,
            approved_by_id=return_obj.approved_by_id,
            created_at=return_obj.created_at,
            updated_at=return_obj.updated_at,
            supplier_name=supplier.name if supplier else None,
            item_name=item.name if item else None,
            approved_by_name=None
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{return_id}", response_model=SupplierReturnResponse)
def get_supplier_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a supplier return by ID"""
    return_obj = SupplierReturnService.get_return_by_id(db=db, return_id=return_id)
    if not return_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Return not found")
    
    # Get related data for response
    supplier = db.query(Supplier).filter(Supplier.id == return_obj.supplier_id).first()
    item = db.query(InventoryItem).filter(InventoryItem.id == return_obj.item_id).first()
    approved_by = db.query(User).filter(User.id == return_obj.approved_by_id).first() if return_obj.approved_by_id else None
    
    return SupplierReturnResponse(
        id=return_obj.id,
        return_id=return_obj.return_id,
        supplier_id=return_obj.supplier_id,
        item_id=return_obj.item_id,
        quantity=return_obj.quantity,
        reason=return_obj.reason,
        return_date=return_obj.return_date,
        status=return_obj.status,
        reference=return_obj.reference,
        notes=return_obj.notes,
        condition=return_obj.condition,
        attachments=return_obj.attachments,
        approved_by_id=return_obj.approved_by_id,
        created_at=return_obj.created_at,
        updated_at=return_obj.updated_at,
        supplier_name=supplier.name if supplier else None,
        item_name=item.name if item else None,
        approved_by_name=approved_by.full_name if approved_by else None
    )


@router.get("/by-return-id/{return_id}", response_model=SupplierReturnResponse)
def get_supplier_return_by_return_id(
    return_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a supplier return by return_id"""
    return_obj = SupplierReturnService.get_return_by_return_id(db=db, return_id=return_id)
    if not return_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Return not found")
    
    # Get related data for response
    supplier = db.query(Supplier).filter(Supplier.id == return_obj.supplier_id).first()
    item = db.query(InventoryItem).filter(InventoryItem.id == return_obj.item_id).first()
    approved_by = db.query(User).filter(User.id == return_obj.approved_by_id).first() if return_obj.approved_by_id else None
    
    return SupplierReturnResponse(
        id=return_obj.id,
        return_id=return_obj.return_id,
        supplier_id=return_obj.supplier_id,
        item_id=return_obj.item_id,
        quantity=return_obj.quantity,
        reason=return_obj.reason,
        return_date=return_obj.return_date,
        status=return_obj.status,
        reference=return_obj.reference,
        notes=return_obj.notes,
        condition=return_obj.condition,
        attachments=return_obj.attachments,
        approved_by_id=return_obj.approved_by_id,
        created_at=return_obj.created_at,
        updated_at=return_obj.updated_at,
        supplier_name=supplier.name if supplier else None,
        item_name=item.name if item else None,
        approved_by_name=approved_by.full_name if approved_by else None
    )


@router.get("/", response_model=SupplierReturnList)
def get_supplier_returns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    supplier_id: Optional[int] = Query(None),
    item_id: Optional[int] = Query(None),
    status: Optional[ReturnStatus] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get supplier returns with filtering and pagination"""
    returns = SupplierReturnService.get_returns(
        db=db,
        skip=skip,
        limit=limit,
        supplier_id=supplier_id,
        item_id=item_id,
        status=status,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get total count for pagination
    total_query = db.query(SupplierReturn)
    if supplier_id:
        total_query = total_query.filter(SupplierReturn.supplier_id == supplier_id)
    if item_id:
        total_query = total_query.filter(SupplierReturn.item_id == item_id)
    if status:
        total_query = total_query.filter(SupplierReturn.status == status)
    if start_date:
        total_query = total_query.filter(SupplierReturn.return_date >= start_date)
    if end_date:
        total_query = total_query.filter(SupplierReturn.return_date <= end_date)
    
    total = total_query.count()
    total_pages = (total + limit - 1) // limit
    
    # Build response with related data
    return_responses = []
    for return_obj in returns:
        supplier = db.query(Supplier).filter(Supplier.id == return_obj.supplier_id).first()
        item = db.query(InventoryItem).filter(InventoryItem.id == return_obj.item_id).first()
        approved_by = db.query(User).filter(User.id == return_obj.approved_by_id).first() if return_obj.approved_by_id else None
        
        return_responses.append(SupplierReturnResponse(
            id=return_obj.id,
            return_id=return_obj.return_id,
            supplier_id=return_obj.supplier_id,
            item_id=return_obj.item_id,
            quantity=return_obj.quantity,
            reason=return_obj.reason,
            return_date=return_obj.return_date,
            status=return_obj.status,
            reference=return_obj.reference,
            notes=return_obj.notes,
            condition=return_obj.condition,
            attachments=return_obj.attachments,
            approved_by_id=return_obj.approved_by_id,
            created_at=return_obj.created_at,
            updated_at=return_obj.updated_at,
            supplier_name=supplier.name if supplier else None,
            item_name=item.name if item else None,
            approved_by_name=approved_by.full_name if approved_by else None
        ))
    
    return SupplierReturnList(
        returns=return_responses,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        total_pages=total_pages
    )


@router.put("/{return_id}", response_model=SupplierReturnResponse)
def update_supplier_return(
    return_id: int,
    update_data: SupplierReturnUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a supplier return"""
    return_obj = SupplierReturnService.update_return(
        db=db,
        return_id=return_id,
        update_data=update_data,
        updated_by_id=current_user.id
    )
    
    if not return_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Return not found")
    
    # Get related data for response
    supplier = db.query(Supplier).filter(Supplier.id == return_obj.supplier_id).first()
    item = db.query(InventoryItem).filter(InventoryItem.id == return_obj.item_id).first()
    approved_by = db.query(User).filter(User.id == return_obj.approved_by_id).first() if return_obj.approved_by_id else None
    
    return SupplierReturnResponse(
        id=return_obj.id,
        return_id=return_obj.return_id,
        supplier_id=return_obj.supplier_id,
        item_id=return_obj.item_id,
        quantity=return_obj.quantity,
        reason=return_obj.reason,
        return_date=return_obj.return_date,
        status=return_obj.status,
        reference=return_obj.reference,
        notes=return_obj.notes,
        condition=return_obj.condition,
        attachments=return_obj.attachments,
        approved_by_id=return_obj.approved_by_id,
        created_at=return_obj.created_at,
        updated_at=return_obj.updated_at,
        supplier_name=supplier.name if supplier else None,
        item_name=item.name if item else None,
        approved_by_name=approved_by.full_name if approved_by else None
    )


@router.post("/{return_id}/approve", response_model=SupplierReturnResponse)
def approve_supplier_return(
    return_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve a supplier return"""
    try:
        return_obj = SupplierReturnService.approve_return(
            db=db,
            return_id=return_id,
            approved_by_id=current_user.id,
            notes=notes
        )
        
        if not return_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Return not found")
        
        # Get related data for response
        supplier = db.query(Supplier).filter(Supplier.id == return_obj.supplier_id).first()
        item = db.query(InventoryItem).filter(InventoryItem.id == return_obj.item_id).first()
        
        return SupplierReturnResponse(
            id=return_obj.id,
            return_id=return_obj.return_id,
            supplier_id=return_obj.supplier_id,
            item_id=return_obj.item_id,
            quantity=return_obj.quantity,
            reason=return_obj.reason,
            return_date=return_obj.return_date,
            status=return_obj.status,
            reference=return_obj.reference,
            notes=return_obj.notes,
            condition=return_obj.condition,
            attachments=return_obj.attachments,
            approved_by_id=return_obj.approved_by_id,
            created_at=return_obj.created_at,
            updated_at=return_obj.updated_at,
            supplier_name=supplier.name if supplier else None,
            item_name=item.name if item else None,
            approved_by_name=current_user.full_name
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{return_id}/reject", response_model=SupplierReturnResponse)
def reject_supplier_return(
    return_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reject a supplier return"""
    try:
        return_obj = SupplierReturnService.reject_return(
            db=db,
            return_id=return_id,
            rejected_by_id=current_user.id,
            reason=reason
        )
        
        if not return_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Return not found")
        
        # Get related data for response
        supplier = db.query(Supplier).filter(Supplier.id == return_obj.supplier_id).first()
        item = db.query(InventoryItem).filter(InventoryItem.id == return_obj.item_id).first()
        
        return SupplierReturnResponse(
            id=return_obj.id,
            return_id=return_obj.return_id,
            supplier_id=return_obj.supplier_id,
            item_id=return_obj.item_id,
            quantity=return_obj.quantity,
            reason=return_obj.reason,
            return_date=return_obj.return_date,
            status=return_obj.status,
            reference=return_obj.reference,
            notes=return_obj.notes,
            condition=return_obj.condition,
            attachments=return_obj.attachments,
            approved_by_id=return_obj.approved_by_id,
            created_at=return_obj.created_at,
            updated_at=return_obj.updated_at,
            supplier_name=supplier.name if supplier else None,
            item_name=item.name if item else None,
            approved_by_name=current_user.full_name
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{return_id}/complete", response_model=SupplierReturnResponse)
def complete_supplier_return(
    return_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete a supplier return (mark as returned to supplier)"""
    try:
        return_obj = SupplierReturnService.complete_return(
            db=db,
            return_id=return_id,
            completed_by_id=current_user.id,
            notes=notes
        )
        
        if not return_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Return not found")
        
        # Get related data for response
        supplier = db.query(Supplier).filter(Supplier.id == return_obj.supplier_id).first()
        item = db.query(InventoryItem).filter(InventoryItem.id == return_obj.item_id).first()
        
        return SupplierReturnResponse(
            id=return_obj.id,
            return_id=return_obj.return_id,
            supplier_id=return_obj.supplier_id,
            item_id=return_obj.item_id,
            quantity=return_obj.quantity,
            reason=return_obj.reason,
            return_date=return_obj.return_date,
            status=return_obj.status,
            reference=return_obj.reference,
            notes=return_obj.notes,
            condition=return_obj.condition,
            attachments=return_obj.attachments,
            approved_by_id=return_obj.approved_by_id,
            created_at=return_obj.created_at,
            updated_at=return_obj.updated_at,
            supplier_name=supplier.name if supplier else None,
            item_name=item.name if item else None,
            approved_by_name=current_user.full_name
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{return_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a supplier return (only if pending)"""
    try:
        success = SupplierReturnService.delete_return(db=db, return_id=return_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Return not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/stats/overview", response_model=SupplierReturnStats)
def get_supplier_return_stats(
    supplier_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get supplier return statistics"""
    return SupplierReturnService.get_return_stats(
        db=db,
        supplier_id=supplier_id,
        start_date=start_date,
        end_date=end_date
    ) 