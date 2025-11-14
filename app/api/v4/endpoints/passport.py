# app/api/v4/endpoints/passport.py

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    Request
)
from fastapi.responses import JSONResponse
from schemas.request import PassportRequest
from schemas.response import PassportResponse
from app.api.v4.deps import get_passport_service
from domain.logic.passport_service import PassportService
from core.logging import logger
import tempfile
import os

router = APIRouter(
    prefix="/v4",
    tags=["passport"],
)

# ----------------------------
# 🔹 Unified Endpoint: POST /v4/passport
# ----------------------------
@router.post("/validate", response_model=PassportResponse)
async def process_passport(
    request: Request,
    service: PassportService = Depends(get_passport_service),
    file: UploadFile = File(None, description="Passport image file (jpg, png, etc.)"),
    source: str = Form(None, description="Image source path, base64 string, or URL"),
):
    """
    Process a passport image to extract MRZ data.
    Supports both:
    - JSON/Form input with `source` (path, URL, or base64)
    - File upload (`multipart/form-data`)
    """
    tmp_path = None

    try:
        # Case 1️⃣: File upload (multipart)
        if file is not None:
            if not (file.content_type and file.content_type.startswith("image/")):
                raise HTTPException(status_code=400, detail="Uploaded file must be an image")

            suffix = os.path.splitext(file.filename)[1] or ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(await file.read())
                tmp_path = tmp.name

            logger.info(f"Processing uploaded image file: {file.filename}")
            mrz_data = service.process_passport(tmp_path)

        # Case 2️⃣: JSON or form field source (URL, base64, or local path)
        elif source:
            logger.info(f"Processing image source: {source[:50]}...")
            mrz_data = service.process_passport(source)

        # Case 3️⃣: No valid input provided
        else:
            raise HTTPException(status_code=400, detail="Please provide an image file or source")

        # Ensure mrz_texts is a flat list of strings ✅
        mrz_dict = mrz_data.dict()
        if "mrz_texts" in mrz_dict and isinstance(mrz_dict["mrz_texts"], list):
            flat_texts = []
            for item in mrz_dict["mrz_texts"]:
                if isinstance(item, list):
                    flat_texts.extend(item)
                else:
                    flat_texts.append(item)
            mrz_dict["mrz_texts"] = flat_texts

        # Return as response
        return PassportResponse(**mrz_dict)

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        logger.exception("Unexpected error in /v4/passport")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

    finally:
        # Clean up temporary file if created
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                logger.warning(f"Failed to delete temp file: {tmp_path}")
