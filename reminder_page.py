"""
Medicine Reminder Page - Advanced UI with Alarm Clock Interface
"""

import streamlit as st
from datetime import datetime, time as datetime_time, timedelta
import time
import textwrap
from reminder_manager import (
    load_reminders, create_reminder, update_reminder, delete_reminder,
    get_active_reminders, mark_reminder_taken, get_next_reminder,
    get_reminder_stats, log_notification
)
from database import get_medications

# Add custom CSS for alarm clock style
st.markdown("""
<style>
    /* Alarm Clock Container */
    .alarm-clock {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 25px;
        padding: 30px;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
        text-align: center;
        margin: 20px 0;
        border: 3px solid #764ba2;
        position: relative;
        overflow: hidden;
    }
    
    .alarm-clock::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
        background-size: 20px 20px;
        animation: float 20s infinite linear;
    }
    
    @keyframes float {
        0% { transform: translate(0, 0); }
        100% { transform: translate(50px, 50px); }
    }
    
    .alarm-time {
        font-size: 64px;
        font-weight: bold;
        color: #ffffff;
        font-family: 'Courier New', monospace;
        margin: 20px 0;
        text-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        letter-spacing: 5px;
    }
    
    .alarm-status {
        font-size: 18px;
        color: #e0e0e0;
        margin: 10px 0;
    }
    
    .alarm-medicine {
        font-size: 24px;
        color: #ffd700;
        font-weight: bold;
        margin: 15px 0;
        text-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
    }
    
    /* Reminder Cards */
    .reminder-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border-left: 5px solid #ffd700;
        color: white;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
        position: relative;
    }
    
    .reminder-card.urgent {
        border-left-color: #ff6b6b;
        background: linear-gradient(135deg, #ff6b6b 0%, #ff4757 100%);
    }
    
    .reminder-card.taken {
        opacity: 0.6;
        border-left-color: #51cf66;
    }
    
    .reminder-time-display {
        font-size: 32px;
        font-weight: bold;
        color: #ffd700;
        font-family: 'Courier New', monospace;
        margin: 10px 0;
    }
    
    .reminder-details {
        margin: 10px 0;
        font-size: 14px;
    }
    
    .reminder-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        padding: 5px 12px;
        border-radius: 20px;
        margin: 5px 5px 5px 0;
        font-size: 12px;
        font-weight: bold;
    }
    
    .stats-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        color: white;
        margin: 10px;
        border: 2px solid #764ba2;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stats-number {
        font-size: 28px;
        font-weight: bold;
        color: #ffd700;
    }
    
    .stats-label {
        font-size: 12px;
        margin-top: 5px;
        color: #e0e0e0;
    }
    
    /* Button Styles */
    .btn-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 24px;
        border: none;
        border-radius: 25px;
        font-weight: bold;
        cursor: pointer;
        margin: 5px;
        transition: all 0.3s ease;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    .btn-danger {
        background: #ff6b6b;
        color: white;
        padding: 8px 16px;
        border: none;
        border-radius: 20px;
        font-weight: bold;
        cursor: pointer;
        font-size: 12px;
    }
    
    .btn-success {
        background: #51cf66;
        color: white;
        padding: 8px 16px;
        border: none;
        border-radius: 20px;
        font-weight: bold;
        cursor: pointer;
        font-size: 12px;
    }
    
    /* Notification Banner */
    .notification-banner {
        background: linear-gradient(135deg, #ffd700 0%, #ffb700 100%);
        color: #333;
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
        border-left: 5px solid #ff9500;
        box-shadow: 0 5px 20px rgba(255, 215, 0, 0.3);
        animation: slideIn 0.5s ease;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .section-title {
        color: #667eea;
        font-size: 24px;
        font-weight: bold;
        margin: 30px 0 20px 0;
        border-bottom: 3px solid #667eea;
        padding-bottom: 10px;
    }
    
    .empty-state {
        text-align: center;
        padding: 40px 20px;
        color: #999;
    }
</style>
""", unsafe_allow_html=True)

