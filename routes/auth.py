from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db  # ✅ Importar de database, no SessionLocal
from models import User
from pydantic import BaseModel, validator
import bcrypt
import traceback

router = APIRouter(prefix="/api", tags=["Auth"])

# ========== SCHEMAS ==========
class UserRegister(BaseModel):
    name: str
    surname: str
    email: str
    password: str
    password_confirmation: str
    
    @validator('name', 'surname')
    def validate_names(cls, v):
        if not v or not v.strip():
            raise ValueError('Name and surname are required')
        return v.strip()
    
    @validator('email')
    def validate_email(cls, v):
        if not v or '@' not in v:
            raise ValueError('Invalid email')
        return v.lower().strip()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v
    
    @validator('password_confirmation')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserLogin(BaseModel):
    email: str
    password: str
    
    @validator('email')
    def validate_email(cls, v):
        if not v or '@' not in v:
            raise ValueError('Invalid email')
        return v.lower().strip()

class UserResponse(BaseModel):
    success: bool
    message: str
    access_token: str = None
    user: dict = None

# ========== REGISTER ==========
@router.post("/register", response_model=UserResponse)
def register_user(data: UserRegister, db: Session = Depends(get_db)):  # ✅ Usa get_db de database
    try:
        print(f"📝 Intentando registrar: {data.email}")
        
        # Verificar si ya existe
        existing_user = db.query(User).filter(User.email == data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=422,
                detail={"errors": {"email": ["This email has already been registered."]}}
            )
        
        # Hash de contraseña
        hashed_password = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Crear usuario
        new_user = User(
            name=data.name,
            surname=data.surname,
            email=data.email,
            password=hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ Usuario registrado: {new_user.email}")
        
        return {
            "success": True,
            "message": "User registered successfully!",
            "access_token": f"token_{new_user.id}_fake",
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "name": new_user.name,
                "surname": new_user.surname
            }
        }
    
    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=422,
            detail={"errors": {"email": ["This email has already been registered."]}}
        )
    except Exception as e:
        db.rollback()
        print(f"❌ Error en register: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# ========== LOGIN ==========
@router.post("/login", response_model=UserResponse)
def login_user(data: UserLogin, db: Session = Depends(get_db)):  # ✅ Usa get_db de database
    try:
        print(f"🔐 Intentando login: {data.email}")
        
        # Buscar usuario
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            raise HTTPException(
                status_code=401,
                detail={"errors": {"email": ["Invalid credentials."]}}
            )
        
        # Verificar contraseña
        if not bcrypt.checkpw(data.password.encode('utf-8'), user.password.encode('utf-8')):
            raise HTTPException(
                status_code=401,
                detail={"errors": {"password": ["Invalid credentials."]}}
            )
        
        print(f"✅ Login exitoso: {user.email}")
        
        return {
            "success": True,
            "message": "Login successful!",
            "access_token": f"token_{user.id}_fake",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "surname": user.surname
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en login: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))