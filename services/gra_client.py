from __future__ import annotations

from typing import Literal

import httpx

from config import get_logger

GRA_ENDPOINT = "https://gra.gov.gh/gra_user_panel/api/Tin_Pin.php"


async def _validate_id(id_value: str, type_value: Literal["validateTin", "validatePin"]) -> bool:
    logger = get_logger()
    if not id_value:
        return False

    headers = {
        "Content-Type": "application/json",
        "Origin": "https://gra.gov.gh",
        "Accept": "*/*",
    }
    payload = {"ID": id_value.upper(), "Type": type_value}

    timeout = httpx.Timeout(10.0, read=10.0)
    async with httpx.AsyncClient(timeout=timeout, verify=True) as client:
        logger.info("Calling GRA Tin_Pin endpoint (educational use only)")
        try:
            response = await client.post(GRA_ENDPOINT, json=payload, headers=headers)
        except httpx.HTTPError as exc:
            logger.error(f"Error connecting to GRA endpoint: {exc}")
            return False

    if response.status_code != 200:
        logger.error(f"GRA endpoint returned non-200 status: {response.status_code}")
        return False

    text = response.text.strip().lower()
    return text.split()[0] == "true" if text else False


async def validate_tin(tin: str) -> bool:
    return await _validate_id(tin, "validateTin")


async def validate_ghana_card_number(card_number: str) -> bool:
    return await _validate_id(card_number, "validatePin")
