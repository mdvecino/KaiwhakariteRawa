from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from ..db import get_db
from ..auth.dependencies import get_current_user, require_manager
from ..services.supplier_service import SupplierService
from ..schemas.suppliers import SupplierCreate, SupplierUpdate, SupplierResponse
from ..models.users import User

router = APIRouter()


@router.post("/", response_model=SupplierResponse)
async def create_supplier(
    supplier_data: SupplierCreate,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Create a new supplier"""
    supplier_service = SupplierService(db)
    supplier = supplier_service.create_supplier(supplier_data, current_user.id)
    return supplier


@router.get("/", response_model=List[SupplierResponse])
async def get_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all suppliers"""
    supplier_service = SupplierService(db)
    return supplier_service.get_suppliers(skip=skip, limit=limit)


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get supplier by ID"""
    supplier_service = SupplierService(db)
    supplier = supplier_service.get_supplier_by_id(supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    return supplier


@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Update supplier"""
    supplier_service = SupplierService(db)
    supplier = supplier_service.update_supplier(supplier_id, supplier_data)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    return supplier


@router.delete("/{supplier_id}")
async def delete_supplier(
    supplier_id: int,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Delete supplier"""
    supplier_service = SupplierService(db)
    success = supplier_service.delete_supplier(supplier_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    return {"message": "Supplier deleted successfully"} 