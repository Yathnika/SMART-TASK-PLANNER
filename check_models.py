# check_models.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

try:
    print("Fetching models...")
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"- {model.name}")
    print("\nFinished.")

except Exception as e:
    print(f"An error occurred: {e}")