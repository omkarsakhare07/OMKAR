"""
Email Notification Handler for Family Alerts
Sends real emails via Gmail SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email_alert(email_address, subject, body):
    """Send email alert to family member"""
    try:
        # For testing - use your Gmail credentials
        sender_email = "caremedai.alert@gmail.com"  # Change this
        sender_password = "your_app_password_here"  # Change this - use Gmail App Password
        
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = email_address
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))
        
        # Send email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email_address, message.as_string())
        
        print(f"[EMAIL SENT] To: {email_address}")
        return True
        
    except Exception as e:
        print(f"[EMAIL FAILED] Error: {e}")
        # For testing without Gmail setup
        print(f"[EMAIL ALERT SIMULATION] To: {email_address} | Subject: {subject}")
        return False

def send_alert_8(family_emails, medication_name, dosage, doctor_email=""):
    """Send warning at 8 reminder attempts to family and doctor"""
    subject = f"⚠️ CareMed Alert: {medication_name} - WARNING"
    body = f"""
    <h2>⚠️ Warning Alert</h2>
    <p>Medication <b>{medication_name}</b> ({dosage}) reminder has been triggered <b>8 times</b> and still not taken.</p>
    <p>If not taken/stopped within 2 more attempts, family will receive notification.</p>
    <p><strong>Please check on the patient immediately.</strong></p>
    <hr>
    <p><em>CareMed_AI Medication Reminder System</em></p>
    """
    
    # Send to family members
    for email in family_emails:
        send_email_alert(email, subject, body)
        print(f"[8-ALERT] Warning sent to {email} for {medication_name}")
    
    # Send to doctor/provider if available
    if doctor_email and doctor_email.strip():
        send_email_alert(doctor_email, subject, body)
        print(f"[8-ALERT] Warning sent to doctor {doctor_email} for {medication_name}")

def send_alert_10(family_emails, medication_name, dosage):
    """Send alert at 10 reminder attempts"""
    subject = f"🚨 CareMed URGENT: {medication_name} - NOT TAKEN"
    body = f"""
    <h2>🚨 URGENT ALERT</h2>
    <p><strong>Medication '{medication_name}' ({dosage}) reminder has been triggered 10 TIMES and still not taken!</strong></p>
    <p><strong>Patient needs immediate assistance.</strong></p>
    <p>Reminder will AUTO-STOP after 12 more attempts.</p>
    <p><strong>Action Required: Check on patient NOW</strong></p>
    <hr>
    <p><em>CareMed_AI Medication Reminder System</em></p>
    """
    
    for email in family_emails:
        send_email_alert(email, subject, body)
        print(f"[10-ALERT] Urgent alert sent to {email} for {medication_name}")

def send_alert_12(family_emails, medication_name, dosage, doctor_email=""):
    """Send critical alert at 12 reminder attempts (auto-stop) to family and doctor"""
    subject = f"⛔ CareMed CRITICAL: {medication_name} - AUTO-STOPPED"
    body = f"""
    <h2>⛔ CRITICAL ALERT</h2>
    <p><strong>Medication '{medication_name}' ({dosage}) reminder has been AUTO-STOPPED after 12 attempts!</strong></p>
    <p><strong>Patient may require immediate medical attention.</strong></p>
    <p>⚠️ This is a critical safety alert.</p>
    <ul>
        <li>Check on patient's condition</li>
        <li>Contact emergency services if needed</li>
        <li>Visit hospital if symptoms are serious</li>
    </ul>
    <hr>
    <p><em>CareMed_AI Medication Reminder System</em></p>
    """
    
    # Send to family members
    for email in family_emails:
        send_email_alert(email, subject, body)
        print(f"[12-ALERT] CRITICAL alert sent to {email} for {medication_name}")
    
    # Send to doctor/provider if available
    if doctor_email and doctor_email.strip():
        send_email_alert(doctor_email, subject, body)
        print(f"[12-ALERT] CRITICAL alert sent to doctor {doctor_email} for {medication_name}")
