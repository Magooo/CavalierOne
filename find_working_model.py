import google.generativeai as genai
import os
import sys
import time

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

candidates = [
    'models/gemini-1.5-flash',
    'models/gemini-1.5-flash-001',
    'models/gemini-1.5-flash-002',
    'models/gemini-1.5-flash-8b',
    'models/gemini-1.5-pro',
    'models/gemini-1.5-pro-001',
    'models/gemini-pro',
    'models/gemini-1.0-pro',
    'models/gemini-2.0-flash'
]

with open("model_log.txt", "w") as log:
    log.write("--- MODEL CHECK LOG ---\n")
    for model_name in candidates:
        print(f"Testing: {model_name} ...")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hi")
            log.write(f"{model_name}: SUCCESS\n")
            print(f"SUCCESS: {model_name}")
            break
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg:
                log.write(f"{model_name}: FAILED (404)\n")
            elif "429" in error_msg:
                log.write(f"{model_name}: FAILED (429)\n")
            else:
                log.write(f"{model_name}: FAILED ({error_msg[:50]}...)\n")
            time.sleep(1)
    log.write("--- END LOG ---\n")
