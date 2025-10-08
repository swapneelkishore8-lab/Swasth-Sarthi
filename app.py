# app.py
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Flask app
app = Flask(__name__, template_folder="templates")
CORS(app)

# --- Gemini config (Google Generative AI) ---
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GOOGLE_API_KEY not set in .env")
genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
SYSTEM_INSTRUCTIONS = (
    "You are Swasth_Sarthi, a friendly, non-judgemental rural healthcare assistant for India. "
    "Keep responses simple, culturally sensitive, and helpful. Use light Hinglish where appropriate. "
    "Always advise consulting a local doctor for serious issues and emergencies."
)
# Initialize model/chat
gemini_model = genai.GenerativeModel(model_name=MODEL_NAME, system_instruction=SYSTEM_INSTRUCTIONS)
chat = gemini_model.start_chat(history=[])

# --- Google Sheets setup ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_ID = os.getenv("SHEET_ID", "1PNXFatNXRQgtTAQaiYD7UHxIXH1snE2zVBbfdL1Ezyo")

try:
    import json
    creds = None
    creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if creds_json:
        info = json.loads(creds_json)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        print("⚠️ GOOGLE_APPLICATION_CREDENTIALS_JSON not found — skipping Google Sheets connection.")
    if creds:
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).sheet1
        print(f"✅ Connected to Google Sheet: {sheet.title}")
    else:
        sheet = None
except Exception as e:
    print("⚠️ Google Sheet connection failed:", e)
    sheet = None

# Temporary user storage (keeps onboarding state per server run)
user_data = {"name": None, "age": None, "gender": None, "location": None, "details_collected": False}

# ---------------- ROUTES ----------------

@app.route("/")
def index():
    try:
        return render_template("index.html")
    except Exception:
        return "<h2>Welcome to Swasth Sarthi 🚑</h2><p>The index.html template is missing. Please add it in the templates folder.</p>"


@app.route("/get", methods=["POST"])
def chatbot_response():
    """
    Primary chat endpoint. Expects form-encoded 'msg'.
    Uses a simple onboarding flow server-side as well (age/gender/location) if server-side user_data not present.
    Once onboarding done, will send conversation context to Gemini and return reply.
    """
    global user_data
    user_message = request.form.get("msg", "").strip()
    if not user_message:
        return jsonify({"reply": "Please type or speak a message to start."})

    # if name not collected server-side, we won't enforce here because frontend collects name and calls /profile.
    # We'll, however, keep the prior server-side behavior of collecting age/gender/location if needed.

    # Collect age if missing
    if not user_data.get("age"):
        try:
            user_data["age"] = int(user_message)
            return jsonify({"reply": "Got it! Ab bataye apka gender (Male / Female / Other)?"})
        except ValueError:
            return jsonify({"reply": "Please enter your age as a number (e.g., 25)."})
    # Collect gender
    elif not user_data.get("gender"):
        user_data["gender"] = user_message.strip().capitalize()
        return jsonify({"reply": "Thanks! Ab bataye apka location (village/city name)?"})
    # Collect location
    elif not user_data.get("location"):
        user_data["location"] = user_message.strip().title()
        user_data["details_collected"] = True

        # Save collected user details to sheet
        if sheet:
            try:
                sheet.append_row([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Profile (server-onboarding)",
                    user_data.get("name", ""),
                    user_data.get("age", ""),
                    user_data.get("gender", ""),
                    user_data.get("location", "")
                ])
            except Exception as e:
                print("⚠️ Error saving onboarding info to sheet:", e)

        return jsonify({"reply": f"Shukriya! Aap {user_data['location']} se hain. Bataiye, health related kis tarah ki madad chahiye?"})

    # Normal conversation
    if user_data.get("details_collected"):
        try:
            context = (
                f"User details — Name: {user_data.get('name','')}, Age: {user_data.get('age')}, "
                f"Gender: {user_data.get('gender')}, Location: {user_data.get('location')}. "
                f"User says: {user_message}"
            )
            response = chat.send_message(context)
            return jsonify({"reply": response.text})
        except Exception as e:
            print("❌ Gemini error:", e)
            return jsonify({"reply": "Sorry, temporary error generating reply. Please try again."})

    # default fallback
    return jsonify({"reply": "Sorry, I couldn't understand that. Please try again."})


@app.route("/profile", methods=["POST"])
def profile():
    """
    Receives JSON with user profile fields (name, age, gender, location) from frontend onboarding.
    Saves to Google Sheets and updates server-side user_data store (so /get can use it).
    """
    global user_data
    data = request.json or {}
    name = data.get("name")
    age = data.get("age")
    gender = data.get("gender")
    location = data.get("location")

    # Update server-side user_data
    if name: user_data["name"] = name
    if age: user_data["age"] = age
    if gender: user_data["gender"] = gender
    if location:
        user_data["location"] = location
        user_data["details_collected"] = True

    # Save to sheet
    if sheet:
        try:
            sheet.append_row([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Profile",
                name or "",
                age or "",
                gender or "",
                location or ""
            ])
        except Exception as e:
            print("⚠️ Error saving profile to sheet:", e)

    return jsonify({"reply": "Profile saved"})


@app.route("/get_ngos", methods=["GET"])
def get_ngos():
    ngos = [
        {"name": "Smile Foundation", "focus": "Rural Health & Education", "link": "https://www.smilefoundationindia.org"},
        {"name": "SEWA Rural", "focus": "Maternal & Child Health", "link": "https://www.sewarural.org"},
        {"name": "CARE India", "focus": "Women’s Health & Nutrition", "link": "https://www.careindia.org"},
        {"name": "HelpAge India", "focus": "Elderly Healthcare", "link": "https://www.helpageindia.org"}
    ]
    return jsonify({"ngos": ngos})


