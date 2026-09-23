import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents="Hello"
    )
    print("gemini-3.6-flash works!")
except Exception as e:
    print(f"gemini-3.6-flash failed: {e}")

try:
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents="Hello"
    )
    print("gemini-1.5-flash works!")
except Exception as e:
    print(f"gemini-1.5-flash failed: {e}")
