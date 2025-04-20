from fastapi import FastAPI, File, UploadFile, Depends
import joblib
import os
import tempfile
from app.auth import router as auth_router, load_users  # استيراد load_users
from app.audio_processing import extract_features

# ✅ تحميل المستخدمين عند بدء التشغيل
load_users()

# تحميل الموديل
model_path = "models/KNN_xbestx_model.pkl"
try:
    model = joblib.load(model_path)
    print("✅ Model loaded successfully!")
except Exception as e:
    model = None
    print(f"❌ Error loading model: {str(e)}")

app = FastAPI()

# تضمين مسارات المصادقة في التطبيق
app.include_router(auth_router)

@app.post("/analyze/")
async def analyze_audio(file: UploadFile = File(...)):
    try:
        # حفظ الملف مؤقتًا
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_audio_path = temp_audio.name
            temp_audio.write(await file.read())

        # التحقق من تحميل النموذج قبل الاستخدام
        if model is None:
            return {"error": "❌ Model not loaded"}

        # استخراج الميزات
        features = extract_features(temp_audio_path)

        # التنبؤ باستخدام النموذج
        prediction = model.predict(features)[0]

        # إرجاع النتيجة
        result = "Correct" if prediction == 1 else "Incorrect"
        return {"result": result}

    except ValueError as ve:
        return {"error": str(ve)}
    except Exception as e:
        return {"error": f"⚠️ Error analyzing audio: {str(e)}"}
    finally:
        # حذف الملف المؤقت
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
