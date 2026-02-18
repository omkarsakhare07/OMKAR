"""
SMS Notification Handler for Family Alerts
Uses Twilio API for sending SMS
"""

import os
from datetime import datetime

# SMS Simulation - for demo purposes
# In production, use Twilio API

def send_sms_alert(phone_number, medication_name, dosage, reminder_count):
    """Send SMS alert to family member"""
    try:
        message = f"🚨 ALERT: Medication '{medication_name}' ({dosage}) reminder NOT STOPPED after {reminder_count} attempts! Patient needs help. Check app immediately!"
        
        # For now, we're just logging the SMS (simulating)
        # In production, integrate with Twilio:
        # from twilio.rest import Client
        # account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        # auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        #     body=message,
        #     from_=os.getenv('TWILIO_PHONE_NUMBER'),
        #     to=phone_number
        # )
        
        print(f"[SMS ALERT] To: {phone_number} | Message: {message}")
        return True
        
    except Exception as e:
        print(f"SMS Error: {e}")
        return False

def send_alert_30(family_numbers, medication_name, dosage):
    """Send SMS alert after 30 reminder attempts"""
    for number in family_numbers:
        send_sms_alert(number, medication_name, dosage, 30)
        print(f"[30-ALERT] Sent to {number} for {medication_name}")

def send_alert_40(family_numbers, medication_name, dosage):
    """Send SMS alert after 40 reminder attempts (auto-stop)"""
    for number in family_numbers:
        msg = f"⛔ CRITICAL: Medication '{medication_name}' reminder AUTO-STOPPED after 40 attempts! Patient may need immediate medical attention!"
        print(f"[40-ALERT] {msg} | Sent to {number}")
