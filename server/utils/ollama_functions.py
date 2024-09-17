from openai import OpenAI
import requests


def create_completion_ollama(system_prompt, user_message, model="llama3.1"):
    client = OpenAI(base_url="http://localhost:11434/v1", api_key="llama3")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=1000,
    )
    return response.choices[0].message.content


def list_ollama_models():
    url = "http://localhost:11434/api/tags"
    response = requests.get(url)

    if response.status_code == 200:
        models = response.json().get("models", [])
        return models
    else:
        return []


if __name__ == "__main__":
    models = list_ollama_models()
    print(models)
    # answer = create_completion_ollama("hello worl")
