from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import tempfile
import shutil

from vision_service import analyze as ocr_analyze

app = FastAPI(title="CafeArchive Vision API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(tempfile.gettempdir()) / "cafearchive_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


@app.post("/api/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """
    Receive an image, save it temporarily, OCR it with EasyOCR,
    parse cafe name and menu items.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files accepted")

    # Save uploaded file
    safe_filename = file.filename or "upload.jpg"
    file_path = UPLOAD_DIR / safe_filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # OCR + parse
    result = ocr_analyze(str(file_path))
    result["filename"] = safe_filename
    result["file_path"] = str(file_path)

    return result


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "CafeArchive Vision API"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)