def render_alarm_clock():
    """Render animated alarm clock display"""
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    
    next_reminder = get_next_reminder()
    next_time_text = "No reminders set"
    next_medicine_text = ""
    
    if next_reminder:
        next_time_text = next_reminder["time"]
        next_medicine_text = next_reminder["medicine_name"]
    
    html_content = f'''<div class="alarm-clock"><div style="position: relative; z-index: 1;"><div style="font-size: 14px; color: #e0e0e0; margin-bottom: 20px;">⏰ CURRENT TIME</div><div class="alarm-time">{current_time}</div><div style="margin-top: 20px; border-top: 2px solid rgba(255, 255, 255, 0.2); padding-top: 20px;"><div style="font-size: 14px; color: #e0e0e0; margin-bottom: 10px;">🔔 NEXT REMINDER</div><div class="alarm-time" style="font-size: 48px;">{next_time_text}</div><div class="alarm-medicine">{next_medicine_text}</div></div></div></div>'''
    st.markdown(html_content, unsafe_allow_html=True)

def render_statistics():
    """Render reminder statistics"""
    stats = get_reminder_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_html = f'<div class="stats-box"><div class="stats-number">{stats["total"]}</div><div class="stats-label">Total Reminders</div></div>'
        st.markdown(total_html, unsafe_allow_html=True)
    
    with col2:
        active_html = f'<div class="stats-box"><div class="stats-number">{stats["active"]}</div><div class="stats-label">Active</div></div>'
        st.markdown(active_html, unsafe_allow_html=True)
    
    with col3:
        today_html = f'<div class="stats-box"><div class="stats-number">{stats["today"]}</div><div class="stats-label">Today</div></div>'
        st.markdown(today_html, unsafe_allow_html=True)
    
    with col4:
        week_html = f'<div class="stats-box"><div class="stats-number">{stats["this_week"]}</div><div class="stats-label">This Week</div></div>'
        st.markdown(week_html, unsafe_allow_html=True)

def render_reminder_card(reminder):
    """Render a single reminder card"""
    is_taken = reminder.get("last_taken") is not None
    
    # Check if upcoming soon (within 1 hour)
    now = datetime.now()
    r_hour, r_minute = map(int, reminder["time"].split(":"))
    reminder_dt = now.replace(hour=r_hour, minute=r_minute, second=0, microsecond=0)
    
    time_diff = (reminder_dt - now).total_seconds() / 60  # in minutes
    is_urgent = 0 < time_diff <= 60
    
    card_class = "reminder-card urgent" if is_urgent else ("reminder-card taken" if is_taken else "reminder-card")
    
    status_badge = "✅ TAKEN" if is_taken else ("⚠️ URGENT" if is_urgent else "🔔 UPCOMING")
    status_color = "#51cf66" if is_taken else ("#ff6b6b" if is_urgent else "#ffd700")
    
    weekdays_text = ", ".join(reminder.get("weekdays", [])[:3]) + ("..." if len(reminder.get("weekdays", [])) > 3 else "")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        # Display reminder info as plain text, not HTML
        st.markdown(f"**{reminder['time']}** - 💊 **{reminder['medicine_name']}**")
        st.markdown(f"- 📊 **Dosage:** {reminder['dosage']}")
        st.markdown(f"- 📅 **Frequency:** {reminder['frequency']}")
        st.markdown(f"- 📆 **Days:** {weekdays_text}")
        if reminder.get('notes'):
            st.markdown(f"- 📝 **Notes:** {reminder['notes']}")
        if reminder.get('last_taken'):
            st.markdown(f"- ✅ **Last Taken:** {reminder['last_taken'][:10]}")
        # Notification badges as plain text
        badges = []
        if reminder.get('notification_enabled'):
            badges.append('🔔 Notifications ON')
        if reminder.get('sound_enabled'):
            badges.append('🔊 Sound ON')
        if reminder.get('pop_notification_enabled'):
            badges.append('📱 Pop Notification ON')
        if badges:
            st.markdown(' '.join(badges))
    
    with col2:
        if st.button("✏️", key=f"edit_{reminder['id']}", help="Edit reminder"):
            st.session_state.edit_reminder_id = reminder['id']
            st.session_state.show_edit_form = True
    
    with col3:
        if st.button("🗑️", key=f"delete_{reminder['id']}", help="Delete reminder"):
            if delete_reminder(reminder['id']):
                st.success(f"Reminder for {reminder['medicine_name']} deleted!")
                st.rerun()

