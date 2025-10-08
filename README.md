# 🩺 Swasth Sarthi — Rural Healthcare Assistant (AI + Flask)

Swasth Sarthi is a bilingual (English + Hindi) **AI-powered rural healthcare assistant** that helps users access local health information, hospital details, NGOs, insurance programs, and health education in an easy, conversational way.  
Built with **Flask**, **Gemini API**, and **Google Sheets** integration — deployable instantly on **Render**.

---

## 🌟 Features
- 💬 **AI Chat Assistant** — powered by Google Gemini 2.5  
- 🎤 **Voice Input** — English / Hindi speech recognition  
- 🌍 **Bilingual Support** — auto-detects Hindi and responds accordingly  
- 🏥 **Hospitals** — lists nearby government / private facilities  
- 🤝 **NGOs & Aid** — displays verified healthcare NGOs  
- 🛡 **Insurance** — government and private health-insurance schemes  
- 🎒 **Education** — key health awareness topics for rural families  
- 🌤 **Health Tips** — seasonal preventive healthcare guidance  
- ⭐ **Feedback** — user feedback saved to Google Sheets  
- 🚑 **Ambulance / Emergency Numbers** — quick access helplines  

---

## 🧱 Tech Stack
| Layer | Technology |
|-------|-------------|
| **Backend** | Flask (Python 3.10+) |
| **AI Model** | Google Gemini Generative AI |
| **Frontend** | HTML, CSS, JS (static) |
| **Data Store** | Google Sheets API |
| **Deployment** | Render Web Service |
| **Voice Recognition** | Web Speech API |

---

## ⚙️ Local Setup

### 1️⃣ Clone Repo
```bash
git clone https://github.com/yourusername/Swasth_Sarthi.git
cd Swasth_Sarthi
```

### 2️⃣ Create Virtual Env & Activate
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Create .env
```bash
GOOGLE_API_KEY=your_google_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
SHEET_ID=your_google_sheet_id
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account","project_id":"...","private_key":"...","client_email":"..."}
FLASK_ENV=development
PORT=5000
```

*(💡 Never commit the real `.env` — add it to `.gitignore`.)*

### 5️⃣ Run Locally
```bash
python app.py
```
Open: **http://127.0.0.1:5000**

---

## 🚀 Deployment on Render

### 🧩 Required Files
- `requirements.txt`
- `Procfile`
- `app.py`
- `templates/index.html`
- `.env` (environment variables added in Render Dashboard)

### 🔧 Render Configuration
| Setting | Value |
|----------|--------|
| **Environment** | Python 3.10+ |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Port** | `5000` |

Render will automatically detect Flask, install dependencies, and start your app.

---

## 📜 Environment Variables (Required)
| Key | Description |
|-----|--------------|
| `GOOGLE_API_KEY` | Gemini API key |
| `GEMINI_MODEL` | Default model (`gemini-2.5-flash`) |
| `SHEET_ID` | Google Sheet ID for data storage |
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | Service Account JSON credentials (stringified) |
| `FLASK_ENV` | `production` or `development` |
| `PORT` | `5000` |

---

## 🧠 How It Works
1. User interacts via chat / voice.  
2. Gemini API generates context-aware, culturally sensitive answers.  
3. Hospital/NGO/Insurance/Education data fetched via Flask API routes.  
4. Google Sheets logs user profiles and feedback.  

---

## 📁 Project Structure
```
Swasth_Sarthi/
├── app.py
├── requirements.txt
├── Procfile
├── templates/
│   └── index.html
├── static/              # optional assets
└── .env
```

---

## 🧾 Example APIs
| Endpoint | Method | Description |
|-----------|---------|-------------|
| `/get` | POST | AI chat response |
| `/profile` | POST | Save user profile |
| `/get_hospitals` | GET | Hospitals list by state |
| `/get_ngos` | GET | NGOs data |
| `/get_insurance` | GET | Insurance programs |
| `/get_education` | GET | Health education |
| `/get_tips` | GET | Seasonal health tips |
| `/get_ambulance` | GET | Emergency helplines |
| `/submit_feedback` | POST | User feedback |
| `/reset` | POST | Reset session |

---

## 👩‍⚕️ Developer Notes
- For **Hindi/English voice**, use Chrome or Edge (latest version).  
- Keep Gemini replies concise and context-aware.  
- Enable “Always On” in Render Free Tier to prevent cold starts.  

---

## 🧡 Acknowledgements
- [Google Generative AI (Gemini)](https://ai.google.dev/)  
- [Google Sheets API](https://developers.google.com/sheets/api)  
- [Render Cloud Hosting](https://render.com/)
