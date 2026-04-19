# app/routes/registro.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app import models, schemas
from app.database import get_db
import app.crud as crud

router = APIRouter(prefix="/registro", tags=["Registro Emocional"])

@router.post("/", response_model=schemas.RegistroEmocionalResponse)
def crear_registro_emocional(
    registro: schemas.RegistroEmocionalCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo registro emocional con sus actividades asociadas.
    """
    # Por ahora simulamos un usuario (id_usuario = 1)
    id_usuario = 1

    # Verificar que la emoción exista
    emocion = db.query(models.Emocion).filter(models.Emocion.id_emocion == registro.id_emocion).first()
    if not emocion:
        raise HTTPException(status_code=404, detail="La emoción no existe")

    # Crear registro emocional
    nuevo_registro = models.RegistroEmocional(
        id_usuario=id_usuario,
        id_emocion=registro.id_emocion,
        nota=registro.nota,
        fecha_registro=datetime.utcnow()
    )
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)

    # Asociar actividades (si hay)
    for id_actividad in registro.actividades:
        actividad = db.query(models.Actividad).filter(models.Actividad.id_actividad == id_actividad).first()
        if actividad:
            link = models.RegistroActividad(
                id_registro=nuevo_registro.id_registro,
                id_actividad=id_actividad
            )
            db.add(link)
    db.commit()

    # Obtener actividades asociadas
    actividades = (
        db.query(models.Actividad)
        .join(models.RegistroActividad)
        .filter(models.RegistroActividad.id_registro == nuevo_registro.id_registro)
        .all()
    )

    return schemas.RegistroEmocionalResponse(
        id_registro=nuevo_registro.id_registro,
        id_usuario=nuevo_registro.id_usuario,
        id_emocion=nuevo_registro.id_emocion,
        fecha_registro=nuevo_registro.fecha_registro,
        nota=nuevo_registro.nota,
        emocion=emocion,
        actividades=actividades
    )

@router.get("/{id_usuario}", response_model=list[schemas.RegistroEmocionalResponse])
def get_registros(id_usuario: int, db: Session = Depends(get_db)):
    registros = (
        db.query(models.RegistroEmocional)
        .filter(models.RegistroEmocional.id_usuario == id_usuario)
        .order_by(models.RegistroEmocional.fecha_registro.desc())
        .all()
    )

    if not registros:
        return []

    # Construir respuesta completa
    respuesta = []
    for r in registros:
        emocion = db.query(models.Emocion).filter(models.Emocion.id_emocion == r.id_emocion).first()

        actividades = (
            db.query(models.Actividad)
            .join(models.RegistroActividad)
            .filter(models.RegistroActividad.id_registro == r.id_registro)
            .all()
        )

        respuesta.append(
            schemas.RegistroEmocionalResponse(
                id_registro=r.id_registro,
                id_usuario=r.id_usuario,
                id_emocion=r.id_emocion,
                fecha_registro=r.fecha_registro,
                nota=r.nota,
                emocion=emocion,
                actividades=actividades
            )
        )

    return respuesta
