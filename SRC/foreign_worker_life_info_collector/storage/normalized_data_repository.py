from __future__ import annotations

from ..models import LifeServiceBusiness
from .db_writer import SQLiteDBWriter


class NormalizedDataRepository:
    def __init__(self, writer: SQLiteDBWriter):
        self.writer = writer

    def save(self, business: LifeServiceBusiness) -> int:
        return self.writer.insert_business(business)
