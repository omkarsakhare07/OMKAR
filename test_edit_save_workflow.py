#!/usr/bin/env python3
"""
Test the complete edit and save workflow
"""

from database import (
    get_user_patient_data, 
    update_user_patient_data,
    get_user_by_username
)

print("=" * 80)
print("TEST: Complete Edit and Save Workflow")
print("=" * 80)

username = "TestUser123"

# Step 1: Try to get existing data (may be None for new user)
print("\n[STEP 1] Getting initial patient data...")
initial_data = get_user_patient_data(username)
print(f"Initial data: {initial_data}")

# Step 2: Create and save new patient data
print("\n[STEP 2] Saving new patient data...")
new_data = {
    "name": "John Patient",
    "age": 35,
    "medication": "Aspirin 75mg daily, Lisinopril 10mg once daily",
    "family_contacts": ["Jane Doe - 9876543210, jane@example.com", "Bob Smith - 8765432109"],
    "doctor_email": "dr.johnson@hospital.com",
    "saved_at": "2026-01-15 20:45:00"
}

result = update_user_patient_data(username, new_data)
print(f"Save result: {result}")

# Step 3: Immediately retrieve the data back
print("\n[STEP 3] Retrieving saved data immediately...")
retrieved_data = get_user_patient_data(username)

# Step 4: Verify all fields match
print("\n[STEP 4] Verifying saved data matches...")
fields_to_check = ["name", "age", "medication", "doctor_email", "saved_at"]
all_match = True

for field in fields_to_check:
    saved_value = new_data.get(field, "NOT SET")
    retrieved_value = retrieved_data.get(field, "NOT SET") if retrieved_data else "NO DATA"
    
    match = saved_value == retrieved_value
    status = "✓" if match else "✗"
    
    print(f"  {status} {field}: saved='{saved_value}' retrieved='{retrieved_value}'")
    
    if not match:
        all_match = False

# Step 5: Verify family contacts
print("\n[STEP 5] Verifying family contacts...")
saved_contacts = new_data.get("family_contacts", [])
retrieved_contacts = retrieved_data.get("family_contacts", []) if retrieved_data else []

if saved_contacts == retrieved_contacts:
    print(f"  ✓ Family contacts match: {len(retrieved_contacts)} contact(s)")
else:
    print(f"  ✗ Family contacts mismatch!")
    print(f"    Saved: {saved_contacts}")
    print(f"    Retrieved: {retrieved_contacts}")
    all_match = False

# Step 6: Summary
print("\n" + "=" * 80)
if all_match and retrieved_data:
    print("TEST RESULT: SUCCESS - All data saved and retrieved correctly!")
else:
    print("TEST RESULT: FAILED - Some data was lost or not saved")
    print(f"\nFull retrieved data:")
    print(retrieved_data)
print("=" * 80)
