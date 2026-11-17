from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Configuración de SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./veterinaria.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de la Base de Datos
class CitaModel(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True, index=True)
    mascota = Column(String, index=True)
    especie = Column(String)
    dueno = Column(String)
    telefono = Column(String)
    fecha = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Clínica Veterinaria",
    description="Backend para agendar, consultar y cancelar citas médicas con persistencia SQLite.",
    version="2.0.0"
)

def obtener_base_datos():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelos Pydantic (Validación)
class CitaCrear(BaseModel):
    mascota: str
    especie: str
    dueno: str
    telefono: str
    fecha: str

    class Config:
        from_attributes = True

class CitaRespuesta(CitaCrear):
    id: int


# ENDPOINTS

@app.post("/citas", response_model=CitaRespuesta, status_code=201, tags=["Citas"])
def agendar_cita(cita: CitaCrear, db: Session = Depends(obtener_base_datos)):
    """Registra una nueva cita médica en el sistema."""
    db_cita = CitaModel(**cita.model_dump())
    db.add(db_cita)
    db.commit()
    db.refresh(db_cita)
    return db_cita

@app.get("/citas", response_model=List[CitaRespuesta], tags=["Citas"])
def listar_citas(db: Session = Depends(obtener_base_datos)):
    """Devuelve todas las citas agendadas en la clínica."""
    return db.query(CitaModel).all()

@app.delete("/citas/{cita_id}", status_code=204, tags=["Citas"])
def cancelar_cita(cita_id: int, db: Session = Depends(obtener_base_datos)):
    """Cancela y elimina una cita médica usando su ID."""
    cita = db.query(CitaModel).filter(CitaModel.id == cita_id).first()
    if not cita:
        raise HTTPException(status_code=404, detail="La cita no existe o ya fue cancelada.")
    
    db.delete(cita)
    db.commit()
    return
