#!/usr/bin/env python3
from database import get_user_by_username, update_user_patient_data, get_user_patient_data

# Test with correct username
username = "Babu"
user = get_user_by_username(username)
print(f"User found: {bool(user)}")
print(f"Username in DB: {user.get('username') if user else 'N/A'}")

# Try to update
test_data = {
    "name": "Test Updated Name",
    "age": 30,
    "medication": "New medicine list",
    "family_contacts": ["New Contact - 1234567890"],
    "doctor_email": "test@hospital.com",
    "saved_at": "2026-01-15 21:30:00"
}

result = update_user_patient_data(username, test_data)
print(f"\nUpdate result: {result}")

# Verify
retrieved = get_user_patient_data(username)
print(f"Name after save: {retrieved.get('name') if retrieved else 'FAILED'}")
