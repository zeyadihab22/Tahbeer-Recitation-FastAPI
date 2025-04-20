import json
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

# 🔹 إعداد كلمة المرور
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔹 إعداد نظام OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 🔹 إعداد مفتاح توقيع الـ JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 🔹 ملف تخزين المستخدمين
USERS_FILE = "users.json"

# 🔹 دالة لتشفير كلمة المرور
def hash_password(password: str):
    return pwd_context.hash(password)

# 🔹 دالة للتحقق من كلمة المرور
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 🔹 دالة لإنشاء رمز الوصول (Access Token)
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 🔹 دالة لكتابة المستخدمين إلى الملف
def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

# 🔹 دالة لقراءة المستخدمين من الملف مع التأكد من أنه غير فارغ
def load_users():
    if not os.path.exists(USERS_FILE) or os.stat(USERS_FILE).st_size == 0:
        print("🔹 users.json فارغ! سيتم إنشاء مستخدم admin تلقائيًا.")
        first_user = {
            "admin": {
                "username": "admin",
                "full_name": "Administrator",
                "hashed_password": hash_password("admin123"),  # كلمة مرور افتراضية
            }
        }
        save_users(first_user)  # حفظ المستخدم في الملف
        return first_user  # إرجاع القاموس مع المستخدم الافتراضي

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ users.json تالف! سيتم إعادة إنشائه.")
            return {}  # إعادة قاموس فارغ إذا كانت البيانات تالفة

# 🔹 دالة للحصول على مستخدم معين
def get_user(username: str):
    users = load_users()
    return users.get(username)

# 🔹 نموذج بيانات المستخدم عند التسجيل
class UserCreate(BaseModel):
    username: str
    full_name: str
    password: str

# 🔹 إنشاء الـ API Router
router = APIRouter()

# ✅ **تسجيل مستخدم جديد**
@router.post("/register")
async def register(user: UserCreate):
    users = load_users()  # قراءة بيانات المستخدمين من الملف

    # التحقق من وجود المستخدم مسبقًا
    if user.username in users:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # إضافة المستخدم الجديد إلى الملف
    users[user.username] = {
        "username": user.username,
        "full_name": user.full_name,
        "hashed_password": hash_password(user.password),
    }
    save_users(users)  # تحديث الملف

    return {"message": "User registered successfully"}

# ✅ **تسجيل الدخول واستلام توكن JWT**
@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    users = load_users()  # قراءة بيانات المستخدمين من الملف

    user = users.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # إنشاء توكن JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({"sub": form_data.username}, access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}