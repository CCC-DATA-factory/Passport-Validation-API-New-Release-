# utils/image.py

import cv2
import base64
import numpy as np
import requests
from io import BytesIO
from typing import Union
from pathlib import Path
from PIL import Image


# ----------------------------
# 1. Load Image from Local Path
# ----------------------------

def load_image_from_path(path: Union[str, Path]) -> np.ndarray:
    """Load image from a local file path."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Image path not found: {path}")
    img = cv2.imread(str(path))
    if img is None:
        raise ValueError(f"Could not read image from path: {path}")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


# ----------------------------
# 2. Load Image from URL
# ----------------------------

def load_image_from_url(url: str, timeout: int = 10) -> np.ndarray:
    """Load image from a remote URL and return as RGB numpy array."""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert("RGB")
        return np.array(image)
    except Exception as e:
        raise ValueError(f"Failed to load image from URL: {url} ({e})")


# ----------------------------
# 3. Load Image from Base64
# ----------------------------

def load_image_from_base64(b64_str: str) -> np.ndarray:
    """
    Decode base64-encoded image string into RGB numpy array.
    Accepts full data URI (e.g. 'data:image/jpeg;base64,...') or raw base64.
    """
    try:
        if b64_str.startswith("data:image"):
            b64_str = b64_str.split(",")[1]
        image_bytes = base64.b64decode(b64_str)
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        return np.array(image)
    except Exception as e:
        raise ValueError(f"Failed to decode base64 image ({e})")


# ----------------------------
# 4. Unified Loader (Auto-detect)
# ----------------------------

def load_image(source: str) -> np.ndarray:
    """
    Load image from path, URL, or base64 automatically.
    Returns numpy array in RGB format.
    """
    # Heuristic detection
    if source.startswith("http://") or source.startswith("https://"):
        return load_image_from_url(source)
    elif Path(source).exists():
        return load_image_from_path(source)
    elif source.strip().startswith("data:image") or len(source.strip()) > 1000:
        # long base64 strings usually > 1000 chars
        return load_image_from_base64(source)
    else:
        raise ValueError("Unsupported image source format.")
