import streamlit as st
import pandas as pd
from datetime import datetime
import time
import base64
import os
import re

from database import (add_medication, get_medications, get_active_medications, 
                      delete_medication, delete_all_medications, stop_medication, 
                      resume_medication, edit_medication, increment_remind_count, set_alert_sent, reset_remind_count,
                      add_user, get_user_by_username, get_user_by_email, authenticate_user,
                      update_user_patient_data, get_user_patient_data, add_disease_to_patient, 
                      update_disease, delete_disease, get_patient_diseases)
from suggestions import (get_medication_suggestions, get_doctor_suggestions, get_all_diseases, 
                         get_llm_health_insights, format_llm_response, get_diet_recommendations,
                         get_exercise_plan, check_drug_interactions, get_preventive_care_tips,
                         get_affordable_medication_alternatives, ask_health_question)
from reminder_page import render_medicine_reminders_page
from notification_system import check_and_notify_reminders, reset_daily_reminders

# Audio file loading removed

# ---------- Page Config ----------
st.set_page_config(page_title="CareMed_AI", page_icon="💊", layout="wide")

# Add CSS for enhanced horizontal navigation and colorful design
st.markdown("""
<style>
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Hide sidebar */
    [data-testid="collapsedControl"] {
        display: none;
    }
    
    /* Make text white on dark background */
    body, .stApp, p, h1, h2, h3, h4, h5, h6, span, label {
        color: white !important;
    }
    
    /* Main page background */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
    }
    
    body {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
    }
    
    /* Horizontal Navigation Bar */
    .nav-bar {
        display: flex;
        justify-content: center;
        gap: 10px;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        margin-bottom: 25px;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        flex-wrap: wrap;
    }
    
    .nav-button {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        padding: 12px 24px;
        border: 2px solid rgba(255, 255, 255, 0.4);
        border-radius: 25px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 600;
        text-decoration: none;
        font-size: 14px;
    }
    
    .nav-button:hover {
        background: rgba(255, 255, 255, 0.3);
        border-color: white;
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }
    
    .nav-button-active {
        background: rgba(255, 255, 255, 0.95);
        color: #667eea;
        border-color: white;
        font-weight: 700;
    }
    
    /* Patient Cards */
    .patient-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin: 12px 0;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
    }
    
    .patient-card:hover {
        border-color: #fff;
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .patient-info-section {
        background: linear-gradient(135deg, #f8f9ff 0%, #f0f1ff 100%);
        padding: 25px;
        border-radius: 12px;
        margin: 15px 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
    
    .medication-list {
        background: rgba(240, 241, 255, 0.7);
        padding: 18px;
        border-radius: 10px;
        margin: 12px 0;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    /* Profile Page Styles */
    .profile-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 35px;
        border-radius: 18px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.35);
    }
    
    .profile-item {
        background: rgba(255, 255, 255, 0.15);
        padding: 18px;
        margin: 12px 0;
        border-radius: 12px;
        border-left: 5px solid #FFD700;
        backdrop-filter: blur(10px);
    }
    
    .medicine-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin: 12px 0;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.2);
    }
    
    .medicine-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 30px rgba(245, 87, 108, 0.35);
    }
    
    .stat-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 25px rgba(79, 172, 254, 0.25);
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 35px rgba(79, 172, 254, 0.4);
    }
    
    .main-header {
        text-align: center;
        padding: 35px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 18px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.8em;
        font-weight: 700;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    .profile-button {
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 14px 24px;
        border: none;
        border-radius: 30px;
        cursor: pointer;
        font-size: 16px;
        font-weight: 700;
        box-shadow: 0 6px 20px rgba(245, 87, 108, 0.3);
        z-index: 100;
        transition: all 0.3s ease;
    }
    
    .profile-button:hover {
        transform: scale(1.08);
        box-shadow: 0 10px 30px rgba(245, 87, 108, 0.45);
    }
    
    /* Input and button improvements */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
    }
    
    /* Expander styles */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    
    /* Select box improvements */
    .stSelectbox {
        color: #333 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Session State ----------
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "show_create_account" not in st.session_state:
    st.session_state.show_create_account = False
if "show_edit_patient" not in st.session_state:
    st.session_state.show_edit_patient = False
if "disease_added_success" not in st.session_state:
    st.session_state.disease_added_success = False
if "diseases_updated_refresh" not in st.session_state:
    st.session_state.diseases_updated_refresh = 0



# ---------- Authentication Functions ----------
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None



def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, "Password is strong"

def validate_username(username):
    """Validate username"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, "Username is valid"

def login_form():
    """Display login form with database authentication"""
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            color: white;
        }
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .login-header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .login-header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        .stTextInput > div > div > input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        .stTextInput > div > div > input:focus {
            border-color: #4CAF50;
            outline: none;
        }
        .login-button {
            width: 100%;
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 15px;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
            margin-bottom: 10px;
        }
        .login-button:hover {
            transform: translateY(-2px);
        }
        .create-account-button {
            width: 100%;
            background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
            color: white;
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            margin-bottom: 15px;
        }
        .error-message {
            background-color: #ff4444;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
            text-align: center;
        }
        .success-message {
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
            text-align: center;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            opacity: 0.8;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-header">', unsafe_allow_html=True)
    st.markdown('<h1>💊 CareMed</h1>', unsafe_allow_html=True)
    st.markdown('<p>Medicine Notification System</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if not st.session_state.show_create_account:
        # Login Form
        st.markdown("### 🔐 Login to Your Account")
        
        # Username/Email field
        username_or_email = st.text_input("👤 Username or Email", placeholder="Enter your username or email", key="login_username_email")
        
        # Password field
        password = st.text_input("🔒 Password", placeholder="Enter your password", type="password", key="login_password")
        
        # Login button
        if st.button("🚀 Login", key="login_button", help="Login to your account"):
            if not username_or_email.strip() or not password.strip():
                st.markdown('<div class="error-message">❌ Please fill in all fields</div>', unsafe_allow_html=True)
            else:
                user, message = authenticate_user(username_or_email, password)
                
                if user:
                    st.session_state.current_user = user
                    patient_data = get_user_patient_data(user["username"])
                    
                    if patient_data:
                        st.session_state.patient_data = patient_data
                        st.markdown('<div class="success-message">✅ Login successful! Welcome back!</div>', unsafe_allow_html=True)
                        time.sleep(1)
                        st.rerun()
                    else:
                        # New user who hasn't filled patient details yet
                        st.markdown('<div class="success-message">✅ Login successful! Please complete your patient details.</div>', unsafe_allow_html=True)
                        time.sleep(1)
                        st.rerun()
                else:
                    st.markdown(f'<div class="error-message">❌ {message}</div>', unsafe_allow_html=True)
        
        # Create Account button
        if st.button("📝 Create New Account", key="create_account_button", help="Create a new account"):
            st.session_state.show_create_account = True
            st.rerun()
    
    else:
        # Create Account Form
        st.markdown("### 📝 Create New Account")
        
        # Username field
        new_username = st.text_input("👤 Username", placeholder="Choose a username", key="new_username")
        
        # Email field
        new_email = st.text_input("📧 Email Address", placeholder="Enter your email", key="new_email")
        
        # Password field
        new_password = st.text_input("🔒 Password", placeholder="Create a password", type="password", key="new_password")
        
        # Confirm Password field
        confirm_password = st.text_input("🔒 Confirm Password", placeholder="Confirm your password", type="password", key="confirm_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Create Account", key="submit_create_account"):
                # Validation
                errors = []
                
                if not new_username.strip():
                    errors.append("👤 Username is required")
                elif not validate_username(new_username)[0]:
                    errors.append(f"👤 {validate_username(new_username)[1]}")
                
                if not new_email.strip():
                    errors.append("📧 Email is required")
                elif not validate_email(new_email):
                    errors.append("📧 Please enter a valid email address")
                
                if not new_password.strip():
                    errors.append("🔒 Password is required")
                elif not validate_password(new_password)[0]:
                    errors.append(f"🔒 {validate_password(new_password)[1]}")
                
                if new_password != confirm_password:
                    errors.append("🔒 Passwords do not match")
                
                if errors:
                    for error in errors:
                        st.markdown(f'<div class="error-message">{error}</div>', unsafe_allow_html=True)
                else:
                    # Create account
                    success, message = add_user(new_username, new_email, new_password)
                    if success:
                        st.markdown('<div class="success-message">✅ Account created successfully! Please complete your patient details.</div>', unsafe_allow_html=True)
                        # Auto-login the new user
                        user, _ = authenticate_user(new_username, new_password)
                        st.session_state.current_user = user
                        st.session_state.show_create_account = False
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.markdown(f'<div class="error-message">❌ {message}</div>', unsafe_allow_html=True)
        
        with col2:
            if st.button("🔙 Back to Login", key="back_to_login"):
                st.session_state.show_create_account = False
                st.rerun()
    
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown('<p>💊 CareMed - Your AI Medication Assistant</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def patient_details_form():
    """Display patient details form with AI disease suggestions"""
    st.markdown("""
    <style>
        .patient-container {
            max-width: 700px;
            margin: 0 auto;
            padding: 30px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            color: white;
        }
        .patient-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .patient-header h1 {
            font-size: 2.2em;
            margin-bottom: 10px;
        }
        .form-section {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .form-section h3 {
            margin-top: 0;
            color: #fff;
        }
        .stTextInput > div > div > input, .stNumberInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div {
            background: rgba(255,255,255,0.9);
            color: black;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .submit-button {
            width: 100%;
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 15px;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 20px;
        }
        .back-button {
            width: 100%;
            background: linear-gradient(135deg, #ff6b6b 0%, #ff5252 100%);
            color: white;
            padding: 10px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 10px;
        }
        .patient-summary {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 2px solid #ff6b6b;
        }
        .patient-summary h4 {
            margin-top: 0;
            color: #fff;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="patient-container">', unsafe_allow_html=True)
    st.markdown('<div class="patient-header">', unsafe_allow_html=True)
    st.markdown('<h1>📋 Patient Details</h1>', unsafe_allow_html=True)
    st.markdown('<p>Please fill in all the required patient information</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # AI Disease Suggestions
    disease_options = [
        "Select Disease/Condition",
        "Diabetes",
        "Hypertension (High Blood Pressure)",
        "Heart Disease",
        "Asthma",
        "Arthritis",
        "Depression",
        "Anxiety",
        "Thyroid Disorder",
        "Chronic Kidney Disease",
        "COPD (Chronic Obstructive Pulmonary Disease)",
        "Cancer",
        "Alzheimer's Disease",
        "Parkinson's Disease",
        "Stroke Recovery",
        "Others"
    ]

    # Personal Information Section
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<h3>👤 Personal Information</h3>', unsafe_allow_html=True)

    # Initialize color states for mandatory fields
    if "name_filled" not in st.session_state:
        st.session_state.name_filled = False
    if "age_filled" not in st.session_state:
        st.session_state.age_filled = False
    if "disease_filled" not in st.session_state:
        st.session_state.disease_filled = False

    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("Full Name *", placeholder="Enter patient's full name", key="patient_name")
        st.session_state.name_filled = bool(patient_name.strip())
    with col2:
        patient_age = st.number_input("Age *", min_value=1, max_value=120, key="patient_age")
        st.session_state.age_filled = patient_age > 0

    # Disease Selection with AI suggestions
    selected_disease = st.selectbox("Disease/Condition *", disease_options, key="selected_disease")
    st.session_state.disease_filled = selected_disease != "Select Disease/Condition"

    # Custom disease input (shown only when "Others" is selected)
    custom_disease = ""
    if selected_disease == "Others":
        custom_disease = st.text_input("Specify Disease/Condition *", placeholder="Enter the specific disease or condition", key="custom_disease")
        st.session_state.disease_filled = bool(custom_disease.strip())

    # Final disease value
    final_disease = custom_disease if selected_disease == "Others" else (selected_disease if selected_disease != "Select Disease/Condition" else "")

    st.markdown('</div>', unsafe_allow_html=True)

    # Medication Information Section
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<h3>💊 Medication Information</h3>', unsafe_allow_html=True)

    medication = st.text_area("Prescribed Medication *", placeholder="List all prescribed medications with dosages (e.g., Aspirin 75mg daily, Metformin 500mg twice daily)", height=100, key="medication")
    
    # Initialize medication filled state
    if "medication_filled" not in st.session_state:
        st.session_state.medication_filled = False
    st.session_state.medication_filled = bool(medication.strip())
    
    # Display color feedback for medication field
    med_color = "#90EE90" if st.session_state.medication_filled else "#FFB6C1"
    med_status = "✅ Medication added" if st.session_state.medication_filled else "⚠️ Medication required"
    st.markdown(f"""<div style="padding: 8px; border-radius: 5px; background-color: {med_color}; color: white; font-size: 13px; text-align: center;">{med_status}</div>""", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Family Contact Information Section
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<h3>📞 Family Contact Details</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 14px; color: #fff;">At least one family contact is required</p>', unsafe_allow_html=True)

    # Doctor/Provider email (for alerts)
    doctor_email = st.text_input("📨 Doctor/Provider Email (Optional)", placeholder="doctor@hospital.com", key="doctor_email", 
                                  help="Your primary care doctor email - will receive medication alerts")

    # Family contact fields
    family_contacts = []

    # Contact 1 (Required)
    st.markdown("**Family Contact 1 (Required):**")
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        contact1_name = st.text_input("Name *", placeholder="Full name", key="contact1_name")
    with col2:
        contact1_phone = st.text_input("Phone *", placeholder="Phone number", key="contact1_phone")
    with col3:
        contact1_email = st.text_input("Email", placeholder="Email address", key="contact1_email")

    if contact1_name and contact1_phone:
        family_contacts.append({
            "name": contact1_name,
            "phone": contact1_phone,
            "email": contact1_email
        })

    # Contact 2 (Optional)
    st.markdown("**Family Contact 2 (Optional):**")
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        contact2_name = st.text_input("Name", placeholder="Full name", key="contact2_name")
    with col2:
        contact2_phone = st.text_input("Phone", placeholder="Phone number", key="contact2_phone")
    with col3:
        contact2_email = st.text_input("Email", placeholder="Email address", key="contact2_email")

    if contact2_name and contact2_phone:
        family_contacts.append({
            "name": contact2_name,
            "phone": contact2_phone,
            "email": contact2_email
        })

    # Contact 3 (Optional)
    st.markdown("**Family Contact 3 (Optional):**")
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        contact3_name = st.text_input("Name", placeholder="Full name", key="contact3_name")
    with col2:
        contact3_phone = st.text_input("Phone", placeholder="Phone number", key="contact3_phone")
    with col3:
        contact3_email = st.text_input("Email", placeholder="Email address", key="contact3_email")

    if contact3_name and contact3_phone:
        family_contacts.append({
            "name": contact3_name,
            "phone": contact3_phone,
            "email": contact3_email
        })

    st.markdown('</div>', unsafe_allow_html=True)

    # Patient Summary Display
    if patient_name and patient_age and final_disease:
        st.markdown('<div class="patient-summary">', unsafe_allow_html=True)
        st.markdown('<h4>📋 Patient Summary</h4>', unsafe_allow_html=True)
        st.markdown(f"**👤 Name:** {patient_name}")
        st.markdown(f"**🎂 Age:** {patient_age}")
        st.markdown(f"**🏥 Disease:** {final_disease}")
        st.markdown(f"**💊 Medication:** {medication[:100]}{'...' if len(medication) > 100 else ''}")
        st.markdown(f"**👨‍👩‍👧‍👦 Family Contacts:** {len(family_contacts)} contact(s) added")
        st.markdown('</div>', unsafe_allow_html=True)

    # Submit and Back buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Patient Details", key="save_details", help="Save the patient information"):
            # Validate required fields
            errors = []

            if not patient_name.strip():
                errors.append("❌ Patient name is required")
            if not final_disease.strip():
                errors.append("❌ Disease/condition is required")
            if not medication.strip():
                errors.append("❌ Medication information is required")
            if len(family_contacts) == 0:
                errors.append("❌ At least one family contact is required")
            if selected_disease == "Others" and not custom_disease.strip():
                errors.append("❌ Please specify the disease/condition")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Format family contacts for storage
                formatted_contacts = []
                for contact in family_contacts:
                    contact_str = f"{contact['name']} - {contact['phone']}"
                    if contact['email']:
                        contact_str += f", {contact['email']}"
                    formatted_contacts.append(contact_str)

                # Save to database
                patient_data = {
                    "name": patient_name,
                    "age": int(patient_age),
                    "disease": final_disease,
                    "medication": medication,
                    "family_contacts": formatted_contacts,
                    "doctor_email": doctor_email.strip() if doctor_email else "",
                    "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                if update_user_patient_data(st.session_state.current_user["username"], patient_data):
                    # Update session state so disease and patient info show instantly
                    st.session_state.patient_data = patient_data
                    st.success("✅ Patient details saved successfully!")
                    time.sleep(1)
                    st.rerun()  # Redirect to home page
                else:
                    st.error("❌ Failed to save patient details. Please try again.")

    with col2:
        if st.button("🏠 Back to Home Page", key="back_to_home", help="Return to home page"):
            st.rerun()  # Redirect to home page

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- EDIT PATIENT DETAILS FORM ----------
def edit_patient_form():
    """Display form to edit patient details"""
    st.markdown("""
    <style>
        .patient-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .patient-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 10px;
            color: white;
            margin-bottom: 30px;
        }
        .patient-header h1 {
            margin: 0;
        }
        .form-section {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 2px solid #667eea;
        }
        .patient-summary {
            background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 2px solid #ff6b6b;
        }
        .patient-summary h4 {
            margin-top: 0;
            color: #fff;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="patient-container">', unsafe_allow_html=True)
    st.markdown('<div class="patient-header">', unsafe_allow_html=True)
    st.markdown('<h1>✏️ Edit Patient Details</h1>', unsafe_allow_html=True)
    st.markdown('<p>Update patient information</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Get current patient data - ALWAYS fresh from database
    username = st.session_state.current_user["username"]
    current_patient = get_user_patient_data(username)
    
    # Validate data was loaded
    if not current_patient:
        st.error("❌ Failed to load patient data. Please go back and try again.")
        if st.button("🔙 Go Back", key="go_back_from_error"):
            st.session_state.show_edit_patient = False
            st.rerun()
        st.stop()
    
    # Create a form to properly capture all fields
    with st.form("edit_patient_form", clear_on_submit=False):
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<h3>👤 Personal Information</h3>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            default_name = current_patient.get("name", "") if current_patient else ""
            patient_name = st.text_input(
                "Full Name *",
                value=default_name,
                placeholder="Enter patient's full name"
            )
        with col2:
            default_age = int(current_patient.get("age", 1)) if current_patient and current_patient.get("age") else 1
            patient_age = st.number_input(
                "Age *",
                value=default_age,
                min_value=1,
                max_value=120
            )

        st.markdown('</div>', unsafe_allow_html=True)

        # Medication Information Section
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<h3>💊 Medication Information</h3>', unsafe_allow_html=True)

        default_medication = current_patient.get("medication", "") if current_patient else ""
        medication = st.text_area(
            "Prescribed Medication *",
            value=default_medication,
            placeholder="List all prescribed medications with dosages",
            height=100
        )

        st.markdown('</div>', unsafe_allow_html=True)

        # Family Contact Information Section
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<h3>📞 Family Contact Details & Doctor Email</h3>', unsafe_allow_html=True)

        default_doctor_email = current_patient.get("doctor_email", "") if current_patient else ""
        doctor_email = st.text_input(
            "📨 Doctor/Provider Email (Optional)",
            value=default_doctor_email,
            placeholder="doctor@hospital.com",
            help="Your primary care doctor email - will receive medication alerts"
        )

        family_contacts = []
        current_contacts = current_patient.get("family_contacts", []) if current_patient else []

        for i in range(1, 4):
            st.markdown(f"**Family Contact {i} {'(Required):' if i == 1 else '(Optional):'}")
            
            # Parse existing contact if available
            existing_contact = current_contacts[i-1] if i-1 < len(current_contacts) else None
            existing_name = ""
            existing_phone = ""
            existing_email = ""
            
            if existing_contact:
                # Parse contact string format: "Name - Phone, Email"
                parts = existing_contact.split(" - ")
                existing_name = parts[0] if parts else ""
                if len(parts) > 1:
                    phone_email = parts[1].split(", ")
                    existing_phone = phone_email[0] if phone_email else ""
                    existing_email = phone_email[1] if len(phone_email) > 1 else ""
            
            col1, col2, col3 = st.columns([2, 2, 2])
            with col1:
                name = st.text_input(
                    "Name",
                    value=existing_name,
                    placeholder="Full name",
                    key=f"contact{i}_name"
                )
            with col2:
                phone = st.text_input(
                    "Phone",
                    value=existing_phone,
                    placeholder="Phone number",
                    key=f"contact{i}_phone"
                )
            with col3:
                email = st.text_input(
                    "Email",
                    value=existing_email,
                    placeholder="Email address",
                    key=f"contact{i}_email"
                )

            if name and phone:
                family_contacts.append({
                    "name": name,
                    "phone": phone,
                    "email": email
                })

        st.markdown('</div>', unsafe_allow_html=True)

        # Display summary before submission
        if patient_name and patient_age:
            st.markdown('<div class="patient-summary">', unsafe_allow_html=True)
            st.markdown('<h4>📋 Patient Summary</h4>', unsafe_allow_html=True)
            st.markdown(f"**👤 Name:** {patient_name}")
            st.markdown(f"**🎂 Age:** {patient_age}")
            # Show disease if available
            if current_patient and current_patient.get("disease"):
                st.markdown(f"**🏥 Disease:** {current_patient.get('disease')}")
            st.markdown(f"**💊 Medication:** {medication[:100]}{'...' if len(medication) > 100 else ''}")
            st.markdown(f"**👨‍👩‍👧‍👦 Family Contacts:** {len(family_contacts)} contact(s) added")
            st.markdown('</div>', unsafe_allow_html=True)

        # Form submission buttons
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)
        with col2:
            st.form_submit_button("🏠 Back to Home", use_container_width=True, key="back_btn_form")
        
        # Handle form submission
        if submitted:
            errors = []

            if not patient_name.strip():
                errors.append("❌ Patient name is required")
            if not medication.strip():
                errors.append("❌ Medication information is required")
            if len(family_contacts) == 0:
                errors.append("❌ At least one family contact is required")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Format family contacts for storage
                formatted_contacts = []
                for contact in family_contacts:
                    contact_str = f"{contact['name']} - {contact['phone']}"
                    if contact['email']:
                        contact_str += f", {contact['email']}"
                    formatted_contacts.append(contact_str)

                # Save to database - preserve existing data
                patient_data = {
                    "name": patient_name,
                    "age": int(patient_age),
                    "medication": medication,
                    "family_contacts": formatted_contacts,
                    "doctor_email": doctor_email.strip() if doctor_email else "",
                    "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Preserve disease/condition info if it exists
                if current_patient:
                    if "disease" in current_patient:
                        patient_data["disease"] = current_patient["disease"]

                # Use actual username from session state
                actual_username = st.session_state.current_user.get("username", "").strip()
                
                if not actual_username:
                    st.error("❌ Error: Username not found in session. Please login again.")
                elif update_user_patient_data(actual_username, patient_data):
                    # Update session so the new patient info (including disease) appears instantly
                    st.session_state.patient_data = patient_data
                    st.success("✅ Patient details updated successfully!")
                    st.balloons()
                    time.sleep(1)
                    st.session_state.show_edit_patient = False
                    st.rerun()
                else:
                    st.error(f"❌ Failed to save patient details for user '{actual_username}'. Please try again.")

    # Disease Management Section - Sub-part of Edit Patient Details
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<h3>🏥 Disease/Condition Management</h3>', unsafe_allow_html=True)

    # Create container for disease section - forces refresh
    st.markdown('</div>', unsafe_allow_html=True)

    # Medication Information Section
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<h3>💊 Medication Information</h3>', unsafe_allow_html=True)

    default_medication = current_patient.get("medication", "") if current_patient else ""
    medication = st.text_area(
        "Prescribed Medication *",
        value=default_medication,
        placeholder="List all prescribed medications with dosages",
        height=100,
        key=f"edit_medication_{st.session_state.diseases_updated_refresh}"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # Family Contact Information Section
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<h3>📞 Family Contact Details & Doctor Email</h3>', unsafe_allow_html=True)

    default_doctor_email = current_patient.get("doctor_email", "") if current_patient else ""
    doctor_email = st.text_input(
        "📨 Doctor/Provider Email (Optional)",
        value=default_doctor_email,
        placeholder="doctor@hospital.com",
        key=f"edit_doctor_email_{st.session_state.diseases_updated_refresh}",
        help="Your primary care doctor email - will receive medication alerts"
    )

    family_contacts = []
    current_contacts = current_patient.get("family_contacts", []) if current_patient else []

    for i in range(1, 4):
        st.markdown(f"**Family Contact {i} {'(Required):' if i == 1 else '(Optional):'}")
        
        # Parse existing contact if available
        existing_contact = current_contacts[i-1] if i-1 < len(current_contacts) else None
        existing_name = ""
        existing_phone = ""
        existing_email = ""
        
        if existing_contact:
            # Parse contact string format: "Name - Phone, Email"
            parts = existing_contact.split(" - ")
            existing_name = parts[0] if parts else ""
            if len(parts) > 1:
                phone_email = parts[1].split(", ")
                existing_phone = phone_email[0] if phone_email else ""
                existing_email = phone_email[1] if len(phone_email) > 1 else ""
        
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            name = st.text_input(
                "Name",
                value=existing_name,
                placeholder="Full name",
                key=f"edit_contact{i}_name_{st.session_state.diseases_updated_refresh}"
            )
        with col2:
            phone = st.text_input(
                "Phone",
                value=existing_phone,
                placeholder="Phone number",
                key=f"edit_contact{i}_phone_{st.session_state.diseases_updated_refresh}"
            )
        with col3:
            email = st.text_input(
                "Email",
                value=existing_email,
                placeholder="Email address",
                key=f"edit_contact{i}_email_{st.session_state.diseases_updated_refresh}"
            )

        if name and phone:
            family_contacts.append({
                "name": name,
                "phone": phone,
                "email": email
            })

    st.markdown('</div>', unsafe_allow_html=True)

    # Patient Summary Display - WITH DISEASES - ALWAYS FRESH
    if patient_name and patient_age:
        summary_container = st.container()
        with summary_container:
            st.markdown('<div class="patient-summary">', unsafe_allow_html=True)
            st.markdown('<h4>📋 Patient Summary</h4>', unsafe_allow_html=True)
            st.markdown(f"**👤 Name:** {patient_name}")
            st.markdown(f"**🎂 Age:** {patient_age}")
            # Include disease info when editing (preserve from current_patient)
            if current_patient and current_patient.get("disease"):
                st.markdown(f"**🏥 Disease:** {current_patient.get('disease')}")
            
            st.markdown(f"**💊 Medication:** {medication[:100]}{'...' if len(medication) > 100 else ''}")
            st.markdown(f"**👨‍👩‍👧‍👦 Family Contacts:** {len(family_contacts)} contact(s) added")
            st.markdown('</div>', unsafe_allow_html=True)

    # Submit and Back buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Changes", key="save_edited_details", help="Save the updated patient information"):
            errors = []

            if not patient_name.strip():
                errors.append("❌ Patient name is required")
            if not medication.strip():
                errors.append("❌ Medication information is required")
            if len(family_contacts) == 0:
                errors.append("❌ At least one family contact is required")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Format family contacts for storage
                formatted_contacts = []
                for contact in family_contacts:
                    contact_str = f"{contact['name']} - {contact['phone']}"
                    if contact['email']:
                        contact_str += f", {contact['email']}"
                    formatted_contacts.append(contact_str)

                # Save to database - preserve existing data
                patient_data = {
                    "name": patient_name,
                    "age": int(patient_age),
                    "medication": medication,
                    "family_contacts": formatted_contacts,
                    "doctor_email": doctor_email.strip() if doctor_email else "",
                    "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Preserve disease/condition info if it exists
                if current_patient:
                    if "disease" in current_patient:
                        patient_data["disease"] = current_patient["disease"]

                # Use actual username from session state
                actual_username = st.session_state.current_user.get("username", "").strip()
                
                if not actual_username:
                    st.error("❌ Error: Username not found in session. Please login again.")
                elif update_user_patient_data(actual_username, patient_data):
                    st.success("✅ Patient details updated successfully!")
                    time.sleep(1)
                    st.session_state.show_edit_patient = False
                    st.rerun()
                else:
                    st.error(f"❌ Failed to save patient details for user '{actual_username}'. Please try again.")

    with col2:
        if st.button("🏠 Back to Home Page", key="back_to_home_edit", help="Return to home page"):
            st.session_state.diseases_updated_refresh += 1
            st.session_state.show_edit_patient = False
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Sound Function with Escalating Frequency ----------
def play_alarm(continuous=False, frequency_level=1):
    """Play alarm with continuous irritating beeping pattern
    Designed to be attention-grabbing and keep ringing until user responds
    """
    try:
        if os.name == 'nt':
            import winsound
            
            # IRRITATING continuous alarm pattern - multiple beeps with varying frequencies
            # Creates an obnoxious, attention-grabbing sound that repeats
            beep_patterns = {
                1: [  # Base pattern
                    (1000, 100), (1100, 100), (1200, 100), (1100, 100),
                    (2000, 150), (2000, 150),
                    (1500, 100), (1500, 100), (1500, 100),
                ],
                2: [  # Escalated pattern
                    (1500, 80), (1600, 80), (1700, 80), (1800, 80), (1700, 80),
                    (2500, 120), (2500, 120),
                    (2000, 100), (2000, 100), (2000, 100),
                ],
                3: [  # High pattern
                    (2000, 60), (2200, 60), (2400, 60), (2200, 60),
                    (3000, 100), (3000, 100),
                    (2500, 80), (2500, 80), (2500, 80),
                ],
                4: [  # Maximum pattern
                    (2500, 50), (2700, 50), (2900, 50), (2700, 50),
                    (3500, 80), (3500, 80),
                    (3000, 60), (3000, 60), (3000, 60),
                ]
            }
            
            # Get pattern based on frequency level
            pattern = beep_patterns.get(frequency_level, beep_patterns[1])
            
            # Play pattern MULTIPLE times for continuous irritating effect
            # 5 cycles = ~10+ seconds of continuous beeping per page render
            for cycle in range(5):
                for freq, duration in pattern:
                    winsound.Beep(freq, duration)
                time.sleep(0.3)  # Brief pause between cycles
    
    except Exception as e:
        print(f"Alarm beep error: {e}")

# ---------- Animation ----------
def show_medicine_animation():
    st.markdown("""<style>@keyframes bounce{0%,100%{transform:translateY(0);}50%{transform:translateY(-30px);}}
    .medicine{font-size:100px;animation:bounce 0.6s infinite;text-align:center;}</style><div class="medicine">💊</div>""", unsafe_allow_html=True)



# ---------- AUTHENTICATION CHECK ----------
if not st.session_state.current_user:
    # Show login form
    login_form()
    st.stop()  # Stop execution here if not logged in
elif st.session_state.show_edit_patient:
    # Show edit patient form if user wants to edit
    edit_patient_form()
    st.stop()  # Stop execution here until patient data is saved
elif not get_user_patient_data(st.session_state.current_user["username"]):
    # Show patient details form if logged in but no patient data
    patient_details_form()
    st.stop()  # Stop execution here until patient data is saved

# ---------- MAIN TITLE ----------
st.markdown("""<div class="main-header"><h1>💊 CareMed_AI</h1><p>Medicine Notification System</p></div>""", unsafe_allow_html=True)

# Initialize page state
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Home"
if "show_profile_page" not in st.session_state:
    st.session_state.show_profile_page = False

# Horizontal Navigation Bar
col_nav = st.columns(7)
nav_items = ["🏠 Home", "📊 Dashboard", "➕ Add Medicine", "⏰ Reminders", "🤖 AI Suggestions", "💬 Health Q&A"]

for idx, nav_item in enumerate(nav_items):
    with col_nav[idx]:
        if st.button(nav_item, use_container_width=True, key=f"nav_{nav_item}"):
            st.session_state.current_page = nav_item
            st.session_state.show_profile_page = False
            st.rerun()

# Profile Button (Top Right, Fixed)
st.markdown("""
<div style="position: fixed; top: 20px; right: 20px; z-index: 100;">
""", unsafe_allow_html=True)

col_profile = st.columns([1])
with col_profile[0]:
    if st.button("👤 Profile", key="profile_btn_top", help="View your profile"):
        st.session_state.show_profile_page = True
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
st.divider()

# Set page based on state
page = st.session_state.current_page

# Check and show reminders notification
reset_daily_reminders()  # Reset daily reminder tracking at midnight
active_reminders = check_and_notify_reminders()  # Check for current reminders

# Show Profile Page if requested
if st.session_state.show_profile_page:
    st.markdown("## 👤 My Profile")
    
    # Back button
    if st.button("← Back to Home", key="back_from_profile"):
        st.session_state.show_profile_page = False
        st.rerun()
    
    st.divider()
    
    # User Personal Information
    st.markdown('<div class="profile-container">', unsafe_allow_html=True)
    st.markdown("### 👤 Personal Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="profile-item">
        <b>👤 Username:</b><br>
        {} 
        </div>
        """.format(st.session_state.current_user['username']), unsafe_allow_html=True)
        
        st.markdown("""
        <div class="profile-item">
        <b>🎂 Account Status:</b><br>
        Active
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="profile-item">
        <b>📧 Email:</b><br>
        {}
        </div>
        """.format(st.session_state.current_user['email']), unsafe_allow_html=True)
        
        st.markdown("""
        <div class="profile-item">
        <b>📅 Account Created:</b><br>
        {}
        </div>
        """.format(st.session_state.current_user.get('created_at', 'N/A')), unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Patient Information Section
    st.markdown("### 🏥 Patient Information")
    
    patient_data = get_user_patient_data(st.session_state.current_user["username"]) if st.session_state.current_user else None
    username = st.session_state.current_user["username"] if st.session_state.current_user else None
    
    if patient_data:
        patients = patient_data if isinstance(patient_data, list) else [patient_data]
        
        for idx, patient in enumerate(patients[:3], 1):
            with st.expander(f"👤 Patient #{idx} - {patient.get('name', 'Unknown')}", expanded=(idx == 1)):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div class="profile-item">
                    <b>👤 Full Name:</b> {patient.get('name', 'N/A')}<br>
                    <b>🎂 Age:</b> {patient.get('age', 'N/A')} years<br>
                    <b>🏥 Disease:</b> {patient.get('disease', 'N/A')}<br>
                    <b>📅 Profile Created:</b> {patient.get('saved_at', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("**💊 Current Medications:**")
                st.info(patient.get('medication', 'No medications listed'))
                
                st.markdown("**👨‍👩‍👧‍👦 Family Emergency Contacts:**")
                contacts = patient.get('family_contacts', [])
                if isinstance(contacts, list) and len(contacts) > 0:
                    for contact_idx, contact in enumerate(contacts, 1):
                        st.write(f"**Contact {contact_idx}:** {contact}")
                else:
                    st.info("No family contacts added")
    else:
        st.warning("⚠️ No patient information added yet. Please complete your patient details.")
    
    st.divider()
    
    # Logout button
    if st.button("🚪 Logout", key="logout_profile"):
        st.session_state.current_user = None
        st.session_state.patient_data = {}
        st.session_state.show_create_account = False
        st.session_state.reminder_active = False
        st.session_state.active_reminder_med = None
        st.session_state.freq_level = 1
        st.session_state.show_profile_page = False
        st.success("✅ Logged out successfully!")
        time.sleep(1)
        st.rerun()
    
    st.stop()  # Stop here if showing profile page

# ==================== HOME ====================
if page == "🏠 Home":
    st.markdown("## 🏠 Home")
    
    # ---------- PATIENT PROFILE SECTION ----------
    # Always load fresh data from database
    username = st.session_state.current_user["username"] if st.session_state.current_user else None
    patient_data = get_user_patient_data(username) if username else None
    
    if patient_data:
        st.markdown("### 👤 Your Patient Profile")
        
        # Create a container for profile info that updates instantly - with refresh key
        profile_container = st.container(key=f"profile_refresh_{st.session_state.diseases_updated_refresh}_{username}")
        
        with profile_container:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="profile-item">
                <b>👤 Name:</b> {patient_data.get('name', 'N/A')}<br>
                <b>🎂 Age:</b> {patient_data.get('age', 'N/A')} years<br>
                <b>💊 Medications:</b> {len(get_medications())} added<br>
                <b>📨 Doctor Email:</b> {patient_data.get('doctor_email', 'Not provided') if patient_data.get('doctor_email') else 'Not provided'}
                </div>
                """, unsafe_allow_html=True)
            

        
        st.divider()
        
        # Edit button (now includes disease management)
        if st.button("✏️ Edit Patient Details", use_container_width=True, key="home_edit_patient"):
            st.session_state.show_edit_patient = True
            st.rerun()
        
        st.divider()
    else:
        st.warning("⚠️ No patient profile found. Please set up your patient details first.")
        if st.button("➕ Create Patient Profile", use_container_width=True, key="create_patient_profile"):
            st.session_state.show_edit_patient = True
            st.rerun()
        st.divider()
    
    # Quick Stats
    meds = get_medications()
    active_count = len([m for m in meds if m.get("active", True)])
    
    st.markdown("### 📊 Quick Stats")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
        <h3>💊</h3>
        <h4>Total Medicines</h4>
        <h2>{len(meds)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);">
        <h3>✅</h3>
        <h4>Active</h4>
        <h2>{active_count}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
        <h3>⏸️</h3>
        <h4>Paused</h4>
        <h2>{len(meds) - active_count}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);">
        <h3>👥</h3>
        <h4>Patients</h4>
        <h2>1</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔊 Test Alarm", use_container_width=True, key="home_test_alarm"):
            st.error("🚨 **TESTING ALARM**")
            play_alarm()
            show_medicine_animation()
    
    with col2:
        if st.button("➕ Add New Medicine", use_container_width=True, key="home_add_med"):
            st.session_state.current_page = "➕ Add Medicine"
            st.rerun()
    
    with col3:
        if st.button("📊 View Dashboard", use_container_width=True, key="home_dashboard"):
            st.session_state.current_page = "📊 Dashboard"
            st.rerun()
    
    st.divider()
    
    # Recent Medicines
    if meds:
        st.markdown("### 📝 Recent Medicines")
        for med in reversed(meds[-3:]):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**💊 {med['name']}**", unsafe_allow_html=True)
                st.write(f"{med['dosage']}")
            with col2:
                st.write(f"⏰ {med['time']}")
            with col3:
                status = "🟢 Active" if med.get("active", True) else "🔴 Stopped"
                st.write(status)
    else:
        st.info("📌 No medicines added yet. Click 'Add New Medicine' to get started!")

# ==================== DASHBOARD ====================
elif page == "📊 Dashboard":
    st.markdown("## 📊 Complete Health Dashboard")
    
    # Comprehensive Dashboard Stats
    meds = get_medications()
    active_count = len([m for m in meds if m.get("active", True)])
    
    # Get diseases for stats
    username = st.session_state.current_user["username"] if st.session_state.current_user else None
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 15px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h3>💊</h3>
        <h4>Total Medicines</h4>
        <h2 style="margin: 10px 0;">{}</h2>
        <p style="font-size: 12px; opacity: 0.9;">All medications</p>
        </div>
        """.format(len(meds)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 25px; border-radius: 15px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h3>✅</h3>
        <h4>Active Medicines</h4>
        <h2 style="margin: 10px 0;">{}</h2>
        <p style="font-size: 12px; opacity: 0.9;">Currently active</p>
        </div>
        """.format(active_count), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 25px; border-radius: 15px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h3>⏸️</h3>
        <h4>Paused Medicines</h4>
        <h2 style="margin: 10px 0;">{}</h2>
        <p style="font-size: 12px; opacity: 0.9;">Temporarily paused</p>
        </div>
        """.format(len(meds) - active_count), unsafe_allow_html=True)
    
    st.divider()
    
    # Patient Information Section
    st.markdown("### 👥 Patient Profile Information")
    
    patient_data = get_user_patient_data(st.session_state.current_user["username"]) if st.session_state.current_user else None
    
    if patient_data:
        patients = patient_data if isinstance(patient_data, list) else [patient_data]
        patients = patients[:3]
        
        for patient_idx, patient in enumerate(patients, 1):
            with st.expander(f"👤 {patient.get('name', 'Patient')} - Patient #{patient_idx}", expanded=(patient_idx == 1)):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #f0f1ff 0%, #f8f9ff 100%); padding: 15px; border-radius: 10px; border-left: 5px solid #667eea;">
                    """, unsafe_allow_html=True)
                    st.write(f"**👤 Full Name:** {patient.get('name', 'N/A')}")
                    st.write(f"**🎂 Age:** {patient.get('age', 'N/A')} years old")
                    st.write(f"**📧 Email:** {st.session_state.current_user['email']}")
                    st.write(f"**👤 Username:** {st.session_state.current_user['username']}")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #fff0f1 0%, #fff8f9 100%); padding: 15px; border-radius: 10px; border-left: 5px solid #f5576c;">
                    """, unsafe_allow_html=True)
                    
                    # Show doctor email if available
                    doctor_email = patient.get('doctor_email', '')
                    if doctor_email:
                        st.write(f"**📨 Doctor Email:** {doctor_email}")
                    
                    st.write(f"**📅 Profile Updated:** {patient.get('saved_at', 'N/A')}")
                    st.write(f"**📍 Status:** Active")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("**💊 Current Medications:**")
                st.write(patient.get('medication', 'No medications listed'))
                
                st.markdown("**👨‍👩‍👧‍👦 Family Emergency Contacts:**")
                contacts = patient.get('family_contacts', [])
                if isinstance(contacts, list) and len(contacts) > 0:
                    for idx, contact in enumerate(contacts, 1):
                        st.write(f"**Contact {idx}:** {contact}")
                else:
                    st.info("No family contacts added yet")
    
    st.divider()
    
    # Medicine Statistics Table
    st.markdown("### 📊 Medicine Management")
    
    if meds:
        st.markdown("**View, Edit, or Remove Your Medicines:**")
        
        # Create interactive medicine list with delete buttons
        for idx, med in enumerate(meds):
            col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 1, 1])
            
            with col1:
                st.markdown(f"**💊 {med['name']}**")
                st.caption(f"{med['dosage']}")
            
            with col2:
                st.markdown(f"⏰ **{med['time']}**")
                st.caption(f"{med.get('frequency', 'Daily')}")
            
            with col3:
                status = "🟢 Active" if med.get("active", True) else "🔴 Stopped"
                st.markdown(status)
                st.caption(f"Reminders: {med.get('remind_count', 0)}")
            
            with col4:
                if st.button("⏸️", key=f"pause_{med['id']}", help="Pause this medicine"):
                    if med.get("active", True):
                        stop_medication(med['id'])
                        st.success(f"⏸️ {med['name']} paused")
                    else:
                        resume_medication(med['id'])
                        st.success(f"▶️ {med['name']} resumed")
                    st.rerun()
            
            with col5:
                if st.button("🗑️", key=f"delete_{med['id']}", help="Delete this medicine"):
                    delete_medication(med['id'])
                    st.success(f"✅ {med['name']} removed!")
                    time.sleep(1)
                    st.rerun()
            
            st.divider()
    else:
        st.info("📌 No medicines added yet. Go to 'Add Medicine' to get started!")

# ==================== ADD MEDICINE ====================
elif page == "➕ Add Medicine":
    st.markdown("## ➕ Add New Medicine(s)")
    
    # Initialize medicines list in session state
    if "medicines_to_add" not in st.session_state:
        st.session_state.medicines_to_add = []
    
    if "med_count" not in st.session_state:
        st.session_state.med_count = 1
    
    st.info("💡 You can add multiple medicines at once. Fill below and click 'Add Another Medicine' to add more.")
    
    # Medicine counter
    col_title1, col_title2, col_title3 = st.columns([2, 1, 1])
    with col_title1:
        st.markdown("### Medicine #1")
    with col_title2:
        if st.button("➕ Add Another Medicine", use_container_width=True, key="add_med_btn"):
            st.session_state.med_count += 1
            st.rerun()
    with col_title3:
        if st.session_state.med_count > 1:
            if st.button("❌ Remove Last", use_container_width=True, key="remove_med_btn"):
                st.session_state.med_count -= 1
                st.rerun()
    
    st.divider()
    
    # Input fields for medicines
    medicines_input = []
    
    for med_idx in range(st.session_state.med_count):
        col1, col2 = st.columns(2)
        with col1:
            med_name = st.text_input(f"💊 Medicine Name #{med_idx + 1}", placeholder="e.g., Aspirin", key=f"med_name_{med_idx}")
        with col2:
            med_dosage = st.text_input(f"📏 Dosage #{med_idx + 1}", placeholder="e.g., 1 tablet, 500mg", key=f"med_dosage_{med_idx}")
        
        col1, col2 = st.columns(2)
        with col1:
            med_frequency = st.selectbox(f"📅 Frequency #{med_idx + 1}", ["Daily", "Weekdays Only", "Weekends Only", "Custom Days"], key=f"med_freq_{med_idx}")
        with col2:
            st.write("")  # Empty space for alignment
        
        # Frequency selection
        selected_weekdays = []
        if med_frequency == "Daily":
            selected_weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        elif med_frequency == "Weekdays Only":
            selected_weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        elif med_frequency == "Weekends Only":
            selected_weekdays = ["Saturday", "Sunday"]
        elif med_frequency == "Custom Days":
            st.write(f"**Select which days for Medicine #{med_idx + 1}:**")
            col1, col2, col3, col4 = st.columns(4)
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            selected_days = []
            
            with col1:
                if st.checkbox("📍 Mon", key=f"mon_{med_idx}"):
                    selected_days.append("Monday")
                if st.checkbox("📍 Thu", key=f"thu_{med_idx}"):
                    selected_days.append("Thursday")
            with col2:
                if st.checkbox("📍 Tue", key=f"tue_{med_idx}"):
                    selected_days.append("Tuesday")
                if st.checkbox("📍 Fri", key=f"fri_{med_idx}"):
                    selected_days.append("Friday")
            with col3:
                if st.checkbox("📍 Wed", key=f"wed_{med_idx}"):
                    selected_days.append("Wednesday")
                if st.checkbox("📍 Sat", key=f"sat_{med_idx}"):
                    selected_days.append("Saturday")
            with col4:
                if st.checkbox("📍 Sun", key=f"sun_{med_idx}"):
                    selected_days.append("Sunday")
            
            selected_weekdays = selected_days if selected_days else ["Monday"]
        
        # Family emails
        family_emails_str = st.text_input(f"📧 Family Emails #{med_idx + 1} (optional)", 
                                          placeholder="e.g., mom@gmail.com, dad@gmail.com",
                                          help="Separate emails with commas",
                                          key=f"family_emails_{med_idx}")
        family_emails = [email.strip() for email in family_emails_str.split(",") if email.strip()]
        
        medicines_input.append({
            "name": med_name,
            "time": "00:00",
            "dosage": med_dosage,
            "frequency": med_frequency,
            "weekdays": selected_weekdays,
            "family_emails": family_emails
        })
        
        if med_idx < st.session_state.med_count - 1:
            st.divider()
    
    # Save all medicines
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 Save All Medicines", use_container_width=True, key="save_all_meds"):
            errors = []
            saved_count = 0
            
            for idx, med in enumerate(medicines_input):
                if not med['name'].strip():
                    errors.append(f"Medicine #{idx + 1}: Name is required")
                elif not med['dosage'].strip():
                    errors.append(f"Medicine #{idx + 1}: Dosage is required")
                else:
                    add_medication(med['name'], med['time'], med['dosage'], med['frequency'], med['weekdays'], med['family_emails'])
                    saved_count += 1
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            
            if saved_count > 0:
                st.success(f"✅ {saved_count} medicine(s) saved successfully!")
                time.sleep(1)
                st.session_state.med_count = 1
                st.rerun()
    
    with col2:
        if st.button("🧪 Test Sound", use_container_width=True, key="test_sound_add"):
            st.error("🚨 **SOUND TEST - Escalating**")
            play_alarm(continuous=False, frequency_level=3)
    
    with col3:
        if st.button("🔄 Clear Form", use_container_width=True, key="clear_form_add"):
            st.session_state.med_count = 1
            st.rerun()


# ==================== AI SUGGESTIONS ====================
elif page == "🤖 AI Suggestions":
    st.markdown("## 🤖 AI-Powered Medication & Health Insights")
    st.info("💡 Select your disease to get AI-powered recommendations, validated medications, and top doctors")
    
    st.divider()
    
    # Disease selection
    diseases = get_all_diseases()
    selected_disease = st.selectbox("🏥 Select Your Disease/Condition:", diseases, key="disease_selector")
    
    if selected_disease:
        col1, col2 = st.columns(2)
        
        # Medications Section
        with col1:
            st.markdown("### 💊 Recommended Medications")
            medications = get_medication_suggestions(selected_disease)
            
            if medications:
                for idx, med in enumerate(medications, 1):
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin: 10px 0; color: white;">
                    <b>{idx}. {med['name']}</b><br>
                    <span style="font-size: 12px;">📋 Dosage: {med['dosage']}</span><br>
                    <span style="font-size: 12px;">📝 Purpose: {med['purpose']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No medications found for this disease")
        
        # Doctors Section
        with col2:
            st.markdown("### 👨‍⚕️ Top Recommended Doctors")
            doctors = get_doctor_suggestions(selected_disease)
            
            if doctors:
                for idx, doc in enumerate(doctors, 1):
                    rating_stars = "⭐" * int(doc['rating']) + ("½⭐" if doc['rating'] % 1 >= 0.5 else "")
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 15px; border-radius: 10px; margin: 10px 0; color: white;">
                    <b>{idx}. Dr. {doc['name']}</b><br>
                    <span style="font-size: 12px;">🎓 Specialty: {doc['specialty']}</span><br>
                    <span style="font-size: 12px;">📅 Experience: {doc['experience']}</span><br>
                    <span style="font-size: 12px;">🏥 Hospital: {doc['hospital']}</span><br>
                    <span style="font-size: 12px;">📍 Location: {doc['location']}</span><br>
                    <span style="font-size: 14px;">{rating_stars} ({doc['rating']}/5.0)</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No doctors found for this disease")
        
        st.divider()
        
        # AI-Powered Health Insights Section
        st.markdown("### 🧠 AI-Powered Health Insights (LLM-Generated)")
        
        # Get patient data for context
        username = st.session_state.current_user["username"] if st.session_state.current_user else None
        patient_data = get_user_patient_data(username) if username else None
        patient_age = patient_data.get('age') if patient_data else None
        patient_meds = patient_data.get('medication', '') if patient_data else ''
        
        if st.button("🤖 Get Personalized AI Insights", use_container_width=True, key="generate_insights"):
            with st.spinner("🧠 AI is analyzing your condition and generating personalized insights..."):
                insights = get_llm_health_insights(
                    selected_disease, 
                    medications,
                    patient_age=patient_age,
                    medications_list=[patient_meds] if patient_meds else None
                )
                
                if insights:
                    # Display insights in a proper container with text visible
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 25px; border-radius: 15px; color: white; margin-top: 20px; border: 2px solid #00d4ff;">
                    <div style="font-family: 'Arial', sans-serif; line-height: 1.8; font-size: 14px; white-space: pre-wrap; word-wrap: break-word;">
                    {format_llm_response(insights)}
                    </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Save insights to session
                    st.session_state.last_insights = insights
                    st.success("✅ AI insights generated successfully!")
                else:
                    st.error("❌ Failed to generate insights. Please try again.")
        
        st.divider()
        
        # ========== NEW FEATURES SECTION ==========
        st.markdown("### 🌟 Additional Health Recommendations")
        
        # Create tabs for different recommendations
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🥗 Diet Plan", "💪 Exercise", "🔍 Drug Check", "📋 Preventive Care", "💰 Affordable Options"])
        
        with tab1:
            st.markdown("#### 🥗 Disease-Specific Diet Recommendations")
            diet = get_diet_recommendations(selected_disease)
            st.markdown(f"**{diet['title']}**")
            
            col_diet1, col_diet2 = st.columns(2)
            with col_diet1:
                st.markdown("**❌ Foods to Avoid:**")
                for food in diet['avoid']:
                    st.markdown(f"• {food}")
            
            with col_diet2:
                st.markdown("**✅ Foods to Include:**")
                for food in diet['include']:
                    st.markdown(f"• {food}")
            
            st.markdown("**🍽️ Meal Ideas:**")
            for meal in diet['meal_ideas']:
                st.markdown(f"• {meal}")
            
            st.markdown("**💡 Tips:**")
            for tip in diet['tips']:
                st.markdown(f"• {tip}")
        
        with tab2:
            st.markdown("#### 💪 Personalized Exercise Plan")
            exercise = get_exercise_plan(selected_disease, patient_age)
            st.markdown(f"**{exercise['title']}**")
            
            col_ex1, col_ex2 = st.columns(2)
            with col_ex1:
                st.markdown(f"**📅 Frequency:** {exercise['frequency']}")
                st.markdown(f"**⏱️ Duration:** {exercise['duration']}")
            with col_ex2:
                st.markdown("**🎯 Benefits:**")
                for benefit in exercise['benefits']:
                    st.markdown(f"• {benefit}")
            
            st.markdown("**🏃 Recommended Exercises:**")
            for ex in exercise['exercises']:
                st.markdown(f"• {ex}")
            
            st.markdown("**⚠️ Precautions:**")
            for precaution in exercise['precautions']:
                st.markdown(f"• {precaution}")
        
        with tab3:
            st.markdown("#### 🔍 Drug Interaction Checker")
            st.info("Check if your medications have any interactions")
            
            # Get current medications
            if st.session_state.current_user:
                current_meds = get_medications()  # No argument needed
                med_names_list = [med['name'] for med in current_meds]
                
                if med_names_list:
                    st.markdown(f"**Your Current Medications:** {', '.join(med_names_list)}")
                    
                    interactions = check_drug_interactions(med_names_list)
                    
                    if interactions:
                        st.warning("⚠️ Potential Drug Interactions Found!")
                        for interaction in interactions:
                            severity_color = "🔴" if interaction["severity"] == "HIGH" else "🟡"
                            st.markdown(f"""
                            {severity_color} **{interaction['severity']} - {interaction['drugs']}**
                            - **Warning:** {interaction['warning']}
                            - **Recommendation:** {interaction['recommendation']}
                            """)
                    else:
                        st.success("✅ No major drug interactions detected!")
                else:
                    st.info("Add medications first to check for interactions")
            else:
                st.info("Please login to check drug interactions")
        
        with tab4:
            st.markdown("#### 📋 Preventive Care Plan")
            preventive = get_preventive_care_tips(selected_disease)
            
            st.markdown("**🔬 Recommended Screening Tests:**")
            for screening in preventive['screening']:
                st.markdown(f"• {screening}")
            
            st.markdown("**⚠️ Complications to Prevent:**")
            for comp in preventive['complications_to_prevent']:
                st.markdown(f"• {comp}")
            
            st.markdown("**🏥 Self-Care Tips:**")
            for care in preventive['self_care']:
                st.markdown(f"• {care}")
        
        with tab5:
            st.markdown("#### 💰 Cost-Effective Medication Alternatives")
            st.info("Generic alternatives with similar effectiveness at lower cost")
            
            alternatives = get_affordable_medication_alternatives(selected_disease)
            
            for alt in alternatives:
                st.markdown(f"""
                **{alt['original']} → {alt['generic']}**
                - 💰 Cost Saving: {alt['cost_saving']}
                - 📝 Note: {alt['note']}
                """)
        
        st.divider()
        # Add to Medications Button
        st.markdown("### ➕ Quick Add Medications")
        col_med1, col_med2 = st.columns(2)
        
        medications = get_medication_suggestions(selected_disease)
        med_names = [f"{med['name']} ({med['dosage']})" for med in medications]
        
        with col_med1:
            selected_med = st.selectbox("Choose medication to add:", med_names, key="med_selector")
        
        with col_med2:
            if st.button("➕ Add to My Medicines", use_container_width=True):
                if selected_med:
                    med_name = selected_med.split(" (")[0]
                    med_dosage = selected_med.split(" (")[1].rstrip(")")
                    med_time = st.time_input("Select time to take medicine:", key="med_time_selector")
                    
                    if st.button("💾 Save Medicine", key="save_suggested_med"):
                        add_medication(med_name, med_time.strftime("%H:%M"), med_dosage)
                        st.success(f"✅ {med_name} added to your medicines!")
                        time.sleep(1)
                        st.rerun()


# ==================== MEDICINE REMINDERS ====================
elif page == "⏰ Reminders":
    render_medicine_reminders_page()


# ==================== HEALTH Q&A CHAT ====================
elif page == "💬 Health Q&A":
    st.markdown("## 💬 AI Health Assistant - Ask Any Health Question")
    st.info("🤖 Ask me anything about health, diseases, medications, exercise, diet, or wellness. I'll provide evidence-based answers!")
    
    st.divider()
    
    # Initialize chat history
    if "health_chat_history" not in st.session_state:
        st.session_state.health_chat_history = []
    
    # Display chat history
    if st.session_state.health_chat_history:
        st.markdown("### 📝 Chat History")
        for msg in st.session_state.health_chat_history:
            if msg["role"] == "user":
                st.markdown(f"**👤 You:** {msg['content']}")
            else:
                st.markdown(f"**🤖 AI Assistant:** {msg['content']}")
            st.divider()
    
    # Input section
    st.markdown("### 🗣️ Ask Your Question")
    
    user_question = st.text_area(
        "Type your health question here:",
        placeholder="Example: How do I manage diabetes? | What are symptoms of high blood pressure? | Best exercises for back pain?",
        height=100,
        key="health_question_input"
    )
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        if st.button("🚀 Get AI Answer", use_container_width=True, key="submit_health_question"):
            if user_question.strip():
                with st.spinner("🧠 AI is analyzing your question..."):
                    # Get AI response
                    response = ask_health_question(
                        user_question,
                        chat_history=st.session_state.health_chat_history
                    )
                    
                    if response["success"]:
                        # Add to chat history
                        st.session_state.health_chat_history.append({
                            "role": "user",
                            "content": user_question
                        })
                        st.session_state.health_chat_history.append({
                            "role": "assistant",
                            "content": response["answer"]
                        })
                        
                        # Display the answer
                        st.markdown("---")
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 25px; border-radius: 15px; color: white; margin-top: 20px; border: 2px solid #00d4ff;">
                        <div style="font-family: 'Arial', sans-serif; line-height: 1.8; font-size: 14px; white-space: pre-wrap; word-wrap: break-word;">
                        {response['answer']}
                        </div>
                        <p style="margin-top: 15px; font-size: 12px; opacity: 0.8;">📊 Source: {response['source']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.success("✅ Answer saved to chat history!")
                        st.rerun()
                    else:
                        st.error(f"❌ {response['answer']}")
            else:
                st.warning("⚠️ Please enter a question first")
    
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_chat"):
            st.session_state.health_chat_history = []
            st.success("✅ Chat cleared!")
            st.rerun()
    
    st.divider()
    
    # Quick example questions
    st.markdown("### 💡 Quick Examples")
    st.markdown("""
    Try asking about:
    - **Diseases:** "How to manage diabetes?" | "Symptoms of heart disease?"
    - **Medications:** "Side effects of aspirin" | "Drug interactions?"
    - **Lifestyle:** "Best exercises for weight loss" | "Healthy diet tips"
    - **Symptoms:** "What causes headaches?" | "When should I see a doctor?"
    - **Prevention:** "How to prevent infections?" | "Wellness tips"
    """)    
    
    # Disclaimer
    st.warning("""
    ⚠️ **IMPORTANT DISCLAIMER:**
    - This AI is for informational purposes only
    - Not a substitute for professional medical advice
    - This tool should not be used for self-diagnosis
    - For emergency situations, call your local emergency services
    - Always consult a qualified healthcare provider for diagnosis and treatment
    """)