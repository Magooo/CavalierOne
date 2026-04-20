"""
kie_client.py — CavalierOne wrapper for the kie.ai Market API.

Docs: https://docs.kie.ai/market/quickstart
Auth: Bearer token (KIE_API_KEY from .env)

All generation calls are asynchronous (task-based):
  1. POST https://api.kie.ai/api/v1/jobs/createTask  → get taskId
  2. GET  https://api.kie.ai/api/v1/jobs/taskDetail?taskId=<id>
         → poll until status == "succeed" / "success" / "completed"

The model slug format is e.g. "flux-2/flex-text-to-image" (slash, not dash).
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

KIE_BASE_URL = "https://api.kie.ai/api/v1"
KIE_API_KEY = os.environ.get("KIE_API_KEY", "")

# Default polling config
POLL_INTERVAL_SECONDS = 5
MAX_WAIT_SECONDS = 180


def _headers() -> dict:
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
    Poll GET /api/v1/jobs/taskDetail?taskId=<id> until done or timeout.

    Returns the full response dict on success.
    Raises RuntimeError on failure or TimeoutError on timeout.
    """
    url = f"{KIE_BASE_URL}/jobs/taskDetail"
    elapsed = 0

    while elapsed < max_wait:
        resp = requests.get(
            url,
            headers=_headers(),
            params={"taskId": task_id},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        # KIE.ai wraps everything in {"code": 200, "data": {...}}
        inner = data.get("data") or {}
        status = (
            inner.get("status")
            or inner.get("taskStatus")
            or data.get("status", "")
        )

        if str(status).lower() in ("succeed", "success", "completed", "done", "finish", "finished"):
            return data

        if str(status).lower() in ("failed", "error", "fail"):
            err = (
                inner.get("errorMessage")
                or inner.get("error_message")
                or data.get("msg", "Unknown error")
            )
            raise RuntimeError(f"kie.ai task {task_id} failed: {err}")

        time.sleep(POLL_INTERVAL_SECONDS)
        elapsed += POLL_INTERVAL_SECONDS

    raise TimeoutError(f"kie.ai task {task_id} timed out after {max_wait}s")


def _extract_image_urls(result: dict) -> list[str]:
    """
    Extract image URLs from a completed task result.
    KIE.ai nests output differently per model — try all known paths.
    """
    inner = result.get("data") or {}

    candidates = [
        inner.get("output"),           # may be a list of URLs or a dict
        inner.get("images"),
        inner.get("imageUrls"),
        inner.get("image_urls"),
    ]

    urls = []
    for candidate in candidates:
        if candidate is None:
            continue
        if isinstance(candidate, str) and candidate.startswith("http"):
            urls.append(candidate)
            break
        if isinstance(candidate, list):
            for item in candidate:
                if isinstance(item, str) and item.startswith("http"):
                    urls.append(item)
                elif isinstance(item, dict):
                    url = item.get("url") or item.get("image_url") or item.get("imageUrl", "")
                    if url:
                        urls.append(url)
            if urls:
                break
        if isinstance(candidate, dict):
            url = (
                candidate.get("url")
                or candidate.get("image_url")
                or candidate.get("imageUrl")
            )
            if url:
                urls.append(url)
                break

    return [u for u in urls if u]


def generate_image(
    prompt: str,
    model: str = "flux-2/flex-text-to-image",
    aspect_ratio: str = "16:9",
    resolution: str = "1K",
    negative_prompt: str = "",
    max_wait: int = MAX_WAIT_SECONDS,
) -> list[str]:
    """
    Generate image(s) using a kie.ai Market model.

    Args:
        prompt:          The generation prompt.
        model:           kie.ai model slug (slash format, e.g. "flux-2/flex-text-to-image").
        aspect_ratio:    "1:1" | "16:9" | "9:16" | "4:3" etc.
        resolution:      "1K" | "2K" | "4K"
        negative_prompt: Things to avoid in the image.
        max_wait:        Max seconds to wait for generation.

    Returns:
        List of image URLs (CDN hosted by kie.ai).
    """
    payload = {
        "model": model,
        "input": {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "nsfw_checker": False,
        },
    }
    if negative_prompt:
        payload["input"]["negative_prompt"] = negative_prompt

    resp = requests.post(
        f"{KIE_BASE_URL}/jobs/createTask",
        headers=_headers(),
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    # Extract taskId — KIE.ai returns {"code":200, "data":{"taskId":"..."}}
    task_id = (
        (data.get("data") or {}).get("taskId")
        or (data.get("data") or {}).get("task_id")
        or data.get("taskId")
    )

    if not task_id:
        raise RuntimeError(f"kie.ai did not return a taskId. Response: {data}")

    result = _poll_task(task_id, max_wait=max_wait)
    urls = _extract_image_urls(result)

    if not urls:
        raise RuntimeError(
            f"kie.ai completed but returned no image URLs. Full response: {result}"
        )

    return urls


def remove_background(image_url: str, max_wait: int = 60) -> str:
    """Remove background from an image using Recraft via kie.ai."""
    payload = {
        "model": "recraft/remove-background",
        "input": {"image_url": image_url},
    }
    resp = requests.post(
        f"{KIE_BASE_URL}/jobs/createTask",
        headers=_headers(),
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    task_id = (data.get("data") or {}).get("taskId") or data.get("taskId")
    if not task_id:
        raise RuntimeError(f"kie.ai remove_background: no taskId. Response: {data}")

    result = _poll_task(task_id, max_wait=max_wait)
    urls = _extract_image_urls(result)
    if not urls:
        raise RuntimeError(f"remove_background completed but returned no URL. Response: {result}")
    return urls[0]


def upscale_image(image_url: str, scale: int = 2, max_wait: int = 120) -> str:
    """Upscale an image using Topaz via kie.ai."""
    payload = {
        "model": "topaz/image-upscale",
        "input": {"image_url": image_url, "scale": scale},
    }
    resp = requests.post(
        f"{KIE_BASE_URL}/jobs/createTask",
        headers=_headers(),
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    task_id = (data.get("data") or {}).get("taskId") or data.get("taskId")
    if not task_id:
        raise RuntimeError(f"kie.ai upscale_image: no taskId. Response: {data}")

    result = _poll_task(task_id, max_wait=max_wait)
    urls = _extract_image_urls(result)
    if not urls:
        raise RuntimeError(f"upscale_image completed but returned no URL. Response: {result}")
    return urls[0]


def get_available_image_models() -> list[str]:
    """
    Returns recommended kie.ai image model slugs for CavalierOne.
    Use slash-format slugs as required by the Market API.
    """
    return [
        # Fast & affordable — good for iteration
        "flux-2/flex-text-to-image",          # Flux-2 Flex (default)
        "google/nano-banana-2",               # Google Nano Banana 2 (very fast)

        # High quality — best for final assets
        "flux-2/pro-text-to-image",           # Flux-2 Pro
        "ideogram/v3-text-to-image",          # Ideogram V3 (great with text)
        "gpt-image/1-5-text-to-image",        # GPT-Image-1.5

        # Editing / image-to-image
        "flux-2/flex-image-to-image",         # Flux-2 Flex img2img
        "flux-2/pro-image-to-image",          # Flux-2 Pro img2img
    ]
