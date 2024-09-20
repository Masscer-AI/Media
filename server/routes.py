from fastapi import APIRouter, File, UploadFile, HTTPException, Request, Depends, Header
from pydantic import BaseModel
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from server.utils.openai_functions import (
    transcribe_audio,
    create_completion_openai,
    async_create_streaming_completion,
    stream_completion,
    generate_speech_stream,
    generate_image,
)
from server.utils.ollama_functions import list_ollama_models

from server.utils.completions import create_completion, get_system_prompt
from database import database, Conversation, Message, Audio, User, Token
from datetime import datetime, timedelta
import os
from sqlalchemy.orm import Session
from database import SessionLocal
from passlib.context import CryptContext
import uuid
from typing import List

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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_token(authorization: str = Header(None), db: Session = Depends(get_db)):
    if authorization is None or not authorization.startswith("Token "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    token_str = authorization.split(" ")[1]
    token = db.query(Token).filter(Token.token == token_str).first()
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    return token


# Definir el modelo de datos para la solicitud de generación de discurso
class SpeechRequest(BaseModel):
    text: str


@router.post("/generate_speech/")
async def generate_speech(request: SpeechRequest):
    output_path = os.path.join(AUDIO_DIR, "output.mp3")
    await generate_speech_stream(request.text, output_path)
    return FileResponse(output_path, media_type="audio/mpeg", filename="output.mp3")


@router.post("/upload-audio/")
async def upload_audio(
    file: UploadFile = File(...), token: Token = Depends(verify_token)
):
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


class Model(BaseModel):
    name: str
    provider: str


class CompletionRequest(BaseModel):
    message: str
    context: str
    model: Model


@router.post("/get_completion/")
async def get_completion(
    request: CompletionRequest,
    token: Token = Depends(verify_token),
    db: Session = Depends(get_db),
):
    system_prompt = get_system_prompt(context=request.context)

    complete_response = ""

    async def event_generator():
        async for chunk in stream_completion(
            system_prompt,
            request.message,
            model=request.model.name,
        ):
            complete_response += chunk
            yield chunk

    
    async with database.transaction():
        # Crear una nueva conversación si no existe
        conversation_query = Conversation.__table__.insert().values(
            user_id=token.user_id
        )  # Include user_id
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
        # assistant_message_query = Message.__table__.insert().values(
        #     conversation_id=conversation_id,
        #     sender="assistant",
        #     text="".join([chunk async for chunk in response_chunks]),
        #     timestamp=datetime.utcnow(),
        # )
        # await database.execute(assistant_message_query)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


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

    token_str = str(uuid.uuid4())
    token = Token(user_id=db_user.id, token=token_str, is_permanent=False)
    db.add(token)
    db.commit()
    db.refresh(token)

    return {"message": "Login successful", "token": token.token}


class ImageRequest(BaseModel):
    prompt: str


@router.post("/generate_image/")
async def generate_image_route(
    request: ImageRequest, token: Token = Depends(verify_token)
):
    image_url = generate_image(request.prompt)
    print(image_url)
    return {"image_url": image_url}


@router.get("/", response_class=HTMLResponse)
async def get_root(request: Request):
    file_path = os.path.join("client", "dist", "index.html")
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            html_content = file.read()

        return HTMLResponse(content=html_content)
    return HTMLResponse(content="Page not found", status_code=404)


@router.get("/get-models")
async def get_models():
    # print("models")
    models = list_ollama_models()
    # print(models)
    return models


class MessageResponse(BaseModel):
    id: int
    content: str


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    message_count: int

    class Config:
        from_attributes = True


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_user_conversations(
    token: Token = Depends(verify_token), db: Session = Depends(get_db)
):
    user_id = token.user_id
    conversations = db.query(Conversation).filter(Conversation.user_id == user_id).all()

    serialized_conversations = []
    for conversation in conversations:
        message_count = len(conversation.messages)
        serialized_conversation = ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            message_count=message_count,
        )
        serialized_conversations.append(serialized_conversation)

    return serialized_conversations


class MessageResponse(BaseModel):
    id: int
    sender: str
    text: str
    timestamp: datetime


class ConversationDetailResponse(BaseModel):
    id: int
    user_id: int
    messages: List[MessageResponse]

    class Config:
        from_attributes = True


@router.get(
    "/conversation/{conversation_id}", response_model=ConversationDetailResponse
)
async def get_conversation(
    conversation_id: int,
    token: Token = Depends(verify_token),
    db: Session = Depends(get_db),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id, Conversation.user_id == token.user_id
        )
        .first()
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = (
        db.query(Message).filter(Message.conversation_id == conversation_id).all()
    )

    return ConversationDetailResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        messages=[
            MessageResponse(
                id=msg.id, sender=msg.sender, text=msg.text, timestamp=msg.timestamp
            )
            for msg in messages
        ],
    )


@router.get("/{page_name}", response_class=HTMLResponse)
async def get_page(request: Request, page_name: str):
    print("RETURNING STATIC")
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
