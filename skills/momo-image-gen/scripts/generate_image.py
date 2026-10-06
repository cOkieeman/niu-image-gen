#!/usr/bin/env python3
"""Generate an image from a prefixed prompt.

Usage:
  generate_image.py "么么哒 写实风格成年女性肖像，自然光，高清摄影，背景简洁"
  generate_image.py "么么哒pro --横图 --1k 写实风格成年女性肖像，自然光，高清摄影，背景简洁"
  generate_image.py "么么哒改 把这张图片改成黑白超现实主义风格" --input-image /path/to/source.jpg
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
from datetime import datetime
from os.path import expanduser
from pathlib import Path
from typing import Any
from urllib import error, request


DEFAULT_PREFIX = "么么哒"
PRO_PREFIX = "么么哒pro"
EDIT_PREFIX = "么么哒改"
PRO_EDIT_PREFIX = "么么哒pro改"
API_KEY = "麦当劳"
NIU_CONFIG_PATH = Path(expanduser("~")) / ".codex" / "niu-image-gen-config.json"
MODEL_ENDPOINTS = {
    DEFAULT_PREFIX: "https://api.iiiiitoken.com/v1beta/models/gemini-3.1-flash-image:generateContent",
    PRO_PREFIX: "https://api.iiiiitoken.com/v1beta/models/gemini-3-pro-image:generateContent",
    EDIT_PREFIX: "https://api.iiiiitoken.com/v1beta/models/gemini-3.1-flash-image:generateContent",
    PRO_EDIT_PREFIX: "https://api.iiiiitoken.com/v1beta/models/gemini-3-pro-image:generateContent",
}


def get_api_key() -> str | None:
    env_key = os.environ.get("IIIIITOKEN_API_KEY") or os.environ.get("API_KEY")
    if env_key:
        return env_key

    try:
        config = json.loads(NIU_CONFIG_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        config = {}

    config_key = config.get("apiKey")
    if isinstance(config_key, str) and config_key:
        return config_key

    if API_KEY and API_KEY != "麦当劳":
        return API_KEY

    return None
ASPECT_RATIO_FLAGS = {
    "--横图": "16:9",
    "--方图": "1:1",
    "--竖图": "9:16",
}
IMAGE_SIZE_FLAGS = {
    "--1k": "1K",
    "--2k": "2K",
    "--4k": "4K",
}


def strip_prefix(text: str, prefix: str) -> str:
    stripped = text.strip()
    if stripped.startswith(prefix):
        stripped = stripped[len(prefix):].lstrip(" :：,，\t")
    return stripped


def detect_prefix(text: str) -> tuple[str, str]:
    stripped = text.strip()
    for prefix in (PRO_EDIT_PREFIX, EDIT_PREFIX, PRO_PREFIX, DEFAULT_PREFIX):
        if stripped.startswith(prefix):
            return prefix, strip_prefix(stripped, prefix)
    return DEFAULT_PREFIX, stripped


def extract_options(prompt: str, default_aspect_ratio: str, default_image_size: str) -> tuple[str, str, str]:
    tokens = prompt.split()
    aspect_ratio = default_aspect_ratio
    image_size = default_image_size
    remaining: list[str] = []

    for token in tokens:
        mapped = ASPECT_RATIO_FLAGS.get(token)
        if mapped is not None:
            aspect_ratio = mapped
            continue
        mapped_size = IMAGE_SIZE_FLAGS.get(token)
        if mapped_size is not None:
            image_size = mapped_size
            continue
        remaining.append(token)

    return " ".join(remaining).strip(), aspect_ratio, image_size


def build_payload(prompt: str, aspect_ratio: str, image_size: str, input_image: str | None) -> dict[str, Any]:
    parts: list[dict[str, Any]] = [{"text": prompt}]
    if input_image:
        image_path = Path(input_image)
        mime_type = mimetypes.guess_type(image_path.name)[0] or "image/png"
        parts.append(
            {
                "inlineData": {
                    "mimeType": mime_type,
                    "data": base64.b64encode(image_path.read_bytes()).decode("ascii"),
                }
            }
        )

    return {
        "contents": [
            {
                "role": "user",
                "parts": parts,
            }
        ],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
                "imageSize": image_size,
            },
        },
    }


def recursive_find(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if isinstance(value.get("inlineData"), dict):
            found.append(value["inlineData"])
        if isinstance(value.get("inline_data"), dict):
            found.append(value["inline_data"])
        if isinstance(value.get("fileData"), dict):
            found.append(value["fileData"])
        for item in value.values():
            found.extend(recursive_find(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(recursive_find(item))
    return found


def decode_image_from_json(data: Any) -> tuple[bytes | None, str | None]:
    for node in recursive_find(data):
        mime_type = node.get("mimeType") or node.get("mime_type") or "image/png"
        raw = node.get("data") or node.get("bytesBase64Encoded") or node.get("bytes")
        if isinstance(raw, str):
            try:
                return base64.b64decode(raw), mime_type
            except Exception:
                pass
        uri = node.get("fileUri") or node.get("uri")
        if isinstance(uri, str) and uri.startswith(("http://", "https://")):
            with request.urlopen(uri, timeout=60) as resp:  # nosec: B310
                return resp.read(), resp.headers.get_content_type()
    return None, None


def filename_for(mime_type: str | None) -> str:
    if mime_type and "jpeg" in mime_type:
        ext = "jpg"
    elif mime_type and "webp" in mime_type:
        ext = "webp"
    elif mime_type and "gif" in mime_type:
        ext = "gif"
    elif mime_type and "json" in mime_type:
        ext = "json"
    else:
        ext = "png"
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"momo-image-{stamp}.{ext}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", help="Prompt text, optionally prefixed with 么么哒, 么么哒pro, 么么哒改, or 么么哒pro改")
    parser.add_argument("--output-dir", default="outputs", help="Directory to write the image into")
    parser.add_argument("--output", help="Explicit output file path")
    parser.add_argument("--input-image", "--参考图", dest="input_image", help="Reference image path for image editing")
    parser.add_argument("--aspect-ratio", default="1:1")
    parser.add_argument("--image-size", default="4K")
    parser.add_argument("--endpoint", help="Override the model endpoint")
    args = parser.parse_args()

    api_key = get_api_key()
    if not api_key:
        print("Missing API key. Set $IIIIITOKEN_API_KEY, $API_KEY, or configure niu-image-gen.", file=sys.stderr)
        return 2

    prefix, prompt = detect_prefix(args.prompt)
    prompt, aspect_ratio, image_size = extract_options(prompt, args.aspect_ratio, args.image_size)
    if not prompt:
        print("Prompt is empty after stripping the trigger keyword.", file=sys.stderr)
        return 2

    endpoint = args.endpoint or MODEL_ENDPOINTS[prefix]
    if args.input_image and not Path(args.input_image).exists():
        print(f"Input image not found: {args.input_image}", file=sys.stderr)
        return 2

    payload = build_payload(prompt, aspect_ratio, image_size, args.input_image)
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        endpoint,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "x-goog-api-key": api_key,
        },
    )

    try:
        with request.urlopen(req, timeout=120) as resp:  # nosec: B310
            content_type = resp.headers.get_content_type()
            raw = resp.read()
    except error.HTTPError as exc:
        print(exc.read().decode("utf-8", errors="replace"), file=sys.stderr)
        return exc.code
    except error.URLError as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if content_type.startswith("image/"):
        image_bytes = raw
        mime_type = content_type
    else:
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            data = None

        image_bytes = None
        mime_type = None
        if data is not None:
            image_bytes, mime_type = decode_image_from_json(data)
        if image_bytes is None:
            json_path = Path(args.output) if args.output else output_dir / filename_for("application/json")
            json_path.write_text(raw.decode("utf-8", errors="replace"), encoding="utf-8")
            print(str(json_path))
            return 0

    out_path = Path(args.output) if args.output else output_dir / filename_for(mime_type)
    out_path.write_bytes(image_bytes)
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
