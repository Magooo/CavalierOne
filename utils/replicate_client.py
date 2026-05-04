import os
import replicate

def generate_image_controlnet(prompt, image_path, api_token=None, guidance=3.5, control_strength=0.85):
    """
    Generates an image using ControlNet (Canny Edge) via Replicate.
    
    Uses xlabs-ai/flux-dev-controlnet as primary (exposes control_strength for
    tight structural adherence), with black-forest-labs/flux-canny-pro as fallback.
    
    Args:
        prompt (str): The positive prompt describing the style/materials.
        image_path (str): Path to the source image OR a public https:// URL.
        api_token (str): Replicate API Token. If None, looks for env var.
        guidance (float): Prompt guidance scale (1-10 for dev, 1-100 for pro).
        control_strength (float): How tightly to follow the edge map (0-1.0).
                                   Higher = more structurally faithful.
    Returns:
        str: URL of the generated image.
    """
    if not api_token:
        api_token = os.environ.get("REPLICATE_API_TOKEN")
        
    if not api_token:
        raise ValueError("REPLICATE_API_TOKEN is missing.")

    os.environ["REPLICATE_API_TOKEN"] = api_token

    # Structural description FIRST (highest weight in Flux), style after.
    high_quality_prompt = (
        f"{prompt} "
        f"Professional architectural exterior photograph, photorealistic, "
        f"natural lighting, soft shadows. "
        f"No text, no labels, no watermarks, no extra windows."
    )
    
    # Support both local file paths and public URLs
    if image_path.startswith("http://") or image_path.startswith("https://"):
        control_image = image_path
        print(f"[ControlNet] Using public URL: {image_path[:80]}...")
    else:
        control_image = open(image_path, "rb")
        print(f"[ControlNet] Using local file: {image_path}")

    # ── PRIMARY: xlabs-ai/flux-dev-controlnet ──────────────────────────
    # Exposes control_strength for tight structural adherence.
    # control_strength range: 0-3 (0.85 = tight, 1.0 = very tight)
    print(f"[ControlNet] PRIMARY: xlabs flux-dev-controlnet (strength={control_strength}, guidance={guidance})")
    print(f"[ControlNet] Prompt: {high_quality_prompt[:300]}...")
    
    try:
        output = replicate.run(
            "xlabs-ai/flux-dev-controlnet",
            input={
                "control_image": control_image,
                "prompt": high_quality_prompt,
                "control_type": "canny",
                "control_strength": control_strength,
                "guidance_scale": guidance,
                "num_inference_steps": 28,
                "output_format": "jpg",
                "output_quality": 100,
            }
        )
        
        if isinstance(output, list) and len(output) > 0:
            result = output[0]
        else:
            result = output
        return str(result)

    except Exception as dev_err:
        # ── FALLBACK: flux-canny-pro (no control_strength) ─────────────
        print(f"[ControlNet] Dev model failed ({dev_err}), falling back to flux-canny-pro")
        
        # Re-open file handle if needed (consumed by first attempt)
        if not isinstance(control_image, str):
            control_image = open(image_path, "rb") if not image_path.startswith("http") else image_path
        
        try:
            output = replicate.run(
                "black-forest-labs/flux-canny-pro",
                input={
                    "control_image": control_image,
                    "prompt": high_quality_prompt,
                    "steps": 40,
                    "guidance": 25,
                    "safety_tolerance": 5,
                    "output_format": "jpg",
                    "output_quality": 100,
                    "megapixels": "1",
                }
            )
            
            if isinstance(output, list) and len(output) > 0:
                result = output[0]
            else:
                result = output
            return str(result)
            
        except Exception as pro_err:
            print(f"[ControlNet] Both models failed: dev={dev_err}, pro={pro_err}")
            raise pro_err
