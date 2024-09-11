# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from contextlib import asynccontextmanager
from database import database  # Importar desde el nuevo módulo
from server.routes import router  # Importar el router desde el nuevo módulo

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

AUDIO_DIR = "audios"

# Crear el directorio /audios si no existe
os.makedirs(AUDIO_DIR, exist_ok=True)

# Incluir las rutas desde el router
app.include_router(router)

app.mount("/", StaticFiles(directory="client/dist", html=True), name="dist")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
