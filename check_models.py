import google.generativeai as genai
import os
import sys

# Load env safely
env_path = os.path.join(os.getcwd(), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k] = v.strip('"\'')

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("API Key missing")
    sys.exit(1)

genai.configure(api_key=api_key)

try:
    print("--- AVAILABLE MODELS ---")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Name: {m.name} | Display: {m.display_name}")
    print("------------------------")
except Exception as e:
    print(f"Error: {e}")
