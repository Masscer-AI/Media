import os
from openai import OpenAI
from dotenv import load_dotenv
import requests
from ..logger import logger

# from pydub import AudioSegment

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def transcribe_audio(audio_file, output_format="verbose_json") -> str:
    transcription = client.audio.transcriptions.create(
        response_format=output_format, model="whisper-1", file=audio_file
    )

    if output_format == "vtt":
        return transcription
    return transcription.text


def create_completion_openai(
    system_prompt: str, user_message: str, model="gpt-4o-mini"
):
    completion = client.chat.completions.create(
        model=model,
        max_tokens=500,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": user_message},
        ],
    )
    return completion.choices[0].message.content


import asyncio

async def create_streaming_completion(
    system_prompt: str, user_message: str, model="gpt-4o-mini"
):
    response = client.chat.completions.create(
        model=model,
        max_tokens=500,
        stream=True,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": user_message},
        ],
    )
    for chunk in response:
        content = chunk.choices[0].delta.content

        print(chunk)
        logger.debug(chunk.choices[0])
        if isinstance(content, str):
            yield content
        else:
            logger.debug(f"The content is not a string is: {content}")



async def stream_completion(prompt, user_message, model="gpt-4o-mini", imageB64=""):
    logger.debug(f"MODEL TO COMPLETE: {model}")
    content = user_message

    if imageB64 != "" and imageB64 is not None:
        if model not in [
            "gpt-4-vision-preview",
            "gpt-4",
            "gpt-4o",
            "gpt-4-turbo",
            "gpt=4o-mini",
        ]:
            model = "gpt-4o"
        logger.info(f"Image detected, using {model} model")

        content = [
            {"type": "text", "text": user_message},
            {"type": "image_url", "image_url": {"url": imageB64}},
        ]

    max_tokens = 4000
    if model == "gpt-4o-mini":
        max_tokens = 10000

    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": content},
        ],
        temperature=0.5,
        stream=True,
    )

    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content



async def async_create_streaming_completion(*args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, create_streaming_completion, *args, **kwargs)

async def generate_speech_stream(
    text: str,
    output_path: str,
    model: str = "tts-1",
    voice: str = "alloy",
    output_format: str = "mp3",
):
    try:
        with open(output_path, "wb") as output_file:
            response = client.audio.speech.create(model=model, voice=voice, input=text)
            response.stream_to_file(output_file.name)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def generate_speech_api(
    text: str, model: str = "tts-1-1106", voice: str = "onyx"
) -> bytes:
    try:
        response = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
            },
            json={
                "model": model,
                "input": text,
                "voice": voice,
            },
        )

        response.raise_for_status()  # Raise an error for bad status codes

        audio = b""
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            audio += chunk

        return audio

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return b""


def generate_image(
    prompt: str,
    model: str = "dall-e-3",
    size: str = "1024x1024",
    quality: str = "standard",
    n: int = 1,
) -> str:
    try:
        response = client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=n,
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        print(e)
        return f"Error generating image: {e}"
