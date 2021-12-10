from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class CheckedItems(Base):
    __tablename__ = "checked_items"

    id = Column(Integer, primary_key=True)
    product_code = Column(String(250), nullable=False)
    location = Column(String(250), nullable=False)
    item_from = Column(String(250), nullable=False)
    item_type = Column(String(250), nullable=False)
    time_scanned = Column(String, nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, product_code, location, item_from, item_type, time_scanned):
        self.product_code = product_code
        self.location = location
        self.item_from = item_from
        self.item_type = item_type
        self.time_scanned = time_scanned
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        dict = {}
        dict['id'] = self.id
        dict['product_code'] = self.product_code
        dict['location'] = self.location
        dict['item_from'] = self.item_from
        dict['item_type'] = self.item_type
        dict['time_scanned'] = self.time_scanned
        dict['date_created'] = self.date_created

        return dict