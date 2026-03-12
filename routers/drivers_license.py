from __future__ import annotations

import tempfile
from pathlib import Path

import aiofiles
import pytesseract
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from config import get_logger
from models import DriversLicenseResponse
from services.image_processing import process_image
from services.ocr import serialize_drivers_license_data

router = APIRouter(tags=["drivers-license"])

ACCEPTABLE_EXTENSIONS = {"png", "jpg", "jpeg"}


@router.post("/validate-drivers-license", response_model=DriversLicenseResponse)
async def validate_drivers_license(file: UploadFile = File(...)) -> JSONResponse:
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
            raw_text = pytesseract.image_to_string(processed)
            result = serialize_drivers_license_data(raw_text)

        if result is None:
            raise HTTPException(status_code=400, detail="Could not read data from image")

        return JSONResponse(content=result.model_dump())
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error processing drivers license image: {exc}")
        raise HTTPException(status_code=400, detail="Could not read data from image")
