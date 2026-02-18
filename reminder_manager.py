"""
Advanced Medicine Reminder Manager
Handles saving, loading, and managing medicine reminders with notifications
"""

import streamlit as st
from datetime import datetime, time as datetime_time
from database import (add_medication, get_medications, edit_medication, 
                      delete_medication, load_data, save_data)
import json
from pathlib import Path

REMINDERS_FILE = "reminders_settings.json"

def load_reminders():
    """Load all reminder settings from JSON file"""
    try:
        if Path(REMINDERS_FILE).exists():
            with open(REMINDERS_FILE, "r") as f:
                return json.load(f)
        return {"reminders": [], "last_updated": None}
    except Exception as e:
        st.warning(f"Error loading reminders: {e}")
        return {"reminders": [], "last_updated": None}

def save_reminders(reminders_data):
    """Save reminder settings to JSON file"""
    try:
        reminders_data["last_updated"] = datetime.now().isoformat()
        with open(REMINDERS_FILE, "w") as f:
            json.dump(reminders_data, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving reminders: {e}")
        return False

def create_reminder(medicine_name, reminder_time, dosage, frequency="Daily", 
                   weekdays=None, notes="", notification_enabled=True):
    """
    Create a new medicine reminder
    
    Args:
        medicine_name: Name of the medicine
        reminder_time: Time as HH:MM format
        dosage: Dosage information
        frequency: Daily, Weekly, or Custom
        weekdays: List of days for weekly reminders
        notes: Additional notes
        notification_enabled: Enable notifications for this reminder
    
    Returns:
        Success status and reminder ID
    """
    try:
        # Add to database (for tracking active medications)
        add_medication(
            name=medicine_name,
            time=reminder_time,
            dosage=dosage,
            frequency=frequency,
            weekdays=weekdays or ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            family_emails=[]
        )
        
        # Load and update reminders settings
        reminders = load_reminders()
        
        new_reminder = {
            "id": max([r.get("id", 0) for r in reminders.get("reminders", [])], default=0) + 1,
            "medicine_name": medicine_name,
            "time": reminder_time,
            "dosage": dosage,
            "frequency": frequency,
            "weekdays": weekdays or ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "notes": notes,
            "notification_enabled": notification_enabled,
            "created_at": datetime.now().isoformat(),
            "last_taken": None,
            "notifications_sent": [],
            "alarm_enabled": True,
            "vibration_enabled": True,
            "sound_enabled": True,
            "pop_notification_enabled": True,
            "active": True
        }
        
        reminders["reminders"].append(new_reminder)
        
        if save_reminders(reminders):
            return True, new_reminder["id"]
        return False, None
        
    except Exception as e:
        st.error(f"Error creating reminder: {e}")
        return False, None

def update_reminder(reminder_id, **kwargs):
    """Update an existing reminder"""
    try:
        reminders = load_reminders()
        
        for reminder in reminders.get("reminders", []):
            if reminder["id"] == reminder_id:
                reminder.update(kwargs)
                reminder["updated_at"] = datetime.now().isoformat()
                save_reminders(reminders)
                return True
        
        return False
    except Exception as e:
        st.error(f"Error updating reminder: {e}")
        return False

def delete_reminder(reminder_id):
    """Delete a reminder"""
    try:
        reminders = load_reminders()
        reminders["reminders"] = [r for r in reminders.get("reminders", []) if r["id"] != reminder_id]
        save_reminders(reminders)
        return True
    except Exception as e:
        st.error(f"Error deleting reminder: {e}")
        return False

def get_active_reminders():
    """Get all active reminders"""
    reminders = load_reminders()
    return [r for r in reminders.get("reminders", []) if r.get("active", True)]

def get_reminders_for_time(hour, minute):
    """Get reminders that match the given time"""
    reminders = get_active_reminders()
    matching = []
    
    for reminder in reminders:
        r_hour, r_minute = map(int, reminder["time"].split(":"))
        if r_hour == hour and r_minute == minute:
            matching.append(reminder)
    
    return matching

def mark_reminder_taken(reminder_id):
    """Mark a reminder as taken"""
    try:
        update_reminder(reminder_id, last_taken=datetime.now().isoformat())
        return True
    except:
        return False

def log_notification(reminder_id, notification_type="pop"):
    """Log that a notification was sent"""
    try:
        reminders = load_reminders()
        
        for reminder in reminders.get("reminders", []):
            if reminder["id"] == reminder_id:
                if "notifications_sent" not in reminder:
                    reminder["notifications_sent"] = []
                
                reminder["notifications_sent"].append({
                    "type": notification_type,
                    "sent_at": datetime.now().isoformat()
                })
                
                save_reminders(reminders)
                return True
        
        return False
    except Exception as e:
        print(f"Error logging notification: {e}")
        return False

def get_reminder_stats():
    """Get reminder statistics"""
    reminders = get_active_reminders()
    stats = {
        "total": len(reminders),
        "today": 0,
        "this_week": 0,
        "active": sum(1 for r in reminders if r.get("active", True))
    }
    
    now = datetime.now()
    
    for reminder in reminders:
        r_hour, r_minute = map(int, reminder["time"].split(":"))
        
        # Check if today
        if r_hour > now.hour or (r_hour == now.hour and r_minute > now.minute):
            stats["today"] += 1
        
        # Check this week
        if reminder.get("frequency", "Daily") == "Daily":
            stats["this_week"] += 7
        elif reminder.get("frequency") == "Weekly":
            stats["this_week"] += 1
    
    return stats

def get_next_reminder():
    """Get the next upcoming reminder"""
    reminders = get_active_reminders()
    
    if not reminders:
        return None
    
    now = datetime.now()
    next_rem = None
    
    for reminder in reminders:
        r_hour, r_minute = map(int, reminder["time"].split(":"))
        r_time = datetime.now().replace(hour=r_hour, minute=r_minute, second=0, microsecond=0)
        
        if r_time > now:
            if next_rem is None or r_time < datetime.now().replace(hour=int(next_rem["time"].split(":")[0]), 
                                                                    minute=int(next_rem["time"].split(":")[1])):
                next_rem = reminder
    
    return next_rem
