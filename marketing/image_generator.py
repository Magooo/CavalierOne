"""
image_generator.py — Cavalier Homes branded image generation via kie.ai.

Builds Cavalier-specific prompts from brand_config.json and uses kie_client
to generate on-brand lifestyle images for:
  - Listing hero shots (exterior, lifestyle)
  - Interior lifestyle scenes
  - Social media (feed / story formats)
  - Document/brochure supporting imagery
"""

import json
import os

# Brand style constants injected into every prompt
_BRAND_STYLE = (
    "modern Australian residential home, fresh bright natural lighting, "
    "lush lawn and landscaping, clean contemporary architecture, "
    "high-quality professional real estate photography style, "
    "warm inviting atmosphere, no people, photorealistic"
)

_NEGATIVE = (
    "cartoon, illustration, low quality, blurry, dark, cluttered, "
    "people, text, watermark, logo, oversaturated, distorted"
)


def _load_brand_config() -> dict:
    """Load brand_config.json for colours and imagery rules."""
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "resources", "brand_config.json"
    )
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    return {}


def _imagery_rules_string() -> str:
    """Return imagery rules from brand config as a comma-separated string."""
    cfg = _load_brand_config()
    rules = cfg.get("imagery_rules", [])
    return ", ".join(rules) if rules else ""


def build_listing_hero_prompt(suburb: str = "", house_type: str = "", extras: str = "") -> str:
    """
    Build a prompt for a house listing hero image.

    Args:
        suburb:     Suburb name (e.g. 'Shepparton')
        house_type: House style (e.g. 'single storey', 'double storey', 'acreage')
        extras:     Any additional prompt details

    Returns:
        Full image generation prompt string.
    """
    imagery_rules = _imagery_rules_string()

    suburb_str = f"in {suburb}, regional Victoria, Australia" if suburb else "in regional Victoria, Australia"
    house_str = f"{house_type} home" if house_type else "home"

    prompt = (
        f"Front elevation of a beautiful modern {house_str} {suburb_str}. "
        f"{_BRAND_STYLE}. "
        f"Golden hour lighting, blue sky with light clouds. "
    )

    if imagery_rules:
        prompt += f"{imagery_rules}. "

    if extras:
        prompt += f"{extras}."

    return prompt.strip()


def build_interior_lifestyle_prompt(room: str = "kitchen", extras: str = "") -> str:
    """
    Build a prompt for an interior lifestyle image.

    Args:
        room:   Room type (e.g. 'kitchen', 'living room', 'master bedroom', 'alfresco')
        extras: Additional prompt details

    Returns:
        Full image generation prompt string.
    """
    prompt = (
        f"Modern Australian residential {room} interior, "
        f"styled and staged for real estate photography, "
        f"natural light streaming through windows, "
        f"neutral tones with warm accents, high ceilings, "
        f"premium finishes and fittings, immaculate and clean, "
        f"professional interior photography, photorealistic, "
        f"no people. "
    )

    if extras:
        prompt += f"{extras}."

    return prompt.strip()


def build_social_feed_prompt(
    caption_context: str = "",
    format: str = "square",
    extras: str = ""
) -> str:
    """
    Build a prompt for a social media feed image.

    Args:
        caption_context: What the post is about (e.g. 'new display home opening')
        format:          'square' (1:1), 'portrait' (4:5), 'landscape' (16:9)
        extras:          Additional prompt details

    Returns:
        Full image generation prompt string.
    """
    format_map = {
        "square": "square format 1:1 aspect ratio",
        "portrait": "portrait format 4:5 aspect ratio",
        "landscape": "landscape format 16:9 aspect ratio",
        "story": "portrait format 9:16 aspect ratio for Instagram Story",
    }
    aspect = format_map.get(format, format_map["square"])

    prompt = (
        f"Premium real estate lifestyle photograph, {aspect}, "
        f"modern Australian home exterior or interior, "
        f"{_BRAND_STYLE}, "
        f"aspirational lifestyle feel, "
    )

    if caption_context:
        prompt += f"context: {caption_context}, "

    prompt += "clean composition with space for text overlay."

    if extras:
        prompt += f" {extras}."

    return prompt.strip()


def build_brochure_section_prompt(section_title: str = "", extras: str = "") -> str:
    """
    Build a prompt for a supporting image in a PDF brochure/document.

    Args:
        section_title: The document section this image accompanies
                       (e.g. 'Inclusions', 'Site Works', 'Process')
        extras:        Additional prompt details

    Returns:
        Full image generation prompt string.
    """
    prompt = (
        f"Clean minimal real estate lifestyle photograph for a brochure, "
        f"modern Australian home, professional photography, "
        f"bright and airy, white and neutral tones, "
        f"wide letterbox crop suitable for a document header or section image, "
    )

    if section_title:
        prompt += f"representing the concept of '{section_title}', "

    prompt += "no people, photorealistic, premium quality."

    if extras:
        prompt += f" {extras}."

    return prompt.strip()


def generate_cavalier_image(
    image_type: str,
    model: str = "flux-2-flex-text-to-image",
    width: int = 1024,
    height: int = 768,
    **kwargs
) -> dict:
    """
    High-level function: build a Cavalier-branded prompt and generate via kie.ai.

    Args:
        image_type: One of 'listing_hero', 'interior', 'social_feed', 'brochure'
        model:      kie.ai model slug (default: Flux-2 Flex)
        width, height: Image dimensions
        **kwargs:   Passed to the corresponding prompt builder

    Returns:
        dict with keys: image_urls, prompt, model, image_type
    """
    from utils.kie_client import generate_image

    # Build the appropriate prompt
    prompt_builders = {
        "listing_hero": build_listing_hero_prompt,
        "interior": build_interior_lifestyle_prompt,
        "social_feed": build_social_feed_prompt,
        "brochure": build_brochure_section_prompt,
    }

    if image_type not in prompt_builders:
        raise ValueError(
            f"Unknown image_type '{image_type}'. "
            f"Choose from: {', '.join(prompt_builders.keys())}"
        )

    prompt = prompt_builders[image_type](**kwargs)

    image_urls = generate_image(
        prompt=prompt,
        model=model,
        width=width,
        height=height,
    )

    return {
        "image_urls": image_urls,
        "image_url": image_urls[0] if image_urls else None,
        "prompt": prompt,
        "model": model,
        "image_type": image_type,
    }
