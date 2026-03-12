from __future__ import annotations

import tempfile
from pathlib import Path

import aiofiles
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from config import get_logger
from models import MrzResponse
from services.mrz import detect_and_extract_mrz

router = APIRouter(tags=["ghana-card"])

ACCEPTABLE_EXTENSIONS = {"png", "jpg", "jpeg"}


@router.post("/validate-ghana-card", response_model=MrzResponse)
async def validate_ghana_card(file: UploadFile = File(...)) -> JSONResponse:
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

            mrz_data = detect_and_extract_mrz(str(tmp_path))
            if mrz_data is None:
                raise HTTPException(status_code=400, detail="Could not read data from image")

        return JSONResponse(content=MrzResponse(**mrz_data).model_dump())
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error processing ghana card image: {exc}")
        raise HTTPException(status_code=400, detail="Could not read data from image")
