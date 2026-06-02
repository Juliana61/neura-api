from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

router = APIRouter(prefix="/ia", tags=["Inteligencia Artificial"])

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

SYSTEM_PROMPT = """Eres NeuraApp, un asistente emocional empático y profesional 
diseñado para apoyar el bienestar mental de estudiantes universitarios del 
Politécnico Colombiano Jaime Isaza Cadavid.

Tu rol es:
- Escuchar activamente y validar las emociones del usuario sin juzgar
- Ofrecer perspectivas y estrategias de afrontamiento saludables
- Detectar señales de alerta emocional como estrés extremo, tristeza profunda 
  o pensamientos negativos recurrentes, y sugerir buscar apoyo profesional
- Dar recomendaciones personalizadas según el estado emocional expresado
- Mantener siempre un tono cálido, cercano y empático
- Responder en español colombiano de forma natural y conversacional

Importante: No eres un sustituto de atención psicológica profesional. 
Si detectas una posible crisis emocional, orienta al usuario hacia los 
servicios de bienestar universitario del Politécnico Colombiano."""

class ChatRequest(BaseModel):
    mensaje: str

@router.post("/chat")
async def responder_ia(req: ChatRequest):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://neura-api-5s0g.onrender.com",
                    "X-Title": "NeuraApp"
                },
                json={
                    "model": "anthropic/claude-3-haiku",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": req.mensaje}
                    ],
                    "max_tokens": 1024
                },
                timeout=30.0
            )
            data = response.json()

            if "choices" not in data:
                print(f"Respuesta inesperada: {data}")
                raise HTTPException(status_code=500, detail="Respuesta inválida del modelo")

            return {"respuesta": data["choices"][0]["message"]["content"]}

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="El modelo tardó demasiado en responder")
    except Exception as e:
        print(f"Error en OpenRouter: {e}")
        raise HTTPException(status_code=500, detail=f"Error del servidor IA: {str(e)}")