# schemas/response.py

from pydantic import BaseModel
from typing import List, Optional


class PassportResponse(BaseModel):
    """
    Output schema for passport MRZ API.
    Mirrors MRZData model for response consistency.
    """
    mrz_texts: List[str]
    mrz_type: Optional[str]
    valid_score: Optional[int]
    document_type: Optional[str]
    country_code: Optional[str]
    passport_number: Optional[str]
    date_of_birth: Optional[str]  # YYYY-MM-DD
    expiration_date: Optional[str]  # YYYY-MM-DD
    nationality: Optional[str]
    sex: Optional[str]
    given_names: Optional[str]
    surname: Optional[str]
    personal_number: Optional[str]
    check_number: Optional[str]
    check_date_of_birth: Optional[str]
    check_expiration_date: Optional[str]
    check_composite: Optional[str]
    check_personal_number: Optional[str]
    valid_number: Optional[bool]
    valid_date_of_birth: Optional[bool]
    valid_expiration_date: Optional[bool]
    valid_composite: Optional[bool]
    valid_personal_number: Optional[bool]
    is_valid: Optional[bool]
