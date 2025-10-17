from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import SessionLocal
from models import Subscribe
from pydantic import BaseModel, validator
import traceback

router = APIRouter(prefix="/api", tags=["Subscribe"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schemas
class SubscribeCreate(BaseModel):
    email: str
    
    @validator('email')
    def validate_email(cls, v):
        if not v or not v.strip():
            raise ValueError('Email cannot be empty')
        v = v.strip().lower()
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v

class SubscribeResponse(BaseModel):
    success: bool
    message: str

# Endpoint
@router.post("/subscribe", response_model=SubscribeResponse)
async def subscribe_user(request: Request, data: SubscribeCreate, db: Session = Depends(get_db)):
    try:
        body = await request.body()
        print(f"📦 Body recibido: {body.decode()}")
        print(f"📧 Email parseado: {data.email}")
        
        # Verificar si ya existe
        existing = db.query(Subscribe).filter(Subscribe.email == data.email).first()
        if existing:
            raise HTTPException(
                status_code=422,
                detail={"errors": {"email": ["This email has already been registered."]}}
            )
        
        # Crear suscripción
        new_sub = Subscribe(email=data.email)
        db.add(new_sub)
        db.commit()
        db.refresh(new_sub)
        
        print(f"✅ Suscripción exitosa: {data.email}")
        return {"success": True, "message": "Thank you for subscribing!"}
    
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
        print(f"❌ Error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))