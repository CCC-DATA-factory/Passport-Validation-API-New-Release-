# domain/logic/mrz_adapter.py

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import cv2
from skimage import io
from mrzscanner import MRZScanner
from turbojpeg import TurboJPEG
from pathlib import Path
import os


# ----------------------------
# 1. Abstract Interface
# ----------------------------

class BaseMRZDetector(ABC):
    """Abstract interface for MRZ detection & recognition."""

    @abstractmethod
    def detect(self, image: np.ndarray) -> Dict[str, Any]:
        """Perform MRZ detection and recognition on the input image."""
        pass


# ----------------------------
# 2. MRZScanner Concrete Implementation
# ----------------------------

class MRZScannerAdapter(BaseMRZDetector):
    """Concrete adapter that wraps the MRZScanner model."""

    def __init__(
        self,
        turbojpeg_lib_path: Optional[str] = None,
        do_center_crop: bool = False,
        do_postprocess: bool = True,
    ):
        """
        Initialize MRZScanner adapter.

        Args:
            turbojpeg_lib_path: Optional path to TurboJPEG DLL/so.
            do_center_crop: Whether to crop center before inference.
            do_postprocess: Whether to perform postprocessing.
        """
        self.jpeg = None
        if turbojpeg_lib_path:
            turbojpeg_lib_path = Path(turbojpeg_lib_path)
            if not turbojpeg_lib_path.exists():
                raise FileNotFoundError(f"TurboJPEG library not found: {turbojpeg_lib_path}")
            self.jpeg = TurboJPEG(lib_path=str(turbojpeg_lib_path))
        else:
            # try to read path from env if available
            env_path = os.getenv("TURBOJPEG_DLL_PATH")
            if env_path:
                self.jpeg = TurboJPEG(lib_path=env_path)
            else:
                # try default constructor (system wide)
                self.jpeg = TurboJPEG()

        # Initialize MRZScanner model
        self.model = MRZScanner()
        self.do_center_crop = do_center_crop
        self.do_postprocess = do_postprocess

    # ----------------------------
    # 3. MRZ Detection & Inference
    # ----------------------------

    def detect(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Run MRZ detection and recognition on an image.

        Args:
            image: numpy RGB array

        Returns:
            {
                "mrz_texts": [line1, line2],
                "mrz_polygon": np.ndarray,
                "msg": "No error." | str,
            }
        """
        if image is None or not isinstance(image, np.ndarray):
            raise ValueError("Invalid image provided to MRZScannerAdapter.")

        try:
            # Convert to BGR for MRZScanner
            bgr_img = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            result = self.model(
                bgr_img,
                do_center_crop=self.do_center_crop,
                do_postprocess=self.do_postprocess,
            )

            # Ensure expected structure
            mrz_texts = result.get("mrz_texts", [])
            polygon = result.get("mrz_polygon", None)
            msg = str(result.get("msg", "Unknown"))

            if not mrz_texts:
                raise ValueError(f"MRZScanner returned no MRZ lines. msg={msg}")

            # Return consistent dict
            return {
                "mrz_texts": mrz_texts,
                "mrz_polygon": polygon,
                "msg": msg,
            }

        except Exception as e:
            raise RuntimeError(f"MRZScanner inference failed: {e}") from e
