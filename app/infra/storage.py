from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile

from app.core.settings import settings


async def save_product_image(upload: UploadFile) -> str:
    root = Path(settings.MEDIA_ROOT) / "products"
    root.mkdir(parents=True, exist_ok=True)

    suffix = Path(upload.filename or "").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".jpg"

    filename = f"{uuid4().hex}{suffix}"
    path = root / filename

    data = await upload.read()
    await upload.close()
    path.write_bytes(data)

    return f"products/{filename}"
