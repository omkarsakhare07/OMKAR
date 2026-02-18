#!/usr/bin/env python3
"""
Test script for database user management functions
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import add_user, authenticate_user, update_user_patient_data, get_user_patient_data
from datetime import datetime

def test_database_functions():
    print("🧪 Testing Database User Management Functions")
    print("=" * 50)

    # Test 1: Add new user
    print("\n1. Testing user creation...")
    success, message = add_user("testuser123", "test@example.com", "TestPass123!")
    print(f"   Result: {success} - {message}")

    # Test 2: Authenticate user
    print("\n2. Testing user authentication...")
    user, message = authenticate_user("testuser123", "TestPass123!")
    print(f"   Result: {user is not None} - {message}")

    # Test 3: Wrong password
    print("\n3. Testing wrong password...")
    user, message = authenticate_user("testuser123", "WrongPass123!")
    print(f"   Result: {user is not None} - {message}")

    # Test 4: Non-existent user
    print("\n4. Testing non-existent user...")
    user, message = authenticate_user("nonexistent", "TestPass123!")
    print(f"   Result: {user is not None} - {message}")

    # Test 5: Update patient data
    print("\n5. Testing patient data update...")
    patient_data = {
        "name": "John Doe",
        "age": 45,
        "disease": "Diabetes",
        "medication": "Metformin 500mg twice daily",
        "family_contacts": ["Jane Doe - 123-456-7890, jane@email.com"],
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    result = update_user_patient_data("testuser123", patient_data)
    print(f"   Result: {result}")

    # Test 6: Retrieve patient data
    print("\n6. Testing patient data retrieval...")
    retrieved_data = get_user_patient_data("testuser123")
    if retrieved_data:
        print(f"   Retrieved: Name={retrieved_data.get('name')}, Age={retrieved_data.get('age')}, Disease={retrieved_data.get('disease')}")
    else:
        print("   No data retrieved")

    print("\n✅ All tests completed!")

if __name__ == "__main__":
    test_database_functions()