def show_add_reminder_form():
    """Show form to add new reminder"""
    st.markdown("### ➕ Add New Medicine Reminder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        medicine_name = st.text_input(
            "🏥 Medicine Name *",
            placeholder="e.g., Aspirin, Metformin, Lisinopril",
            help="Enter the name of the medicine"
        )
        
        reminder_time = st.time_input(
            "⏰ Reminder Time *",
            value=datetime_time(9, 0),
            help="Set the time when you want to be reminded"
        )
        
        dosage = st.text_input(
            "📊 Dosage *",
            placeholder="e.g., 500mg, 1 tablet, 5ml",
            help="Enter the dosage amount"
        )
    
    with col2:
        frequency = st.selectbox(
            "📅 Frequency *",
            ["Daily", "Weekly", "Every other day"],
            help="How often to take the medicine"
        )
        
        if frequency == "Weekly":
            selected_days = st.multiselect(
                "📆 Select Days",
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                default=["Monday", "Wednesday", "Friday"],
                help="Choose days for this reminder"
            )
        else:
            selected_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        notes = st.text_input(
            "📝 Notes (Optional)",
            placeholder="e.g., Take with water, after breakfast",
            help="Any special instructions"
        )
    
    st.markdown("---")
    st.markdown("### 🔔 Notification Settings")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        notification_enabled = st.checkbox(
            "Enable Notifications",
            value=True,
            help="Receive notifications when it's time to take medicine"
        )
    
    with col2:
        pop_notification = st.checkbox(
            "Pop-up Notification",
            value=True,
            help="Show pop-up reminder with medicine name"
        )
    
    with col3:
        sound_enabled = st.checkbox(
            "Sound Alert",
            value=True,
            help="Play sound when reminder time arrives"
        )
    
    with col4:
        vibration_enabled = st.checkbox(
            "Vibration (Mobile)",
            value=True,
            help="Vibrate on mobile devices"
        )
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("💾 Save Reminder", use_container_width=True):
            if not medicine_name or not dosage or not reminder_time:
                st.error("❌ Please fill in all required fields (marked with *)")
            else:
                success, reminder_id = create_reminder(
                    medicine_name=medicine_name,
                    reminder_time=reminder_time.strftime("%H:%M"),
                    dosage=dosage,
                    frequency=frequency,
                    weekdays=selected_days if frequency == "Weekly" else None,
                    notes=notes,
                    notification_enabled=notification_enabled
                )
                
                if success:
                    st.success(f"✅ Reminder for {medicine_name} saved successfully!")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Failed to save reminder. Please try again.")

