import os
from pathlib import Path
from typing import Optional
from app.core.settings import settings


def check_media_file_exists(relative_path: str) -> bool:
    """Проверяет существует ли файл относительно /app/media"""
    if not relative_path:
        return False

    if relative_path.startswith('/'):
        relative_path = relative_path[1:]

    full_path = Path(settings.MEDIA_ROOT) / relative_path
    return full_path.exists() and full_path.is_file()


def get_media_url(relative_path: Optional[str]) -> str:
    """Получает URL для медиа-файла или возвращает заглушку"""
    if not relative_path or not check_media_file_exists(relative_path):
        return f"/{settings.MEDIA_ROOT}/no_image_data.jpg"

    relative_path = relative_path.lstrip('/')
    return f"/{settings.MEDIA_ROOT}/{relative_path}"
