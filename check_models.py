import os
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

print("--- AVAILABLE MODELS ---")
# This lists every model your API key can talk to
for model in client.models.list():
    print(f"Name: {model.name}")
    print(f"Supported Methods: {model.supported_methods}")
    print("-" * 30)