def show_edit_reminder_form(reminder_id):
    """Show form to edit existing reminder"""
    reminders = load_reminders()
    reminder = next((r for r in reminders.get("reminders", []) if r["id"] == reminder_id), None)
    
    if not reminder:
        st.error("Reminder not found")
        return
    
    st.markdown("### ✏️ Edit Medicine Reminder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        medicine_name = st.text_input(
            "🏥 Medicine Name *",
            value=reminder["medicine_name"]
        )
        
        time_parts = reminder["time"].split(":")
        reminder_time = st.time_input(
            "⏰ Reminder Time *",
            value=datetime_time(int(time_parts[0]), int(time_parts[1]))
        )
        
        dosage = st.text_input(
            "📊 Dosage *",
            value=reminder["dosage"]
        )
    
    with col2:
        frequency = st.selectbox(
            "📅 Frequency *",
            ["Daily", "Weekly", "Every other day"],
            index=["Daily", "Weekly", "Every other day"].index(reminder["frequency"])
        )
        
        if frequency == "Weekly":
            selected_days = st.multiselect(
                "📆 Select Days",
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                default=reminder.get("weekdays", [])
            )
        else:
            selected_days = reminder.get("weekdays", [])
        
        notes = st.text_input(
            "📝 Notes (Optional)",
            value=reminder.get("notes", "")
        )
    
    st.markdown("---")
    st.markdown("### 🔔 Notification Settings")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        notification_enabled = st.checkbox(
            "Enable Notifications",
            value=reminder.get("notification_enabled", True)
        )
    
    with col2:
        pop_notification = st.checkbox(
            "Pop-up Notification",
            value=reminder.get("pop_notification_enabled", True)
        )
    
    with col3:
        sound_enabled = st.checkbox(
            "Sound Alert",
            value=reminder.get("sound_enabled", True)
        )
    
    with col4:
        vibration_enabled = st.checkbox(
            "Vibration (Mobile)",
            value=reminder.get("vibration_enabled", True)
        )
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        if st.button("💾 Update Reminder", use_container_width=True):
            if not medicine_name or not dosage or not reminder_time:
                st.error("❌ Please fill in all required fields")
            else:
                update_reminder(
                    reminder_id,
                    medicine_name=medicine_name,
                    time=reminder_time.strftime("%H:%M"),
                    dosage=dosage,
                    frequency=frequency,
                    weekdays=selected_days,
                    notes=notes,
                    notification_enabled=notification_enabled,
                    pop_notification_enabled=pop_notification,
                    sound_enabled=sound_enabled,
                    vibration_enabled=vibration_enabled
                )
                st.success("✅ Reminder updated successfully!")
                st.session_state.show_edit_form = False
                time.sleep(1)
                st.rerun()
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.show_edit_form = False
            st.rerun()

