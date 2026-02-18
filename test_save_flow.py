#!/usr/bin/env python3
"""
Test to verify the complete save flow for existing user
"""

from database import get_user_patient_data, update_user_patient_data, get_user_by_username
import json

print("=" * 80)
print("Testing Database Save Flow for Existing User")
print("=" * 80)

username = "Omkar"

# Step 1: Check if user exists
print(f"\n[STEP 1] Checking if user '{username}' exists...")
user = get_user_by_username(username)
if user:
    print(f"✓ User found in database")
    print(f"  Username: {user.get('username')}")
    print(f"  Email: {user.get('email')}")
else:
    print(f"✗ User NOT found in database!")
    print("Cannot proceed with test")
    exit(1)

# Step 2: Get current patient data
print(f"\n[STEP 2] Getting current patient data for '{username}'...")
current_data = get_user_patient_data(username)
if current_data:
    print(f"✓ Current patient data found")
    print(f"  Name: {current_data.get('name')}")
    print(f"  Age: {current_data.get('age')}")
    print(f"  Doctor Email: {current_data.get('doctor_email')}")
else:
    print(f"! No current patient data (this is ok for new users)")

# Step 3: Prepare new data to save
print(f"\n[STEP 3] Preparing new patient data to save...")
new_patient_data = {
    "name": "Omkar Updated",
    "age": 26,
    "medication": "Updated Medication List - Aspirin 100mg",
    "family_contacts": ["John Doe - 9876543210, john@gmail.com"],
    "doctor_email": "newdoctor@hospital.com",
    "saved_at": "2026-01-15 21:00:00"
}
print(f"✓ New data prepared:")
for key, value in new_patient_data.items():
    print(f"  {key}: {value}")

# Step 4: Save to database
print(f"\n[STEP 4] Saving new patient data to database...")
save_result = update_user_patient_data(username, new_patient_data)
print(f"Save Result: {save_result}")

if not save_result:
    print("✗ SAVE FAILED!")
    print("update_user_patient_data returned False")
    exit(1)

print("✓ Save returned True")

# Step 5: Immediately verify the save
print(f"\n[STEP 5] Verifying saved data (immediate read)...")
retrieved_data = get_user_patient_data(username)

if not retrieved_data:
    print("✗ VERIFICATION FAILED - No data retrieved!")
    exit(1)

print(f"✓ Data retrieved successfully")

# Step 6: Compare saved vs retrieved
print(f"\n[STEP 6] Comparing saved vs retrieved data...")
all_match = True

for key in new_patient_data.keys():
    saved_value = new_patient_data[key]
    retrieved_value = retrieved_data.get(key, "MISSING")
    
    match = saved_value == retrieved_value
    status = "✓" if match else "✗"
    
    print(f"{status} {key}")
    if not match:
        print(f"   Saved:     {saved_value}")
        print(f"   Retrieved: {retrieved_value}")
        all_match = False

# Step 7: Check in raw user object
print(f"\n[STEP 7] Checking raw user data from get_user_by_username...")
user_again = get_user_by_username(username)
if user_again and user_again.get('patient_data'):
    print(f"✓ patient_data exists in user object")
    print(f"  Keys: {list(user_again['patient_data'].keys())}")
    print(f"  Name in user data: {user_again['patient_data'].get('name')}")
else:
    print(f"✗ patient_data missing from user object!")
    all_match = False

# Summary
print("\n" + "=" * 80)
if all_match:
    print("TEST RESULT: SUCCESS - All data saved and retrieved correctly!")
else:
    print("TEST RESULT: FAILED - Some data was not saved correctly")
print("=" * 80)
