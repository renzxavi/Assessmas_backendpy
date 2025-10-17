from pydantic import BaseModel, EmailStr

class SubscribeCreate(BaseModel):
    email: EmailStr

class SubscribeResponse(BaseModel):
    success: bool
    message: str

    class Config:
        orm_mode = True

class CompanyLevels(BaseModel):
    company: str
    c_suite: int
    vp: int
    director: int
    manager: int
    other: int

    class Config:
        orm_mode = True