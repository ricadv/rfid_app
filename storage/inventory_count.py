from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class InventoryCount(Base):
    __tablename__ = "inventory_count"

    id = Column(Integer, primary_key=True)
    total_count = Column(Integer, nullable=False)
    expected_count = Column(Integer, nullable=False)
    items_missing = Column(Integer, nullable=False)
    surplus = Column(Integer, nullable=False)
    time_scanned = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, total_count, expected_count, items_missing, surplus, time_scanned):
        self.total_count = total_count
        self.expected_count = expected_count
        self.items_missing = items_missing
        self.surplus = surplus
        self.time_scanned = time_scanned
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        dict = {}
        dict['id'] = self.id
        dict['total_count'] = self.total_count
        dict['expected_count'] = self.expected_count
        dict['items_missing'] = self.items_missing
        dict['surplus'] = self.surplus
        dict['time_scanned'] = self.time_scanned
        dict['date_created'] = self.date_created

        return dict