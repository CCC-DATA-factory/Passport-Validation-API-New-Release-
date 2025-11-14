# app/api/v4/deps.py

from fastapi import Depends
from domain.logic.passport_service import PassportService
from domain.logic.mrz_adapter import MRZScannerAdapter
from domain.logic.parser_adapter import PassportEyeParser
import os
# ----------------------------
# Dependency injection
# ----------------------------

def get_mrz_detector() -> MRZScannerAdapter:
    """
    Returns a ready-to-use MRZScannerAdapter.
    Can be replaced with a mock or different adapter for testing.
    """
    # Example: provide TurboJPEG path if needed
    turbojpeg_path = None
    # prefer environment variable; you can also set this in main config
    turbojpeg_path = os.getenv("TURBOJPEG_DLL_PATH")

    return MRZScannerAdapter(turbojpeg_lib_path=turbojpeg_path)  # optional on Windows
    
    

def get_mrz_parser() -> PassportEyeParser:
    """
    Returns a ready-to-use PassportEyeParser.
    Can be replaced with a mock parser for testing.
    """
    return PassportEyeParser()


def get_passport_service(
    detector: MRZScannerAdapter = Depends(get_mrz_detector),
    parser: PassportEyeParser = Depends(get_mrz_parser),
) -> PassportService:
    """
    Provides a PassportService instance with real detector + parser injected.
    """
    return PassportService(mrz_detector=detector, mrz_parser=parser)
