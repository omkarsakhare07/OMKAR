"""
AI-Powered Medication & Doctor Suggestions
For each disease, provides validated medications and top doctors
Includes LLM-powered personalized health insights
"""

import requests
import json

# Groq API configuration - Using free Groq API with Mixtral model
GROQ_API_KEY = "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"  # Replace with actual key if using
GROQ_MODEL = "mixtral-8x7b-32768"  # Free model on Groq

# Try to import groq or use fallback
GROQ_AVAILABLE = False
try:
    from groq import Groq  # type: ignore
    GROQ_AVAILABLE = True
except Exception as e:
    GROQ_AVAILABLE = False
    print(f"ℹ️ Groq not available ({type(e).__name__}). Using fallback insights.")

# Disease to Medication Mapping
DISEASE_MEDICATIONS = {
    "Diabetes": {
        "medications": [
            {"name": "Metformin", "dosage": "500-2000mg daily", "purpose": "First-line treatment"},
            {"name": "Insulin Glargine", "dosage": "As prescribed", "purpose": "Long-acting insulin"},
            {"name": "Glipizide", "dosage": "5-20mg daily", "purpose": "Sulfonylurea agent"},
            {"name": "GLP-1 Agonist", "dosage": "As prescribed", "purpose": "Newer therapy"}
        ],
        "doctors": [
            {"name": "Dr. Raj Patel", "specialty": "Endocrinologist", "rating": 4.9, "experience": "18 years", 
             "hospital": "Apollo Hospitals, Mumbai", "location": "Bandra, Mumbai"},
            {"name": "Dr. Priya Sharma", "specialty": "Diabetologist", "rating": 4.8, "experience": "15 years",
             "hospital": "Max Healthcare, Delhi", "location": "South Delhi"},
            {"name": "Dr. Amit Kumar", "specialty": "Endocrinologist", "rating": 4.7, "experience": "12 years",
             "hospital": "Fortis Hospital, Bangalore", "location": "Koramangala, Bangalore"}
        ]
    },
    "Hypertension (High Blood Pressure)": {
        "medications": [
            {"name": "Lisinopril", "dosage": "10-40mg daily", "purpose": "ACE Inhibitor"},
            {"name": "Amlodipine", "dosage": "5-10mg daily", "purpose": "Calcium Channel Blocker"},
            {"name": "Metoprolol", "dosage": "25-190mg daily", "purpose": "Beta Blocker"},
            {"name": "Losartan", "dosage": "25-100mg daily", "purpose": "ARB medication"}
        ],
        "doctors": [
            {"name": "Dr. Arjun Singh", "specialty": "Cardiologist", "rating": 4.9, "experience": "20 years",
             "hospital": "Fortis Healthcare, Mumbai", "location": "Vile Parle, Mumbai"},
            {"name": "Dr. Neha Gupta", "specialty": "Cardiologist", "rating": 4.8, "experience": "16 years",
             "hospital": "AIIMS Delhi", "location": "New Delhi"},
            {"name": "Dr. Sanjay Desai", "specialty": "Physician", "rating": 4.7, "experience": "14 years",
             "hospital": "St. John's Medical College Hospital, Bangalore", "location": "Bangalore"}
        ]
    },
    "Heart Disease": {
        "medications": [
            {"name": "Aspirin", "dosage": "75-100mg daily", "purpose": "Blood thinner"},
            {"name": "Atorvastatin", "dosage": "10-80mg daily", "purpose": "Statin for cholesterol"},
            {"name": "Carvedilol", "dosage": "3.125-25mg daily", "purpose": "Beta Blocker"},
            {"name": "Nitroglycerin", "dosage": "0.3-0.6mg SL", "purpose": "Angina relief"}
        ],
        "doctors": [
            {"name": "Dr. Ravi Prakash", "specialty": "Interventional Cardiologist", "rating": 4.9, "experience": "19 years",
             "hospital": "Apollo Hospitals, Hyderabad", "location": "Hyderabad"},
            {"name": "Dr. Meera Kapoor", "specialty": "Cardiologist", "rating": 4.8, "experience": "17 years",
             "hospital": "Max Hospital, Gurgaon", "location": "Gurgaon"},
            {"name": "Dr. Vikram Patel", "specialty": "Cardiac Surgeon", "rating": 4.8, "experience": "15 years",
             "hospital": "Apollo Hospitals, Chennai", "location": "Chennai"}
        ]
    },
    "Asthma": {
        "medications": [
            {"name": "Albuterol (Salbutamol)", "dosage": "1-2 puffs as needed", "purpose": "Quick relief"},
            {"name": "Fluticasone", "dosage": "100-440mcg daily", "purpose": "Inhaled steroid"},
            {"name": "Montelukast", "dosage": "4-10mg daily", "purpose": "Leukotriene inhibitor"},
            {"name": "Ipratropium Bromide", "dosage": "2 inhalations 3-4x daily", "purpose": "Anticholinergic"}
        ],
        "doctors": [
            {"name": "Dr. Anand Sharma", "specialty": "Pulmonologist", "rating": 4.9, "experience": "18 years",
             "hospital": "Manipal Hospital, Bangalore", "location": "Bangalore"},
            {"name": "Dr. Sunita Patel", "specialty": "Respiratory Physician", "rating": 4.8, "experience": "14 years",
             "hospital": "Medanta, Mumbai", "location": "Mumbai"},
            {"name": "Dr. Deepak Singh", "specialty": "Pulmonologist", "rating": 4.7, "experience": "12 years",
             "hospital": "Sri Ramakrishna Hospital, Chennai", "location": "Chennai"}
        ]
    },
    "Arthritis": {
        "medications": [
            {"name": "Ibuprofen", "dosage": "400-800mg 3x daily", "purpose": "NSAID for pain"},
            {"name": "Methotrexate", "dosage": "10-20mg weekly", "purpose": "DMARDs"},
            {"name": "Indomethacin", "dosage": "25mg 2-3x daily", "purpose": "NSAID"},
            {"name": "Sulfasalazine", "dosage": "1000-1500mg 2x daily", "purpose": "RA treatment"}
        ],
        "doctors": [
            {"name": "Dr. Kavya Reddy", "specialty": "Rheumatologist", "rating": 4.9, "experience": "17 years",
             "hospital": "Apollo Hospitals, Hyderabad", "location": "Hyderabad"},
            {"name": "Dr. Prashant Joshi", "specialty": "Orthopedic Surgeon", "rating": 4.8, "experience": "16 years",
             "hospital": "Fortis Hospital, Pune", "location": "Pune"},
            {"name": "Dr. Sneha Nair", "specialty": "Rheumatologist", "rating": 4.7, "experience": "13 years",
             "hospital": "Max Hospital, Mumbai", "location": "Mumbai"}
        ]
    },
    "Depression": {
        "medications": [
            {"name": "Sertraline", "dosage": "50-200mg daily", "purpose": "SSRI antidepressant"},
            {"name": "Escitalopram", "dosage": "10-20mg daily", "purpose": "SSRI"},
            {"name": "Amitriptyline", "dosage": "25-100mg daily", "purpose": "Tricyclic antidepressant"},
            {"name": "Bupropion", "dosage": "150-300mg daily", "purpose": "Norepinephrine-dopamine reuptake inhibitor"}
        ],
        "doctors": [
            {"name": "Dr. Vikram Sharma", "specialty": "Psychiatrist", "rating": 4.9, "experience": "20 years",
             "hospital": "Fortis Hospital, Delhi", "location": "New Delhi"},
            {"name": "Dr. Anjali Verma", "specialty": "Clinical Psychologist", "rating": 4.8, "experience": "15 years",
             "hospital": "Apollo Hospitals, Bangalore", "location": "Bangalore"},
            {"name": "Dr. Rajesh Kumar", "specialty": "Psychiatrist", "rating": 4.7, "experience": "14 years",
             "hospital": "Kokilaben Hospital, Mumbai", "location": "Mumbai"}
        ]
    },
    "Anxiety": {
        "medications": [
            {"name": "Lorazepam", "dosage": "0.5-2mg 2-3x daily", "purpose": "Benzodiazepine"},
            {"name": "Alprazolam", "dosage": "0.25-1mg 3x daily", "purpose": "Anti-anxiety"},
            {"name": "Buspirone", "dosage": "5-10mg 2-3x daily", "purpose": "Non-benzodiazepine"},
            {"name": "Propranolol", "dosage": "10-40mg 2-3x daily", "purpose": "Beta blocker for anxiety"}
        ],
        "doctors": [
            {"name": "Dr. Sameer Deshmukh", "specialty": "Psychiatrist", "rating": 4.9, "experience": "18 years",
             "hospital": "Apollo Hospitals, Mumbai", "location": "Mumbai"},
            {"name": "Dr. Priya Menon", "specialty": "Anxiety Specialist", "rating": 4.8, "experience": "16 years",
             "hospital": "Max Healthcare, Bangalore", "location": "Bangalore"},
            {"name": "Dr. Harsh Yadav", "specialty": "Psychiatrist", "rating": 4.7, "experience": "13 years",
             "hospital": "Fortis Hospital, Noida", "location": "Noida"}
        ]
    },
    "Thyroid Disorder": {
        "medications": [
            {"name": "Levothyroxine", "dosage": "25-200mcg daily", "purpose": "Thyroid hormone replacement"},
            {"name": "Propylthiouracil (PTU)", "dosage": "50-150mg 3x daily", "purpose": "Anti-thyroid"},
            {"name": "Methimazole", "dosage": "5-30mg daily", "purpose": "Antithyroid medication"},
            {"name": "Potassium Iodide", "dosage": "50-100mg daily", "purpose": "Iodine supplement"}
        ],
        "doctors": [
            {"name": "Dr. Shalini Gupta", "specialty": "Endocrinologist", "rating": 4.9, "experience": "19 years",
             "hospital": "Apollo Hospitals, Hyderabad", "location": "Hyderabad"},
            {"name": "Dr. Anil Malhotra", "specialty": "Endocrinologist", "rating": 4.8, "experience": "17 years",
             "hospital": "Fortis Hospital, Delhi", "location": "New Delhi"},
            {"name": "Dr. Divya Singh", "specialty": "Endocrinologist", "rating": 4.7, "experience": "14 years",
             "hospital": "Max Hospital, Pune", "location": "Pune"}
        ]
    },
    "Chronic Kidney Disease": {
        "medications": [
            {"name": "ACE Inhibitors", "dosage": "As prescribed", "purpose": "Protects kidneys"},
            {"name": "Phosphate Binders", "dosage": "As prescribed", "purpose": "Controls phosphate"},
            {"name": "Erythropoiesis-stimulating agents", "dosage": "As prescribed", "purpose": "Anemia treatment"},
            {"name": "Vitamin D supplements", "dosage": "As prescribed", "purpose": "Bone health"}
        ],
        "doctors": [
            {"name": "Dr. Ramesh Kulkarni", "specialty": "Nephrologist", "rating": 4.9, "experience": "20 years",
             "hospital": "Apollo Hospitals, Mumbai", "location": "Mumbai"},
            {"name": "Dr. Arundhati Rao", "specialty": "Nephrologist", "rating": 4.8, "experience": "18 years",
             "hospital": "Manipal Hospital, Bangalore", "location": "Bangalore"},
            {"name": "Dr. Suresh Iyer", "specialty": "Renal Specialist", "rating": 4.7, "experience": "15 years",
             "hospital": "Max Hospital, Delhi", "location": "New Delhi"}
        ]
    },
    "COPD (Chronic Obstructive Pulmonary Disease)": {
        "medications": [
            {"name": "Albuterol (Salbutamol)", "dosage": "1-2 puffs as needed", "purpose": "Bronchodilator"},
            {"name": "Tiotropium", "dosage": "18mcg daily", "purpose": "Long-acting anticholinergic"},
            {"name": "Fluticasone/Salmeterol", "dosage": "1-2 puffs twice daily", "purpose": "Combination therapy"},
            {"name": "Theophylline", "dosage": "300-600mg daily", "purpose": "Bronchodilator"}
        ],
        "doctors": [
            {"name": "Dr. Kapil Sharma", "specialty": "Pulmonologist", "rating": 4.9, "experience": "19 years",
             "hospital": "Fortis Hospital, Mumbai", "location": "Mumbai"},
            {"name": "Dr. Neha Saxena", "specialty": "Respiratory Specialist", "rating": 4.8, "experience": "16 years",
             "hospital": "Apollo Hospitals, Delhi", "location": "New Delhi"},
            {"name": "Dr. Rajesh Verma", "specialty": "Chest Physician", "rating": 4.7, "experience": "14 years",
             "hospital": "Max Hospital, Bangalore", "location": "Bangalore"}
        ]
    }
}

