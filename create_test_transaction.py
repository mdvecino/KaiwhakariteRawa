#!/usr/bin/env python3
"""
Script to create test transactions in the database
"""

import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def create_test_transactions():
    """Create some test transactions in the database"""
    try:
        from backend.db import get_db
        from backend.models.inventory import InventoryItem, InventoryTransaction, TransactionType
        from backend.models.users import User
        from sqlalchemy.orm import Session
        
        print("🔧 Creating test transactions...")
        
        # Get database session
        db = next(get_db())
        
        # Check if we have any users
        users = db.query(User).all()
        if not users:
            print("❌ No users found in database. Please create a user first.")
            return False
        
        # Check if we have any inventory items
        items = db.query(InventoryItem).all()
        if not items:
            print("❌ No inventory items found. Please create some items first.")
            return False
        
        # Get first user and item for testing
        test_user = users[0]
        test_item = items[0]
        
        print(f"👤 Using user: {test_user.username}")
        print(f"📦 Using item: {test_item.name}")
        
        # Create some test transactions
        test_transactions = [
            {
                'transaction_type': TransactionType.stock_in,
                'quantity': 100,
                'related_party': 'Test Supplier',
                'reference': 'PO-TEST-001',
                'notes': 'Initial stock receipt for testing',
                'unit_price': 10.50,
                'total_value': 1050.00,
                'batch_number': 'BATCH-001',
                'condition': 'Good'
            },
            {
                'transaction_type': TransactionType.stock_out,
                'quantity': 25,
                'related_party': 'Test Customer',
                'reference': 'SO-TEST-001',
                'notes': 'Sale to test customer',
                'unit_price': 15.00,
                'total_value': 375.00,
                'condition': 'Good'
            },
            {
                'transaction_type': TransactionType.transfer,
                'quantity': 10,
                'from_location': 'Main Warehouse',
                'to_location': 'Retail Store',
                'reference': 'TR-TEST-001',
                'notes': 'Transfer to retail location',
                'condition': 'Good'
            },
            {
                'transaction_type': TransactionType.adjustment,
                'quantity': 5,
                'reference': 'ADJ-TEST-001',
                'notes': 'Found additional units during count',
                'condition': 'Good'
            },
            {
                'transaction_type': TransactionType.customer_return,
                'quantity': 2,
                'related_party': 'Test Customer',
                'reference': 'RET-TEST-001',
                'notes': 'Customer returned defective items',
                'condition': 'Damaged'
            }
        ]
        
        # Create transactions with different dates
        base_date = datetime.utcnow()
        for i, tx_data in enumerate(test_transactions):
            # Create transaction
            transaction = InventoryTransaction(
                item_id=test_item.id,
                created_by_id=test_user.id,
                created_at=base_date - timedelta(days=i),
                transaction_date=base_date - timedelta(days=i),
                **tx_data
            )
            
            db.add(transaction)
            print(f"✅ Created {tx_data['transaction_type']} transaction")
        
        # Commit all transactions
        db.commit()
        print(f"\n🎉 Successfully created {len(test_transactions)} test transactions!")
        
        # Show current item quantity
        db.refresh(test_item)
        print(f"📊 Current stock for {test_item.name}: {test_item.quantity} units")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error creating test transactions: {e}")
        return False

if __name__ == "__main__":
    success = create_test_transactions()
    if success:
        print("\n🚀 You can now view these transactions in the frontend!")
        print("   Make sure to log in to the system first.")
    else:
        print("\n❌ Failed to create test transactions.")
        sys.exit(1) 