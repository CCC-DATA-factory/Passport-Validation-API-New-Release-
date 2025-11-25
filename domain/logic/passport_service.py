# domain/logic/passport_service.py

from typing import Optional, List
from utils.image import load_image
from domain.logic.mrz_adapter import BaseMRZDetector, MRZScannerAdapter
from domain.logic.parser_adapter import BaseMRZParser, PassportEyeParser
from domain.models.mrz_data import MRZData
from core.logging import logger


class PassportService:
    """
    Core service that orchestrates MRZ detection, parsing, and validation.
    """

    def __init__(
        self,
        mrz_detector: Optional[BaseMRZDetector] = None,
        mrz_parser: Optional[BaseMRZParser] = None,
    ):
        # Allow dependency injection for flexibility / testing
        self.detector = mrz_detector if mrz_detector else MRZScannerAdapter()
        self.parser = mrz_parser if mrz_parser else PassportEyeParser()

    # ----------------------------
    # Main processing method
    # ----------------------------

    def process_passport(self, source: str) -> MRZData:
        """
        Process passport image from path, URL, or base64.
        """
        # 1️⃣ Load image
        image = load_image(source)

        # 2️⃣ Detect MRZ lines
        detection_result = self.detector.detect(image)
        mrz_texts: List[str] = detection_result.get("mrz_texts", [])
        
        # ✅ LOG THE DETECTED MRZ
        logger.info(f"Detected MRZ lines: {mrz_texts}")
        
        if not mrz_texts:
            raise ValueError(f"No MRZ lines detected. Msg: {detection_result.get('msg')}")

        # 3️⃣ Parse MRZ lines
        try:
            parsed_data = self.parser.parse(mrz_texts)
            logger.info(f"Parsed data keys: {list(parsed_data.keys())}")  # ✅ Debug
            # ✅ ADD THIS - Log the actual 'type' value
            logger.info(f"Type field value: {parsed_data.get('type')}")
            logger.info(f"Type field type: {type(parsed_data.get('type'))}")
        except ValueError as e:
            logger.error(f"Parsing failed: {e}")
            raise ValueError("Image does not contain a valid passport MRZ. Please try another image.")
        # 4️⃣ Convert to MRZData model (enforces typing + normalization)
        mrz_data = MRZData(
            mrz_texts=mrz_texts,
            mrz_type=parsed_data.get("mrz_type"),
            valid_score=parsed_data.get("valid_score"),
            document_type=parsed_data.get("type"),
            country_code=parsed_data.get("country"),
            passport_number=parsed_data.get("number"),
            date_of_birth=parsed_data.get("date_of_birth"),
            expiration_date=parsed_data.get("expiration_date"),
            nationality=parsed_data.get("nationality"),
            sex=parsed_data.get("sex"),
            given_names=parsed_data.get("names"),
            surname=parsed_data.get("surname"),
            personal_number=parsed_data.get("personal_number"),
            check_number=parsed_data.get("check_number"),
            check_date_of_birth=parsed_data.get("check_date_of_birth"),
            check_expiration_date=parsed_data.get("check_expiration_date"),
            check_composite=parsed_data.get("check_composite"),
            check_personal_number=parsed_data.get("check_personal_number"),
            valid_number=parsed_data.get("valid_number"),
            valid_date_of_birth=parsed_data.get("valid_date_of_birth"),
            valid_expiration_date=parsed_data.get("valid_expiration_date"),
            valid_composite=parsed_data.get("valid_composite"),
            valid_personal_number=parsed_data.get("valid_personal_number"),
            is_valid=parsed_data.get("is_valid"),
        )
        logger.info(f"MRZData dict: {mrz_data.dict()}")

        return mrz_data