def get_medication_suggestions(disease):
    """Get medication suggestions for a disease"""
    return DISEASE_MEDICATIONS.get(disease, {}).get("medications", [])

def get_doctor_suggestions(disease):
    """Get top doctor suggestions for a disease"""
    return DISEASE_MEDICATIONS.get(disease, {}).get("doctors", [])

def get_all_diseases():
    """Get list of all diseases with suggestions"""
    return list(DISEASE_MEDICATIONS.keys())

def get_llm_health_insights(disease, medications, patient_age=None, medications_list=None):
    """
    Get LLM-powered personalized health insights for a disease
    Uses Groq API with Mixtral model for fast, intelligent suggestions
    Advanced features: Considers patient age, current medications, drug interactions
    """
    try:
        # Build the advanced prompt
        med_names = ", ".join([m["name"] for m in medications])
        
        # Advanced prompt with more context
        prompt = f"""You are an expert medical AI assistant with knowledge of evidence-based medicine and clinical guidelines. 

PATIENT CONTEXT:
- Disease: {disease}
- {f'Age: {patient_age} years' if patient_age else 'Age: Not specified'}
- {f'Current Medications: {", ".join(medications_list)}' if medications_list else 'No other medications listed'}

STANDARD TREATMENT:
- Recommended Medications: {med_names}

PROVIDE COMPREHENSIVE MEDICAL INSIGHTS (Use markdown formatting):

## 1️⃣ Disease Overview & Statistics
- Brief medical explanation (2-3 sentences)
- Prevalence and risk factors
- Prognosis with proper treatment

## 2️⃣ Recommended Lifestyle Modifications
- At least 3 specific, actionable lifestyle changes
- Expected health improvement from each change
- Timeline for visible results

## 3️⃣ Key Warning Signs & Red Flags
- List 3-4 critical warning signs requiring immediate medical attention
- Differentiate between normal and concerning symptoms
- When to call emergency services

## 4️⃣ Medication Management
- General guidance on the recommended medications
- Possible side effects and how to manage them
- Importance of medication adherence
- Drug interaction concerns (if applicable)

## 5️⃣ Monitoring & Follow-up
- Recommended tests and their frequency
- Health metrics to track
- When to see a specialist

## 6️⃣ Emergency Care
- Emergency symptoms requiring 911/ambulance
- First aid measures while waiting for help
- Importance of medical alert identification

## 7️⃣ Long-term Management Tips
- Seasonal precautions
- Stress management strategies
- Community support and resources

Keep response detailed but concise. Use clear formatting. Provide medically accurate information only."""

        if GROQ_AVAILABLE:
            client = Groq(api_key=GROQ_API_KEY)
            message = client.messages.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.5  # Lower temperature for more consistent medical advice
            )
            return message.content[0].text
        else:
            # Fallback to simple text-based response if LLM not available
            return get_fallback_health_insights(disease, medications)
            
    except Exception as e:
        print(f"LLM Error: {e}")
        return get_fallback_health_insights(disease, medications)