def show_notification_popup(reminder):
    """Show pop-up notification for a reminder"""
    notes_section = f'<div style="font-size: 14px; margin: 10px 0; color: #666;"><strong>Note:</strong> {reminder.get("notes", "")}</div>' if reminder.get("notes") else ""
    
    popup_html = f'''
    <div class="notification-banner">
        <div style="font-size: 24px; font-weight: bold; margin-bottom: 10px;">
            🔔 TIME TO TAKE YOUR MEDICINE!
        </div>
        <div style="font-size: 32px; font-weight: bold; color: #ff6b6b; margin: 15px 0;">
            💊 {reminder["medicine_name"]}
        </div>
        <div style="font-size: 16px; margin: 10px 0;">
            <strong>Dosage:</strong> {reminder["dosage"]}
        </div>
        <div style="font-size: 16px; margin: 10px 0;">
            <strong>Scheduled Time:</strong> {reminder["time"]}
        </div>
        {notes_section}
    </div>
    '''
    st.markdown(popup_html, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Mark as Taken", key=f"taken_{reminder['id']}", use_container_width=True):
            mark_reminder_taken(reminder['id'])
            log_notification(reminder['id'], "pop")
            st.success("✅ Medicine marked as taken!")
            time.sleep(2)
            st.rerun()
    
    with col2:
        if st.button("⏰ Remind me later", key=f"later_{reminder['id']}", use_container_width=True):
            st.info("⏰ You'll be reminded in 5 minutes")

def render_medicine_reminders_page():
    """Main page for medicine reminders"""
    st.markdown("# Medicine Reminder")
    st.markdown("---")
    
    # Initialize session state
    if "show_edit_form" not in st.session_state:
        st.session_state.show_edit_form = False
    if "edit_reminder_id" not in st.session_state:
        st.session_state.edit_reminder_id = None
    
    # Check for active reminders to show pop-up
    now = datetime.now()
    current_reminders = []
    
    for reminder in get_active_reminders():
        r_hour, r_minute = map(int, reminder["time"].split(":"))
        if r_hour == now.hour and (r_minute >= now.minute - 1 and r_minute <= now.minute + 5):
            if not reminder.get("last_taken"):
                current_reminders.append(reminder)
    
    if current_reminders:
        st.markdown("## ⏰ ACTIVE REMINDERS NOW")
        st.markdown("---")
        for reminder in current_reminders:
            show_notification_popup(reminder)
        st.markdown("---")
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Dashboard",
        "➕ Add Reminder",
        "📋 All Reminders",
        "⚙️ Settings"
    ])
    
    with tab1:
        st.markdown('<div class="section-title">⏰ Alarm Clock Display</div>', unsafe_allow_html=True)
        render_alarm_clock()
        
        st.markdown('<div class="section-title">📊 Quick Statistics</div>', unsafe_allow_html=True)
        render_statistics()
        
        st.markdown("---")
        st.markdown("### 📌 Today's Schedule")
        
        today_reminders = []
        for reminder in get_active_reminders():
            if reminder.get("frequency") == "Daily":
                today_reminders.append(reminder)
        
        if today_reminders:
            today_reminders = sorted(today_reminders, key=lambda r: r["time"])
            for reminder in today_reminders:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{reminder['time']}** - 💊 {reminder['medicine_name']} ({reminder['dosage']})")
                with col2:
                    if reminder.get("last_taken"):
                        st.markdown("✅ Taken")
                    else:
                        st.markdown("⏳ Pending")
        else:
            st.info("📝 No reminders scheduled for today")
    
    with tab2:
        if st.session_state.show_edit_form and st.session_state.edit_reminder_id:
            show_edit_reminder_form(st.session_state.edit_reminder_id)
        else:
            show_add_reminder_form()
    
    with tab3:
        st.markdown('<div class="section-title">📋 Upcoming Medicine Reminders</div>', unsafe_allow_html=True)
        reminders = get_active_reminders()
        # Only show reminders that are not taken (upcoming)
        upcoming_reminders = [r for r in reminders if not r.get("last_taken")]
        if upcoming_reminders:
            # Optionally, sort by time
            upcoming_reminders = sorted(upcoming_reminders, key=lambda r: r["time"])
            for reminder in upcoming_reminders:
                render_reminder_card(reminder)
        else:
            empty_html = textwrap.dedent("""
            <div class="empty-state">
                <div style="font-size: 48px; margin-bottom: 20px;">📭</div>
                <div style="font-size: 18px; margin-bottom: 10px;">No upcoming reminders</div>
                <div style="font-size: 14px; color: #666;">
                    All reminders are completed or none are scheduled. Add a new reminder using the "Add Reminder" tab.
                </div>
            </div>
            """).strip()
            st.markdown(empty_html, unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="section-title">⚙️ Reminder Settings</div>', unsafe_allow_html=True)
        
        st.markdown("### 🔔 Global Notification Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Notification Preferences:**
            - Enable/disable all notifications
            - Sound alerts
            - Pop-up notifications
            - Vibration alerts
            """)
        
        with col2:
            st.info("""
            💡 **Tips:**
            - Set different reminder times for different medicines
            - Use notes field for special instructions
            - Enable pop-up notifications for important medicines
            - Check 'Upcoming' filter to see today's reminders
            """)
        
        st.markdown("---")
        
        st.markdown("### 📊 Reminder Statistics")
        stats = get_reminder_stats()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **Total Reminders:** {stats['total']}
            
            **Active:** {stats['active']}
            """)
        
        with col2:
            st.markdown(f"""
            **Today's Reminders:** {stats['today']}
            
            **This Week:** {stats['this_week']}
            """)
        
        st.markdown("---")
        
        st.markdown("### 📥 Import/Export Settings")
        
        if st.button("📥 Export Reminders", use_container_width=True):
            import json
            reminders_data = load_reminders()
            json_str = json.dumps(reminders_data, indent=2)
            st.download_button(
                label="📥 Download as JSON",
                data=json_str,
                file_name="medicine_reminders.json",
                mime="application/json"
            )
        
        st.info("💡 You can backup your reminder settings and import them later if needed.")

# Run the page
if __name__ == "__main__":
    render_medicine_reminders_page()
