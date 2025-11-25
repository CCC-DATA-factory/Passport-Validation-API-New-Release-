# utils/validators.py

from datetime import datetime
from typing import Dict, Optional, Tuple

# ----------------------------
# 1. MRZ Character → Numeric Value Mapping
# ----------------------------

def char_value(ch: str) -> int:
    """Convert MRZ character to its ICAO numeric value."""
    if ch == "<":
        return 0
    if ch.isdigit():
        return ord(ch) - ord("0")
    if "A" <= ch <= "Z":
        return ord(ch) - ord("A") + 10
    return 0  # unknown characters contribute 0 by ICAO rules


# ----------------------------
# 2. Checksum Computation
# ----------------------------

WEIGHTS = [7, 3, 1]

def compute_checksum(field: str) -> int:
    """Compute ICAO MRZ checksum for a given field."""
    total = 0
    for i, ch in enumerate(field):
        total += char_value(ch) * WEIGHTS[i % 3]
    return total % 10


def verify_checksum(field: Optional[str], check_digit: Optional[str]) -> bool:
    """
    Verify that the computed checksum of the field matches the given check digit.
    Returns False if input is invalid.
    """
    if not field or not check_digit or not check_digit.isdigit():
        return False
    try:
        return compute_checksum(field) == int(check_digit)
    except Exception:
        return False


# ----------------------------
# 3. MRZ Field Normalization
# ----------------------------

def normalize_field(value: Optional[str]) -> Optional[str]:
    """Clean filler '<', uppercase letters, and strip spaces."""
    if value is None:
        return None
    return value.replace("<", "").strip().upper()


# ----------------------------
# 4. Date Conversion & Validation
# ----------------------------

def convert_date(value: Optional[str], is_expiration: bool = False) -> Optional[str]:
    """
    Convert YYMMDD to YYYY-MM-DD format with safe century handling.
    
    Args:
        value: string in YYMMDD format
        is_expiration: if True, use expiration date logic; else date_of_birth logic
    
    Returns:
        YYYY-MM-DD string or None if invalid
    """
    if not value or len(value) != 6 or not value.isdigit():
        return None
    try:
        yy = int(value[:2])
        mm = int(value[2:4])
        dd = int(value[4:6])
        today = datetime.today()

        if is_expiration:
            # Expiration date: pick century so date is nearest to today (future preferred)
            year_2000 = 2000 + yy
            year_1900 = 1900 + yy

            date_2000 = datetime(year_2000, mm, dd)
            date_1900 = datetime(year_1900, mm, dd)

            # Choose the date closest to today
            if abs((date_2000 - today).days) <= abs((date_1900 - today).days):
                year = year_2000
            else:
                year = year_1900
        else:
            # Date of birth: age <= 120
            century = 1900 if yy > today.year % 100 else 2000
            year = century + yy
            if today.year - year > 120:
                year -= 100

        return datetime(year, mm, dd).strftime("%Y-%m-%d")
    except Exception:
        return None


def validate_date_format(date_str: Optional[str]) -> bool:
    """Check if date string is a valid YYYY-MM-DD."""
    if not date_str:
        return False
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


# ----------------------------
# 5. MRZ Structure Validation
# ----------------------------

def validate_mrz_structure(mrz_texts: str) -> Tuple[bool, str]:
    """
    Check MRZ structure validity: correct number of lines and length per line.
    Returns (is_valid, message).
    """
    if not mrz_texts:
        return False, "Empty MRZ text."

    lines = [l.strip() for l in mrz_texts.splitlines() if l.strip()]
    if len(lines) not in [2, 3]:
        return False, f"Invalid MRZ lines count ({len(lines)})."

    # TD3 (Passports) → 2 lines × 44 chars
    if len(lines) == 2 and not all(len(l) == 44 for l in lines):
        return False, f"Invalid line length for TD3 MRZ. Expected 44 chars per line."

    return True, "Valid MRZ structure."


# ----------------------------
# 6. Aggregate MRZ Field Validation
# ----------------------------

def validate_mrz_fields(mrz_data: Dict[str, str]) -> Dict[str, bool]:
    """
    Validate MRZ core fields using ICAO checksum rules.
    Input: dict containing field values and their check digits.
    Returns: dict of boolean flags for each field.
    """
    return {
        "valid_number": verify_checksum(mrz_data.get("passport_number"), mrz_data.get("check_number")),
        "valid_date_of_birth": verify_checksum(mrz_data.get("date_of_birth"), mrz_data.get("check_date_of_birth")),
        "valid_expiration_date": verify_checksum(mrz_data.get("expiration_date"), mrz_data.get("check_expiration_date")),
        "valid_personal_number": verify_checksum(mrz_data.get("personal_number"), mrz_data.get("check_personal_number")),
        "valid_composite": verify_checksum(
            "".join([
                mrz_data.get("passport_number", ""),
                mrz_data.get("check_number", ""),
                mrz_data.get("date_of_birth", ""),
                mrz_data.get("check_date_of_birth", ""),
                mrz_data.get("expiration_date", ""),
                mrz_data.get("check_expiration_date", ""),
                mrz_data.get("personal_number", ""),
                mrz_data.get("check_personal_number", ""),
            ]),
            mrz_data.get("check_composite"),
        ),
    }


# ----------------------------
# 7. Global Validation Summary
# ----------------------------

def compute_overall_validity(flags: Dict[str, bool]) -> bool:
    """Return True only if all flags that exist are True."""
    if not flags:
        return False
    return all(v is True for v in flags.values() if v is not None)


