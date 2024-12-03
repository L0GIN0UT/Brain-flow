from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models.device_type import DeviceType, DeviceTypeFilter
from db.postgres import AsyncSession
from typing import Tuple, List, Any


async def get_device_types_filter(device_type_filter: DeviceTypeFilter, session: AsyncSession) -> tuple[list[Any], None] | tuple[None, Any]:
    try:
        query = select(DeviceType).options(selectinload(DeviceType.device))
        query = device_type_filter.filter(query)
        result = await session.execute(query)
        device_types = result.scalars().unique().all()
        return device_types, None
    except Exception as e:
        print(f"Error: {e}")
        return None, e
    finally:
        await session.close()