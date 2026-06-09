"""
CafeArchive Vision Service — OCR text extraction from cafe menu images.
Uses Tesseract OCR (lightweight, works on Render free tier).
Supports Korean + English via traineddata files.
"""

from pathlib import Path
import re
import logging
import subprocess

logger = logging.getLogger(__name__)


def extract_text_from_image(file_path: str) -> str:
    """
    Extract text from an image file using Tesseract OCR.
    Requires tesseract to be installed on the system.
    Supports Korean (kor) and English (eng) languages.
    """
    try:
        import pytesseract
        from PIL import Image

        img = Image.open(file_path)
        # Use Korean + English
        text = pytesseract.image_to_string(img, lang='kor+eng')
        return text.strip() or ""
    except ImportError:
        # Fallback: call tesseract CLI directly
        result = subprocess.run(
            ['tesseract', str(file_path), 'stdout', '-l', 'kor+eng'],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip() or ""
    except Exception as e:
        logger.error(f"Tesseract OCR failed: {e}")
        return ""


def parse_cafe_info(text: str) -> dict:
    """
    Parse extracted text to identify cafe name and menu items.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    cafe_name = None
    menu_items = []

    price_pattern = re.compile(r'[\d,]+[원\s]*$|₩[\d,]+|\$[\d.]+|[0-9,]+원')

    for line in lines[:20]:
        if cafe_name is None and len(line) > 2:
            if not price_pattern.search(line) and len(line) < 30:
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
    """
    Full pipeline: extract text from image → parse cafe info.
    """
    try:
        text = extract_text_from_image(file_path)
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