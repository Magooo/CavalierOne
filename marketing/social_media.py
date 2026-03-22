from utils.prompt_builder import build_marketing_prompt

class SocialMediaPost:
    def __init__(self, platform, raw_content=None, tone="Professional", home_name=None, target_audience=None, land_details=None, inclusions=None, image_path=None):
        self.platform = platform
        self.raw_content = raw_content
        self.tone = tone
        self.home_name = home_name or "General"
        self.target_audience = target_audience or "General Audience"
        self.land_details = land_details
        self.inclusions = inclusions
        self.image_path = image_path
        self.generated_content = None

    def generate_draft(self):
        """
        Generates the prompt for the AI to create the post content.
        In a real system, this would call the LLM API.
        Current behavior: Returns the constructed prompt string.
        """
        if self.raw_content:
            # New "Raw Data" mode
            # We need to manually construct the prompt here or update prompt_builder
            from utils.data_loader import get_style_guide, get_company_info
            
            # Add note about image if present
            img_context = "(An image is attached to this request)" if self.image_path else "(No image provided)"
            
            self.generated_content = f"""
---
## CONTEXT
**Style Guide:**
{get_style_guide()}

**Company Info:**
{get_company_info()}

## USER INPUT (Raw Notes)
**Platform:** {self.platform}
**Tone:** {self.tone}
**Image Context:** {img_context}
**Notes:**
{self.raw_content}

## INSTRUCTION
Write a high-quality social media post based on the raw notes above and the attached image (if any).
Ensure the tone matches the requested style.
## INSTRUCTION
Write a high-quality social media post based on the raw notes above and the attached image (if any).
Ensure the tone matches the requested style.
IMPORTANT: 
1. Return ONLY the post text/caption. Do not include headers like "Here is your post" or "## Facebook Post".
2. Use the exact names and details from the **Company Info** section. Do not hallucinate names (e.g., Use "Jason McHugh", NOT "Jason Hughes").
3. **Strict Fact Check:** Do not invent features or prices not listed in the Raw Notes.
"""
            return self.generated_content

        else:
            # Legacy/Structured Mode
            data = {
                'media_type': f"Social Media Post for {self.platform}",
                'home_name': self.home_name,
                'target_audience': self.target_audience,
                'land_details': self.land_details,
                'inclusions': self.inclusions,
            }
            # Build the prompt using the existing utility
            self.generated_content = build_marketing_prompt(data)
            return self.generated_content

    def generate_content(self, provider="openai"):
        """
        Generates the final post content using the LLMClient.
        """
        # Ensure we have a prompt
        if not self.generated_content:
            self.generate_draft()
        
        from .llm_client import LLMClient
        client = LLMClient(provider=provider)
        
        print(f"Generating content using {provider}...")
        # Pass the image path specifically
        return client.generate_text(self.generated_content, image_path=self.image_path)

    def __repr__(self):
        return f"<SocialMediaPost platform='{self.platform}' home='{self.home_name}'>"
