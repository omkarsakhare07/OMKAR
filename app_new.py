import streamlit as st
import pandas as pd
from datetime import datetime
import time

from database import (add_medication, get_medications, get_active_medications, 
                      delete_medication, delete_all_medications, stop_medication, 
                      resume_medication, edit_medication)
from reminder import check_reminders

# ---------- Page Config ----------
st.set_page_config(
    page_title="CareMed_AI",
    page_icon="💊",
    layout="centered"
)

# ---------- Session State ----------
if "last_reminder_time" not in st.session_state:
    st.session_state.last_reminder_time = None

# ---------- Advanced Sound Function - Multiple Methods ----------
def play_alarm_sound():
    """Play alarm sound using multiple methods for reliability"""
    
    sound_js = """
    <script>
        // Attempt 1: Web Audio API with maximum volume
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            function createBeep(freq, duration, startTime, volume = 0.8) {
                const osc = audioContext.createOscillator();
                const gain = audioContext.createGain();
                const filter = audioContext.createBiquadFilter();
                
                osc.frequency.setValueAtTime(freq, audioContext.currentTime);
                osc.type = 'square'; // Square wave is louder than sine
                
                gain.gain.setValueAtTime(volume, audioContext.currentTime + startTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + startTime + duration);
                
                osc.connect(filter);
                filter.connect(gain);
                gain.connect(audioContext.destination);
                
                osc.start(audioContext.currentTime + startTime);
                osc.stop(audioContext.currentTime + startTime + duration);
            }
            
            // Aggressive alarm pattern
            createBeep(1200, 0.3, 0, 1);      // Loud high tone
            createBeep(1500, 0.3, 0.35, 1);   // Even higher
            createBeep(1200, 0.3, 0.7, 1);    // Back to first
            createBeep(1800, 0.5, 1.05, 1);   // Very high, longer
        } catch(e) {
            console.log('Audio method 1 error');
        }
    </script>
    """
    
    st.markdown(sound_js, unsafe_allow_html=True)

# ---------- Medicine Animation ----------
def show_medicine_animation():
    """Show animated medicine bottle"""
    animation_html = """
    <style>
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }
        
        @keyframes rotate {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .medicine-bottle {
            font-size: 80px;
            animation: bounce 0.6s infinite;
            text-align: center;
        }
        
        .medicine-spin {
            font-size: 60px;
            display: inline-block;
            animation: rotate 2s linear infinite;
        }
    </style>
    <div class="medicine-bottle">💊</div>
    """
    st.markdown(animation_html, unsafe_allow_html=True)

# ---------- Title ----------
st.markdown("<h1 style='text-align:center;'>💊 CareMed_AI</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;'>AI‑Based Medication & Appointment Reminder System</p>",
    unsafe_allow_html=True
)
st.divider()

# ---------- Add Medication ----------
st.subheader("➕ Add Medication")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Medicine Name")
with col2:
    med_time = st.time_input("Medicine Time")

dosage = st.text_input("Dosage (e.g. 1 tablet)")

if st.button("💾 Save Medication", use_container_width=True):
    if name:
        add_medication(name, med_time.strftime("%H:%M"), dosage)
        st.success("✅ Medication saved successfully!")
        time.sleep(1)
        st.rerun()
    else:
        st.error("Medicine name required")

st.divider()

# ---------- Test Alarm ----------
st.subheader("🧪 Test Notification & Sound")
col1, col2 = st.columns(2)

with col1:
    if st.button("🔊 Test Alarm", use_container_width=True):
        st.error("🚨 **TEST ALARM - Medicine Reminder!**\n\nCheck if you can hear the sound!")
        play_alarm_sound()
        show_medicine_animation()

with col2:
    if st.button("🔄 Refresh Reminders", use_container_width=True):
        st.rerun()

st.divider()

# ---------- View All Reminders (Expandable) ----------
st.subheader("📋 All Reminders")

with st.expander("👁️ View & Manage All Reminders", expanded=False):
    meds = get_medications()
    
    if meds:
        # Show all reminders in a table
        display_data = []
        for med in meds:
            status = "🟢 Active" if med.get("active", True) else "🔴 Stopped"
            display_data.append({
                "Medicine": med['name'],
                "Time": med['time'],
                "Dosage": med['dosage'],
                "Status": status
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Advanced Management Section
        st.write("**Advanced Management:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            med_select = st.selectbox(
                "Select medicine",
                [f"{m['name']} - {m['time']}" for m in meds],
                key="med_manage"
            )
        
        selected_med = None
        for m in meds:
            if f"{m['name']} - {m['time']}" == med_select:
                selected_med = m
                break
        
        # Action buttons for selected medicine
        action_col1, action_col2, action_col3, action_col4 = st.columns(4)
        
        with action_col1:
            if st.button("✏️ Edit", use_container_width=True, key="edit_btn"):
                st.session_state.editing = True
        
        with action_col2:
            if selected_med and selected_med.get("active", True):
                if st.button("⏸️ Stop", use_container_width=True, key="stop_btn"):
                    stop_medication(selected_med['id'])
                    st.success("✅ Reminder stopped!")
                    st.rerun()
            else:
                if st.button("▶️ Resume", use_container_width=True, key="resume_btn"):
                    resume_medication(selected_med['id'])
                    st.success("✅ Reminder resumed!")
                    st.rerun()
        
        with action_col3:
            if st.button("🗑️ Delete", use_container_width=True, key="delete_btn"):
                delete_medication(selected_med['id'])
                st.success("✅ Reminder deleted!")
                st.rerun()
        
        with action_col4:
            if st.button("🗑️ Delete All", use_container_width=True, key="delete_all_btn"):
                delete_all_medications()
                st.success("✅ All reminders deleted!")
                st.rerun()
        
        # Edit section
        if "editing" in st.session_state and st.session_state.editing:
            st.write("**Edit Reminder:**")
            
            edit_col1, edit_col2, edit_col3 = st.columns(3)
            
            with edit_col1:
                new_name = st.text_input("New name", value=selected_med['name'], key="edit_name")
            with edit_col2:
                new_time = st.text_input("New time (HH:MM)", value=selected_med['time'], key="edit_time")
            with edit_col3:
                new_dosage = st.text_input("New dosage", value=selected_med['dosage'], key="edit_dosage")
            
            if st.button("💾 Save Changes", use_container_width=True):
                edit_medication(selected_med['id'], new_name, new_time, new_dosage)
                st.success("✅ Reminder updated!")
                st.session_state.editing = False
                st.rerun()
        
    else:
        st.info("No reminders added yet.")

st.divider()

# ---------- Active Reminder Checker ----------
st.subheader("⏰ Active Reminder")

current_time = datetime.now().strftime("%H:%M")
active_reminders = check_reminders()

if active_reminders:
    # Filter only active medications
    active_reminders = [m for m in active_reminders if m.get("active", True)]
    
    if active_reminders:
        if st.session_state.last_reminder_time != current_time:
            for med in active_reminders:
                st.error(f"🚨 **MEDICINE TIME: {med['name']}!**\n\nDosage: {med['dosage']}\nTime: {med['time']}")
                play_alarm_sound()
                show_medicine_animation()
            
            st.session_state.last_reminder_time = current_time
        else:
            st.info("✅ Reminder already shown for this time.")
    else:
        st.info(f"No active reminders right now. Current time: {current_time}")
else:
    st.info(f"No reminders at this time. Current time: {current_time}")
