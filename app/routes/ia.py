from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

router = APIRouter(prefix="/ia", tags=["Inteligencia Artificial"])

# Inicializar Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class ChatRequest(BaseModel):
    mensaje: str

@router.post("/chat")
def responder_ia(req: ChatRequest):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")

        response = model.generate_content(req.mensaje)

        return {"respuesta": response.text}
    
    except Exception as e:
        print(f"🔴 Error en Gemini: {e}")
        raise HTTPException(status_code=500, detail=f"Error del servidor IA: {e}")
