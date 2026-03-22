import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Use the most recent upload if available, or error
upload_dir = os.path.join("resources", "uploads")
files = [os.path.join(upload_dir, f) for f in os.listdir(upload_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
if not files:
    print("No images found in uploads to test.")
    exit()

latest_file = max(files, key=os.path.getctime)
print(f"Testing variation on: {latest_file}")

try:
    response = client.images.create_variation(
        image=open(latest_file, "rb"),
        n=1,
        size="1024x1024"
    )
    print("Variation URL:", response.data[0].url)
except Exception as e:
    print("Variation Error:", e)
