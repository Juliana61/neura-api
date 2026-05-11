from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import get_db, engine
import app.models as models
import app.schemas as schemas
import app.crud as crud
import re
from app.routes import registro
from app.routes import ia
from app.routes.test import router as test_router
from app.routes.estadisticas import router as estadisticas_router
from app.auth import hashear_password, verificar_password, crear_token


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

def validar_password(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    if len(password) > 72:
        return False, "La contraseña no puede tener más de 72 caracteres"
    if not re.search(r"[A-Z]", password):
        return False, "Debe contener al menos una letra mayúscula"
    if not re.search(r"[a-z]", password):
        return False, "Debe contener al menos una letra minúscula"
    if not re.search(r"\d", password):
        return False, "Debe contener al menos un número"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-\+\=\[\]\\\/]", password):
        return False, "Debe contener al menos un carácter especial (!@#$%...)"
    return True, "OK"

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
    if not usuario.correo.endswith("@elpoli.edu.co"):
        return schemas.AuthResponse(
            success=False,
            message="Debe usar correo institucional @elpoli.edu.co"
        )

    if len(usuario.password) > 72:
        return schemas.AuthResponse(
            success=False,
            message="La contraseña no puede tener más de 72 caracteres"
        )

    db_usuario = crud.get_usuario_by_email(db, usuario.correo)
    if db_usuario:
        return schemas.AuthResponse(
            success=False,
            message="El usuario ya está registrado"
        )

    # Hashear password con auth.py
    usuario_data = usuario.dict()
    usuario_data["password"] = hashear_password(usuario.password)

    db_usuario = models.Usuario(
        nombre=usuario_data["nombre"],
        correo=usuario_data["correo"],
        password=usuario_data["password"],
        carrera=usuario_data.get("carrera"),
        semestre=usuario_data.get("semestre")
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)

    token = crear_token({"sub": db_usuario.correo, "id": db_usuario.id_usuario})

    return schemas.AuthResponse(
        success=True,
        message="Usuario registrado exitosamente",
        user=schemas.UsuarioResponse.from_orm(db_usuario),
        token=token
    )


@app.post("/auth/login", response_model=schemas.AuthResponse)
def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    if not login_data.correo.endswith("@elpoli.edu.co"):
        return schemas.AuthResponse(
            success=False,
            message="Debe usar correo institucional @elpoli.edu.co"
        )

    db_usuario = crud.get_usuario_by_email(db, login_data.correo)
    if not db_usuario:
        return schemas.AuthResponse(
            success=False,
            message="Usuario no encontrado"
        )

    if not db_usuario.password:
        return schemas.AuthResponse(
            success=False,
            message="Credenciales incorrectas"
        )

    if not verificar_password(login_data.password, db_usuario.password):
        return schemas.AuthResponse(
            success=False,
            message="Credenciales incorrectas"
        )

    token = crear_token({"sub": db_usuario.correo, "id": db_usuario.id_usuario})

    return schemas.AuthResponse(
        success=True,
        message="Login exitoso",
        user=schemas.UsuarioResponse.from_orm(db_usuario),
        token=token
    )

    
app.include_router(registro.router)
app.include_router(ia.router)
app.include_router(test_router, prefix="")
app.include_router(estadisticas_router)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)