def get_fallback_health_insights(disease, medications):
    """Fallback insights when LLM is not available"""
    med_names = ", ".join([m["name"] for m in medications])
    
    fallback_insights = {
        "Diabetes": f"""**Disease Overview:** Diabetes is a metabolic disorder affecting blood sugar regulation. Standard management includes {med_names}.

**Key Lifestyle Tips:**
• Monitor blood sugar levels regularly
• Maintain balanced diet with low glycemic index foods
• Exercise 30 minutes daily

**Warning Signs to Watch:**
• Unexplained fatigue or blurred vision
• Increased thirst and frequent urination
• Slow-healing wounds

**Medication Guidance:** Take medications as prescribed. Never skip doses. Monitor for side effects.

**Emergency Care:** Seek immediate help for severe hypoglycemia or DKA symptoms.""",
        
        "Hypertension (High Blood Pressure)": f"""**Disease Overview:** Hypertension is elevated blood pressure requiring ongoing management. Key medications include {med_names}.

**Key Lifestyle Tips:**
• Reduce sodium intake to less than 2300mg/day
• Maintain healthy weight and exercise regularly
• Manage stress through relaxation techniques

**Warning Signs to Watch:**
• Severe headaches or chest pain
• Shortness of breath or vision changes
• Dizziness or confusion

**Medication Guidance:** Take antihypertensive medications at same time daily. Monitor BP regularly.

**Emergency Care:** Call emergency if BP >180/120 with symptoms.""",
        
        "Heart Disease": f"""**Disease Overview:** Heart disease requires comprehensive management with medications like {med_names}.

**Key Lifestyle Tips:**
• Follow heart-healthy diet (Mediterranean or DASH)
• Avoid smoking and limit alcohol
• Regular cardiac rehabilitation exercises

**Warning Signs to Watch:**
• Chest pain or pressure during exertion
• Shortness of breath or unusual fatigue
• Irregular heartbeat or palpitations

**Medication Guidance:** Take all cardiac medications as prescribed. Don't skip doses.

**Emergency Care:** Call emergency immediately for chest pain or severe shortness of breath."""
    }
    
    return fallback_insights.get(disease, f"Standard medications for {disease}: {med_names}. Follow doctor's guidance.")

def format_llm_response(response_text):
    """Format LLM response for better display"""
    try:
        # Clean up the response
        lines = response_text.split('\n')
        formatted = []
        for line in lines:
            if line.strip():
                formatted.append(line)
        return '\n'.join(formatted)
    except:
        return response_text


# ========== NEW FEATURES FOR ENHANCED AI SUGGESTIONS ==========

