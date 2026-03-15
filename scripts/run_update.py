import asyncio

from backend.app.db import get_session
from backend.app.services.parser import update_laws_from_source


async def main() -> None:
    async with get_session() as session:
        await update_laws_from_source(session)


if __name__ == "__main__":
    asyncio.run(main())

