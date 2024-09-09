from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.responses import FileResponse
from server.utils.openai_functions import (
    transcribe_audio,
    create_completion_openai,
    generate_speech_stream,
)

import uvicorn
import os


def get_system_prompt(context: str):
    SYSTEM_PROMPT = f"""
You are an useful conversational assistant. You answers must be as shorter as you can to avoid too much time while generating answers. You must keep in mind that your answer will be spoken by another AI model. Keep it simple and useful.

These are previous message between you and the user:
---
{context}
---

Continue the conversation naturally
"""
    return SYSTEM_PROMPT


app = FastAPI()

SUPPORTED_FORMATS = {
    "flac",
    "m4a",
    "mp3",
    "mp4",
    "mpeg",
    "mpga",
    "oga",
    "ogg",
    "wav",
    "webm",
}
AUDIO_DIR = "audios"

# Crear el directorio /audios si no existe
os.makedirs(AUDIO_DIR, exist_ok=True)


# Definir el modelo de datos para la solicitud de generación de discurso
class SpeechRequest(BaseModel):
    text: str


@app.post("/generate_speech/")
async def generate_speech(request: SpeechRequest):
    output_path = os.path.join(AUDIO_DIR, "output.mp3")
    await generate_speech_stream(request.text, output_path)
    return FileResponse(output_path, media_type="audio/mpeg", filename="output.mp3")


@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    if file.content_type.split("/")[1] not in SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    audio_file_path = os.path.join(AUDIO_DIR, file.filename)
    with open(audio_file_path, "wb") as audio_file:
        while contents := await file.read(1024):
            audio_file.write(contents)

    with open(audio_file_path, "rb") as audio_file:
        transcription = transcribe_audio(audio_file)

    return {
        "file_size": os.path.getsize(audio_file_path),
        "transcription": transcription,
    }


class CompletionRequest(BaseModel):
    message: str
    context: str


@app.post("/get_completion/")
async def get_completion(request: CompletionRequest):
    response = create_completion_openai(get_system_prompt(context=request.context), request.message)
    return {"response": response}


app.mount("/", StaticFiles(directory="client/dist", html=True), name="dist")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
