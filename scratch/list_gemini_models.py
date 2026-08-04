import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("--- ALL MODELS ---")
for m in genai.list_models():
    print(f"Name: {m.name}, Supported Methods: {m.supported_generation_methods}")
