from datetime import datetime
from database import get_medications
import os

def check_reminders():
    """Check for medications that need to be taken now"""
    now = datetime.now()
    current_minutes = now.hour * 60 + now.minute

    meds = get_medications()
    active = []

    for med in meds:
        # time may be "HH:MM" or "HH:MM:SS"
        time_parts = med["time"].split(":")
        h = int(time_parts[0])
        m = int(time_parts[1])

        med_minutes = h * 60 + m

        # 5-minute window (improved reliability for Streamlit)
        if 0 <= current_minutes - med_minutes <= 5:
            active.append(med)

    return active

def play_system_sound():
    """Play system beep sound"""
    try:
        if os.name == 'nt':  # Windows
            import winsound
            # Play multiple beeps
            for i in range(3):
                winsound.Beep(1000, 500)
                winsound.Sleep(200)
                winsound.Beep(1200, 500)
                winsound.Sleep(200)
    except Exception as e:
        print(f"Sound error: {e}")
