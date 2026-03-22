import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("No GEMINI_API_KEY found in .env")
    exit()

genai.configure(api_key=api_key)

models = []
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            models.append(m.name)
            
    import json
    with open('models.json', 'w') as f:
        json.dump(models, f, indent=2)
    print(f"Saved {len(models)} models to models.json")

except Exception as e:
    with open('models.json', 'w') as f:
        f.write(str(e))
    print(f"Error: {e}")
