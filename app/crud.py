import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Car

logger = logging.getLogger(__name__)


async def save_car(session: AsyncSession, data: dict) -> None:
    car = await session.scalar(
        select(Car).where(Car.url == data['url'])
    )
    if car is None:
        car = Car(**data)
        session.add(car)
    else:
        for key, value in data.items():
            setattr(car, key, value)
    await session.commit()

    logger.info(f"Successfully saved/updated data for {data['url']}")
