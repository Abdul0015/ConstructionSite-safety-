from fastapi import UploadFile, HTTPException, status

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB limit

# Magic byte signatures for image formats
JPEG_MAGIC_BYTES = b"\xff\xd8\xff"
PNG_MAGIC_BYTES = b"\x89PNG\r\n\x1a\n"

def validate_uploaded_image(file: UploadFile, contents: bytes) -> None:
    """
    Validates uploaded hazard report image file against size limits, MIME type whitelist, 
    and magic byte content verification.
    """
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed limit of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB."
        )

    # 1. Content-Type Header check
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Disallowed file MIME type '{file.content_type}'. Only JPEG and PNG image files are allowed."
        )

    # 2. Magic byte content verification (never trust client-provided file extension alone)
    is_jpeg = contents.startswith(JPEG_MAGIC_BYTES)
    is_png = contents.startswith(PNG_MAGIC_BYTES)

    if not (is_jpeg or is_png):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content does not match a valid JPEG or PNG image binary header."
        )
