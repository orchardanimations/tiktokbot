import os
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

print("--- AVAILABLE MODELS ---")
for model in client.models.list():
    # Changed 'supported_methods' to 'supported_actions'
    print(f"Name: {model.name}")
    print(f"Actions: {model.supported_actions}")
    print("-" * 30)
