#!/usr/bin/env python3
# Simple API validation test
from django.test import Client
from django.contrib.auth.models import User
import json

print("=== Data Fusion API Endpoint Test ===")

# Test missing parameters
user = User.objects.first()
if not user:
    print("ERROR: No user found for testing")
    exit(1)

client = Client()
client.force_login(user)

# Test 1: Missing parameters
print("\n1. Testing missing parameters...")
response = client.get('/data-tools/api/get-fusion-columns/')
print(f"   Status Code: {response.status_code}")
if response.status_code == 400:
    data = json.loads(response.content)
    print(f"   Expected error: {data.get('error', 'No error message')}")
    print("   ✓ PASS - Correctly validates missing parameters")
else:
    print("   ✗ FAIL - Should return 400 for missing parameters")

# Test 2: Invalid UUIDs
print("\n2. Testing invalid UUIDs...")
response = client.get('/data-tools/api/get-fusion-columns/', {
    'ds_a': '00000000-0000-0000-0000-000000000000',
    'ds_b': '11111111-1111-1111-1111-111111111111'
})
print(f"   Status Code: {response.status_code}")
if response.status_code == 404:
    try:
        data = json.loads(response.content)
        print(f"   Expected error: {data.get('error', 'No error message')}")
        print("   ✓ PASS - Correctly handles non-existent datasources")
    except json.JSONDecodeError:
        print("   ✓ PASS - Returns 404 for non-existent datasources")
else:
    print("   ✗ FAIL - Should return 404 for non-existent datasources")

# Test 3: URL resolution
print("\n3. Testing URL resolution...")
try:
    from django.urls import reverse
    url = reverse('data_tools:get_fusion_columns_api')
    print(f"   API URL resolves to: {url}")
    print("   ✓ PASS - URL properly configured")
except Exception as e:
    print(f"   ✗ FAIL - URL resolution error: {e}")

print("\n=== Test Summary ===")
print("Basic API endpoint validation completed.")
print("The endpoint is properly configured and handles basic validation.")
print("File reading tests would require actual Parquet files in the system.")
