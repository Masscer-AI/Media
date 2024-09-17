from .ollama_functions import create_completion_ollama
from .openai_functions import create_completion_openai


def create_completion(provider: str, model: str, system_prompt: str, user_message: str):
    print("Generating completion with ", provider)

    if provider == "openai":
        res = create_completion_openai(system_prompt, user_message, model=model)

    if provider == "ollama":
        res = create_completion_ollama(system_prompt, user_message, model=model)

    return res




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
