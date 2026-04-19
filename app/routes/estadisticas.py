from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database  import get_db
from app.crud import generar_estadisticas
from app.schemas import EstadisticaCreate, EstadisticaResponse

router = APIRouter()

@router.get("/estadisticas/{usuario_id}", response_model=EstadisticaResponse)
def obtener_estadisticas(usuario_id: int, db: Session = Depends(get_db)):
    try:
        return generar_estadisticas(db, usuario_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