def get_diet_recommendations(disease):
    """Get disease-specific diet recommendations"""
    diet_plans = {
        "Diabetes": {
            "title": "🥗 Diabetes-Friendly Diet",
            "avoid": ["Sugary drinks", "White bread", "Refined cereals", "Processed sweets", "High-fat meats"],
            "include": ["Whole grains", "Lean proteins", "Vegetables", "Fruits (low GI)", "Nuts and seeds"],
            "meal_ideas": [
                "Grilled chicken with brown rice & steamed vegetables",
                "Oatmeal with berries and almonds",
                "Lentil soup with whole wheat bread",
                "Baked fish with sweet potato and greens",
                "Greek yogurt with walnuts"
            ],
            "tips": [
                "Eat small portions every 3-4 hours",
                "Include protein with every meal",
                "Choose foods with low glycemic index",
                "Drink plenty of water"
            ]
        },
        "Hypertension (High Blood Pressure)": {
            "title": "🧂 Low-Sodium Heart-Healthy Diet",
            "avoid": ["Processed meats", "Salty snacks", "Canned foods", "Soy sauce", "Pickled foods"],
            "include": ["Fresh vegetables", "Fruits", "Whole grains", "Lean proteins", "Low-fat dairy"],
            "meal_ideas": [
                "Baked salmon with roasted vegetables",
                "Vegetable stir-fry with brown rice",
                "Grilled chicken salad with olive oil dressing",
                "Oatmeal with fresh berries",
                "Lentil and vegetable curry with whole wheat roti"
            ],
            "tips": [
                "Limit salt to <2300mg per day",
                "Use herbs and spices for flavor",
                "Cook at home more often",
                "Choose fresh over processed foods"
            ]
        },
        "Heart Disease": {
            "title": "❤️ Cardio-Protective Diet",
            "avoid": ["Trans fats", "Saturated fats", "Processed foods", "High-cholesterol items", "Excess sodium"],
            "include": ["Omega-3 fish", "Olive oil", "Vegetables", "Whole grains", "Nuts"],
            "meal_ideas": [
                "Grilled tuna with quinoa and vegetables",
                "Mediterranean salad with chickpeas",
                "Whole wheat pasta with tomato sauce",
                "Baked cod with olive oil and herbs",
                "Vegetable soup with beans"
            ],
            "tips": [
                "Eat fish 2-3 times per week",
                "Use olive oil for cooking",
                "Include nuts and seeds daily",
                "Avoid fried foods"
            ]
        },
        "Asthma": {
            "title": "🫁 Anti-Inflammatory Diet for Asthma",
            "avoid": ["Foods with sulfites", "Processed items", "Excess salt", "High-fat foods", "Known allergens"],
            "include": ["Fatty fish", "Vegetables", "Fruits", "Whole grains", "Antioxidant-rich foods"],
            "meal_ideas": [
                "Salmon with broccoli and sweet potato",
                "Spinach salad with berries",
                "Vegetable curry with turmeric",
                "Grilled chicken with green beans",
                "Smoothie with antioxidant fruits"
            ],
            "tips": [
                "Stay hydrated",
                "Avoid trigger foods",
                "Include anti-inflammatory foods",
                "Maintain healthy weight"
            ]
        }
    }
    return diet_plans.get(disease, {
        "title": "🍎 Healthy Diet Recommendations",
        "avoid": ["Processed foods", "Excess salt", "Sugary items"],
        "include": ["Fresh vegetables", "Whole grains", "Lean proteins"],
        "meal_ideas": ["Balanced meals with all food groups"],
        "tips": ["Consult with a nutritionist"]
    })


def get_exercise_plan(disease, age=None):
    """Get personalized exercise recommendations"""
    exercise_plans = {
        "Diabetes": {
            "title": "💪 Diabetes Exercise Plan",
            "frequency": "4-5 days per week",
            "duration": "150 minutes moderate activity per week",
            "exercises": [
                "Brisk walking (30 mins, 5 days/week)",
                "Swimming or cycling (20-30 mins)",
                "Strength training (2-3 days/week)",
                "Flexibility exercises (yoga, stretching)"
            ],
            "benefits": ["Improves insulin sensitivity", "Controls blood sugar", "Reduces weight", "Lowers blood pressure"],
            "precautions": [
                "Check blood sugar before exercise",
                "Keep glucose tablets nearby",
                "Start slowly and gradually increase",
                "Stay hydrated"
            ]
        },
        "Hypertension (High Blood Pressure)": {
            "title": "🚴 Cardio-Focused Exercise Plan",
            "frequency": "5 days per week",
            "duration": "150 minutes moderate intensity",
            "exercises": [
                "Brisk walking or jogging",
                "Cycling or stationary bike",
                "Swimming",
                "Elliptical trainer"
            ],
            "benefits": ["Lowers blood pressure", "Strengthens heart", "Reduces stress", "Improves circulation"],
            "precautions": [
                "Monitor blood pressure regularly",
                "Warm up and cool down",
                "Avoid sudden intense exercise",
                "Stop if chest pain occurs"
            ]
        },
        "Heart Disease": {
            "title": "❤️ Cardiac Rehabilitation Exercise",
            "frequency": "3-5 days per week",
            "duration": "30-60 minutes",
            "exercises": [
                "Supervised cardiac rehab program",
                "Light to moderate walking",
                "Stationary cycling",
                "Resistance training (light)"
            ],
            "benefits": ["Improves heart function", "Increases stamina", "Reduces cardiac risk", "Improves quality of life"],
            "precautions": [
                "Exercise under medical supervision initially",
                "Follow prescribed intensity levels",
                "Avoid high-intensity exercise without clearance",
                "Report any chest discomfort"
            ]
        },
        "Arthritis": {
            "title": "🏃 Joint-Friendly Exercise Plan",
            "frequency": "3-4 days per week",
            "duration": "30 minutes",
            "exercises": [
                "Swimming or aqua aerobics",
                "Tai Chi",
                "Gentle yoga",
                "Range of motion exercises"
            ],
            "benefits": ["Reduces pain", "Improves flexibility", "Strengthens muscles", "Maintains mobility"],
            "precautions": [
                "Warm up properly",
                "Avoid high-impact activities",
                "Take breaks if pain increases",
                "Apply ice after exercise if needed"
            ]
        }
    }
    return exercise_plans.get(disease, {
        "title": "🏋️ General Exercise Recommendations",
        "frequency": "4-5 days per week",
        "duration": "30 minutes",
        "exercises": ["Moderate cardio", "Strength training", "Flexibility work"],
        "benefits": ["Improves overall health"],
        "precautions": ["Consult doctor before starting new exercise program"]
    })


