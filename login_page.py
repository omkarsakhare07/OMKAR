import streamlit as st
import re
import time
from datetime import datetime

# ---------- Page Config ----------
st.set_page_config(page_title="CareMed_AI - Login", page_icon="🔐", layout="centered")

# ---------- Custom CSS for Advanced Login UI ----------
st.markdown("""
<style>
    .login-container {
        max-width: 420px;
        margin: 0 auto;
        padding: 45px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
        color: white;
    }
    .login-header {
        text-align: center;
        margin-bottom: 35px;
    }
    .login-header h1 {
        font-size: 2.8em;
        margin-bottom: 12px;
        font-weight: 700;
        text-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    .login-header p {
        font-size: 1.15em;
        opacity: 0.95;
        font-weight: 500;
    }
    .input-field {
        margin-bottom: 20px;
    }
    .input-field label {
        display: block;
        margin-bottom: 5px;
        font-weight: bold;
    }
    .stTextInput > div > div > input {
        width: 100% !important;
        padding: 15px 18px !important;
        border: 2px solid #1e88e5 !important;
        border-radius: 12px !important;
        font-size: 15px !important;
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        transition: all 0.3s ease !important;
        font-weight: 500 !important;
        box-shadow: 0 2px 8px rgba(30, 136, 229, 0.1) !important;
    }
    input[type="text"]::placeholder, input[type="password"]::placeholder {
        color: #999999 !important;
    }
    input[type="text"]:focus, input[type="password"]:focus {
        border-color: #4CAF50 !important;
        background-color: #f8f9ff !important;
        box-shadow: 0 0 25px rgba(76, 175, 80, 0.5) !important;
        outline: none !important;
    }
    .stTextInput label {
        color: white !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        text-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
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
    }
    .login-button:hover {
        transform: translateY(-2px);
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

# ---------- Session State Initialization ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "patient_data" not in st.session_state:
    st.session_state.patient_data = {}

# ---------- Validation Functions ----------
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

# ---------- Login Form ----------
def login_form():
    # Blue gradient brand box with logo and CareMed text (centered, above login)
    st.markdown('''
    <div style="display:flex; justify-content:center; align-items:center; margin-bottom:35px;">
        <div style="padding:28px 60px; border-radius:18px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); box-shadow:0 8px 32px rgba(102,126,234,0.25); display:flex; flex-direction:column; align-items:center;">
            <span style="font-size:54px; margin-bottom:8px;">💊</span>
            <span style="font-size:2.3em; font-weight:900; color:#fff; letter-spacing:1px; text-shadow:0 2px 8px rgba(0,0,0,0.18);">CareMed</span>
            <span style="font-size:1.1em; color:#e0e0e0; font-weight:500; margin-top:2px;">Medicine Notification System</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-header">', unsafe_allow_html=True)
    st.markdown('<h1 style="margin-top:0;">🔐 Login to Your Account</h1>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Username field
    username = st.text_input("👤 Username", placeholder="Enter your username", key="username")
    
    # Email field
    email = st.text_input("📧 Email Address", placeholder="Enter your email", key="email")
    
    # Password field
    password = st.text_input("🔒 Password", placeholder="Enter your password", type="password", key="password")
    
    # Login button
    if st.button("🚀 Login / Sign In", key="login_button", help="Click to login or sign in"):
        # Validation
        errors = []
        
        # Validate username
        username_valid, username_msg = validate_username(username)
        if not username_valid:
            errors.append(f"👤 {username_msg}")
        
        # Validate email
        if not validate_email(email):
            errors.append("📧 Please enter a valid email address")
        
        # Validate password
        password_valid, password_msg = validate_password(password)
        if not password_valid:
            errors.append(f"🔒 {password_msg}")
        
        # Display errors or success
        if errors:
            for error in errors:
                st.markdown(f'<div class="error-message">{error}</div>', unsafe_allow_html=True)
        else:
            # Success - store login info and redirect
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.email = email
            st.markdown('<div class="success-message">✅ Login successful! Redirecting...</div>', unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()
    
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown('<p>💊 CareMed_AI - Your AI Medication Assistant</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Patient Details Form ----------
def patient_details_form():
    st.markdown("""
    <style>
        .patient-container {
            max-width: 650px;
            margin: 0 auto;
            padding: 40px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border-radius: 20px;
            box-shadow: 0 15px 40px rgba(245, 87, 108, 0.4);
            color: white;
        }
        .patient-header {
            text-align: center;
            margin-bottom: 35px;
        }
        .patient-header h1 {
            font-size: 2.5em;
            margin-bottom: 12px;
            font-weight: 700;
            text-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }
        .form-section {
            background: rgba(255,255,255,0.15);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 25px;
            border: 1px solid rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
        }
        .form-section h3 {
            margin-top: 0;
            color: #fff;
            font-weight: 700;
            font-size: 1.2em;
        }
        .stTextInput > div > div > input, .stNumberInput > div > div > input, .stTextArea > div > div > textarea {
            background: rgba(255,255,255,0.95) !important;
            color: #1a1a1a !important;
            border: 2px solid rgba(255,255,255,0.3) !important;
            border-radius: 12px !important;
            font-weight: 500 !important;
        }
        .submit-button {
            width: 100%;
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 16px;
            border: none;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            margin-top: 20px;
            transition: all 0.3s ease;
            box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        }
        .submit-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .back-button {
            width: 100%;
            background: linear-gradient(135deg, #ff6b6b 0%, #ff5252 100%);
            color: white;
            padding: 14px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 10px;
            font-weight: 700;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }
        .back-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.25);
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="patient-container">', unsafe_allow_html=True)
    st.markdown('<div class="patient-header">', unsafe_allow_html=True)
    st.markdown('<h1>📋 Patient Details</h1>', unsafe_allow_html=True)
    st.markdown('<p>Please fill in the patient information</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Personal Information Section
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<h3>👤 Personal Information</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("Full Name", placeholder="Enter patient's full name", key="patient_name")
    with col2:
        patient_age = st.number_input("Age", min_value=1, max_value=120, key="patient_age")
    
    patient_disease = st.text_area("Disease/Condition", placeholder="Describe the patient's medical condition", height=100, key="patient_disease")
    st.markdown('</div>', unsafe_allow_html=True)

    # Medication Information Section
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<h3>💊 Medication Information</h3>', unsafe_allow_html=True)
    
    medication = st.text_area("Prescribed Medication", placeholder="List all prescribed medications with dosages", height=100, key="medication")
    st.markdown('</div>', unsafe_allow_html=True)

    # Family Contact Information Section
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<h3>📞 Family Contact Details</h3>', unsafe_allow_html=True)
    
    family_contacts = st.text_area("Family Member Contacts", 
                                   placeholder="Enter family member names and contact details (e.g., John Doe - 123-456-7890, jane@email.com)", 
                                   height=100, key="family_contacts")
    st.markdown('</div>', unsafe_allow_html=True)

    # Submit and Back buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Patient Details", key="save_details", help="Save the patient information"):
            # Validate required fields
            if not patient_name.strip():
                st.error("❌ Please enter the patient's name")
            elif not patient_disease.strip():
                st.error("❌ Please enter the patient's disease/condition")
            elif not medication.strip():
                st.error("❌ Please enter prescribed medication")
            elif not family_contacts.strip():
                st.error("❌ Please enter family contact details")
            else:
                # Save to session state
                st.session_state.patient_data = {
                    "name": patient_name,
                    "age": patient_age,
                    "disease": patient_disease,
                    "medication": medication,
                    "family_contacts": family_contacts,
                    "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.success("✅ Patient details saved successfully!")
                time.sleep(1)
    
    with col2:
        if st.button("🔙 Back to Login", key="back_to_login", help="Return to login page"):
            st.session_state.logged_in = False
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Main App Logic ----------
if not st.session_state.logged_in:
    login_form()
else:
    patient_details_form()

# ---------- Footer ----------
st.markdown("---")
st.markdown("**🔐 Secure Login System** | **📊 Patient Management** | **💊 CareMed_AI**")