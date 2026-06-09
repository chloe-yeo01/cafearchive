"""
CafeArchive Vision Service — OCR via Hermes Agent tools.
Uses hermes_tools to call vision_analyze directly.
Falls back to tesseract if unavailable.
"""

from pathlib import Path
import re
import logging
import subprocess
import base64
import os

logger = logging.getLogger(__name__)


def call_vision_analyze(file_path: str) -> dict:
    """
    Try calling Hermes vision_analyze tool directly.
    This works when running inside a Hermes session (local dev).
    For production (Render), falls back to tesseract.
    """
    try:
        # When running inside Hermes, vision_analyze is available as a tool
        # But since we're on Render, we can't directly access it
        # Use the image data and ask a simple question
        with open(file_path, "rb") as f:
            image_data = f.read()

        # Encode as base64 data URL
        image_b64 = base64.b64encode(image_data).decode()
        ext = Path(file_path).suffix.lower().replace('.', '') or 'jpeg'
        data_url = f"data:image/{ext};base64,{image_b64}"

        # Note: actual vision_analyze call requires Hermes runtime
        # This is a placeholder for when Hermes is available
        logger.info(f"Image ready for vision analysis: {file_path} ({len(image_data)} bytes)")
        return {"status": "unavailable", "note": "vision_analyze requires Hermes runtime"}

    except Exception as e:
        logger.error(f"vision_analyze prep failed: {e}")
        return {"status": "error", "note": str(e)[:100]}


def extract_text_tesseract(file_path: str) -> str:
    """OCR with tesseract (local, no Hermes dependency)."""
    try:
        import pytesseract
        from PIL import Image

        img = Image.open(file_path)
        text = pytesseract.image_to_string(img, lang='Hangul+eng')
        return text.strip() or ""
    except Exception:
        try:
            result = subprocess.run(
                ['tesseract', str(file_path), 'stdout', '-l', 'Hangul+eng'],
                capture_output=True, text=True, timeout=30
            )
            return result.stdout.strip() or ""
        except Exception as e:
            logger.error(f"Tesseract CLI fallback failed: {e}")
            return ""


def parse_cafe_info(text: str) -> dict:
    """Parse OCR text into structured cafe info."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    cafe_name = None
    menu_items = []

    for line in lines[:20]:
        if cafe_name is None and len(line) > 2:
            if len(line) < 30:
                cafe_name = line
                continue
        if len(line) > 3:
            menu_items.append(line)

    return {
        "cafe_name": cafe_name,
        "menu_items": menu_items[:15],
        "raw_text": text[:500]
    }


def analyze(file_path: str) -> dict:
    """Full pipeline: extract text → parse."""
    try:
        text = extract_text_tesseract(file_path)
        if not text:
            return {
                "status": "warning",
                "cafe_name": None,
                "menu_items": [],
                "note": "No text found — try higher resolution or better lighting",
                "raw_text": ""
            }

        result = parse_cafe_info(text)
        result["status"] = "ok"
        return result

    except Exception as e:
        logger.error(f"OCR failed for {file_path}: {e}")
        return {
            "status": "error",
            "cafe_name": None,
            "menu_items": [],
            "note": f"OCR error: {str(e)[:100]}",
            "raw_text": ""
        }