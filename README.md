# 🛡️ Ulekh AI — AI-Powered Fake Identity & Document Screening System

Ulekh AI reads identity documents (ID cards, passports, licenses), extracts and validates
their fields, checks for tampering, verifies the holder's face against a live selfie, and
generates a clear risk score — helping flag fraudulent documents before they cause harm.

🔗 **Live Demo:** https://ulekh-ai.onrender.com
*(hosted on a free tier — may take 30-50s to load if idle)*

## ✨ Features

- **OCR Extraction** — reads names, ID numbers, and dates from document photos using RapidOCR
- **Field Validation** — pattern-matches extracted text into dates, ID numbers, and text fields
- **Tampering Detection** — analyzes image compression and sharpness (OpenCV) to flag edited documents
- **Face Verification** — compares the document photo against a live selfie
- **Risk Scoring** — combines every signal into a Low / Medium / High verdict
- **Secure Audit Trail** — every screening is logged per-user in a database
- **Full Authentication** — signup, login, and OTP verification

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| OCR | RapidOCR (ONNX Runtime) |
| Computer Vision | OpenCV |
| Database | SQLite |
| Auth | bcrypt (password hashing), itsdangerous (sessions) |
| Frontend | HTML, CSS, JavaScript |
| Deployment | Render |

## 🚀 Running Locally

```bash
git clone https://github.com/riteshr04/ulekh-ai.git
cd ulekh-ai
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open `http://127.0.0.1:8000` in your browser.

## 📐 How It Works

```
User uploads document + selfie (Frontend)
            ↓
FastAPI backend receives the request
            ↓
RapidOCR extracts text → Validation checks fields
            ↓
OpenCV checks for tampering → Face verification runs
            ↓
All signals combine into a Risk Score
            ↓
Result is saved to the database and returned to the user
```

## 🔭 Future Scope

- Replace basic face-matching with a deep-learning face embedding model for higher accuracy
- Real email-based OTP delivery (currently shown on-screen for demo purposes)
- Blockchain-based tamper-proof audit trail
- Containerized deployment (Docker) for production-scale hosting

---
Built by [Ritesh](https://github.com/riteshr04) as a self-taught project — second-year B.Tech CSE (AI/ML) student.