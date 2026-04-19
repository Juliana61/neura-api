from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import get_db, engine
import app.models as models
import app.schemas as schemas
import app.crud as crud
from app.routes import registro
from app.routes import ia
from app.routes.test import router as test_router
from app.routes.estadisticas import router as estadisticas_router


# Crear tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Diario Emocional API",
    description="API para análisis de bienestar estudiantil - Politécnico Colombiano Jaime Isaza Cadavid",
    version="1.0.0"
)

# CORS para conectar con Android
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Diario Emocional API - Bienestar Universitario",
        "universidad": "Politécnico Colombiano Jaime Isaza Cadavid",
        "correo_permitido": "@elpoli.edu.co"
    }

@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        users_count = db.query(models.Usuario).count()
        emotions_count = db.query(models.Emocion).count()
        activities_count = db.query(models.Actividad).count()
        
        return {
            "status": "connected",
            "total_usuarios": users_count,
            "total_emociones": emotions_count,
            "total_actividades": activities_count
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/emociones", response_model=list[schemas.EmocionResponse])
def get_emociones(db: Session = Depends(get_db)):
    return crud.get_emociones(db)

@app.get("/actividades", response_model=list[schemas.ActividadResponse])
def get_actividades(db: Session = Depends(get_db)):
    return crud.get_actividades(db)

@app.post("/auth/register", response_model=schemas.AuthResponse)
def register(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # Validar correo institucional
    if not usuario.correo.endswith("@elpoli.edu.co"):
        return schemas.AuthResponse(
            success=False,
            message="Debe usar correo institucional @elpoli.edu.co"
        )
    
    # Verificar si el usuario ya existe
    db_usuario = crud.get_usuario_by_email(db, usuario.correo)
    if db_usuario:
        return schemas.AuthResponse(
            success=False,
            message="El usuario ya está registrado"
        )
    
    # Crear usuario
    nuevo_usuario = crud.crear_usuario(db, usuario)
    
    return schemas.AuthResponse(
        success=True,
        message="Usuario registrado exitosamente",
        user=schemas.UsuarioResponse.from_orm(nuevo_usuario),
        token="simulated_token"  # En producción usar JWT real
    )

@app.post("/auth/login", response_model=schemas.AuthResponse)
def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    # Validar correo institucional
    if not login_data.correo.endswith("@elpoli.edu.co"):
        return schemas.AuthResponse(
            success=False,
            message="Debe usar correo institucional @elpoli.edu.co"
        )
    
    # Buscar usuario (en producción verificar password hash)
    db_usuario = crud.get_usuario_by_email(db, login_data.correo)
    if not db_usuario:
        return schemas.AuthResponse(
            success=False,
            message="Usuario no encontrado"
        )
    
    # Simular verificación de password (en producción usar hash)
    if login_data.password != "password123":  # Temporal para pruebas
        return schemas.AuthResponse(
            success=False,
            message="Credenciales incorrectas"
        )
    
    return schemas.AuthResponse(
        success=True,
        message="Login exitoso",
        user=schemas.UsuarioResponse.from_orm(db_usuario),
        token="simulated_token"
    )
    


    
app.include_router(registro.router)
app.include_router(ia.router)
app.include_router(test_router, prefix="")
app.include_router(estadisticas_router)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)