import cv2
import numpy as np
import easyocr
import re

print("=" * 55)
print("       ULEKH AI - DOCUMENT SCREENING PIPELINE")
print("=" * 55)

risk_points = 0   # jitna zyada, utna zyada risk

# ---------- MODULE 1: OCR ----------
print("\n[1/4] OCR se text nikala ja raha hai...")
reader = easyocr.Reader(['en'])
result = reader.readtext('sample_id.jpeg')

extracted_data = []
for detection in result:
    text, confidence = detection[1], detection[2]
    if confidence > 0.5:
        extracted_data.append(text.strip())

print(f"   ✓ Extracted: {extracted_data}")
if len(extracted_data) < 2:
    print("   ⚠️ Bahut kam text mila - document unclear ho sakta hai")
    risk_points += 1

# ---------- MODULE 2: VALIDATION ----------
print("\n[2/4] Fields validate kiye ja rahe hai...")
validated = {"dates": [], "id_numbers": [], "text_fields": []}
for item in extracted_data:
    if re.match(r'^\d{1,2}\s\d{1,2}$', item):
        validated["dates"].append(item)
    elif re.match(r'^\d{5,}$', item):
        validated["id_numbers"].append(item)
    elif re.match(r'^[A-Za-z]+$', item):
        validated["text_fields"].append(item)

print(f"   ✓ Structured data: {validated}")
if not validated["id_numbers"]:
    print("   ⚠️ Koi ID number nahi mila - suspicious")
    risk_points += 2

# ---------- MODULE 3: TAMPERING DETECTION ----------
print("\n[3/4] Tampering check ho raha hai...")
image = cv2.imread('sample_id.jpeg')
cv2.imwrite('temp_compressed.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 90])
compressed = cv2.imread('temp_compressed.jpg')
diff_score = np.mean(cv2.absdiff(image, compressed))

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

print(f"   ✓ Error Level Score: {diff_score:.2f} | Sharpness: {sharpness:.2f}")
if diff_score > 5:
    print("   ⚠️ Possible tampering signs")
    risk_points += 3
if sharpness < 50:
    print("   ⚠️ Photo bahut blurry hai")
    risk_points += 1

# ---------- MODULE 4: FACE VERIFICATION ----------
print("\n[4/4] Face verification ho raha hai...")
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def get_face(path):
    img = cv2.imread(path)
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(g, 1.1, 4)
    if len(faces) == 0:
        return None
    x, y, w, h = max(faces, key=lambda f: f[2]*f[3])
    return cv2.resize(g[y:y+h, x:x+w], (200, 200))

face1, face2 = get_face('sample_id.jpeg'), get_face('selfie.jpeg')
if face1 is None or face2 is None:
    print("   ⚠️ Face detect nahi hua")
    risk_points += 2
else:
    similarity = cv2.matchTemplate(face1, face2, cv2.TM_CCOEFF_NORMED)[0][0]
    print(f"   ✓ Similarity Score: {similarity:.4f}")
    if similarity < 0.5:
        print("   ⚠️ Face match nahi hua")
        risk_points += 3

# ---------- FINAL RISK ASSESSMENT ----------
print("\n" + "=" * 55)
print("           FINAL RISK ASSESSMENT")
print("=" * 55)
print(f"Total Risk Points: {risk_points}")

if risk_points == 0:
    verdict = "✅ LOW RISK - Document Verified"
elif risk_points <= 3:
    verdict = "🟡 MEDIUM RISK - Manual Review Recommended"
else:
    verdict = "🔴 HIGH RISK - Flagged for Investigation"

print(f"Verdict: {verdict}")
print("=" * 55)