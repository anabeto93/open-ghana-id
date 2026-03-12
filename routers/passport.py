from __future__ import annotations

import tempfile
from pathlib import Path

import aiofiles
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from config import get_logger
from models import MrzResponse
from services.image_processing import process_image
from services.mrz import detect_and_extract_mrz

router = APIRouter(tags=["passport"])

ACCEPTABLE_EXTENSIONS = {"png", "jpg", "jpeg"}


@router.post("/validate-passport", response_model=MrzResponse)
async def validate_passport(file: UploadFile = File(...)) -> JSONResponse:
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

            processed = process_image(str(tmp_path))
            mrz_data = detect_and_extract_mrz(processed)
            if mrz_data is None:
                raise HTTPException(status_code=400, detail="Could not read data from image")

        return JSONResponse(content=MrzResponse(**mrz_data).model_dump())
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error processing passport image: {exc}")
        raise HTTPException(status_code=400, detail="Could not read data from image")
