#!/usr/bin/env python3
from database import get_user_patient_data

data = get_user_patient_data('Omkar')
if data:
    print("Doctor Email:", data.get('doctor_email', 'NOT SET'))
    print("Name:", data.get('name', 'NOT SET'))
    print("Age:", data.get('age', 'NOT SET'))
    print("Medication:", data.get('medication', 'NOT SET')[:50])
    print("\nData retrieval: SUCCESS")
else:
    print("ERROR: No data found")
