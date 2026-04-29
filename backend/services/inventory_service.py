from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from ..models.inventory import (
    InventoryItem, ItemStatus, ItemCategory, InventoryTransaction
)
from ..models.suppliers import Supplier
from ..schemas.inventory import InventoryItemCreate, InventoryItemUpdate
from datetime import datetime
import logging
from ..services import BaseService


class InventoryService(BaseService[InventoryItem]):
    """Service class for inventory management operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, InventoryItem)
        self.db = db
    
    def create_item(self, item_data: InventoryItemCreate, 
                    user_id: int) -> InventoryItem:
        """Create a new inventory item"""
        # Auto-generate SKU if not provided
        sku = item_data.sku
        if not sku:
            cat = str(item_data.category)[:3].upper()
            # Find the max id for this category
            last_item = self.db.query(InventoryItem).filter(
                InventoryItem.category == item_data.category
            ).order_by(InventoryItem.id.desc()).first()
            next_num = (last_item.id + 1) if last_item else 1
            sku = f"{cat}-{next_num:04d}"
        
        # Check if SKU or barcode already exists (only if provided)
        existing_item = None
        if sku:
            existing_item = self.db.query(InventoryItem).filter(
                InventoryItem.sku == sku
            ).first()
        if existing_item:
            raise ValueError("SKU already exists")
            
        if item_data.barcode:
            existing_item = self.db.query(InventoryItem).filter(
                InventoryItem.barcode == item_data.barcode
            ).first()
            if existing_item:
                raise ValueError("Barcode already exists")
        
        # Calculate total value
        total_value = None
        if item_data.unit_price and item_data.quantity:
            total_value = item_data.unit_price * item_data.quantity
        
        # Create item - convert to dict and handle enums properly
        item_dict = item_data.dict()
        item_dict['sku'] = sku
        item_dict.pop('total_value', None)  # Remove total_value if present
        
        # Ensure is_active is set to True by default
        item_dict['is_active'] = True
        
        db_item = InventoryItem(
            **item_dict,
            total_value=total_value,
            created_by_id=user_id
        )
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item
    
    def get_item_by_id(self, item_id: int) -> Optional[InventoryItem]:
        """Get inventory item by ID"""
        return self.get_by_id(item_id)
    
    def get_item_by_sku(self, sku: str) -> Optional[InventoryItem]:
        """Get inventory item by SKU"""
        return self.db.query(InventoryItem).filter(
            InventoryItem.sku == sku
        ).first()
    
    def get_item_by_barcode(self, barcode: str) -> Optional[InventoryItem]:
        """Get inventory item by barcode"""
        return self.db.query(InventoryItem).filter(
            InventoryItem.barcode == barcode
        ).first()
    
    def get_items(self, skip: int = 0, limit: int = 100, 
                  category: Optional[ItemCategory] = None,
                  status: Optional[ItemStatus] = None) -> List[InventoryItem]:
        """Get inventory items with filters"""
        query = self.db.query(InventoryItem).filter(
            InventoryItem.is_active.is_(True)  # Only return active items
        )
        
        if category:
            query = query.filter(InventoryItem.category == category)
        if status:
            query = query.filter(InventoryItem.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    def update_item(self, item_id: int, 
                    item_data: InventoryItemUpdate) -> Optional[InventoryItem]:
        """Update inventory item"""
        item = self.get_item_by_id(item_id)
        if not item:
            return None
        
        # Update fields
        update_data = item_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        
        # Recalculate total value if unit_price or quantity changed
        if 'unit_price' in update_data or 'quantity' in update_data:
            if item.unit_price is not None and item.quantity is not None:
                item.total_value = float(item.unit_price) * float(item.quantity)
        
        setattr(item, 'updated_at', datetime.utcnow())
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def delete_item(self, item_id: int) -> bool:
        """Soft delete an inventory item"""
        item = self.get_item_by_id(item_id)
        if not item:
            return False
        
        setattr(item, 'is_active', False)
        setattr(item, 'updated_at', datetime.utcnow())
        self.db.commit()
        return True
    
    def update_quantity(self, item_id: int, 
                       new_quantity: int) -> Optional[InventoryItem]:
        """Update item quantity"""
        item = self.get_item_by_id(item_id)
        if not item:
            return None
        
        setattr(item, 'quantity', new_quantity)
        if item.unit_price is not None:
            item.total_value = float(item.unit_price) * float(new_quantity)
        
        setattr(item, 'updated_at', datetime.utcnow())
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_low_stock_items(self) -> List[InventoryItem]:
        """Get items with quantity below minimum"""
        # Debug: Check all items first
        all_items = self.db.query(InventoryItem).filter(
            InventoryItem.is_active.is_(True)
        ).all()
        
        logging.debug(f"Total active items: {len(all_items)}")
        
        # Check items with explicit low stock condition
        low_stock_items = []
        for item in all_items:
            # Use default min_quantity of 5 if not set
            min_qty = item.min_quantity if item.min_quantity is not None and item.min_quantity > 0 else 5
            
            logging.debug(f"{item.name} - Qty: {item.quantity}, Min: {item.min_quantity} (using {min_qty})")
            
            if item.quantity is not None and item.quantity <= min_qty and getattr(item, 'stock_alert', True):
                low_stock_items.append(item)
                logging.debug(f"  -> LOW STOCK: {item.name}")
        
        logging.debug(f"Found {len(low_stock_items)} low stock items")
        return low_stock_items
    
    def get_maori_items(self) -> List[InventoryItem]:
        """Get items with Māori cultural significance"""
        # Define Māori cultural categories
        maori_categories = ['taonga', 'raranga', 'whakairo', 'rongoa', 'kai', 'kakahu']
        
        return self.db.query(InventoryItem).filter(
            and_(
                or_(
                    # Items in Māori cultural categories
                    InventoryItem.category.in_(maori_categories),
                    # Items with Māori cultural fields filled
                    InventoryItem.iwi.isnot(None),
                    InventoryItem.tapu_status.is_(True),
                    InventoryItem.is_sacred.is_(True),
                    InventoryItem.korero.isnot(None),
                    InventoryItem.whakapapa.isnot(None),
                    InventoryItem.tikanga_notes.isnot(None),
                    InventoryItem.cultural_notes.isnot(None),
                    InventoryItem.item_origin.isnot(None),
                    InventoryItem.maori_name.isnot(None),
                    InventoryItem.cultural_significance.isnot(None),
                    InventoryItem.kaitiaki.isnot(None)
                ),
                InventoryItem.is_active.is_(True)
            )
        ).all()
    
    def get_tapu_items(self) -> List[InventoryItem]:
        """Get items with tapu status"""
        return self.db.query(InventoryItem).filter(
            and_(
                InventoryItem.tapu_status.is_(True),
                InventoryItem.is_active.is_(True)
            )
        ).all()
    
    def get_inventory_stats(self) -> Dict[str, Any]:
        """Get inventory statistics"""
        total_items = self.db.query(func.count(InventoryItem.id)).scalar()
        total_value = self.db.query(
            func.sum(InventoryItem.total_value)
        ).scalar() or 0
        low_stock_count = len(self.get_low_stock_items())
        maori_items_count = len(self.get_maori_items())
        
        # Add supplier and transaction counts
        total_suppliers = self.db.query(func.count(Supplier.id)).filter(
            Supplier.is_active.is_(True)
        ).scalar()
        total_transactions = self.db.query(func.count(InventoryTransaction.id)).scalar()

        # Mock revenue calculation (replace with real sales data if available)
        total_revenue = total_value * 0.3
        monthly_revenue = total_revenue * 0.1

        return {
            "total_items": total_items,
            "total_value": total_value,
            "low_stock_count": low_stock_count,
            "maori_items_count": maori_items_count,
            "total_suppliers": total_suppliers,
            "total_transactions": total_transactions,
            "total_revenue": total_revenue,
            "monthly_revenue": monthly_revenue
        } 