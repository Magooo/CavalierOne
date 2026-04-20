"""
kie_client.py — CavalierOne wrapper for the kie.ai Market API.

kie.ai is a unified AI API marketplace providing access to premium image, video,
and music generation models via a single API key and credit-based pricing.

Docs: https://docs.kie.ai/market/quickstart
Auth: Bearer token (KIE_API_KEY from .env)

All generation calls are asynchronous (task-based):
  1. POST to submit → get task_id
  2. GET /task/{task_id} → poll until status == "succeed" or "failed"
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

KIE_BASE_URL = "https://api.kie.ai/v1"
KIE_API_KEY = os.environ.get("KIE_API_KEY", "")

# Default polling config
POLL_INTERVAL_SECONDS = 3
MAX_WAIT_SECONDS = 120


def _headers():
    """Return authorisation headers for kie.ai requests."""
    if not KIE_API_KEY:
        raise RuntimeError(
            "KIE_API_KEY is not set. Add it to your .env file.\n"
            "Get your key at: https://kie.ai/api-key"
        )
    return {
        "Authorization": f"Bearer {KIE_API_KEY}",
        "Content-Type": "application/json",
    }


def _poll_task(task_id: str, max_wait: int = MAX_WAIT_SECONDS) -> dict:
    """
    Poll the kie.ai task endpoint until the task completes or times out.

    Returns the completed task payload (dict).
    Raises RuntimeError on failure or timeout.
    """
    url = f"{KIE_BASE_URL}/task/{task_id}"
    elapsed = 0

    while elapsed < max_wait:
        resp = requests.get(url, headers=_headers(), timeout=30)
        resp.raise_for_status()
        data = resp.json()

        status = data.get("data", {}).get("status") or data.get("status", "")

        if status in ("succeed", "success", "completed", "done"):
            return data

        if status in ("failed", "error"):
            error_msg = data.get("data", {}).get("error_message") or data.get("message", "Unknown error")
            raise RuntimeError(f"kie.ai task {task_id} failed: {error_msg}")

        time.sleep(POLL_INTERVAL_SECONDS)
        elapsed += POLL_INTERVAL_SECONDS

    raise TimeoutError(f"kie.ai task {task_id} timed out after {max_wait}s")


def generate_image(
    prompt: str,
    model: str = "flux-2-flex-text-to-image",
    width: int = 1024,
    height: int = 768,
    n: int = 1,
    negative_prompt: str = "",
    max_wait: int = MAX_WAIT_SECONDS,
) -> list[str]:
    """
    Generate image(s) using a kie.ai Market model.

    Args:
        prompt:          The generation prompt.
        model:           kie.ai model slug. Defaults to Flux-2 Flex (fast & affordable).
                         Other options: "flux-2-pro-text-to-image", "google-nano-banana-2",
                         "ideogram-v3-text-to-image", "gpt-image-1-5-text-to-image"
        width:           Image width in pixels (default 1024).
        height:          Image height in pixels (default 768).
        n:               Number of images to generate (default 1).
        negative_prompt: Things to avoid in the image.
        max_wait:        Max seconds to wait for generation (default 120).

    Returns:
        List of image URLs (CDN hosted by kie.ai).
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "width": width,
        "height": height,
        "n": n,
    }
    if negative_prompt:
        payload["negative_prompt"] = negative_prompt

    resp = requests.post(
        f"{KIE_BASE_URL}/images/generations",
        headers=_headers(),
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    # Extract task_id — kie.ai returns it in data.task_id or task_id
    task_id = (
        data.get("data", {}).get("task_id")
        or data.get("task_id")
        or data.get("data", {}).get("taskId")
    )

    if not task_id:
        raise RuntimeError(f"kie.ai did not return a task_id. Response: {data}")

    result = _poll_task(task_id, max_wait=max_wait)

    # Extract image URLs from the result
    images_data = (
        result.get("data", {}).get("output", {}).get("images")
        or result.get("data", {}).get("images")
        or result.get("output", {}).get("images")
        or []
    )

    urls = []
    for img in images_data:
        if isinstance(img, str):
            urls.append(img)
        elif isinstance(img, dict):
            urls.append(img.get("url") or img.get("image_url") or "")

    if not urls:
        raise RuntimeError(f"kie.ai completed but returned no image URLs. Full response: {result}")

    return [u for u in urls if u]  # filter empty strings


def remove_background(image_url: str, max_wait: int = 60) -> str:
    """
    Remove the background from an image using Recraft via kie.ai.

    Args:
        image_url: URL of the source image.
        max_wait:  Max seconds to wait (default 60).

    Returns:
        URL of the background-removed image.
    """
    payload = {
        "model": "recraft-remove-background",
        "image_url": image_url,
    }
    resp = requests.post(
        f"{KIE_BASE_URL}/images/edit",
        headers=_headers(),
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    task_id = data.get("data", {}).get("task_id") or data.get("task_id")
    if not task_id:
        raise RuntimeError(f"kie.ai remove_background: no task_id. Response: {data}")

    result = _poll_task(task_id, max_wait=max_wait)

    output_url = (
        result.get("data", {}).get("output", {}).get("image_url")
        or result.get("data", {}).get("image_url")
        or result.get("output", {}).get("image_url")
    )

    if not output_url:
        raise RuntimeError(f"remove_background completed but returned no URL. Response: {result}")

    return output_url


def upscale_image(image_url: str, scale: int = 2, max_wait: int = 120) -> str:
    """
    Upscale an image using Topaz via kie.ai.

    Args:
        image_url: URL of the source image.
        scale:     Upscale factor (2 or 4, default 2).
        max_wait:  Max seconds to wait (default 120).

    Returns:
        URL of the upscaled image.
    """
    payload = {
        "model": "topaz-image-upscale",
        "image_url": image_url,
        "scale": scale,
    }
    resp = requests.post(
        f"{KIE_BASE_URL}/images/upscale",
        headers=_headers(),
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    task_id = data.get("data", {}).get("task_id") or data.get("task_id")
    if not task_id:
        raise RuntimeError(f"kie.ai upscale_image: no task_id. Response: {data}")

    result = _poll_task(task_id, max_wait=max_wait)

    output_url = (
        result.get("data", {}).get("output", {}).get("image_url")
        or result.get("data", {}).get("image_url")
        or result.get("output", {}).get("image_url")
    )

    if not output_url:
        raise RuntimeError(f"upscale_image completed but returned no URL. Response: {result}")

    return output_url


def get_available_image_models() -> list[str]:
    """
    Returns a list of recommended kie.ai image model slugs for CavalierOne.
    These are all available via the Market API.
    """
    return [
        # Fast & affordable — good for iteration
        "flux-2-flex-text-to-image",         # Flux-2 Flex (default)
        "google-nano-banana-2",              # Google Nano Banana 2 (very fast)

        # High quality — best for final assets
        "flux-2-pro-text-to-image",          # Flux-2 Pro
        "ideogram-v3-text-to-image",         # Ideogram V3 (great with text)
        "gpt-image-1-5-text-to-image",       # GPT-Image-1.5

        # Editing / image-to-image
        "flux-2-flex-image-to-image",        # Flux-2 Flex img2img
        "flux-2-pro-image-to-image",         # Flux-2 Pro img2img
    ]