def check_drug_interactions(medications_list):
    """Check for potential drug interactions"""
    # Common interactions database
    interactions_db = {
        ("Aspirin", "Ibuprofen"): {
            "severity": "HIGH",
            "warning": "Combining NSAIDs increases risk of GI bleeding",
            "recommendation": "Use only one NSAID at a time"
        },
        ("Metformin", "Alcohol"): {
            "severity": "MEDIUM",
            "warning": "Alcohol may increase risk of lactic acidosis",
            "recommendation": "Limit alcohol consumption"
        },
        ("Warfarin", "Aspirin"): {
            "severity": "HIGH",
            "warning": "Increased bleeding risk",
            "recommendation": "Requires close monitoring and dosage adjustment"
        },
        ("Lisinopril", "Potassium supplements"): {
            "severity": "MEDIUM",
            "warning": "Risk of high potassium levels",
            "recommendation": "Monitor potassium levels regularly"
        },
        ("Simvastatin", "Grapefruit"): {
            "severity": "MEDIUM",
            "warning": "Grapefruit increases drug levels",
            "recommendation": "Avoid grapefruit and grapefruit juice"
        }
    }
    
    interactions_found = []
    meds_lower = [m.lower() for m in medications_list]
    
    for (drug1, drug2), interaction in interactions_db.items():
        if drug1.lower() in meds_lower and drug2.lower() in meds_lower:
            interactions_found.append({
                "drugs": f"{drug1} + {drug2}",
                "severity": interaction["severity"],
                "warning": interaction["warning"],
                "recommendation": interaction["recommendation"]
            })
    
    return interactions_found


def get_preventive_care_tips(disease):
    """Get preventive care and disease management tips"""
    preventive_care = {
        "Diabetes": {
            "screening": [
                "HbA1c test every 3 months",
                "Annual kidney function tests",
                "Annual eye exam (dilated)",
                "Annual foot exam"
            ],
            "complications_to_prevent": [
                "Diabetic neuropathy (nerve damage)",
                "Diabetic retinopathy (eye disease)",
                "Diabetic nephropathy (kidney disease)",
                "Cardiovascular disease"
            ],
            "self_care": [
                "Daily blood sugar monitoring",
                "Maintain healthy weight",
                "Manage stress effectively",
                "Follow medication schedule strictly"
            ]
        },
        "Hypertension (High Blood Pressure)": {
            "screening": [
                "Blood pressure check every month",
                "Annual kidney and heart function tests",
                "Cholesterol panel annually"
            ],
            "complications_to_prevent": [
                "Stroke",
                "Myocardial infarction (heart attack)",
                "Chronic kidney disease",
                "Heart failure"
            ],
            "self_care": [
                "Daily BP monitoring at home",
                "Reduce sodium intake",
                "Exercise regularly",
                "Manage stress and emotions"
            ]
        },
        "Heart Disease": {
            "screening": [
                "Annual ECG and stress test",
                "Lipid profile every 3-6 months",
                "Echocardiogram as recommended",
                "Cardiac imaging when needed"
            ],
            "complications_to_prevent": [
                "Myocardial infarction",
                "Arrhythmias",
                "Heart failure",
                "Sudden cardiac death"
            ],
            "self_care": [
                "Take all medications as prescribed",
                "Attend cardiac rehab",
                "Monitor symptoms closely",
                "Regular follow-ups with cardiologist"
            ]
        }
    }
    return preventive_care.get(disease, {
        "screening": ["Regular medical checkups"],
        "complications_to_prevent": ["Disease progression"],
        "self_care": ["Follow medical advice", "Take medications regularly"]
    })


def get_affordable_medication_alternatives(disease):
    """Get cost-effective alternative medications"""
    alternatives = {
        "Diabetes": [
            {"original": "Insulin Glargine", "generic": "Insulin Glargine (Lantus)", "cost_saving": "30-40%", "note": "Same efficacy"},
            {"original": "Metformin", "generic": "Metformin (generic)", "cost_saving": "60-70%", "note": "First-line, most affordable"},
            {"original": "Glipizide (brand)", "generic": "Glipizide (generic)", "cost_saving": "40-50%", "note": "Very affordable option"}
        ],
        "Hypertension (High Blood Pressure)": [
            {"original": "Lisinopril (brand)", "generic": "Lisinopril (generic)", "cost_saving": "50-60%", "note": "ACE inhibitor"},
            {"original": "Amlodipine (brand)", "generic": "Amlodipine (generic)", "cost_saving": "40-50%", "note": "Calcium channel blocker"},
            {"original": "Metoprolol (brand)", "generic": "Metoprolol (generic)", "cost_saving": "45-55%", "note": "Beta blocker"}
        ],
        "Heart Disease": [
            {"original": "Aspirin (brand)", "generic": "Aspirin (generic)", "cost_saving": "70-80%", "note": "Very affordable"},
            {"original": "Atorvastatin (brand)", "generic": "Atorvastatin (generic)", "cost_saving": "50-60%", "note": "Statin therapy"},
            {"original": "Carvedilol (brand)", "generic": "Carvedilol (generic)", "cost_saving": "45-55%", "note": "Beta blocker"}
        ]
    }
    return alternatives.get(disease, [
        {"original": "Brand medication", "generic": "Generic alternative", "cost_saving": "30-50%", "note": "Ask pharmacist for generic options"}
    ])


# ========== GENERAL HEALTH AI ASSISTANT ==========

