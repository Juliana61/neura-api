# ...existing code...
import unicodedata
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas
from passlib.context import CryptContext
from datetime import datetime, date

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_usuario_by_email(db: Session, correo: str):
    return db.query(models.Usuario).filter(models.Usuario.correo == correo).first()

def crear_usuario(db: Session, usuario: schemas.UsuarioCreate):
    hashed_password = pwd_context.hash(usuario.password)
    db_usuario = models.Usuario(
        nombre=usuario.nombre,
        correo=usuario.correo,
        carrera=usuario.carrera,
        semestre=usuario.semestre,
        # Ajusta 'password' si tu modelo usa otro nombre (password_hash, etc.)
        password=hashed_password
    )
    try:
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    except Exception:
        db.rollback()
        raise

def get_emociones(db: Session):
    return db.query(models.Emocion).order_by(models.Emocion.nivel.asc()).all()


def get_actividades(db: Session):
    return db.query(models.Actividad).all()

def crear_registro_emocional(db: Session, registro: schemas.RegistroEmocionalCreate, usuario_id: int):
    db_registro = models.RegistroEmocional(
        id_usuario=usuario_id,
        id_emocion=registro.id_emocion,
        nota=registro.nota,
        fecha_registro=datetime.utcnow()
    )
    try:
        db.add(db_registro)
        db.commit()
        db.refresh(db_registro)

        # Agregar actividades si existen
        if getattr(registro, "actividades", None):
            registros_actividades = [
                models.RegistroActividad(
                    id_registro=db_registro.id_registro,
                    id_actividad=actividad_id
                ) for actividad_id in registro.actividades
            ]
            db.add_all(registros_actividades)

        db.commit()
        return db_registro
    except Exception:
        db.rollback()
        raise

def get_registros_por_usuario(db: Session, usuario_id: int):
    registros = (
        db.query(models.RegistroEmocional)
        .filter(models.RegistroEmocional.id_usuario == usuario_id)
        .order_by(models.RegistroEmocional.fecha_registro.desc())
        .all()
    )
    return registros



def normalizar(texto: str) -> str:
    """Quita tildes y pasa a minúsculas."""
    if not isinstance(texto, str):
        return ""
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

def generar_estadisticas(db, usuario_id: int):
    """Genera estadísticas completas automáticamente para un usuario."""

    # Obtener todos los registros del usuario
    registros = (
        db.query(models.RegistroEmocional)
        .filter(models.RegistroEmocional.id_usuario == usuario_id)
        .order_by(models.RegistroEmocional.fecha_registro.asc())
        .all()
    )

    if not registros:
        raise ValueError("El usuario no tiene registros emocionales todavía")

    # Fecha de inicio y fin
    fecha_inicio = registros[0].fecha_registro
    fecha_fin = registros[-1].fecha_registro

    total_registros = len(registros)

    # Conteo por emoción
    conteo = (
        db.query(models.Emocion.nombre_emocion, func.count(models.RegistroEmocional.id_emocion))
        .join(models.Emocion, models.Emocion.id_emocion == models.RegistroEmocional.id_emocion)
        .filter(models.RegistroEmocional.id_usuario == usuario_id)
        .group_by(models.Emocion.nombre_emocion)
        .all()
    )

    mapa_norm = {normalizar(nombre): cantidad for nombre, cantidad in conteo}
    
    # Nombres normalizados esperados
    labels = {
        "increible": "Increible",
        "bien": "Bien",
        "meh": "Meh",
        "mal": "Mal",
        "horrible": "Horrible",
    }

    # Emoción predominante
    emocion_predominante_norm = max(mapa_norm, key=mapa_norm.get)
    emocion_predominante = labels.get(emocion_predominante_norm, emocion_predominante_norm)
    # Función porcentaje
    def pct(key_norm):
        return (mapa_norm.get(key_norm, 0) * 100) / total_registros

    estadistica = models.Estadistica(
        id_usuario=usuario_id,
        fecha_inicio=fecha_inicio.date(),   # convertimos a date
        fecha_fin=fecha_fin.date(),    
        emocion_predominante=emocion_predominante,
        total_registros=total_registros,
        
        porcentaje_increible=pct("increible"),
        porcentaje_bien=pct("bien"),
        porcentaje_meh=pct("meh"),
        porcentaje_mal=pct("mal"),
        porcentaje_horrible=pct("horrible")
    )

    db.add(estadistica)
    db.commit()
    db.refresh(estadistica)

    return estadistica