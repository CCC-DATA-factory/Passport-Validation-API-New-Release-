from pydantic import BaseModel, Field, validator, field_validator
from datetime import datetime
from typing import Optional, List
from utils.validators import convert_date 

class MRZData(BaseModel):
    # --- Raw MRZ text from detection ---
    mrz_texts: List[str] = Field(..., description="Raw MRZ lines extracted from image")

    # --- MRZ fields parsed by the parser ---
    mrz_type: Optional[str] = None
    document_type: Optional[str] = None
    country_code: Optional[str] = None
    passport_number: Optional[str] = None
    date_of_birth: Optional[str] = None  # Will be normalized to YYYY-MM-DD
    expiration_date: Optional[str] = None  # Will be normalized to YYYY-MM-DD
    nationality: Optional[str] = None
    sex: Optional[str] = None
    given_names: Optional[str] = None
    surname: Optional[str] = None
    personal_number: Optional[str] = None

    # --- MRZ check digits ---
    check_number: Optional[str] = None
    check_date_of_birth: Optional[str] = None
    check_expiration_date: Optional[str] = None
    check_composite: Optional[str] = None
    check_personal_number: Optional[str] = None

    # --- MRZ validation results ---
    valid_number: Optional[bool] = None
    valid_date_of_birth: Optional[bool] = None
    valid_expiration_date: Optional[bool] = None
    valid_composite: Optional[bool] = None
    valid_personal_number: Optional[bool] = None
    valid_score: Optional[int] = Field(None, description="Overall MRZ parsing confidence score")

    # --- Derived field ---
    is_valid: Optional[bool] = Field(default=None, description="True if all validations pass")


    # -----------------------------
    # Validators / Normalizers
    # -----------------------------

    @validator(
        "document_type", "country_code", "nationality", "given_names", "surname", "personal_number", "passport_number",
        pre=True, always=True
    )
    def clean_strings(cls, v):
        if v is None:
            return v
        return v.replace("<", "").strip().upper()

    @field_validator("date_of_birth", "expiration_date", mode="before")
    def format_dates(cls, v, info):
        """Convert YYMMDD → YYYY-MM-DD with correct century."""
        if not v:
            return None
        try:
            # Already formatted
            if len(v) == 10 and "-" in v:
                return v

            if len(v) == 6 and v.isdigit():
                yy = int(v[:2])
                mm = int(v[2:4])
                dd = int(v[4:6])
                today = datetime.today()

                field_name = info.name

                if field_name == "date_of_birth":
                    # Make sure age <= 120
                    century = 1900 if yy > today.year % 100 else 2000
                    year = century + yy
                    if today.year - year > 120:
                        year -= 100
                    return datetime(year, mm, dd).strftime("%Y-%m-%d")

                elif field_name == "expiration_date":
                    # Make sure passport expiration is close to today
                    # Assume passports valid <= 20 years
                    # pick century so that date is nearest to today
                    year_2000 = 2000 + yy
                    year_1900 = 1900 + yy

                    date_2000 = datetime(year_2000, mm, dd)
                    date_1900 = datetime(year_1900, mm, dd)

                    # Choose the date closest to today but in the future
                    if abs((date_2000 - today).days) <= abs((date_1900 - today).days):
                        year = year_2000
                    else:
                        year = year_1900

                    return datetime(year, mm, dd).strftime("%Y-%m-%d")

        except Exception:
            return None

        return None
    @validator("is_valid", always=True)
    def compute_is_valid(cls, v, values):
        """Mark passport valid only if all validation flags are True."""
        flags = [
            values.get("valid_number"),
            values.get("valid_date_of_birth"),
            values.get("valid_expiration_date"),
            values.get("valid_composite"),
            values.get("valid_personal_number"),
        ]
        # only consider those that are not None
        active_flags = [f for f in flags if f is not None]
        return all(active_flags) if active_flags else False

    class Config:
        orm_mode = True
        anystr_strip_whitespace = True