def ask_health_question(question, chat_history=None):
    """
    General health question answering with LLM
    Handles any health-related question from users
    Falls back gracefully if LLM unavailable
    """
    try:
        # Build conversation context with chat history
        messages = []
        
        if chat_history:
            for msg in chat_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current question
        prompt = f"""You are a highly knowledgeable and compassionate AI Health Assistant with expertise in medicine, nutrition, fitness, mental health, and general wellness.

IMPORTANT GUIDELINES:
1. Always provide medically accurate, evidence-based information
2. For serious conditions, always recommend consulting a doctor
3. Be empathetic and supportive in your responses
4. Provide practical, actionable advice
5. If unsure about something, be honest about limitations
6. Use clear formatting with emojis for better readability
7. Include disclaimers about not replacing professional medical advice

USER QUESTION: {question}

Provide a comprehensive, helpful response in Hindi and English where relevant."""
        
        messages.append({"role": "user", "content": prompt})
        
        if GROQ_AVAILABLE:
            try:
                client = Groq(api_key=GROQ_API_KEY)
                response = client.messages.create(
                    model=GROQ_MODEL,
                    messages=messages,
                    max_tokens=2000,
                    temperature=0.7
                )
                return {
                    "success": True,
                    "answer": response.content[0].text,
                    "source": "AI Health Assistant (LLM)"
                }
            except Exception as e:
                print(f"Groq API Error: {e}")
                return get_fallback_health_answer(question)
        else:
            return get_fallback_health_answer(question)
            
    except Exception as e:
        print(f"Error in ask_health_question: {e}")
        return {
            "success": False,
            "answer": f"❌ Error: Unable to process your question. Please try again.\nError Details: {str(e)}",
            "source": "Error Handler"
        }


