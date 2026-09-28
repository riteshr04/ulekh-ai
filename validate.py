import re

# Ye wahi data hai jo OCR se mila tha (abhi manually daal rahe hai, 
# baad me hum OCR ke output ko seedha yaha bhejenge)
extracted_data = ['HUNGARY', '30 06', '7012345']

print("========== VALIDATION RESULT ==========")

for item in extracted_data:
    item = item.strip()
    
    # Check 1: Kya ye ek date jaisa dikhta hai? (number number format)
    if re.match(r'^\d{1,2}\s\d{1,2}$', item):
        print(f"📅 '{item}' → Ye ek DATE jaisa lag raha hai (partial)")
    
    # Check 2: Kya ye ek ID number jaisa hai? (sirf digits, 5+ length)
    elif re.match(r'^\d{5,}$', item):
        print(f"🆔 '{item}' → Ye ek ID/DOCUMENT NUMBER lag raha hai")
    
    # Check 3: Kya ye ek country/text field hai? (sirf letters)
    elif re.match(r'^[A-Za-z]+$', item):
        print(f"🌍 '{item}' → Ye TEXT FIELD hai (jaise country/name)")
    
    else:
        print(f"❓ '{item}' → Pehchana nahi gaya, manual check chahiye")

print("\n✅ Validation complete!")