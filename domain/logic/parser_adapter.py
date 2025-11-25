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

        try:
            # ----------------------------
            # Parse MRZ with PassportEye
            # ----------------------------
            mrz_obj = MRZ(mrz_texts)
            if mrz_obj is None:
                raise ValueError("Failed to parse MRZ lines with PassportEye.")

            data = mrz_obj.to_dict()

            # Critical field: document type
            if "type" not in data or data.get("type") is None:
                raise ValueError("MRZ does not look like a valid passport.")

            # ----------------------------
            # Normalize string fields
            # ----------------------------
            string_fields = ["type", "country", "number", "nationality", "sex",
                            "names", "surname", "personal_number"]
            for field in string_fields:
                if field in data:
                    data[field] = normalize_field(data[field])

            # ----------------------------
            # Convert dates
            # ----------------------------
            date_fields = ["date_of_birth", "expiration_date"]
            for field in date_fields:
                if field in data:
                    is_expiration = field == "expiration_date"
                    data[field] = convert_date(data[field], is_expiration=is_expiration)

            # Tunisia fix
            if data.get("country") == "TUN" and "personal_number" in data:
                data["personal_number"] = data["personal_number"][:8]

            # ----------------------------
            # Validate MRZ fields
            # ----------------------------
            validation_flags = validate_mrz_fields(data)
            data.update(validation_flags)

            # ----------------------------
            # Compute validity
            # ----------------------------
            data["is_valid"] = compute_overall_validity(validation_flags)

            return data

        except Exception as e:
            # ⛔ Convert ANY parsing/validation failure into a clean message
            raise ValueError("This image does not contain a valid passport MRZ. Please upload a passport image.") from e
