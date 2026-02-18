# backend.py

medications = []
appointments = []

# -------- Medication Logic --------
def add_medication(name, time, dosage):
    med = {
        "name": name,
        "time": time,
        "dosage": dosage,
        "missed": 0
    }
    medications.append(med)

def get_medications():
    return medications


# -------- Appointment Logic --------
def add_appointment(doctor, date, time):
    app = {
        "doctor": doctor,
        "date": date,
        "time": time
    }
    appointments.append(app)

def get_appointments():
    return appointments


# -------- AI Logic (Basic) --------
def check_missed(med):
    if med["missed"] >= 2:
        return "Warning: Frequently missed!"
    return "OK"
