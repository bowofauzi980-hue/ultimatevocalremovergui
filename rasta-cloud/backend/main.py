
import os
import uuid
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="RASTA MUSIC EXTRACTOR AI",
    version="1.0.0",
    description="Cloud audio processing API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a"}
MAX_FILE_SIZE = 100 * 1024 * 1024


@app.get("/")
def home():
    return {
        "app": "RASTA MUSIC EXTRACTOR AI",
        "status": "online"
    }


@app.get("/api/v1/health")
def health():
    return {
        "status": "healthy",
        "service": "RASTA Cloud API"
    }


@app.post("/api/v1/upload")
async def upload_audio(file: UploadFile = File(...)):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Format audio tidak didukung"
        )

    file_id = str(uuid.uuid4())
    destination = UPLOAD_DIR / f"{file_id}{extension}"

    total_size = 0

    try:
        with destination.open("wb") as output:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="Ukuran file maksimal 100 MB"
                    )

                output.write(chunk)

    except Exception:
        destination.unlink(missing_ok=True)
        raise

    finally:
        await file.close()

    return {
        "success": True,
        "file_id": file_id,
        "filename": file.filename,
        "size_bytes": total_size,
        "status": "uploaded",
        "message": "Audio berhasil diterima RASTA Cloud"
    }
