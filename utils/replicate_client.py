import os
import replicate

def generate_image_controlnet(prompt, image_path, api_token=None):
    """
    Generates an image using ControlNet (Canny Edge) via Replicate.
    
    Args:
        prompt (str): The positive prompt describing the style/materials.
        image_path (str): Path to the source image OR a public https:// URL.
                          Vercel serverless: pass the Supabase public URL.
                          Local dev: pass the local file path.
        api_token (str): Replicate API Token. If None, looks for env var.
        
    Returns:
        str: URL of the generated image.
    """
    if not api_token:
        api_token = os.environ.get("REPLICATE_API_TOKEN")
        
    if not api_token:
        raise ValueError("REPLICATE_API_TOKEN is missing.")

    # Set token for the replicate library
    os.environ["REPLICATE_API_TOKEN"] = api_token

    # Model: black-forest-labs/flux-canny-pro
    # State-of-the-art Canny ControlNet for Flux.1
    model_id = "black-forest-labs/flux-canny-pro"
    
    # PROMPT BOOSTING: FIX "BASIC" LOOK & REMOVE HALLUCINATIONS
    # REMOVED "8k" because Flux was literally writing "8K" on the wall.
    # ADDED "Clean" to discourage text rendering.
    high_quality_prompt = (
        f"Professional Architectural Visualization, High Definition, Photorealistic, "
        f"Cinematic Lighting, Soft Shadows, Hyperdetailed. "
        f"{prompt} "
        f"Minimalist, Modern, Sharp Focus, Clean, No Text, No Annotations, No Dimensions."
    )
    
    print(f"Starting Flux ControlNet generation...")
    print(f"Optimized Prompt: {high_quality_prompt[:100]}...")
    
    # Support both local file paths and public URLs
    # Vercel serverless can't guarantee local file persistence, so we pass a URL
    if image_path.startswith("http://") or image_path.startswith("https://"):
        control_image = image_path  # Pass URL string directly to Replicate
        print(f"[ControlNet] Using public URL: {image_path[:80]}...")
    else:
        control_image = open(image_path, "rb")  # Local dev: open file
        print(f"[ControlNet] Using local file: {image_path}")
    
    try:
        output = replicate.run(
            model_id,
            input={
                "control_image": control_image,
                "prompt": high_quality_prompt,
                "steps": 50,
                "guidance": 12,       # Lower guidance to ignore faint text/dimension lines
                "safety_tolerance": 5,
                "output_format": "jpg"
            }
        )
        
        # Output is a list of URLs or a FileOutput object
        if isinstance(output, list) and len(output) > 0:
            result = output[0]
        else:
            result = output

        # Replicate sometimes returns FileOutput objects — convert to URL string
        return str(result)
            
    except Exception as e:
        print(f"Error calling Replicate: {e}")
        raise e
