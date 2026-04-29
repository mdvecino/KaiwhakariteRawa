#!/usr/bin/env python3
"""
Test script for the new comprehensive inventory transaction system
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_transaction_types():
    """Test that all transaction types are properly defined"""
    try:
        from backend.models.inventory import TransactionType
        
        # Test that all expected transaction types exist
        expected_types = [
            'stock_in', 'stock_out', 'transfer', 'adjustment',
            'customer_return', 'return_to_supplier', 'reservation', 'release',
            'write_off', 'stock_take', 'production_issue', 'production_receipt',
            'consignment_in', 'consignment_out', 'cycle_count',
            'audit', 'repack', 'loaned', 'borrowed'
        ]
        
        print("✅ Testing Transaction Types...")
        for tx_type in expected_types:
            if hasattr(TransactionType, tx_type):
                print(f"  ✓ {tx_type}")
            else:
                print(f"  ✗ {tx_type} - MISSING")
                return False
        
        print(f"\n✅ All {len(expected_types)} transaction types are properly defined!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing transaction types: {e}")
        return False

def test_schemas():
    """Test that the schemas include all new fields"""
    try:
        from backend.schemas.inventory import InventoryTransactionCreate, InventoryTransactionResponse
        
        print("\n✅ Testing Schemas...")
        
        # Test that new fields are in the create schema
        create_fields = InventoryTransactionCreate.__fields__.keys()
        expected_create_fields = [
            'transaction_type', 'quantity', 'related_party', 'reference', 'notes',
            'from_location', 'to_location', 'unit_price', 'total_value', 'batch_number',
            'expiry_date', 'condition', 'approved_by_id', 'approval_notes',
            'reservation_expiry', 'allocated_for', 'production_order', 'work_center',
            'consignment_terms', 'ownership_status', 'count_method', 'variance_reason',
            'transaction_date'
        ]
        
        for field in expected_create_fields:
            if field in create_fields:
                print(f"  ✓ {field} in create schema")
            else:
                print(f"  ✗ {field} - MISSING from create schema")
                return False
        
        # Test that new fields are in the response schema
        response_fields = InventoryTransactionResponse.__fields__.keys()
        expected_response_fields = [
            'id', 'created_by_id', 'created_at', 'quantity_before', 'quantity_after',
            'unit_price', 'total_value', 'batch_number', 'expiry_date', 'condition',
            'approved_by_id', 'approved_at', 'approval_notes', 'reservation_expiry',
            'allocated_for', 'production_order', 'work_center', 'consignment_terms',
            'ownership_status', 'count_method', 'variance_reason', 'transaction_date',
            'created_by_name', 'approved_by_name'
        ]
        
        for field in expected_response_fields:
            if field in response_fields:
                print(f"  ✓ {field} in response schema")
            else:
                print(f"  ✗ {field} - MISSING from response schema")
                return False
        
        print(f"\n✅ All schema fields are properly defined!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing schemas: {e}")
        return False

def test_model_fields():
    """Test that the model includes all new fields"""
    try:
        from backend.models.inventory import InventoryTransaction
        
        print("\n✅ Testing Model Fields...")
        
        # Get all column names from the model
        column_names = [column.name for column in InventoryTransaction.__table__.columns]
        
        expected_columns = [
            'id', 'item_id', 'transaction_type', 'quantity', 'related_party',
            'reference', 'notes', 'from_location', 'to_location', 'unit_price',
            'total_value', 'batch_number', 'expiry_date', 'condition',
            'approved_by_id', 'approved_at', 'approval_notes', 'reservation_expiry',
            'allocated_for', 'production_order', 'work_center', 'consignment_terms',
            'ownership_status', 'count_method', 'variance_reason', 'created_by_id',
            'created_at', 'transaction_date'
        ]
        
        for column in expected_columns:
            if column in column_names:
                print(f"  ✓ {column} in model")
            else:
                print(f"  ✗ {column} - MISSING from model")
                return False
        
        print(f"\n✅ All model fields are properly defined!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing model fields: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Comprehensive Inventory Transaction System")
    print("=" * 60)
    
    tests = [
        test_transaction_types,
        test_schemas,
        test_model_fields
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"\n❌ Test failed: {test.__name__}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The transaction system is ready to use.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 