from __future__ import annotations

from fastapi import APIRouter, HTTPException

from config import get_logger
from models import GhanaCardNumberRequest, GhanaCardNumberResponse
from services.gra_client import validate_ghana_card_number

router = APIRouter(tags=["ghana-card-number"])


@router.post("/validate-ghana-card-number", response_model=GhanaCardNumberResponse)
async def validate_ghana_card_number_route(
    payload: GhanaCardNumberRequest,
) -> GhanaCardNumberResponse:
    if not payload.card_num:
        raise HTTPException(
            status_code=400,
            detail="Please enter a valid Ghana Card Number.",
        )

    logger = get_logger()
    logger.info("Validating Ghana card number via GRA endpoint (educational use only)")
    is_valid = await validate_ghana_card_number(payload.card_num)
    if is_valid:
        return GhanaCardNumberResponse(success=True, message="Ghana card number is valid")
    return GhanaCardNumberResponse(success=False, message="Ghana card number is invalid")
