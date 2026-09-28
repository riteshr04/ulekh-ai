import cv2
import numpy as np

# Photo load karo
image = cv2.imread('sample_id.jpeg')

if image is None:
    print("❌ Photo load nahi hui — naam/path check karo")
else:
    print("✅ Photo load ho gayi, analysis shuru...\n")
    
    # ---------- CHECK 1: Error Level Analysis (basic tampering hint) ----------
    # Image ko compress karke wapas load karo, phir original se compare karo
    cv2.imwrite('temp_compressed.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 90])
    compressed = cv2.imread('temp_compressed.jpg')
    
    diff = cv2.absdiff(image, compressed)
    diff_score = np.mean(diff)
    
    print(f"🔍 Error Level Difference Score: {diff_score:.2f}")
    if diff_score > 5:
        print("⚠️  High difference — photo edited/re-saved multiple times ho sakta hai")
    else:
        print("✅ Normal range — koi major inconsistency nahi dikhi")
    
    # ---------- CHECK 2: Blur/Sharpness Check ----------
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    print(f"\n🔍 Sharpness Score: {laplacian_var:.2f}")
    if laplacian_var < 50:
        print("⚠️  Photo bahut blurry hai — asli document ka photo lena chahiye tha, ya kisi hisse me tampering ho sakti hai")
    else:
        print("✅ Photo sharp hai, normal quality")

    print("\n========== TAMPERING CHECK COMPLETE ==========")