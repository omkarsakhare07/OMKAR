def clear_all_user_data():
    """Clear only the patient_data for all users, keeping user accounts intact."""
    data = load_data()
    users = data.get("users", [])
    for user in users:
        user["patient_data"] = None
    save_data(data)

def clear_all_users():
    """Remove all users from the database"""
    data = load_data()
    data["users"] = []
    save_data(data)

import yaml
from datetime import datetime

DATA_FILE = "data.yaml"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            data = yaml.safe_load(f) or {}
            # Ensure all required keys exist
            if "medications" not in data:
                data["medications"] = []
            if "appointments" not in data:
                data["appointments"] = []
            if "users" not in data:
                data["users"] = []
            return data
    except FileNotFoundError:
        return {"medications": [], "appointments": [], "users": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        yaml.dump(data, f)

def add_medication(name, time, dosage, frequency="Daily", weekdays=None, family_emails=None, alarm_tone=1):
    data = load_data()
    new_id = max([m["id"] for m in data["medications"]], default=0) + 1
    
    # Default weekdays (all days if Daily)
    if frequency == "Daily" or weekdays is None:
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    data["medications"].append({
        "id": new_id,
        "name": name,
        "time": time,
        "dosage": dosage,
        "frequency": frequency,
        "weekdays": weekdays,
        "missed": 0,
        "active": True,
        "remind_count": 0,
        "last_reminded": None,
        "created_at": datetime.now().isoformat(),
        "family_emails": family_emails or [],
        "alarm_tone": alarm_tone,
        "alert_8_sent": False,
        "alert_10_sent": False,
        "alert_12_sent": False
    })
    save_data(data)

def get_medications():
    return load_data()["medications"]

def get_active_medications():
    """Get only active medications"""
    return [med for med in load_data()["medications"] if med.get("active", True)]

def delete_medication(med_id):
    """Delete a medication by ID"""
    data = load_data()
    data["medications"] = [med for med in data["medications"] if med["id"] != med_id]
    save_data(data)

def delete_all_medications():
    """Delete all medications"""
    data = load_data()
    data["medications"] = []
    save_data(data)

def stop_medication(med_id):
    """Stop/pause a medication (mark as inactive)"""
    data = load_data()
    for med in data["medications"]:
        if med["id"] == med_id:
            med["active"] = False
    save_data(data)

def resume_medication(med_id):
    """Resume a stopped medication"""
    data = load_data()
    for med in data["medications"]:
        if med["id"] == med_id:
            med["active"] = True
    save_data(data)

def edit_medication(med_id, name=None, time=None, dosage=None, frequency=None, weekdays=None):
    """Edit medication details"""
    data = load_data()
    for med in data["medications"]:
        if med["id"] == med_id:
            if name:
                med["name"] = name
            if time:
                med["time"] = time
            if dosage:
                med["dosage"] = dosage
            if frequency:
                med["frequency"] = frequency
            if weekdays:
                med["weekdays"] = weekdays
    save_data(data)

def increment_remind_count(med_id):
    """Increment reminder count when reminder is triggered"""
    data = load_data()
    for med in data["medications"]:
        if med["id"] == med_id:
            med["remind_count"] = med.get("remind_count", 0) + 1
            med["last_reminded"] = datetime.now().isoformat()
    save_data(data)
    return next((m for m in data["medications"] if m["id"] == med_id), None)

def set_alert_sent(med_id, alert_type):
    """Mark alert as sent"""
    data = load_data()
    for med in data["medications"]:
        if med["id"] == med_id:
            if alert_type == 8:
                med["alert_8_sent"] = True
            elif alert_type == 10:
                med["alert_10_sent"] = True
            elif alert_type == 12:
                med["alert_12_sent"] = True
    save_data(data)

def reset_remind_count(med_id):
    """Reset reminder count to 0 when manually stopped"""
    data = load_data()
    for med in data["medications"]:
        if med["id"] == med_id:
            med["remind_count"] = 0
            med["alert_8_sent"] = False
            med["alert_10_sent"] = False
            med["alert_12_sent"] = False
    save_data(data)

# ---------- USER MANAGEMENT FUNCTIONS ----------

def add_user(username, email, password):
    """Add a new user to the database"""
    data = load_data()
    
    # Check if user already exists
    if get_user_by_username(username) or get_user_by_email(email):
        return False, "User already exists"
    
    user_id = max([u.get("id", 0) for u in data.get("users", [])], default=0) + 1
    
    data["users"].append({
        "id": user_id,
        "username": username,
        "email": email,
        "password": password,  # In production, this should be hashed
        "patient_data": None,
        "created_at": datetime.now().isoformat(),
        "last_login": None
    })
    save_data(data)
    return True, "User created successfully"

def get_user_by_username(username):
    """Get user by username"""
    data = load_data()
    users = data.get("users", [])
    return next((user for user in users if user["username"] == username), None)

def get_user_by_email(email):
    """Get user by email"""
    data = load_data()
    users = data.get("users", [])
    return next((user for user in users if user["email"] == email), None)

def authenticate_user(username_or_email, password):
    """Authenticate user with username/email and password"""
    data = load_data()
    users = data.get("users", [])
    
    # Try to find user by username or email
    user = None
    for u in users:
        if u["username"] == username_or_email or u["email"] == username_or_email:
            user = u
            break
    
    if not user:
        return None, "User not found"
    
    if user["password"] != password:
        return None, "Incorrect password"
    
    # Update last login
    user["last_login"] = datetime.now().isoformat()
    save_data(data)
    
    return user, "Login successful"

def update_user_patient_data(username, patient_data):
    """Update user's patient data"""
    data = load_data()
    users = data.get("users", [])
    
    for user in users:
        if user["username"] == username:
            user["patient_data"] = patient_data
            user["patient_data"]["updated_at"] = datetime.now().isoformat()
            save_data(data)
            return True
    
    return False

def get_user_patient_data(username):
    """Get user's patient data"""
    user = get_user_by_username(username)
    if user and user.get("patient_data"):
        return user["patient_data"]
    return None

# ---------- PATIENT DISEASE MANAGEMENT ----------

def add_disease_to_patient(username, disease_name, severity="Medium"):
    """Add a new disease to patient's profile"""
    data = load_data()
    users = data.get("users", [])
    
    for user in users:
        if user["username"] == username:
            if user.get("patient_data") is None:
                # Initialize with complete patient data structure
                user["patient_data"] = {
                    "name": user.get("username", "Patient"),
                    "age": 25,
                    "medication": "",
                    "doctor_email": "",
                    "family_contacts": [],
                    "diseases": [],
                    "created_at": datetime.now().isoformat()
                }
            
            if "diseases" not in user["patient_data"]:
                user["patient_data"]["diseases"] = []
            
            # Check if disease already exists
            disease_id = max([d.get("id", 0) for d in user["patient_data"]["diseases"]], default=0) + 1
            
            user["patient_data"]["diseases"].append({
                "id": disease_id,
                "name": disease_name,
                "severity": severity,
                "added_at": datetime.now().isoformat()
            })
            
            user["patient_data"]["updated_at"] = datetime.now().isoformat()
            save_data(data)
            return True
    
    return False

def update_disease(username, disease_id, disease_name=None, severity=None):
    """Update an existing disease in patient's profile"""
    data = load_data()
    users = data.get("users", [])
    
    for user in users:
        if user["username"] == username:
            if user.get("patient_data") and "diseases" in user["patient_data"]:
                for disease in user["patient_data"]["diseases"]:
                    if disease["id"] == disease_id:
                        if disease_name:
                            disease["name"] = disease_name
                        if severity:
                            disease["severity"] = severity
                        disease["updated_at"] = datetime.now().isoformat()
                        user["patient_data"]["updated_at"] = datetime.now().isoformat()
                        save_data(data)
                        return True
    
    return False

def delete_disease(username, disease_id):
    """Delete a disease from patient's profile"""
    data = load_data()
    users = data.get("users", [])
    
    for user in users:
        if user["username"] == username:
            if user.get("patient_data") and "diseases" in user["patient_data"]:
                user["patient_data"]["diseases"] = [d for d in user["patient_data"]["diseases"] if d["id"] != disease_id]
                user["patient_data"]["updated_at"] = datetime.now().isoformat()
                save_data(data)
                return True
    
    return False

def get_patient_diseases(username):
    """Get all diseases for a patient"""
    user = get_user_by_username(username)
    if user and user.get("patient_data") and "diseases" in user["patient_data"]:
        return user["patient_data"]["diseases"]
    return []