import os
import replicate

def generate_image_controlnet(prompt, image_path, api_token=None):
    """
    Generates an image using ControlNet (Canny Edge) via Replicate.
    
    Args:
        prompt (str): The positive prompt describing the style/materials.
        image_path (str): Path to the source image (elevation).
        api_token (str): Replicate API Token. If None, looks for env var.
        
    Returns:
        str: URL of the generated image.
    """
    if not api_token:
        api_token = os.environ.get("REPLICATE_API_TOKEN")
        
    if not api_token:
        raise ValueError("REPLICATE_API_TOKEN is missing.")

    # Model: black-forest-labs/flux-canny-pro
    # State-of-the-art Canny ControlNet for Flux.1
    model_id = "black-forest-labs/flux-canny-pro"
    
    # REVERT: DISABLE "SPECKLE REMOVAL" (It destroyed the image)
    # We go back to raw input which had the correct structure.
    # from utils.image_processor import enhance_lines_for_controlnet
    # processed_image_path = enhance_lines_for_controlnet(image_path)
    
    # PROMPT BOOSTING: FIX "BASIC" LOOK & REMOVE HALLUCINATIONS
    # REMOVED "8k" because Flux was literally writing "8K" on the wall.
    # ADDED "Clean" to discourage text rendering.
    high_quality_prompt = f"Professional Architectural Visualization, High Definition, Photorealistic, Cinematic Lighting, Soft Shadows, Unreal Engine 5 Render, Hyperdetailed. {prompt} . Minimalist, Modern, Sharp Focus, Clean, No Text."
    
    print(f"Starting Flux ControlNet generation...")
    print(f"Optimized Prompt: {high_quality_prompt[:100]}...")
    
    try:
        output = replicate.run(
            model_id,
            input={
                "control_image": open(image_path, "rb"), # Send RAW image (Structure Safe)
                "prompt": high_quality_prompt,
                "steps": 50,         
                "guidance": 12,      # LOWER GUIDANCE (18->12) to ignore faint text lines
                "safety_tolerance": 5, 
                "output_format": "jpg"
            }
        )
        
        # Output is a list of URLs
        if isinstance(output, list) and len(output) > 0:
            return output[0]
        else:
            return str(output)
            
    except Exception as e:
        print(f"Error calling Replicate: {e}")
        raise e
