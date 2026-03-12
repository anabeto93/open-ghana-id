from __future__ import annotations

import tempfile
from pathlib import Path

import aiofiles
from fastapi import APIRouter, File, HTTPException, UploadFile

from config import get_logger
from models import VotersIdResponse
from services.qr import extract_voters_qr_data

router = APIRouter(tags=["voters-id"])

ACCEPTABLE_EXTENSIONS = {"png", "jpg", "jpeg"}


@router.post("/validate-voters-id", response_model=VotersIdResponse)
async def validate_voters_id(file: UploadFile = File(...)) -> VotersIdResponse:
    logger = get_logger()

    suffix = file.filename.split(".")[-1].lower()
    if suffix not in ACCEPTABLE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type not supported")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / "image.png"
            async with aiofiles.open(tmp_path, "wb") as out:
                content = await file.read()
                await out.write(content)

            result = extract_voters_qr_data(str(tmp_path))

        if result is None:
            raise HTTPException(status_code=400, detail="Could not read data from image")

        return result
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error processing voters id image: {exc}")
        raise HTTPException(status_code=400, detail="Could not read data from image")
