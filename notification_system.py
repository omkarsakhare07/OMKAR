"""
Advanced Notification System for Medicine Reminders
Handles pop-up notifications, sound alerts, and system notifications
"""

import streamlit as st
from datetime import datetime
from reminder_manager import (
    get_reminders_for_time, log_notification, mark_reminder_taken
)
import os
import platform

def play_notification_sound():
    """Play notification sound on different platforms"""
    try:
        system = platform.system()
        
        if system == "Windows":
            import winsound
            # Play notification sound
            for _ in range(2):
                winsound.Beep(1000, 300)
                winsound.Sleep(100)
                winsound.Beep(1200, 300)
                winsound.Sleep(100)
        
        elif system == "Darwin":  # macOS
            os.system('afplay /System/Library/Sounds/Glass.aiff')
            os.system('afplay /System/Library/Sounds/Glass.aiff')
        
        elif system == "Linux":
            os.system('paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null || true')
            os.system('paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null || true')
    
    except Exception as e:
        print(f"Sound notification error: {e}")

def show_browser_notification(title, message, medicine_name):
    """Show browser notification using JavaScript"""
    if 'notification_shown' not in st.session_state:
        st.session_state.notification_shown = {}
    
    # Create unique key for this notification
    notification_key = f"{title}_{message}"
    
    if notification_key not in st.session_state.notification_shown:
        st.markdown(f"""
        <script>
            // Request notification permission
            if ("Notification" in window) {{
                if (Notification.permission === "granted") {{
                    new Notification("{title}", {{
                        body: "It's time to take {medicine_name}!\\n{message}",
                        icon: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='75' font-size='75'>💊</text></svg>",
                        badge: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='50' fill='%23667eea'/></svg>",
                        tag: "medicine_reminder",
                        requireInteraction: true
                    }});
                }} else if (Notification.permission !== "denied") {{
                    Notification.requestPermission();
                }}
            }}
        </script>
        """, unsafe_allow_html=True)
        
        st.session_state.notification_shown[notification_key] = True

def trigger_mobile_vibration():
    """Trigger mobile device vibration"""
    st.markdown("""
    <script>
        if (navigator.vibrate) {
            // Vibrate pattern: [wait, vibrate, wait, vibrate, wait, vibrate]
            navigator.vibrate([200, 100, 200, 100, 200]);
        }
    </script>
    """, unsafe_allow_html=True)

def check_and_notify_reminders():
    """
    Check current time and show notifications for active reminders
    This function should be called from the main app
    Notifications trigger at exact time match (HH:MM)
    """
    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute
    current_time_str = f"{current_hour:02d}:{current_minute:02d}"
    
    # Get reminders for EXACT current time
    reminders = get_reminders_for_time(current_hour, current_minute)
    active_reminders = []
    
    # Filter only active reminders
    for reminder in reminders:
        if reminder.get("active", True):
            active_reminders.append(reminder)
    
    # Show notifications for matching time reminders
    if active_reminders:
        # Initialize notification tracking in session
        if 'shown_reminders' not in st.session_state:
            st.session_state.shown_reminders = {}
        
        if 'last_notification_time' not in st.session_state:
            st.session_state.last_notification_time = None
        
        # Only show notifications once per minute to avoid spamming
        should_notify = st.session_state.last_notification_time != current_time_str
        
        if should_notify:
            for reminder in active_reminders:
                reminder_id = reminder['id']
                
                # Play sound if enabled
                if reminder.get('sound_enabled', True):
                    play_notification_sound()
                
                # Trigger vibration if enabled
                if reminder.get('vibration_enabled', True):
                    trigger_mobile_vibration()
                
                # Show browser notification if enabled
                if reminder.get('notification_enabled', True):
                    show_browser_notification(
                        "💊 Medicine Reminder",
                        f"Time to take {reminder['medicine_name']} at {reminder['time']}",
                        reminder['medicine_name']
                    )
                
                # Show Streamlit pop-up notification
                st.warning(f"⏰ **MEDICINE REMINDER** 💊\n\nTime to take: **{reminder['medicine_name']}**\n\nDosage: {reminder.get('dosage', 'As prescribed')}\n\nScheduled time: {reminder['time']}", icon="⏰")
                
                # Log the notification
                log_notification(reminder_id, "system")
            
            # Update last notification time to prevent duplicate notifications
            st.session_state.last_notification_time = current_time_str
        
        return active_reminders
    
    return []

def reset_daily_reminders():
    """Reset reminder notifications at midnight"""
    if 'last_reset_date' not in st.session_state:
        st.session_state.last_reset_date = datetime.now().date()
    
    current_date = datetime.now().date()
    
    if current_date != st.session_state.last_reset_date:
        st.session_state.shown_reminders = []
        st.session_state.last_reset_date = current_date

def get_reminder_status_emoji(reminder):
    """Get emoji based on reminder status"""
    from datetime import datetime, time as datetime_time
    
    now = datetime.now()
    r_hour, r_minute = map(int, reminder["time"].split(":"))
    reminder_dt = now.replace(hour=r_hour, minute=r_minute, second=0, microsecond=0)
    
    time_diff = (reminder_dt - now).total_seconds() / 60  # in minutes
    
    if reminder.get("last_taken"):
        return "✅"  # Taken
    elif 0 < time_diff <= 10:
        return "⚠️"  # Urgent (within 10 minutes)
    elif -5 <= time_diff <= 0:
        return "🔴"  # Critical (overdue)
    else:
        return "🔔"  # Upcoming

def show_mini_notification_widget():
    """Show a mini widget in sidebar with upcoming reminders"""
    from reminder_manager import get_active_reminders
    from datetime import datetime
    
    reminders = get_active_reminders()
    
    if reminders:
        now = datetime.now()
        upcoming = []
        
        for reminder in reminders:
            if not reminder.get("last_taken"):
                r_hour, r_minute = map(int, reminder["time"].split(":"))
                reminder_dt = now.replace(hour=r_hour, minute=r_minute, second=0, microsecond=0)
                
                time_diff = (reminder_dt - now).total_seconds() / 60
                
                if time_diff > 0:
                    upcoming.append((time_diff, reminder))
        
        if upcoming:
            upcoming.sort(key=lambda x: x[0])
            
            st.markdown("""
            <style>
                .notification-widget {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 10px;
                    padding: 15px;
                    margin: 10px 0;
                    color: white;
                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
                }
                
                .notification-widget-title {
                    font-weight: bold;
                    margin-bottom: 10px;
                    font-size: 14px;
                }
                
                .notification-item {
                    padding: 5px 0;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
                    font-size: 12px;
                }
                
                .notification-item:last-child {
                    border-bottom: none;
                }
            </style>
            """, unsafe_allow_html=True)
            
            widget_html = '<div class="notification-widget">'
            widget_html += '<div class="notification-widget-title">📋 Upcoming Reminders</div>'
            
            for time_diff, reminder in upcoming[:3]:
                if time_diff < 60:
                    time_display = f"in {int(time_diff)} min"
                else:
                    hours = int(time_diff // 60)
                    mins = int(time_diff % 60)
                    time_display = f"in {hours}h {mins}m"
                
                widget_html += f'<div class="notification-item">'
                widget_html += f'{get_reminder_status_emoji(reminder)} {reminder["time"]} - {reminder["medicine_name"]}'
                widget_html += f'<br><span style="font-size: 10px; opacity: 0.8;">{time_display}</span>'
                widget_html += '</div>'
            
            widget_html += '</div>'
            
            st.markdown(widget_html, unsafe_allow_html=True)

if __name__ == "__main__":
    # Test the notification system
    print("Notification system loaded successfully")
