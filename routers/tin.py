from __future__ import annotations

from fastapi import APIRouter, HTTPException

from config import get_logger
from models import TinRequest, TinResponse
from services.gra_client import validate_tin

router = APIRouter(tags=["tin"])


@router.post("/validate-tin", response_model=TinResponse)
async def verify_tin(payload: TinRequest) -> TinResponse:
    if not payload.tin_num:
        raise HTTPException(status_code=400, detail="Please enter a valid TIN.")

    logger = get_logger()
    logger.info("Validating TIN via GRA endpoint (educational use only)")
    is_valid = await validate_tin(payload.tin_num)
    if is_valid:
        return TinResponse(success=True, message="Personal TIN is valid")
    return TinResponse(success=False, message="Personal TIN is invalid")
