import os
import replicate
from dotenv import load_dotenv

load_dotenv()

try:
    model = replicate.models.get("lucataco/sdxl-controlnet")
    latest_version = model.latest_version
    print(f"Latest Version ID: {latest_version.id}")
    with open("version.txt", "w") as f:
        f.write(latest_version.id)
except Exception as e:
    print(f"Error: {e}")
