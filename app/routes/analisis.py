from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app import models
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter(prefix="/analisis", tags=["Análisis Emocional"])
client = anthropic.Anthropic(api_key=os.getenv("GEMINI_API_KEY"))

ANALISIS_PROMPT = """Eres un sistema experto en análisis emocional para estudiantes universitarios.
Analiza el siguiente registro emocional y responde ÚNICAMENTE en este formato JSON exacto:

{
  "nivel_bienestar": <número del 1 al 10>,
  "sentimientos_detectados": ["sentimiento1", "sentimiento2"],
  "señal_alerta": <true o false>,
  "tipo_alerta": "<ninguna | estrés_academico | tristeza | ansiedad | crisis>",
  "retroalimentacion": "<mensaje empático de 2-3 oraciones dirigido al usuario>",
  "recomendaciones": ["recomendación1", "recomendación2", "recomendación3"]
}

No agregues nada fuera del JSON."""

class AnalisisRequest(BaseModel):
    nota: str
    emocion: str
    actividad: str

@router.post("/registrar")
def analizar_registro(req: AnalisisRequest, db: Session = Depends(get_db)):
    try:
        prompt_usuario = f"""
Emoción registrada: {req.emocion}
Actividad realizada: {req.actividad}
Nota del usuario: "{req.nota}"
"""
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=ANALISIS_PROMPT,
            messages=[{"role": "user", "content": prompt_usuario}]
        )

        import json
        texto = message.content[0].text.strip()
        resultado = json.loads(texto)
        return resultado

    except Exception as e:
        print(f"Error en análisis: {e}")
        raise HTTPException(status_code=500, detail=f"Error al analizar: {e}")