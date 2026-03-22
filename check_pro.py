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
genai.configure(api_key=api_key)

print("Checking models/gemini-1.5-pro ...")
try:
    model = genai.GenerativeModel('models/gemini-1.5-pro')
    response = model.generate_content("Hi")
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
