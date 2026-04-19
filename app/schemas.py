from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import List, Optional

class UsuarioBase(BaseModel):
    nombre: str
    correo: EmailStr
    carrera: Optional[str] = None
    semestre: Optional[int] = None

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioResponse(UsuarioBase):
    id_usuario: int
    fecha_registro: datetime
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    correo: EmailStr
    password: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UsuarioResponse] = None
    token: Optional[str] = None

class EmocionResponse(BaseModel):
    id_emocion: int
    nombre_emocion: str
    emoji: str
    nivel: int
    
    class Config:
        from_attributes = True

class ActividadResponse(BaseModel):
    id_actividad: int
    nombre_actividad: str
    categoria: str
    icono: str
    
    class Config:
        from_attributes = True

class RegistroEmocionalCreate(BaseModel):
    id_emocion: int
    nota: Optional[str] = None
    actividades: List[int] = []

class RegistroEmocionalResponse(BaseModel):
    id_registro: int
    id_usuario: int
    id_emocion: int
    fecha_registro: datetime
    nota: Optional[str]
    emocion: EmocionResponse
    actividades: List[ActividadResponse] = []
    
    class Config:
        from_attributes = True
        
class EstadisticaBase(BaseModel):
    id_usuario: int
    fecha_inicio: date
    fecha_fin: date

class EstadisticaCreate(EstadisticaBase):
    pass

class EstadisticaResponse(EstadisticaBase):
    id_estadistica: int
    emocion_predominante: str
    total_registros: int
    porcentaje_increible: float
    porcentaje_bien: float
    porcentaje_meh: float
    porcentaje_mal: float
    porcentaje_horrible: float

    class Config:
        from_attributes = True