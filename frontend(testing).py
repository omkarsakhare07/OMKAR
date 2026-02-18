import streamlit as st
import pandas as pd
from datetime import datetime

from database import add_medication, get_medications
from reminder import check_reminders

# ---------- Page Config ----------
st.set_page_config(
    page_title="CareMed_AI",
    page_icon="💊",
    layout="centered"
)

# ---------- Custom CSS ----------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #e0f7fa, #ffffff);
}
.main {
    background-color: #f9f9f9;
}
.card {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
.title {
    text-align: center;
    font-size: 40px;
}
.subtitle {
    text-align: center;
    color: gray;
}
</style>
""", unsafe_allow_html=True)

# ---------- Title ----------
st.markdown("<div class='title'>💊 CareMed_AI</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI‑Based Medication & Appointment Reminder System</div>", unsafe_allow_html=True)
st.markdown("### 🩺 Your Smart Health Assistant")
st.divider()

# =========================================================
# ADD MEDICATION CARD
# =========================================================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("➕ Add Medication 💊")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Medicine Name 🧪")
with col2:
    med_time = st.time_input("Medicine Time ⏰")

dosage = st.text_input("Dosage 💉 (e.g. 1 tablet)")

if st.button("💾 Save Medication", use_container_width=True):
    if name.strip():
        add_medication(name.strip(), med_time.strftime("%H:%M"), dosage.strip())
        st.success("✅ Medication saved successfully!")
    else:
        st.error("Medicine name required")

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# SAVED MEDICATIONS CARD
# =========================================================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📋 Saved Medications")

meds = get_medications()
if meds:
    df = pd.DataFrame(meds).drop(columns=["id"], errors="ignore")
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No medications added yet 💤")

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# ACTIVE REMINDER CARD
# =========================================================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("⏰ Active Reminder 🔔")

current_time = datetime.now().strftime("%H:%M")
active_reminders = check_reminders()

st.caption(f"🕒 Current Time: {current_time}")

if active_reminders:
    for med in active_reminders:
        st.warning(f"💊 **Time to take {med['name']}** ({med['dosage']})")
else:
    st.info("😌 No reminders right now")

st.markdown("</div>", unsafe_allow_html=True)