@app.route("/get_ambulance", methods=["GET"])
def get_ambulance():
    helplines = [
        {"name": "National Ambulance", "number": "108"},
        {"name": "Women Helpline", "number": "1091"},
        {"name": "Child Helpline", "number": "1098"},
        {"name": "Fire & Emergency", "number": "101"}
    ]
    return jsonify({"helplines": helplines})


@app.route("/get_hospitals", methods=["GET"])
def get_hospitals():
    hospitals = {
        "Uttar Pradesh": [
            {"name": "King George’s Medical University", "city": "Lucknow", "contact": "0522-2257450"},
            {"name": "SGPGI", "city": "Lucknow", "contact": "0522-2668700"},
            {"name": "BHIMS", "city": "Varanasi", "contact": "0542-2366789"}
        ],
        "Bihar": [
            {"name": "AIIMS Patna", "city": "Patna", "contact": "0612-2451070"},
            {"name": "IGIMS", "city": "Patna", "contact": "0612-2297631"}
        ],
        "Madhya Pradesh": [
            {"name": "Gandhi Medical College", "city": "Bhopal", "contact": "0755-2739400"},
            {"name": "Jabalpur Hospital", "city": "Jabalpur", "contact": "0761-2623100"}
        ],
        "Rajasthan": [
            {"name": "SMS Hospital", "city": "Jaipur", "contact": "0141-2518400"},
            {"name": "AIIMS Jodhpur", "city": "Jodhpur", "contact": "0291-2435555"}
        ]
    }
    return jsonify(hospitals)


@app.route("/get_insurance", methods=["GET"])
def get_insurance():
    insurance = [
        {"company": "Star Health Insurance", "details": "Affordable rural plans with family coverage."},
        {"company": "LIC Health Plus", "details": "Trusted by millions with hospital benefits."},
        {"company": "Care Health Insurance", "details": "Covers rural and semi-urban areas."},
        {"company": "Niva Bupa", "details": "Cashless treatment in 8000+ hospitals."}
    ]
    return jsonify({"insurance": insurance})


@app.route("/get_education", methods=["GET"])
def get_education():
    education = [
        {"topic": "Clean Water", "message": "Always boil or filter drinking water to prevent diseases."},
        {"topic": "Nutrition", "message": "Include fruits, vegetables, pulses and clean milk for children's growth."},
        {"topic": "Exercise", "message": "Encourage outdoor play and physical activity for at least 30 minutes daily."},
        {"topic": "Hygiene", "message": "Wash hands before meals and after using the toilet."}
    ]
    return jsonify({"education": education})


@app.route("/get_tips", methods=["GET"])
def get_tips():
    """
    Returns detailed seasonal tips keyed by a simple season label.
    The frontend will request this once the user opens the Health Tips tab.
    """
    tips = {
        "summer": [
            {"title": "Hydration & ORS", "advice": "Carry water; sip often. If dehydration signs (weakness, dry mouth) appear, use ORS. Hinglish: 'Pani peete raho — chhota glass 15-20 min mein'."},
            {"title": "Sun Protection", "advice": "Avoid direct sun from 11am-3pm, wear a hat and lightweight clothing. 'Dhoop se bachiye'."},
            {"title": "Food Safety", "advice": "Avoid uncovered foods and street foods that sit in heat; eat freshly cooked meals."}
        ],
        "monsoon": [
            {"title": "Dengue Prevention", "advice": "Remove standing water from pots, tyres; use repellents and nets. 'Machhar maarne ki safai zaroori'."},
            {"title": "Safe Drinking Water", "advice": "Boil water before drinking or use household filters; treat with chlorine if needed."},
            {"title": "Clean Surroundings", "advice": "Keep drains clear and report waterlogging. Seek care early for fever."}
        ],
        "winter": [
            {"title": "Immunity & Warmth", "advice": "Include warm soups, seasonal vegetables, and tea. 'Garam cheezein aur aaram'."},
            {"title": "Cold & Flu Care", "advice": "Use warm fluids, rest, and visit a clinic if fever persists >48 hours."},
            {"title": "Respiratory Safety", "advice": "Avoid smoky kitchens and use proper ventilation."}
        ],
        "spring": [
            {"title": "Allergy Care", "advice": "Wash face/hands after outdoor work; rinse nose with clean water if sneezy."},
            {"title": "Nutrition Focus", "advice": "Fresh produce is plentiful — include seasonal fruits and greens for vitamins."},
            {"title": "Preventive Check", "advice": "Immunize children as per schedule — check with local health worker."}
        ],
        "general": [
            {"title": "Pregnancy Care", "advice": "Regular ANC visits, iron & folic acid, TT immunizations. 'Antenatal visits zaruri hain'."},
            {"title": "Child Health", "advice": "Breastfeeding, timely immunizations, and growth monitoring."},
            {"title": "Mental Health", "advice": "Talk to family, stay active, and seek local counselor if stressed."}
        ]
    }
    return jsonify({"tips": tips})


@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    data = request.json or {}
    name = data.get("name", "Anonymous")
    rating = data.get("rating", "")
    feedback = data.get("feedback", "")

    # Save to Google Sheet
    if sheet:
        try:
            sheet.append_row([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Feedback",
                name,
                rating,
                feedback
            ])
        except Exception as e:
            print("⚠️ Error saving feedback:", e)

    return jsonify({"reply": "🙏 Thank you for your feedback! Swasth Sarthi appreciates your support."})


@app.route("/reset", methods=["POST"])
def reset():
    global user_data
    user_data = {"name": None, "age": None, "gender": None, "location": None, "details_collected": False}
    return jsonify({"reply": "Okay, data reset. Please start again."})


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(debug=True)
