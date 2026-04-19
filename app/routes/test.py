#esto es solo un codigo para probar la conexion con una api externa 
from fastapi import APIRouter
import requests

router = APIRouter()

@router.get("/test-external")
def test_external():
    try:
        r = requests.get("https://httpbin.org/get", timeout=5)
        return {"status": "ok", "response": r.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}
