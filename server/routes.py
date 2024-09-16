from fastapi import APIRouter, File, UploadFile, HTTPException, Request, Depends
from pydantic import BaseModel
from fastapi.responses import FileResponse, HTMLResponse
from server.utils.openai_functions import (
    transcribe_audio,
    create_completion_openai,
    generate_speech_stream,
    generate_image,  # Import the generate_image function
)
from database import database, Conversation, Message, Audio, User
from datetime import datetime
import os
from sqlalchemy.orm import Session
from database import SessionLocal
from passlib.context import CryptContext

router = APIRouter()

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

# Cambiar bcrypt por argon2
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Definir el modelo de datos para la solicitud de generación de discurso
class SpeechRequest(BaseModel):
    text: str


@router.post("/generate_speech/")
async def generate_speech(request: SpeechRequest):
    output_path = os.path.join(AUDIO_DIR, "output.mp3")
    await generate_speech_stream(request.text, output_path)
    return FileResponse(output_path, media_type="audio/mpeg", filename="output.mp3")


@router.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    if file.content_type.split("/")[1] not in SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    audio_file_path = os.path.join(AUDIO_DIR, file.filename)
    with open(audio_file_path, "wb") as audio_file:
        while contents := await file.read(1024):
            audio_file.write(contents)

    with open(audio_file_path, "rb") as audio_file:
        transcription = transcribe_audio(audio_file)

    # Guardar en la base de datos
    async with database.transaction():
        query = Audio.__table__.insert().values(
            filename=file.filename, transcription=transcription
        )
        await database.execute(query)

    return {
        "file_size": os.path.getsize(audio_file_path),
        "transcription": transcription,
    }


class CompletionRequest(BaseModel):
    message: str
    context: str


@router.post("/get_completion/")
async def get_completion(request: CompletionRequest):
    response = create_completion_openai(
        get_system_prompt(context=request.context), request.message
    )

    # Guardar en la base de datos
    async with database.transaction():
        # Crear una nueva conversación si no existe
        conversation_query = Conversation.__table__.insert().values()
        conversation_id = await database.execute(conversation_query)

        # Guardar el mensaje del usuario
        user_message_query = Message.__table__.insert().values(
            conversation_id=conversation_id,
            sender="user",
            text=request.message,
            timestamp=datetime.utcnow(),
        )
        await database.execute(user_message_query)

        # Guardar la respuesta del asistente
        assistant_message_query = Message.__table__.insert().values(
            conversation_id=conversation_id,
            sender="assistant",
            text=response,
            timestamp=datetime.utcnow(),
        )
        await database.execute(assistant_message_query)

    return {"response": response}


class UserLogin(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


@router.post("/signup/")
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully"}


@router.post("/login/")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    return {"message": "Login successful"}


class ImageRequest(BaseModel):
    prompt: str


@router.post("/generate_image/")
async def generate_image_route(request: ImageRequest):
    image_url = generate_image(request.prompt)
    return {"image_url": image_url}


@router.get("/", response_class=HTMLResponse)
async def get_root(request: Request):
    file_path = os.path.join("client", "dist", "index.html")
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            html_content = file.read()

        # Get the data for the page or use defaults if the page_name is not found
        # data = routes_meta["defaults"]

        # Replace placeholders in the HTML content with actual data
        # for key, value in data.items():

        #     placeholder = f"{{{{{key}}}}}"
        #     html_content = html_content.replace(placeholder, value)

        return HTMLResponse(content=html_content)
    return HTMLResponse(content="Page not found", status_code=404)


@router.get("/{page_name}", response_class=HTMLResponse)
async def get_page(request: Request, page_name: str):
    file_path = os.path.join("client", "dist", "index.html")
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            html_content = file.read()
        # data = routes_meta.get(page_name, routes_meta["defaults"])

        # for key, value in data.items():
        #     placeholder = f"{{{{{key}}}}}"
        #     html_content = html_content.replace(placeholder, value)

        return HTMLResponse(content=html_content)
    return HTMLResponse(content="Page not found", status_code=404)
