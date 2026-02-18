#!/usr/bin/env python3
"""List all users in the database"""

from database import load_data

data = load_data()
users = data.get("users", [])

print(f"Total users in database: {len(users)}\n")

for user in users:
    print(f"Username: {user.get('username')}")
    print(f"  Email: {user.get('email')}")
    print(f"  Has patient_data: {bool(user.get('patient_data'))}")
    if user.get('patient_data'):
        print(f"    Name: {user['patient_data'].get('name')}")
    print()
