import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

print("Uploading file to Gemini...")
media_file = genai.upload_file(path="WhatsApp Audio 2026-09-07 at 1.37.20 PM.mp4")
print(f"File uploaded successfully: {media_file.uri}")

model = genai.GenerativeModel("gemini-1.5-flash")

print("Requesting transcription...")
response = model.generate_content([
    media_file,
    "Transcribe exactly what is being said in this audio file. If there are multiple speakers, indicate them. Output ONLY the transcription."
])

with open("whatsapp_transcript.txt", "w", encoding="utf-8") as f:
    f.write(response.text)

print("Transcription saved to whatsapp_transcript.txt")
