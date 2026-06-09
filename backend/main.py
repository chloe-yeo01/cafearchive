from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import tempfile
import shutil

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
    Receive an image, save it temporarily, extract text via vision_analyze.
    Returns cafe name and menu items.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files accepted")

    # Save uploaded file
    safe_filename = file.filename or "upload.jpg"
    file_path = UPLOAD_DIR / safe_filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Placeholder: return image path for now
    # Real implementation: call vision_analyze here
    return {
        "status": "ok",
        "filename": file.filename,
        "file_path": str(file_path),
        "cafe_name": None,
        "menu_items": [],
        "note": "vision_analyze integration pending"
    }


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "CafeArchive Vision API"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)