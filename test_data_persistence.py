#!/usr/bin/env python3
"""
Test script to verify patient data persistence and display
Tests the complete flow: Edit → Save → Retrieve → Display
"""

from database import (
    get_user_patient_data, 
    update_user_patient_data,
    get_user_by_username
)
import json

print("=" * 80)
print("TEST: Patient Data Persistence and Display")
print("=" * 80)

# Test 1: Get existing user data
print("\n[TEST 1] Retrieving existing patient data for user 'Omkar'")
username = "Omkar"
patient_data = get_user_patient_data(username)

if patient_data:
    print(f"✅ Patient data found for {username}")
    print(f"   Name: {patient_data.get('name', 'N/A')}")
    print(f"   Age: {patient_data.get('age', 'N/A')}")
    print(f"   Doctor Email: {patient_data.get('doctor_email', 'NOT SET')}")
    print(f"   Medication: {patient_data.get('medication', 'N/A')[:50]}...")
    print(f"   Family Contacts: {len(patient_data.get('family_contacts', []))} contact(s)")
    print(f"   Saved At: {patient_data.get('saved_at', 'N/A')}")
else:
    print(f"❌ No patient data found for {username}")

# Test 2: Update patient data with new doctor_email
print("\n[TEST 2] Updating patient data with new doctor email")
test_data = {
    "name": patient_data.get('name', 'Test User') if patient_data else 'Test User',
    "age": patient_data.get('age', 25) if patient_data else 25,
    "doctor_email": "dr.smith@hospital.com",
    "medication": "Test medication 500mg daily",
    "family_contacts": ["John - 9876543210, john@gmail.com"],
    "saved_at": "2026-01-15 23:30:00"
}

if update_user_patient_data(username, test_data):
    print(f"✅ Successfully updated patient data for {username}")
else:
    print(f"❌ Failed to update patient data for {username}")

# Test 3: Retrieve updated data immediately
print("\n[TEST 3] Retrieving updated patient data")
updated_data = get_user_patient_data(username)

if updated_data:
    print(f"✅ Updated patient data retrieved for {username}")
    print(f"   Name: {updated_data.get('name', 'N/A')}")
    print(f"   Age: {updated_data.get('age', 'N/A')}")
    print(f"   Doctor Email: {updated_data.get('doctor_email', 'NOT SET')}")
    print(f"   Medication: {updated_data.get('medication', 'N/A')}")
    print(f"   Saved At: {updated_data.get('saved_at', 'N/A')}")
    
    # Verify doctor_email was saved correctly
    if updated_data.get('doctor_email') == "dr.smith@hospital.com":
        print(f"\n✅ SUCCESS: doctor_email was saved and retrieved correctly!")
    else:
        print(f"\n❌ ISSUE: doctor_email mismatch!")
        print(f"   Expected: dr.smith@hospital.com")
        print(f"   Got: {updated_data.get('doctor_email', 'EMPTY')}")
else:
    print(f"❌ Failed to retrieve updated patient data")

# Test 4: Verify data in database structure
print("\n[TEST 4] Checking database structure")
user = get_user_by_username(username)
if user and user.get('patient_data'):
    db_data = user['patient_data']
    print(f"✅ Database contains patient_data for {username}")
    print(f"   Keys in patient_data: {list(db_data.keys())}")
    if 'doctor_email' in db_data:
        print(f"   ✅ doctor_email field exists: '{db_data['doctor_email']}'")
    else:
        print(f"   ❌ doctor_email field is MISSING from database!")
else:
    print(f"❌ User {username} not found in database")

print("\n" + "=" * 80)
print("Test Complete!")
print("=" * 80)
