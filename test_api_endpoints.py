#!/usr/bin/env python3
"""
Test script to verify API endpoints are working
"""

import requests
import json
import time

def test_api_endpoints():
    """Test the transaction API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing API Endpoints")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: Test inventory endpoint
    try:
        response = requests.get(f"{base_url}/api/inventory/", timeout=5)
        print(f"✅ Inventory endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   📦 Items found: {len(data.get('items', []))}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Inventory endpoint failed: {e}")
    
    # Test 3: Test transactions endpoint
    try:
        response = requests.get(f"{base_url}/api/inventory/transactions/all", timeout=5)
        print(f"✅ Transactions endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Transactions found: {len(data)}")
            if len(data) > 0:
                print(f"   📋 Sample transaction: {json.dumps(data[0], indent=2, default=str)}")
        else:
            print(f"   ❌ Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Transactions endpoint failed: {e}")
    
    # Test 4: Test suppliers endpoint
    try:
        response = requests.get(f"{base_url}/api/suppliers/", timeout=5)
        print(f"✅ Suppliers endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   🏢 Suppliers found: {len(data)}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Suppliers endpoint failed: {e}")
    
    # Test 5: Test customers endpoint
    try:
        response = requests.get(f"{base_url}/api/customers/", timeout=5)
        print(f"✅ Customers endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   👥 Customers found: {len(data)}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Customers endpoint failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 API Testing Complete!")
    return True

if __name__ == "__main__":
    # Wait a moment for servers to start
    print("⏳ Waiting for servers to start...")
    time.sleep(3)
    
    test_api_endpoints() 