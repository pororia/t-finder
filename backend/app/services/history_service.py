from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.toilet_history import ToiletHistory
from typing import Optional


class HistoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_change(
        self,
        toilet_id: str,
        old_data: dict,
        new_data: dict,
        change_type: str,
        changed_by: str,
    ):
        changed_fields = [k for k in new_data if old_data.get(k) != new_data.get(k)]
        if change_type == "CREATE":
            changed_fields = list(new_data.keys())

        history = ToiletHistory(
            toilet_id=toilet_id,
            snapshot=old_data,
            changed_fields=changed_fields if changed_fields else None,
            change_type=change_type,
            changed_by=changed_by,
        )
        self.db.add(history)
        await self.db.flush()
