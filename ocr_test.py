import easyocr

reader = easyocr.Reader(['en'])
result = reader.readtext('sample_id.jpeg')

print("========== FILTERED RESULT (sirf confident text) ==========")
extracted_data = []

for detection in result:
    text = detection[1]
    confidence = detection[2]
    
    # Sirf 50% se zyada confidence wala text lenge
    if confidence > 0.5:
        extracted_data.append(text)
        print(f"✓ {text}  (confidence: {confidence:.2f})")

print("\n========== FINAL EXTRACTED FIELDS ==========")
print(extracted_data)