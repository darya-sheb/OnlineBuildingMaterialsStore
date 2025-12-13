from fastapi.templating import Jinja2Templates
from app.core.settings import settings

templates = Jinja2Templates(directory=settings.TEMPLATES_ROOT)
