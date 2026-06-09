"""
CafeArchive Vision Service — OCR text extraction from cafe menu images.
Uses EasyOCR for deep-learning-based text recognition (Korean + English).
"""

from pathlib import Path
import re
import logging

logger = logging.getLogger(__name__)

# Lazy init EasyOCR (loads model on first use, ~300MB download)
_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        import easyocr
        # Korean + English support. GPU=False for CPU-only (works on Render free tier)
        _reader = easyocr.Reader(['ko', 'en'], gpu=False)
    return _reader


def extract_text_from_image(file_path: str) -> str:
    """
    Extract text from an image file using EasyOCR.
    Supports Korean + English characters.
    Returns extracted text string with confidence scores.
    """
    reader = _get_reader()

    # Read image with EasyOCR
    # detail=0 returns just the text strings
    results = reader.readtext(str(file_path), detail=0)

    if not results:
        return ""

    return "\n".join(results)


def parse_cafe_info(text: str) -> dict:
    """
    Parse extracted text to identify cafe name and menu items.
    Uses heuristics: first line often contains cafe name,
    menu items are typically listed with prices/descriptions.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    cafe_name = None
    menu_items = []

    # Common patterns for menu items
    price_pattern = re.compile(r'[\d,]+[원\s]*$|[\d,]+[원\s]*$|₩[\d,]+|\$[\d.]+')

    for line in lines[:20]:
        # First meaningful line might be cafe name
        if cafe_name is None and len(line) > 2:
            if not price_pattern.search(line) and len(line) < 30:
                cafe_name = line
                continue

        # Collect menu items
        if len(line) > 3:
            menu_items.append(line)

    return {
        "cafe_name": cafe_name,
        "menu_items": menu_items[:15],
        "raw_text": text[:500]
    }


def analyze(file_path: str) -> dict:
    """
    Full pipeline: extract text from image → parse cafe info.
    """
    try:
        text = extract_text_from_image(file_path)
        if not text.strip():
            return {
                "status": "warning",
                "cafe_name": None,
                "menu_items": [],
                "note": "No text found — try higher resolution or different angle",
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