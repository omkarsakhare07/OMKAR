import streamlit as st
import pandas as pd
from datetime import datetime
import time
import base64
import os

from database import (add_medication, get_medications, get_active_medications, 
                      delete_medication, delete_all_medications, stop_medication, 
                      resume_medication, edit_medication)
from reminder import check_reminders, play_system_sound

# ---------- Custom CSS for Better UI ----------
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    
    .medicine-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    
    .reminder-active {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    
    .action-button {
        border-radius: 8px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Load Audio File ----------
@st.cache_resource
def load_audio_file():
    """Load audio file and convert to base64"""
    try:
        # Try MP4 first
        audio_path = r"C:\Users\prath\Desktop\tone.mp4"
        if not os.path.exists(audio_path):
            # Try MP3
            audio_path = r"C:\Users\prath\Desktop\tone.mp3"
        
        if os.path.exists(audio_path):
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            audio_base64 = base64.b64encode(audio_data).decode()
            return audio_base64, audio_path.split('.')[-1]
    except Exception as e:
        print(f"Audio load error: {e}")
    
    return None, None

AUDIO_BASE64, AUDIO_FORMAT = load_audio_file()

# ---------- Page Config ----------
st.set_page_config(
    page_title="CareMed_AI",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Session State ----------
if "last_reminder_time" not in st.session_state:
    st.session_state.last_reminder_time = None

if "show_reminder_popup" not in st.session_state:
    st.session_state.show_reminder_popup = False

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# ---------- Sound Function ----------
def play_alarm(with_audio=True):
    """Play alarm sound"""
    
    if with_audio and AUDIO_BASE64:
        audio_type = f"audio/{AUDIO_FORMAT}" if AUDIO_FORMAT else "audio/mp4"
        sound_html = f"""
        <audio autoplay style="display:none;">
            <source src="data:{audio_type};base64,{AUDIO_BASE64}" type="{audio_type}">
        </audio>
        """
        st.markdown(sound_html, unsafe_allow_html=True)
    
    # Python beep
    try:
        if os.name == 'nt':
            import winsound
            winsound.Beep(1000, 500)
    except:
        pass

# ---------- Medicine Animation ----------
def show_medicine_animation():
    """Show animated medicine"""
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("""
        <style>
            @keyframes bounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-30px); }
            }
            .medicine {
                font-size: 100px;
                animation: bounce 0.6s infinite;
                text-align: center;
            }
        </style>
        <div class="medicine">💊</div>
        """, unsafe_allow_html=True)

# ---------- MAIN TITLE ----------
st.markdown("""
<div class="main-header">
    <h1>💊 CareMed_AI</h1>
    <p>AI-Based Medication & Reminder System</p>
</div>
""", unsafe_allow_html=True)

# ---------- SIDEBAR NAVIGATION ----------
st.sidebar.markdown("## 📋 Menu")
page = st.sidebar.radio("", ["🏠 Home", "➕ Add Medicine", "👁️ View All", "⏰ Active Reminder"])

# ==================== PAGE 1: HOME ====================
if page == "🏠 Home":
    st.markdown("## 🏠 Home Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    meds = get_medications()
    active_count = len([m for m in meds if m.get("active", True)])
    total_count = len(meds)
    
    with col1:
        st.metric("Total Medicines", total_count, delta="medicines added")
    
    with col2:
        st.metric("Active Reminders", active_count, delta="active")
    
    with col3:
        st.metric("Stopped", total_count - active_count, delta="paused")
    
    st.divider()
    
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔊 Test Alarm", use_container_width=True, key="test_home"):
            with st.container():
                st.error("🚨 **TEST ALARM ACTIVATED**")
                play_alarm()
                show_medicine_animation()
    
    with col2:
        if st.button("🔄 Refresh Now", use_container_width=True, key="refresh_home"):
            st.rerun()
    
    st.divider()
    
    if meds:
        st.markdown("### 📝 Recent Medicines")
        recent = meds[-3:] if len(meds) > 3 else meds
        
        for med in reversed(recent):
            status = "🟢 Active" if med.get("active", True) else "🔴 Stopped"
            st.markdown(f"""
            <div class="medicine-card">
                <b>{med['name']}</b> - {med['time']} | {med['dosage']} | {status}
            </div>
            """, unsafe_allow_html=True)

# ==================== PAGE 2: ADD MEDICINE ====================
elif page == "➕ Add Medicine":
    st.markdown("## ➕ Add New Medicine")
    
    col1, col2 = st.columns(2)
    
    with col1:
        med_name = st.text_input("💊 Medicine Name", placeholder="e.g., Aspirin")
    
    with col2:
        med_time = st.time_input("🕐 Time to Take")
    
    med_dosage = st.text_input("📏 Dosage", placeholder="e.g., 1 tablet, 5ml")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Medicine", use_container_width=True):
            if med_name:
                add_medication(med_name, med_time.strftime("%H:%M"), med_dosage)
                st.success("✅ Medicine saved successfully!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Please enter medicine name")
    
    with col2:
        if st.button("🧪 Test Sound", use_container_width=True):
            st.error("🚨 **SOUND TEST**")
            play_alarm()
    
    with col3:
        if st.button("❌ Clear", use_container_width=True):
            st.rerun()

# ==================== PAGE 3: VIEW ALL ====================
elif page == "👁️ View All":
    st.markdown("## 👁️ Manage All Medicines")
    
    meds = get_medications()
    
    if meds:
        # Display all medicines
        st.markdown("### 📋 All Medicines")
        
        display_data = []
        for med in meds:
            status = "🟢 Active" if med.get("active", True) else "🔴 Stopped"
            display_data.append({
                "ID": med['id'],
                "Medicine": med['name'],
                "Time": med['time'],
                "Dosage": med['dosage'],
                "Status": status
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.divider()
        st.markdown("### ⚙️ Advanced Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            med_select = st.selectbox(
                "Select Medicine",
                [f"{m['name']} ({m['time']})" for m in meds],
                key="manage_select"
            )
        
        selected_med = None
        for m in meds:
            if f"{m['name']} ({m['time']})" == med_select:
                selected_med = m
                break
        
        with col2:
            st.write("")
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✏️ Edit", use_container_width=True, key="edit_view"):
                st.session_state.editing = True
        
        with col2:
            if selected_med and selected_med.get("active", True):
                if st.button("⏸️ Stop", use_container_width=True):
                    stop_medication(selected_med['id'])
                    st.success("⏸️ Stopped!")
                    st.rerun()
            else:
                if st.button("▶️ Resume", use_container_width=True):
                    resume_medication(selected_med['id'])
                    st.success("▶️ Resumed!")
                    st.rerun()
        
        with col3:
            if st.button("🗑️ Delete", use_container_width=True):
                delete_medication(selected_med['id'])
                st.success("🗑️ Deleted!")
                st.rerun()
        
        with col4:
            if st.button("🗑️ Delete All", use_container_width=True):
                if st.session_state.get("confirm_delete"):
                    delete_all_medications()
                    st.success("All deleted!")
                    st.rerun()
                else:
                    st.session_state.confirm_delete = True
                    st.warning("Click again to confirm")
        
        # Edit section
        if "editing" in st.session_state and st.session_state.editing:
            st.divider()
            st.markdown("### ✏️ Edit Medicine")
            
            edit_col1, edit_col2, edit_col3 = st.columns(3)
            
            with edit_col1:
                new_name = st.text_input("Name", value=selected_med['name'])
            with edit_col2:
                new_time = st.text_input("Time (HH:MM)", value=selected_med['time'])
            with edit_col3:
                new_dosage = st.text_input("Dosage", value=selected_med['dosage'])
            
            if st.button("💾 Save Changes"):
                edit_medication(selected_med['id'], new_name, new_time, new_dosage)
                st.success("✅ Updated!")
                st.session_state.editing = False
                st.rerun()
    
    else:
        st.info("ℹ️ No medicines added yet. Go to 'Add Medicine' to get started!")

# ==================== PAGE 4: ACTIVE REMINDER ====================
elif page == "⏰ Active Reminder":
    st.markdown("## ⏰ Real-Time Reminder")
    
    # Auto-refresh
    placeholder = st.empty()
    
    while True:
        current_time = datetime.now().strftime("%H:%M")
        active_reminders = check_reminders()
        
        with placeholder.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**Current Time:** {current_time}")
            
            with col2:
                if st.button("🔄 Refresh", key="refresh_reminder"):
                    st.rerun()
            
            with col3:
                if st.button("🔊 Test", key="test_reminder"):
                    st.error("🚨 **TEST REMINDER**")
                    play_alarm()
                    show_medicine_animation()
            
            st.divider()
            
            if active_reminders:
                active_reminders = [m for m in active_reminders if m.get("active", True)]
                
                if active_reminders:
                    if st.session_state.last_reminder_time != current_time:
                        for med in active_reminders:
                            st.markdown(f"""
                            <div class="reminder-active">
                                <h2>🚨 TIME TO TAKE: {med['name'].upper()}!</h2>
                                <h4>Dosage: {med['dosage']}</h4>
                                <p>Time: {med['time']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            play_alarm()
                            show_medicine_animation()
                        
                        st.session_state.last_reminder_time = current_time
                    else:
                        st.info("✅ Already reminded for this time")
                else:
                    st.info("ℹ️ No active reminders right now")
            else:
                st.info(f"ℹ️ No reminders scheduled for {current_time}")
        
        time.sleep(5)
