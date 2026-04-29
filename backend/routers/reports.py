from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Dict, Any, List, Optional
from ..db import get_db
from ..auth.dependencies import get_current_user
from ..models.users import User
from ..models.inventory import InventoryItem, InventoryTransaction
from ..services.inventory_service import InventoryService
from datetime import datetime
from sqlalchemy import extract

router = APIRouter()

MAORI_CATEGORIES = [
    'rongoa', 'taonga', 'whakairo', 'raranga', 'kai', 'kakahu'
]


@router.get("/inventory/summary")
async def get_inventory_summary(
    maori: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive inventory summary for reports"""
    inventory_service = InventoryService(db)
    
    # Get all active items
    all_items = db.query(InventoryItem).filter(
        InventoryItem.is_active.is_(True)
    ).all()
    
    # Calculate summary statistics
    total_items = len(all_items)
    total_value = sum(item.total_value or 0 for item in all_items)
    total_quantity = sum(item.quantity or 0 for item in all_items)
    
    # Get low stock items with detailed info
    low_stock_items = inventory_service.get_low_stock_items()
    low_stock_data = []
    
    for item in low_stock_items:
        min_qty = item.min_quantity if item.min_quantity is not None and item.min_quantity > 0 else 5
        shortage = min_qty - (item.quantity or 0)
        reorder_value = (item.unit_price or 0) * shortage if shortage > 0 else 0
        
        low_stock_data.append({
            "id": item.id,
            "name": item.name,
            "sku": item.sku,
            "category": item.category,
            "current_quantity": item.quantity or 0,
            "min_quantity": min_qty,
            "shortage": shortage,
            "unit_price": item.unit_price or 0,
            "reorder_value": reorder_value,
            "location": item.location,
            "supplier": item.supplier.name if item.supplier is not None else None
        })
    
    # Category breakdown
    category_stats = {}
    for item in all_items:
        cat = str(item.category)
        if cat not in category_stats:
            category_stats[cat] = {
                "count": 0,
                "total_value": 0,
                "total_quantity": 0
            }
        category_stats[cat]["count"] += 1
        category_stats[cat]["total_value"] += item.total_value or 0
        category_stats[cat]["total_quantity"] += item.quantity or 0
    
    return {
        "summary": {
            "total_items": total_items,
            "total_value": total_value,
            "total_quantity": total_quantity,
            "low_stock_count": len(low_stock_items),
            "categories_count": len(category_stats)
        },
        "low_stock_items": low_stock_data,
        "category_breakdown": category_stats
    }


@router.get("/inventory/low-stock-detailed")
async def get_low_stock_detailed(
    maori: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed low stock report data"""
    inventory_service = InventoryService(db)
    if maori:
        low_stock_items = [item for item in inventory_service.get_low_stock_items() if item.category in MAORI_CATEGORIES]
    else:
        low_stock_items = inventory_service.get_low_stock_items()
    
    detailed_data = []
    total_shortage_value = 0
    
    for item in low_stock_items:
        min_qty = item.min_quantity if item.min_quantity is not None and item.min_quantity > 0 else 5
        shortage = min_qty - (item.quantity or 0)
        reorder_value = (item.unit_price or 0) * shortage if shortage > 0 else 0
        total_shortage_value += reorder_value
        
        detailed_data.append({
            "id": item.id,
            "name": item.name,
            "sku": item.sku,
            "barcode": item.barcode,
            "category": item.category,
            "subcategory": item.subcategory,
            "current_quantity": item.quantity or 0,
            "min_quantity": min_qty,
            "max_quantity": item.max_quantity,
            "shortage": shortage,
            "unit_price": item.unit_price or 0,
            "reorder_value": reorder_value,
            "location": item.location,
            "supplier_name": item.supplier.name if item.supplier is not None else None,
            "status": item.status,
            "last_updated": item.updated_at.isoformat() if item.updated_at is not None else None
        })
    
    return {
        "low_stock_items": detailed_data,
        "summary": {
            "total_items": len(detailed_data),
            "total_shortage_value": total_shortage_value,
            "average_shortage": sum(item["shortage"] for item in detailed_data) / len(detailed_data) if detailed_data else 0
        }
    }


@router.get("/inventory/analytics")
async def get_inventory_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get inventory analytics data"""
    inventory_service = InventoryService(db)
    
    # Get all active items
    all_items = db.query(InventoryItem).filter(
        InventoryItem.is_active.is_(True)
    ).all()
    
    # Basic stats
    total_items = len(all_items)
    total_value = sum(item.total_value or 0 for item in all_items)
    total_quantity = sum(item.quantity or 0 for item in all_items)
    
    # Value distribution
    value_ranges = {
        "low": 0,      # < $100
        "medium": 0,   # $100 - $1000
        "high": 0      # > $1000
    }
    
    for item in all_items:
        value = item.total_value or 0
        if value < 100:
            value_ranges["low"] += 1
        elif value < 1000:
            value_ranges["medium"] += 1
        else:
            value_ranges["high"] += 1
    
    # Stock level analysis
    stock_levels = {
        "out_of_stock": 0,      # quantity = 0
        "low_stock": 0,         # quantity <= min_quantity
        "adequate": 0,          # quantity > min_quantity
        "overstocked": 0        # quantity > max_quantity
    }
    
    for item in all_items:
        qty = item.quantity or 0
        min_qty = item.min_quantity if item.min_quantity is not None and item.min_quantity > 0 else 5
        max_qty = item.max_quantity
        
        if qty == 0:
            stock_levels["out_of_stock"] += 1
        elif min_qty is not None and qty <= min_qty:
            stock_levels["low_stock"] += 1
        elif max_qty is not None and qty > max_qty:
            stock_levels["overstocked"] += 1
        else:
            stock_levels["adequate"] += 1
    
    # Category analysis
    category_analysis = {}
    for item in all_items:
        cat = str(item.category)
        if cat not in category_analysis:
            category_analysis[cat] = {
                "count": 0,
                "total_value": 0,
                "total_quantity": 0,
                "low_stock_count": 0
            }
        
        category_analysis[cat]["count"] += 1
        category_analysis[cat]["total_value"] += item.total_value or 0
        category_analysis[cat]["total_quantity"] += item.quantity or 0
        
        min_qty = item.min_quantity if item.min_quantity is not None and item.min_quantity > 0 else 5
        if min_qty is not None and (item.quantity or 0) <= min_qty:
            category_analysis[cat]["low_stock_count"] += 1
    
    return {
        "overview": {
            "total_items": total_items,
            "total_value": total_value,
            "total_quantity": total_quantity,
            "average_value_per_item": total_value / total_items if total_items > 0 else 0
        },
        "value_distribution": value_ranges,
        "stock_levels": stock_levels,
        "category_analysis": category_analysis
    }


@router.get("/export/csv")
async def export_csv(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export inventory data as CSV (stub)"""
    # TODO: Implement CSV export logic
    return {"message": "CSV export not implemented yet"}


@router.get("/analytics")
async def get_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics data (stub)"""
    # TODO: Implement analytics logic
    return {"message": "Analytics not implemented yet"} 


@router.get("/revenue-report")
async def get_revenue_report(
    maori: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real revenue report based on stock_out transactions"""
    # Get all stock_out transactions
    stock_out_txs = db.query(InventoryTransaction).filter(
        InventoryTransaction.transaction_type == 'stock_out'
    ).all()

    total_revenue = 0
    monthly_revenue = 0
    by_category = {"General": 0, "Maori": 0}
    now = datetime.now()

    for tx in stock_out_txs:
        item = tx.item
        if not item or not item.unit_price:
            continue
        revenue = float(item.unit_price) * float(tx.quantity)
        total_revenue += revenue
        # Monthly revenue: this month and year
        if tx.created_at and tx.created_at.year == now.year and tx.created_at.month == now.month:
            monthly_revenue += revenue
        # Category breakdown
        if maori:
            if item.category in MAORI_CATEGORIES:
                by_category["Maori"] += revenue
            else:
                by_category["General"] += revenue
        else:
            if item.category in MAORI_CATEGORIES:
                by_category["Maori"] += revenue
            else:
                by_category["General"] += revenue

    return {
        "total_revenue": total_revenue,
        "monthly_revenue": monthly_revenue,
        "by_category": by_category
    } 