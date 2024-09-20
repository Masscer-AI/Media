import anthropic
import base64
import httpx
import os

# Obtener la clave de la API desde una variable de entorno
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise ValueError("La clave de la API no está configurada en la variable de entorno 'ANTHROPIC_API_KEY'")

# Configurar la clave de la API
anthropic_client = anthropic.Anthropic(api_key=api_key)

def make_message_request():
    message = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Hello, Claude"}
        ]
    )
    print(message)
    return message
"""
def make_image_message_request():
    image_url = "https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg"
    image_media_type = "image/jpeg"
    image_data = base64.b64encode(httpx.get(image_url).content).decode("utf-8")

    message = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": image_media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": "¿Qué hay en esta imagen?"
                    }
                ],
            }
        ],
    )
    print(message)

# Llamar a las funciones para probar
make_message_request()
make_image_message_request()
"""