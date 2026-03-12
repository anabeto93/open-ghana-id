from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    message: str


class TinRequest(BaseModel):
    tin_num: str = Field(..., description="Personal TIN (e.g. P0000000000)")


class TinResponse(BaseModel):
    success: bool
    message: str


class GhanaCardNumberRequest(BaseModel):
    card_num: str = Field(..., description="Ghana Card number (e.g. GHA-000000000-0)")


class GhanaCardNumberResponse(BaseModel):
    success: bool
    message: str


class MrzResponse(BaseModel):
    type: str
    confidence_score: int
    id_type: str
    country: str
    id_number: str
    date_of_birth: str
    expiration_date: str
    nationality: str
    sex: str
    names: str
    surname: str
    id_is_valid: bool
    dob_is_valid: bool
    expiration_is_valid: bool


class VotersIdResponse(BaseModel):
    first_name: str
    last_name: str
    gender: str
    id_number: str
    date_of_birth: date
    registration_date: date
    polling_station_code: str


class DriversLicenseResponse(BaseModel):
    first_name: str
    last_name: str
    other_names: str
    date_of_birth: str
    nationality: str
    issue_date: str
    expiry_date: str
    license_number: str
    ref_number: str
