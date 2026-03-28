import requests
import json

class LLMService:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        self.base_url = base_url
        self.model = model

    def generate_response(self, prompt: str, context: str = "") -> str:
        full_prompt = f"""You are an AI Money Mentor, a professional financial advisor assistant.
Your goal is to help users manage their finances, analyze spending, and plan budgets.
Be clear, practical, and structured in your advice.

Context from user documents:
{context}

User Query:
{prompt}

AI Money Mentor:"""

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False
        }

        try:
            response = requests.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            return response.json().get("response", "I'm sorry, I couldn't generate a response.")
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return f"Error: Could not connect to local LLM (Ollama). Please ensure Ollama is running with the '{self.model}' model. {str(e)}"
