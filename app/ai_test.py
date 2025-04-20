import joblib
import numpy as np

# تحميل النموذج
model = joblib.load("KNN_xbestx_model.pkl")

# إنشاء بيانات اختبار عشوائية (استبدلها بميزات حقيقية لاحقًا)
test_features = np.random.rand(1, 32)  # 32 هو عدد الميزات المستخدمة في التدريب

# تنفيذ التوقع
prediction = model.predict(test_features)

# طباعة النتيجة
print("توقع النموذج:", "صح" if prediction[0] == 1 else "غلط")