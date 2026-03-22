import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found")
else:
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello")
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Error with 'gemini-1.5-flash': {e}")
        
    try:
        model2 = genai.GenerativeModel('models/gemini-1.5-flash')
        response2 = model2.generate_content("Hello from models/ prefix")
        print(f"Success with 'models/' prefix! Response: {response2.text}")
    except Exception as e:
        print(f"Error with 'models/gemini-1.5-flash': {e}")
