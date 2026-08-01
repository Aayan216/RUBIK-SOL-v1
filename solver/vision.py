import base64
import json
import os
import re
from typing import Dict, List

import google.generativeai as genai

FACE_ORDER = ["top", "bottom", "front", "back", "left", "right"]

VALID_COLORS = {"white", "yellow", "red", "orange", "blue", "green"}

BATCH_PROMPT = (
    "I will show you 6 photos of a Rubik's Cube, one per face. Each photo is "
    "preceded by a text label naming which face it shows: 'top', 'bottom', "
    "'front', 'back', 'left', or 'right'. For each face, read the 3x3 grid of "
    "sticker colors, left to right, top to bottom. Respond with ONLY a JSON "
    "object whose keys are the 6 face names and whose values are arrays of "
    "exactly 9 color names each. Use only these color names: white, yellow, "
    "red, orange, blue, green. Return nothing else, no explanation, no markdown."
)

_model = None


def _get_model():
    global _model
    if _model is None:
        api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is not set")
        genai.configure(api_key=api_key)
        _model = genai.GenerativeModel("gemini-3.5-flash")
    return _model


def _decode_image(base64_image: str) -> bytes:
    if "," in base64_image and base64_image.strip().startswith("data:"):
        base64_image = base64_image.split(",", 1)[1]
    try:
        return base64.b64decode(base64_image, validate=False)
    except Exception as exc:
        raise ValueError(f"Could not decode base64 image data: {exc}") from exc


def _extract_json_object(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"Model response did not contain a JSON object: {text!r}")

    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Model response was not valid JSON: {text!r}") from exc

    if not isinstance(parsed, dict):
        raise ValueError(f"Expected a JSON object, got: {parsed!r}")

    return parsed


def _normalize_colors(colors, face_name: str) -> List[str]:
    if not isinstance(colors, list) or len(colors) != 9:
        raise ValueError(f"Expected 9 colors for face '{face_name}', got: {colors!r}")

    normalized = []
    for c in colors:
        if not isinstance(c, str):
            raise ValueError(f"Expected color name strings for face '{face_name}', got: {c!r}")
        name = c.strip().lower()
        if name not in VALID_COLORS:
            raise ValueError(
                f"Unexpected color name '{c}' for face '{face_name}' "
                f"(expected one of {sorted(VALID_COLORS)})"
            )
        normalized.append(name)
    return normalized


def get_all_face_colors(images: Dict[str, str]) -> Dict[str, List[str]]:
    """Reads sticker colors for all 6 cube faces in a single Gemini Vision
    request. `images` maps face name -> base64-encoded JPEG. Raises
    ValueError on unexpected output, RuntimeError on API failure."""
    model = _get_model()

    content: list = [BATCH_PROMPT]
    for face_name in FACE_ORDER:
        image_bytes = _decode_image(images[face_name])
        content.append(f"Face: {face_name}")
        content.append({"mime_type": "image/jpeg", "data": image_bytes})

    try:
        response = model.generate_content(content)
    except Exception as exc:
        raise RuntimeError(f"Gemini Vision API request failed: {exc}") from exc

    if not response.text:
        raise ValueError("Gemini Vision API returned an empty response")

    parsed = _extract_json_object(response.text)

    result: Dict[str, List[str]] = {}
    for face_name in FACE_ORDER:
        if face_name not in parsed:
            raise ValueError(f"Model response is missing face '{face_name}': {parsed!r}")
        result[face_name] = _normalize_colors(parsed[face_name], face_name)

    return result


SINGLE_FACE_PROMPT = (
    "This is a photo of one face of a Rubik's Cube. Read the 3x3 grid of "
    "sticker colors, left to right, top to bottom. Respond with ONLY a JSON "
    "object like {{\"colors\": [\"white\",\"red\",\"green\",...]}} containing "
    "exactly 9 color names. Use only: white, yellow, red, orange, blue, green. "
    "Return nothing else, no explanation, no markdown."
)


def get_single_face_colors(face_name: str, image_base64: str) -> List[str]:
    """Reads sticker colors for a single cube face from one Gemini Vision
    request. Raises ValueError on unexpected output, RuntimeError on API failure."""
    model = _get_model()
    image_bytes = _decode_image(image_base64)

    content: list = [SINGLE_FACE_PROMPT, {"mime_type": "image/jpeg", "data": image_bytes}]

    try:
        response = model.generate_content(content)
    except Exception as exc:
        raise RuntimeError(f"Gemini Vision API request failed: {exc}") from exc

    if not response.text:
        raise ValueError("Gemini Vision API returned an empty response")

    parsed = _extract_json_object(response.text)

    if "colors" not in parsed:
        raise ValueError(f"Model response missing 'colors' key: {parsed!r}")

    return _normalize_colors(parsed["colors"], face_name)
