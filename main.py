from fastapi import FastAPI, File, UploadFile, Request, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
import cv2
import numpy as np
import easyocr
import re
import shutil
import os
import sqlite3
import random
from datetime import datetime
import bcrypt
from itsdangerous import URLSafeTimedSerializer, BadSignature

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

print("OCR model load ho raha hai, thoda time lagega...")
reader = easyocr.Reader(['en'])
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
print("Model ready! Server start ho raha hai...")

DB_FILE = "ulekh_ai.db"
SECRET_KEY = os.environ.get("SECRET_KEY", "local-dev-key")
serializer = URLSafeTimedSerializer(SECRET_KEY)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
# email -> {otp, password_hash, expires_at}  (temporary, RAM me hi rehta hai)
pending_signups = {}


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password_hash TEXT,
        created_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS screenings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        timestamp TEXT,
        extracted_text TEXT,
        id_numbers TEXT,
        dates TEXT,
        error_level_score REAL,
        sharpness REAL,
        face_similarity REAL,
        risk_points INTEGER,
        verdict TEXT
    )''')
    conn.commit()
    conn.close()


init_db()


def get_current_user(request: Request):
    token = request.cookies.get("session")
    if not token:
        return None
    try:
        email = serializer.loads(token, max_age=60 * 60 * 24 * 7)  # 7 din valid
        return email
    except BadSignature:
        return None


# ---------------- AUTH PAGES ----------------
@app.get("/")
async def landing_page():
    return FileResponse("landing.html")


@app.get("/signup")
async def signup_page():
    return FileResponse("signup.html")


@app.get("/login")
async def login_page():
    return FileResponse("login.html")


@app.get("/dashboard")
async def dashboard_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login")
    return FileResponse("dashboard.html")


# ---------------- AUTH API ----------------
@app.post("/api/signup")
async def api_signup(email: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE email = ?", (email,))
    existing = c.fetchone()
    conn.close()
    if existing:
        raise HTTPException(status_code=400, detail="Ye email pehle se registered hai. Login karo.")

    otp = str(random.randint(1000, 9999))
    pending_signups[email] = {
        "otp": otp,
                "password_hash": hash_password(password),
    }
    # Real app me ye OTP email se jayega. Abhi demo/testing mode me screen pe dikhate hai.
    return {"message": "OTP generated", "demo_otp": otp}


@app.post("/api/verify-otp")
async def api_verify_otp(email: str = Form(...), otp: str = Form(...)):
    record = pending_signups.get(email)
    if not record:
        raise HTTPException(status_code=400, detail="Pehle signup karo.")
    if record["otp"] != otp:
        raise HTTPException(status_code=400, detail="Galat OTP.")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
              (email, record["password_hash"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    del pending_signups[email]

    token = serializer.dumps(email)
    response = JSONResponse({"message": "Account verified"})
    response.set_cookie(key="session", value=token, httponly=True, max_age=60 * 60 * 24 * 7)
    return response


@app.post("/api/login")
async def api_login(email: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()

    if not row or not verify_password(password, row[0]):
        raise HTTPException(status_code=400, detail="Email ya password galat hai.")

    token = serializer.dumps(email)
    response = JSONResponse({"message": "Login successful"})
    response.set_cookie(key="session", value=token, httponly=True, max_age=60 * 60 * 24 * 7)
    return response


@app.post("/api/logout")
async def api_logout():
    response = JSONResponse({"message": "Logged out"})
    response.delete_cookie("session")
    return response


@app.get("/api/me")
async def api_me(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not logged in")
    return {"email": user}


# ---------------- AI PIPELINE ----------------
def get_face(path):
    img = cv2.imread(path)
    if img is None:
        return None
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(g, 1.1, 4)
    if len(faces) == 0:
        return None
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    return cv2.resize(g[y:y + h, x:x + w], (200, 200))


def save_screening(user_email, data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''INSERT INTO screenings
        (user_email, timestamp, extracted_text, id_numbers, dates, error_level_score, sharpness, face_similarity, risk_points, verdict)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
        user_email,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ", ".join(data["extracted_text"]),
        ", ".join(data["validated_fields"]["id_numbers"]),
        ", ".join(data["validated_fields"]["dates"]),
        data["tampering_check"]["error_level_score"],
        data["tampering_check"]["sharpness"],
        data["face_verification"].get("similarity_score"),
        data["risk_points"],
        data["verdict"]
    ))
    conn.commit()
    conn.close()


@app.post("/screen-document")
async def screen_document(request: Request, document: UploadFile = File(...), selfie: UploadFile = File(...)):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Login required")

    doc_path = f"temp_doc_{document.filename}"
    selfie_path = f"temp_selfie_{selfie.filename}"
    with open(doc_path, "wb") as f:
        shutil.copyfileobj(document.file, f)
    with open(selfie_path, "wb") as f:
        shutil.copyfileobj(selfie.file, f)

    risk_points = 0
    response = {}

    result = reader.readtext(doc_path)
    extracted_data = [d[1].strip() for d in result if d[2] > 0.5]
    response["extracted_text"] = extracted_data
    if len(extracted_data) < 2:
        risk_points += 1

    validated = {"dates": [], "id_numbers": [], "text_fields": []}
    for item in extracted_data:
        if re.match(r'^\d{1,2}\s\d{1,2}$', item):
            validated["dates"].append(item)
        elif re.match(r'^\d{5,}$', item):
            validated["id_numbers"].append(item)
        elif re.match(r'^[A-Za-z]+$', item):
            validated["text_fields"].append(item)
    response["validated_fields"] = validated
    if not validated["id_numbers"]:
        risk_points += 2

    image = cv2.imread(doc_path)
    cv2.imwrite("temp_compressed.jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 90])
    compressed = cv2.imread("temp_compressed.jpg")
    diff_score = float(np.mean(cv2.absdiff(image, compressed)))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    response["tampering_check"] = {"error_level_score": round(diff_score, 2), "sharpness": round(sharpness, 2)}
    if diff_score > 5:
        risk_points += 3
    if sharpness < 50:
        risk_points += 1

    face1, face2 = get_face(doc_path), get_face(selfie_path)
    if face1 is None or face2 is None:
        response["face_verification"] = {"status": "Face not detected"}
        risk_points += 2
    else:
        similarity = float(cv2.matchTemplate(face1, face2, cv2.TM_CCOEFF_NORMED)[0][0])
        response["face_verification"] = {"similarity_score": round(similarity, 4)}
        if similarity < 0.5:
            risk_points += 3

    if risk_points == 0:
        verdict = "LOW RISK - Document Verified"
    elif risk_points <= 3:
        verdict = "MEDIUM RISK - Manual Review Recommended"
    else:
        verdict = "HIGH RISK - Flagged for Investigation"
    response["risk_points"] = risk_points
    response["verdict"] = verdict

    save_screening(user, response)

    os.remove(doc_path)
    os.remove(selfie_path)
    if os.path.exists("temp_compressed.jpg"):
        os.remove("temp_compressed.jpg")

    return response


@app.get("/history")
async def get_history(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Login required")

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM screenings WHERE user_email = ? ORDER BY id DESC LIMIT 50", (user,))
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return {"records": rows}