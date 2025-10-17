from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base

class Subscribe(Base):
    __tablename__ = "subscribes"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Company(Base):
    __tablename__ = "companies"
    
    id_company = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), unique=True, nullable=False)

class JobPosition(Base):
    __tablename__ = "job_positions"
    
    id_job = Column(Integer, primary_key=True, index=True)
    level = Column(String(50), nullable=False)

class JobPositionCompanyLocation(Base):
    __tablename__ = "job_positions_company_location"
    
    id_job = Column(Integer, ForeignKey("job_positions.id_job"), primary_key=True)
    id_company = Column(Integer, ForeignKey("companies.id_company"), primary_key=True)
