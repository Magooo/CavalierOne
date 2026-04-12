import os
import time

class LLMClient:
    def __init__(self, provider="openai"):
        self.provider = provider.lower()
        self.api_key = self._get_api_key()
        
    def _get_env_override(self, key):
        try:
            from flask import has_request_context, session
            if has_request_context() and 'user_env' in session:
                val = session['user_env'].get(key)
                if val:
                    return val
        except ImportError:
            pass
        return os.environ.get(key)

    def _get_api_key(self):
        """Retrieves API key from environment variables based on provider."""
        if self.provider == "gemini":
            return self._get_env_override("GEMINI_API_KEY")
        elif self.provider == "openai":
            return self._get_env_override("OPENAI_API_KEY")
        return None

    def generate_text(self, prompt, image_path=None, max_tokens=None):
        """
        Generates text based on the prompt. 
        If no API key is set, returns a simulated response for testing.
        max_tokens: optional ceiling for response length (defaults to provider default if None)
        """
        if not self.api_key:
            print(f"[{self.provider.upper()}] No API Key found. Returning mock response.")
            return self._mock_response(prompt)

        try:
            if self.provider == "gemini":
                return self._call_gemini(prompt, image_path, max_tokens=max_tokens)
            elif self.provider == "openai":
                return self._call_openai(prompt, image_path, max_tokens=max_tokens)
            else:
                return "Error: Unsupported provider."
        except Exception as e:
            return f"Error calling AI provider: {str(e)}"

    def _mock_response(self, prompt):
        """Simulates an AI response when no key is present."""
        time.sleep(1.5) # Simulate network delay
        return f"""
# [MOCK] AI Generated Content
**Platform:** Social Media
**Status:** Draft

Here is a suggestion based on your prompt:

"Check out this amazing new home design! 🏡✨
Perfect for modern families, featuring open-plan living and luxury inclusions.
#NewHome #Design #CavalierHomes"

*(To get real AI responses, please configure your API Key in the .env file)*
"""

    def generate_image(self, prompt, size="1024x1024", quality="standard"):
        """
        Generates an image using OpenAI's DALL-E 3.
        Returns the URL of the generated image.
        """
        if not self.api_key:
            print(f"[{self.provider.upper()}] No API Key found. Returning mock image.")
            return "https://via.placeholder.com/1024x1024.png?text=Mock+AI+Render"

        try:
            if self.provider == "openai" or self.provider == "gemini": 
                # Gemini doesn't have a simple public image gen API in the same SDK yet usually, 
                # so we default to OpenAI for image gen even if provider is Gemini, 
                # assuming OPENAI_API_KEY is present or we fallback.
                
                # Check for OpenAI Key explicitly if current provider is not OpenAI
                if self.provider != "openai":
                    if self._get_env_override("OPENAI_API_KEY"):
                        # Switch to OpenAI context just for this call
                        from openai import OpenAI
                        client = OpenAI(api_key=self._get_env_override("OPENAI_API_KEY"))
                    else:
                        return "Error: Image generation requires OPENAI_API_KEY (DALL-E 3)."
                else:
                    from openai import OpenAI
                    client = OpenAI(api_key=self.api_key)

                response = client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size=size,
                    quality=quality,
                    style="natural", # Use 'natural' for realistic photos, 'vivid' for hyper-real/artistic
                    n=1,
                )
                return response.data[0].url
            else:
                return "Error: Unsupported provider for image generation."
        except Exception as e:
            return f"Image Gen Error: {str(e)}"

    def vary_image(self, image_path, size="1024x1024"):
        """
        Generates a variation of the input image using DALL-E 2.
        Useful for preserving strict geometry.
        """
        if not self.api_key:
             return "https://via.placeholder.com/1024x1024.png?text=Mock+Variation"
             
        try:
             # Ensure we use an OpenAI client found from environment
             # (Self-repairing logic from generate_image)
             from openai import OpenAI
             api_key = self._get_env_override("OPENAI_API_KEY") or self.api_key
             client = OpenAI(api_key=api_key)
             
             # Image must be a valid PNG, 4MB max, square.
             # We assume input is handled/cropped by app.py or is valid enough for now.
             # (A robust implementation would resize/crop here).
             
             response = client.images.create_variation(
                 image=open(image_path, "rb"),
                 n=1,
                 size=size
             )
             return response.data[0].url
             
        except Exception as e:
             return f"Variation Error: {str(e)}"

    def _call_gemini(self, prompt, image_path=None, max_tokens=None):
        """Real call to Google Gemini API."""
        # Requires: pip install google-generativeai
        try:
            import google.generativeai as genai
            from PIL import Image
            
            genai.configure(api_key=self.api_key)
            # Use 'models/gemini-2.0-flash' as it is a confirmed available model
            generation_config = {}
            if max_tokens:
                generation_config['max_output_tokens'] = max_tokens
            model = genai.GenerativeModel('models/gemini-2.0-flash', generation_config=generation_config if generation_config else None)
            
            content = [prompt]
            if image_path and os.path.exists(image_path):
                img = Image.open(image_path).convert('RGB')
                content.append(img)
                print(f"Attached image to Gemini request: {image_path}")
                
            response = model.generate_content(content)
            return response.text
        except ImportError:
            return "Error: `google-generativeai` library not installed. Run `pip install google-generativeai`."
        except Exception as e:
            return f"Gemini API Error: {str(e)}"

    def _call_openai(self, prompt, image_path=None, max_tokens=None):
        """Real call to OpenAI API (supports Vision)."""
        # Requires: pip install openai
        try:
            import base64
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            messages = []
            
            if image_path and os.path.exists(image_path):
                # Encode image
                with open(image_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                })
            else:
                 messages.append({"role": "user", "content": prompt})

            api_kwargs = {
                "model": "gpt-4o",  # Use GPT-4o for best vision/text performance
                "messages": messages,
            }
            if max_tokens:
                api_kwargs["max_tokens"] = max_tokens

            response = client.chat.completions.create(**api_kwargs)
            return response.choices[0].message.content
        except ImportError:
            return "Error: `openai` library not installed. Run `pip install openai`."
        except Exception as e:
            return f"OpenAI API Error: {str(e)}"
