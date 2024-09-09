import os

from openai import OpenAI
from dotenv import load_dotenv
import requests


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


# def translate_transcription(transcription: str, target_language="English"):
#     completion = client.chat.completions.create(
#         model="gpt-4-vision-preview",
#         max_tokens=2000,
#         messages=[
#             {
#                 "role": "system",
#                 "content": f"You are translator and video editor. You will receive a transcription of a video. Your task is to provide the {target_language} version with the same meaning. The resulting script should be coherent and consistent. Make sure of correcting inconsistencies, keep in mind that the video is a tutorial of an coding exercise of Learnpack, a tool to learn coding skills",
#             },
#             {"role": "user", "content": transcription},
#         ],
#     )
#     return completion.choices[0].message.content


def create_completion_openai(system_prompt: str, user_message: str):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=200,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": user_message},
        ],
    )
    return completion.choices[0].message.content


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
