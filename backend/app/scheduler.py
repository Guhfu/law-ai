import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .db import get_session
from .services.parser import update_laws_from_source


async def run_update_job() -> None:
    async with get_session() as session:
        await update_laws_from_source(session)


def create_scheduler() -> AsyncIOScheduler:
    """
    Создает APScheduler с еженедельним завданням оновлення законів.
    Фактичний запуск планувальника виконується з окремого скрипта або при старті сервера.
    """
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(run_update_job, "cron", day_of_week="mon", hour=3, minute=0)
    return scheduler


async def main() -> None:
    scheduler = create_scheduler()
    scheduler.start()
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

