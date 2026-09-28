import easyocr
import re

# ---------- MODULE 1: OCR ----------
print("Step 1: Document se text nikala ja raha hai...")
reader = easyocr.Reader(['en'])
result = reader.readtext('sample_id.jpeg')

extracted_data = []
for detection in result:
    text = detection[1]
    confidence = detection[2]
    if confidence > 0.5:
        extracted_data.append(text.strip())

print(f"OCR se mila: {extracted_data}\n")

# ---------- MODULE 2: VALIDATION ----------
print("Step 2: Extracted data ko validate kiya ja raha hai...\n")
print("========== VALIDATION RESULT ==========")

validated_fields = {"dates": [], "id_numbers": [], "text_fields": []}

for item in extracted_data:
    if re.match(r'^\d{1,2}\s\d{1,2}$', item):
        print(f"📅 '{item}' → DATE")
        validated_fields["dates"].append(item)
    elif re.match(r'^\d{5,}$', item):
        print(f"🆔 '{item}' → ID/DOCUMENT NUMBER")
        validated_fields["id_numbers"].append(item)
    elif re.match(r'^[A-Za-z]+$', item):
        print(f"🌍 '{item}' → TEXT FIELD")
        validated_fields["text_fields"].append(item)
    else:
        print(f"❓ '{item}' → Unrecognized")

print("\n========== FINAL STRUCTURED DATA ==========")
print(validated_fields)