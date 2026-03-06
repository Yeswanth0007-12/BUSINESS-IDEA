#!/usr/bin/env python3
"""
Debug CSV Upload Issues
"""

import requests
import json

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "csvdebug@example.com"
TEST_PASSWORD = "testpass123"

def test_csv_upload():
    # Register/Login
    print("Logging in...")
    login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    
    # Try to register first
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "company_name": "CSV Debug Company"
    }
    requests.post(f"{BASE_URL}/auth/register", json=register_data)
    
    # Login
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return
    
    token = response.json()["access_token"]
    headers = {'Authorization': f'Bearer {token}'}
    
    print("✓ Logged in successfully\n")
    
    # Test 1: Simple CSV with correct format
    print("=" * 60)
    print("TEST 1: Simple CSV (3 boxes)")
    print("=" * 60)
    
    csv_content = """name,length_cm,width_cm,height_cm,cost_per_unit
Small Box,20,15,10,1.50
Medium Box,35,25,15,2.50
Large Box,50,40,20,3.50"""
    
    print("CSV Content:")
    print(csv_content)
    print()
    
    files = {'file': ('boxes.csv', csv_content, 'text/csv')}
    response = requests.post(f"{BASE_URL}/boxes/bulk-upload", files=files, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # Test 2: CSV with many rows
    print("=" * 60)
    print("TEST 2: Large CSV (10 boxes)")
    print("=" * 60)
    
    csv_lines = ["name,length_cm,width_cm,height_cm,cost_per_unit"]
    for i in range(1, 11):
        csv_lines.append(f"Box {i},{20+i*5},{15+i*3},{10+i*2},{1.0+i*0.5}")
    
    csv_content = "\n".join(csv_lines)
    print(f"CSV has {len(csv_lines)} lines (including header)")
    print()
    
    files = {'file': ('boxes_large.csv', csv_content, 'text/csv')}
    response = requests.post(f"{BASE_URL}/boxes/bulk-upload", files=files, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Created: {result.get('created_count', 0)}")
    print(f"Errors: {len(result.get('errors', []) or [])}")
    
    if result.get('errors'):
        print("\nError Details:")
        for error in result['errors'][:10]:  # Show first 10 errors
            print(f"  - {error}")
    print()
    
    # Test 3: Check what boxes exist
    print("=" * 60)
    print("TEST 3: Verify Boxes in Database")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/boxes", headers=headers)
    if response.status_code == 200:
        boxes = response.json()
        print(f"Total boxes in database: {len(boxes)}")
        if boxes:
            print("\nSample boxes:")
            for box in boxes[:5]:
                print(f"  - {box['name']}: {box['length_cm']}x{box['width_cm']}x{box['height_cm']} @ ${box['cost_per_unit']}")
    else:
        print(f"Failed to get boxes: {response.status_code}")

if __name__ == "__main__":
    test_csv_upload()
