# domain/logic/parser_adapter.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from passporteye.mrz.text import MRZ
from utils.validators import normalize_field, convert_date, validate_mrz_fields, compute_overall_validity


# ----------------------------
# 1. Abstract Interface
# ----------------------------

class BaseMRZParser(ABC):
    """Abstract interface for MRZ parsers."""

    @abstractmethod
    def parse(self, mrz_texts: List[str]) -> Dict[str, Any]:
        """
        Parse MRZ text lines into structured passport fields.

        Args:
            mrz_texts: list of MRZ lines

        Returns:
            Dictionary of parsed fields
        """
        pass


# ----------------------------
# 2. Concrete Implementation: PassportEye
# ----------------------------

class PassportEyeParser(BaseMRZParser):
    """Concrete parser using PassportEye library."""

    def parse(self, mrz_texts: List[str]) -> Dict[str, Any]:
        if not mrz_texts or not isinstance(mrz_texts, list):
            raise ValueError("MRZ texts must be a non-empty list of strings.")

        # Parse MRZ with PassportEye
        mrz_obj = MRZ(mrz_texts)
        if mrz_obj is None:
            raise ValueError("Failed to parse MRZ lines with PassportEye.")

        # Convert to dict
        data = mrz_obj.to_dict()

        # ✅ CHECK IF PARSING FAILED - type field is critical
        if "type" not in data or data.get("type") is None:
            raise ValueError(
                f"PassportEye failed to extract document type. "
                f"MRZ lines may be invalid or unreadable: {mrz_texts}"
            )

        # ----------------------------
        # 1️⃣ Normalize string fields
        # ----------------------------
        string_fields = ["type", "country", "number", "nationality", "sex",
                         "names", "surname", "personal_number"]
        for field in string_fields:
            if field in data:
                data[field] = normalize_field(data[field])

        # ----------------------------
        # 2️⃣ Convert dates to YYYY-MM-DD
        # ----------------------------
        date_fields = ["date_of_birth", "expiration_date"]
        for field in date_fields:
            if field in data:
                is_expiration = field == "expiration_date"
                converted = convert_date(data[field], is_expiration=is_expiration)
                data[field] = converted

        if data.get("country") == "TUN" and "personal_number" in data:
            data["personal_number"] = data["personal_number"][:8]
        # ----------------------------
        # 3️⃣ Validate MRZ fields using utils
        # ----------------------------
        validation_flags = validate_mrz_fields(data)
        data.update(validation_flags)

        # ----------------------------
        # 4️⃣ Compute overall validity
        # ----------------------------
        data["is_valid"] = compute_overall_validity(validation_flags)

        return data
