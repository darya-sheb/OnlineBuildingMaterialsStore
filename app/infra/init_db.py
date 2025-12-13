import asyncio
from app.infra.db import init_models

if __name__ == "__main__":
    asyncio.run(init_models())
