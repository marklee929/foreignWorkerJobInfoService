from __future__ import annotations

from ..models import RawSourceData
from .db_writer import SQLiteDBWriter


class RawDataRepository:
    def __init__(self, writer: SQLiteDBWriter):
        self.writer = writer

    def save(self, raw: RawSourceData) -> int:
        return self.writer.insert_raw(raw)
