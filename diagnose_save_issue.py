#!/usr/bin/env python3
"""
Comprehensive Diagnostic for Save Issues
This script helps identify why patient data saves are failing
"""

from database import load_data, get_user_by_username, update_user_patient_data, get_user_patient_data
import json

print("=" * 80)
print("CAREMED - Patient Data Save Diagnostic")
print("=" * 80)

# Part 1: Database Structure
print("\n[1] DATABASE STRUCTURE CHECK")
print("-" * 80)

data = load_data()
print(f"✓ Database loaded")
print(f"  Total users: {len(data.get('users', []))}")
print(f"  Total medications: {len(data.get('medications', []))}")

# Part 2: Users in Database
print("\n[2] USERS IN DATABASE")
print("-" * 80)

users = data.get('users', [])
for idx, user in enumerate(users, 1):
    print(f"\nUser #{idx}:")
    print(f"  Username: {user.get('username')}")
    print(f"  Email: {user.get('email')}")
    print(f"  Has patient_data: {bool(user.get('patient_data'))}")
    
    if user.get('patient_data'):
        pdata = user['patient_data']
        print(f"    Patient Name: {pdata.get('name', 'N/A')}")
        print(f"    Patient Age: {pdata.get('age', 'N/A')}")
        print(f"    Doctor Email: {pdata.get('doctor_email', 'N/A')}")
        print(f"    Family Contacts: {len(pdata.get('family_contacts', []))} contact(s)")

# Part 3: Test Save Operation
print("\n[3] TEST SAVE OPERATION")
print("-" * 80)

if users:
    test_username = users[0]['username']
    print(f"Testing with user: '{test_username}'")
    
    # Create test data
    test_data = {
        "name": "DIAGNOSTIC TEST - " + users[0]['patient_data'].get('name', 'User') if users[0].get('patient_data') else "Test User",
        "age": 25,
        "medication": "Diagnostic test - Aspirin 100mg",
        "family_contacts": ["Test Contact - 9999999999"],
        "doctor_email": "diagnostic@test.com",
        "saved_at": "2026-01-15 21:00:00"
    }
    
    print(f"\nAttempting to save...")
    result = update_user_patient_data(test_username, test_data)
    print(f"  Save result: {result}")
    
    if result:
        print(f"  ✓ Save succeeded")
        
        # Verify
        retrieved = get_user_patient_data(test_username)
        if retrieved and retrieved.get('name'):
            print(f"  ✓ Data retrieved successfully")
            print(f"    Saved name: {test_data['name']}")
            print(f"    Retrieved name: {retrieved.get('name')}")
            
            if retrieved.get('name') == test_data['name']:
                print(f"  ✓ Data matches!")
            else:
                print(f"  ✗ Data mismatch!")
        else:
            print(f"  ✗ Failed to retrieve data after save")
    else:
        print(f"  ✗ Save failed")

# Part 4: Recommendations
print("\n[4] RECOMMENDATIONS")
print("-" * 80)

if not users:
    print("⚠ No users in database!")
    print("  → Create a user account first via the login/register page")
elif not users[0].get('patient_data'):
    print("⚠ User has no patient data yet!")
    print("  → Fill in patient details via the Patient Details form")
else:
    print("✓ User and patient data exist")
    print("  → If save is failing, check:")
    print("    1. Form field values are being captured (not empty)")
    print("    2. Username in session matches database username")
    print("    3. Browser console for JavaScript errors")
    print("    4. Streamlit terminal for Python errors")

print("\n" + "=" * 80)
