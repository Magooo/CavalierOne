try:
    import openai
    print("✅ OpenAI imported successfully version:", openai.__version__)
except ImportError as e:
    print("❌ Failed to import openai:", e)

try:
    import requests
    print("✅ Requests imported successfully version:", requests.__version__)
except ImportError as e:
    print("❌ Failed to import requests:", e)