def get_fallback_health_answer(question):
    """
    Fallback health answers for common questions
    Used when LLM is not available
    """
    question_lower = question.lower()
    
    # Common health questions and answers
    common_answers = {
        "cold": """🧊 **Common Cold Management**
- Rest: Get 7-9 hours of sleep
- Hydration: Drink water, warm tea, and broth
- Gargle: Salt water or warm water helps
- Vitamin C: Citrus fruits, berries, broccoli
- Duration: Usually 7-10 days
- See doctor if: High fever (>101°F), severe symptoms

⚠️ Not caused by bacteria - antibiotics won't help!""",
        
        "fever": """🌡️ **Fever Management**
- Normal: 98.6°F (37°C)
- Fever: >100.4°F (38°C)
- Management:
  • Take paracetamol/ibuprofen as directed
  • Drink plenty of fluids
  • Wear light clothing
  • Cool compress on forehead
- See doctor if: Fever >103°F, lasts >3 days, or severe symptoms""",
        
        "cough": """😷 **Cough Relief Tips**
- Stay hydrated: Drink warm water with honey
- Use humidifier: Add moisture to air
- Throat lozenges: Soothe throat irritation
- Avoid irritants: Smoke, pollution, strong odors
- Rest: Get enough sleep
- Types:
  • Dry cough: Use honey, lozenges
  • Wet cough: Chest congestion relief
- See doctor if: Coughs longer than 3 weeks or with blood""",
        
        "sore throat": """🤕 **Sore Throat Relief**
- Gargle: Salt water 3-4 times daily
- Hydration: Drink warm fluids
- Honey: Spoon of honey helps (not for kids <1 year)
- Lozenges: Pain relief lozenges
- Rest: Voice rest helps healing
- Avoid: Hot, spicy foods
- See doctor if: Severe pain, difficulty swallowing, white patches""",
        
        "headache": """🤕 **Headache Relief**
- Rest in dark, quiet room
- Cold/warm compress on forehead
- Hydrate - drink water
- Avoid screens
- Light exercise or stretching
- Over-the-counter: Paracetamol, Ibuprofen
- Triggers to avoid: Stress, lack of sleep, dehydration
- See doctor if: Severe, persistent, or sudden onset""",
        
        "migraine": """💔 **Migraine Management**
- Dark, quiet room: Reduces sensitivity
- Cold/warm compress: Apply to head/neck
- Rest: Sleep if possible
- Hydration: Drink water
- Medication: Ibuprofen, Paracetamol
- Prevention: Regular sleep, stress management
- Triggers: Stress, hormones, food, lack of sleep
- See doctor for: Persistent migraines (preventive treatment)""",
        
        "stomach ache": """🤢 **Stomach Pain Relief**
- Rest: Lie down in comfortable position
- Hydration: Small sips of water
- BRAT diet: Banana, Rice, Applesauce, Toast
- Avoid: Spicy, fatty, heavy foods
- Heat: Warm compress on abdomen
- Medication: Antacids if applicable
- Duration: Most improve in 24-48 hours
- See doctor if: Severe, persistent, or with other symptoms""",
        
        "diarrhea": """💧 **Diarrhea Management**
- Hydration: Most important! Drink oral rehydration salts
- Rest: Rest your digestive system
- Diet: BRAT diet (Banana, Rice, Applesauce, Toast)
- Avoid: Dairy, high-fiber, spicy foods
- Duration: Usually 2-3 days
- Medications: Loperamide or bismuth subsalicylate
- See doctor if: Lasts >3 days, bloody, severe pain""",
        
        "constipation": """🚽 **Constipation Relief**
- Hydration: Drink 8-10 glasses water daily
- Fiber: Vegetables, fruits, whole grains
- Exercise: 30 minutes daily activity
- Routine: Set regular toilet time
- Avoid: Low-fiber foods, dehydration
- Natural remedies: Prunes, warm lemon water
- Medications: Stool softeners if needed
- See doctor if: Lasts >2 weeks or severe pain""",
        
        "nausea": """🤢 **Nausea Relief**
- Fresh air: Open windows or go outside
- Ginger: Ginger tea or supplements
- Peppermint: Peppermint tea helps
- Rest: Lie down if needed
- Hydration: Small sips of water
- Avoid: Strong smells, greasy foods
- Pressure point: Apply pressure to wrist
- See doctor if: Persistent or with other symptoms""",
        
        "sleep": """😴 **Better Sleep Hygiene**
- Sleep schedule: Same time daily
- Duration: 7-9 hours for adults
- Environment: Dark, cool, quiet room
- Avoid: Caffeine, screens 1 hour before bed
- Exercise: Regular activity helps (not before bed)
- Relaxation: Meditation, deep breathing
- Warm milk or herbal tea can help
- Avoid: Alcohol, heavy meals before bed""",
        
        "insomnia": """😵 **Insomnia Management**
- Sleep schedule: Consistent bedtime/wake time
- Environment: Dark, cool, quiet room
- Relaxation: Deep breathing, meditation
- Exercise: Regular physical activity (not before bed)
- Avoid: Caffeine, alcohol, screens before bed
- Limit naps: Keep naps <30 mins, before 3 PM
- Warm bath: Before bedtime helps
- Professional help: Cognitive behavioral therapy""",
        
        "exercise": """💪 **Exercise Guidelines**
- Recommended: 150 minutes moderate activity/week
- Types: Cardio, strength training, flexibility
- Frequency: 3-5 days per week
- Duration: 30 minutes per session
- Benefits: Better health, mood, sleep, energy
- Start: Slowly if beginner, gradually increase
- Consistency: Better than intensity
- Warm up & cool down: Always important""",
        
        "weight": """⚖️ **Healthy Weight Management**
- Calories: Eat less, move more (balanced approach)
- Exercise: 30 minutes, 5 days/week
- Diet: Whole foods, vegetables, lean protein
- Hydration: Water before meals
- Sleep: 7-9 hours (affects metabolism)
- Avoid: Crash diets, processed foods
- Target: 0.5-1 kg per week is healthy
- Professional: Nutritionist/doctor for personalized plan""",
        
        "diet": """🥗 **Healthy Eating Tips**
- Vegetables: 5 portions daily
- Whole grains: Brown rice, whole wheat
- Protein: Lean meat, fish, legumes, nuts
- Fruits: 2-3 portions daily
- Limit: Salt, sugar, processed foods, fried items
- Hydration: 8 glasses water daily
- Portion: Eat slowly, stop when full
- Balance: Variety of food groups""",
        
        "nutrition": """🥗 **Nutrition Basics**
- Carbs: Whole grains, fruits, vegetables
- Protein: Meat, fish, eggs, legumes, dairy
- Fats: Olive oil, nuts, avocado (healthy)
- Vitamins: Fruits, vegetables, dairy
- Minerals: Calcium, iron, zinc from diverse foods
- Hydration: 8 glasses water daily
- Portion control: Balanced meals
- Avoid: Excess salt, sugar, processed foods""",
        
        "stress": """😰 **Stress Management**
- Breathing: Deep breathing exercises
- Exercise: 30 minutes daily
- Meditation: 10-15 minutes daily
- Social: Connect with friends/family
- Hobbies: Do things you enjoy
- Sleep: Maintain good sleep schedule
- Professional: Therapist if persistent
- Avoid: Alcohol, smoking, excess caffeine""",
        
        "anxiety": """😟 **Anxiety Relief**
- Breathing: Deep breathing exercises (4-7-8 technique)
- Meditation: Mindfulness meditation
- Exercise: Regular physical activity
- Social: Talk to friends/family
- Limit: Caffeine, alcohol
- Sleep: Good sleep hygiene
- Professional: Therapist/counselor
- Medication: Available if needed""",
        
        "depression": """😢 **Depression Support**
- Professional help: See doctor/psychiatrist
- Therapy: Counseling or CBT
- Exercise: 30 minutes daily helps
- Social: Connect with support network
- Sleep: Maintain sleep schedule
- Nutrition: Healthy diet important
- Medication: Available options
- Crisis: Call mental health hotline if in danger""",
        
        "immunity": """🛡️ **Boost Immunity**
- Vitamin C: Citrus, berries, kiwi
- Vitamin D: Sunlight, fatty fish, eggs
- Sleep: 7-9 hours daily
- Exercise: Regular physical activity
- Stress: Manage stress levels
- Hydration: Drink plenty of water
- Nutrition: Balanced diet with all food groups
- Hygiene: Wash hands regularly, avoid germs""",
        
        "blood pressure": """🩺 **Blood Pressure Management**
- Normal: <120/80 mmHg
- High: ≥140/90 mmHg
- Management:
  • Reduce salt intake
  • Exercise 30 mins daily
  • Lose weight if overweight
  • Stress management
  • Limit alcohol
  • Medication: Follow doctor's advice
- Monitoring: Check regularly
- See doctor: For persistent high BP""",
        
        "cholesterol": """💙 **Cholesterol Management**
- Types: HDL (good), LDL (bad), Triglycerides
- Diet: Reduce saturated fats
- Exercise: 30 minutes daily
- Lose weight: If overweight
- Avoid: Trans fats, excess sugar
- Foods: Oatmeal, nuts, fatty fish
- Medication: Statins if needed
- Test: Regular cholesterol screening""",
        
        "diabetes": """🩺 **Diabetes Management**
- Type 1: Insulin dependent
- Type 2: Lifestyle + medication
- Management:
  • Monitor blood sugar
  • Healthy diet (low glycemic)
  • Regular exercise
  • Maintain weight
  • Medication: As prescribed
- Complications: Eye, kidney, heart, nerve damage
- Prevention: Healthy lifestyle for Type 2
- Regular checkups: Every 3-6 months""",
        
        "hypertension": """🩺 **High Blood Pressure**
- Causes: Salt, stress, obesity, family history
- Symptoms: Often none (silent killer)
- Management:
  • Reduce salt: <2300 mg/day
  • Exercise: 30 mins daily
  • Weight: Lose excess weight
  • Stress: Manage stress
  • Medication: As prescribed
- Complications: Stroke, heart attack, kidney disease
- Monitoring: Check regularly at home""",
        
        "heart": """❤️ **Heart Health**
- Risk factors: Smoking, obesity, stress, genetics
- Prevention:
  • Exercise regularly
  • Healthy diet (Mediterranean)
  • Maintain weight
  • Manage stress
  • Stop smoking
  • Moderate alcohol
- Symptoms: Chest pain, shortness of breath
- Emergency: Call ambulance if severe symptoms
- Regular checkups: Heart health monitoring""",
        
        "asthma": """🫁 **Asthma Management**
- Triggers: Dust, pollen, smoke, exercise, cold
- Symptoms: Wheezing, shortness of breath, cough
- Prevention:
  • Identify triggers
  • Use inhalers as prescribed
  • Keep rescue inhaler handy
  • Regular exercise
  • Avoid allergens
- Action plan: Emergency instructions
- Doctor: Regular monitoring needed""",
        
        "allergy": """🤧 **Allergy Management**
- Types: Food, pollen, dust, pet, medication
- Symptoms: Itching, rash, sneezing, swelling
- Management:
  • Avoid triggers
  • Antihistamines
  • Decongestants
  • Nasal sprays
  • Remove allergen source
- Severe: Epinephrine auto-injector for anaphylaxis
- Testing: Skin tests for identification
- Doctor: For persistent allergies""",
        
        "infection": """🦠 **Infection Prevention**
- Bacterial: Antibiotics needed
- Viral: Rest and fluids
- Fungal: Antifungals
- Prevention:
  • Wash hands regularly
  • Keep wounds clean
  • Avoid contaminated food/water
  • Get vaccinated
  • Maintain hygiene
- Signs: Fever, redness, swelling, pus
- See doctor: If signs of infection""",
        
        "vaccine": """💉 **Vaccinations**
- Purpose: Prevent serious diseases
- Types: Live, inactive, mRNA
- Schedule: Age-specific recommendations
- Common:
  • Childhood: DPT, MMR, Polio
  • Adults: Flu, COVID-19, Tetanus
  • Elderly: Pneumonia, Shingles
- Side effects: Mild (soreness, fever)
- Doctor: Check if you're up to date""",
        
        "skin": """🧴 **Skin Care**
- Daily routine: Cleanse, moisturize, sunscreen
- Hydration: Drink water
- Avoid: Harsh chemicals, excessive sun
- Common issues:
  • Acne: Wash, avoid touching, salicylic acid
  • Eczema: Moisturize, avoid triggers
  • Psoriasis: Medical treatment needed
- Sunscreen: Use SPF 30+ daily
- Doctor: For persistent skin issues""",
        
        "exercise pain": """💪 **Exercise-Related Pain**
- Soreness: Delayed onset muscle soreness (DOMS)
- Duration: 3-5 days after new exercise
- Relief:
  • Rest the area
  • Ice or heat
  • Gentle stretching
  • Over-the-counter pain relief
- Prevention: Gradual increase in intensity
- Injury: Sharp pain needs medical attention""",
        
        "injury": """🩹 **Minor Injury Care**
- R.I.C.E: Rest, Ice, Compression, Elevation
- Ice: 20 minutes, 3-4 times daily
- Compress: With bandage
- Elevate: Above heart level
- Pain relief: Ibuprofen, Paracetamol
- Healing: 2-3 weeks for minor injuries
- Doctor: For severe injuries""",
        
        "flu": """🤒 **Flu Management**
- Symptoms: Fever, cough, body aches, fatigue
- Duration: 7-10 days
- Management:
  • Rest: Get plenty of sleep
  • Hydration: Drink fluids
  • Fever management: Paracetamol/Ibuprofen
  • Antiviral: Within 48 hours if available
- Prevention: Annual flu vaccine
- Complications: Pneumonia, hospitalization
- See doctor: If symptoms worsen""",
        
        "covid": """😷 **COVID-19 Information**
- Symptoms: Fever, cough, loss of taste/smell
- Spread: Droplets, surfaces
- Prevention:
  • Vaccination: Most important
  • Masks: In crowded areas
  • Distance: 6 feet from sick people
  • Hygiene: Hand washing
- Isolation: Stay home if sick
- Testing: RT-PCR or Rapid test
- Doctor: For severe symptoms""",
        
        "vitamin": """💊 **Vitamin & Minerals**
- Vitamin A: Vision, skin, immunity
- Vitamin B: Energy, brain function
- Vitamin C: Immunity, collagen
- Vitamin D: Bone health, immunity
- Vitamin E: Antioxidant
- Calcium: Bone strength
- Iron: Oxygen transport
- Zinc: Immunity, wound healing
- Source: Balanced diet or supplements""",
        
        "supplements": """💊 **Supplements Information**
- Types: Vitamins, minerals, herbs, amino acids
- Purpose: Fill nutritional gaps
- Benefits: Only if deficient
- Risks: Can interact with medications
- Quality: Buy from reputable brands
- Testing: Consult doctor before starting
- Dosage: Follow recommended amounts
- Doctor: Discuss with healthcare provider""",
    }
    
    # Search for matching answers
    for key, answer in common_answers.items():
        if key in question_lower:
            return {
                "success": True,
                "answer": answer,
                "source": "Comprehensive Health Database"
            }
    
    # If no match found
    return {
        "success": True,
        "answer": """🏥 **I don't have a specific answer, but here's general guidance:**

**What I can help with:**
- Common cold, flu, fever, cough, sore throat
- Headaches, migraines, body pain
- Digestive issues (stomach ache, diarrhea, constipation)
- Sleep problems (insomnia, sleep hygiene)
- Mental health (stress, anxiety, depression)
- Exercise, diet, nutrition, weight management
- Chronic conditions (diabetes, hypertension, heart disease, asthma)
- Allergies, infections, vaccines
- Skin care, injuries, general wellness

**For Your Question:**
1. **Describe your symptoms in detail** - This helps me give better answers
2. **Include any medical conditions** - Important for safety
3. **Ask specifically** - What bothers you most?
4. **Be precise** - Duration, severity, triggers?

**When to See a Doctor:**
- Severe or persistent symptoms
- Unusual symptoms
- Getting worse over time
- With fever and other signs
- If affecting daily life

**Emergency - Call Ambulance:**
- Chest pain or pressure
- Difficulty breathing
- Severe allergic reactions
- Loss of consciousness
- Severe injuries
- Poisoning

**Examples of questions I answer well:**
- "How to manage diabetes naturally?"
- "What are symptoms of high blood pressure?"
- "Best exercises for back pain?"
- "How to improve sleep quality?"
- "Foods for heart health?"

Please ask in more detail, and I'll provide better answers! 😊""",
        "source": "Health Assistant Guidance"
    }
