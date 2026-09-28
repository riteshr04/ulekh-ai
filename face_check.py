import cv2
import numpy as np

# Face detect karne ke liye OpenCV ka built-in model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def get_face(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    if len(faces) == 0:
        return None
    
    # Sabse bada face lo (agar multiple mile)
    x, y, w, h = max(faces, key=lambda f: f[2]*f[3])
    face_crop = gray[y:y+h, x:x+w]
    face_resized = cv2.resize(face_crop, (200, 200))
    return face_resized

print("Face detect kiya ja raha hai...\n")

face1 = get_face('sample_id.jpeg')
face2 = get_face('selfie.jpeg')

if face1 is None:
    print("❌ sample_id.jpeg me face nahi mila")
elif face2 is None:
    print("❌ selfie.jpeg me face nahi mila")
else:
    print("✅ Dono photos me face mil gaya\n")
    
    # Simple similarity check - correlation
    correlation = cv2.matchTemplate(face1, face2, cv2.TM_CCOEFF_NORMED)[0][0]
    
    print("========== FACE VERIFICATION RESULT ==========")
    print(f"Similarity Score: {correlation:.4f}  (1.0 = perfect match, 0 = no match)")
    
    if correlation > 0.5:
        print("\n✅ Dono chehre MATCH karte lag rahe hai")
    else:
        print("\n⚠️ Dono chehre MATCH nahi karte")