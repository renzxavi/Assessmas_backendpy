from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import subscribe, auth, company_levels_plotly
from database import Base, engine

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Backend FastAPI")

# CORS - Configurado para aceptar requests desde React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Registrar routers
app.include_router(subscribe.router)
app.include_router(auth.router)
app.include_router(company_levels_plotly.router)

@app.get("/")
def home():
    return {"message": "Backend funcionando 🚀"}