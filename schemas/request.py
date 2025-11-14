# schemas/request.py

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional


class PassportRequest(BaseModel):
    """
    Input schema for passport MRZ API.
    The source can be:
      - local file path
      - URL
      - base64 string
    """
    source: str = Field(
        ...,
        description="Passport image source: local path, URL, or base64 string"
    )
