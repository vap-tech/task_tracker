from sqlalchemy import TIMESTAMP, Column, Integer, String

from src.database import Base


class Operation(Base):
    """Операция"""
    __tablename__ = "operation"

    id = Column(Integer, primary_key=True)
    quantity = Column(String)
    figi = Column(String)
    instrument_type = Column(String)
    date = Column(TIMESTAMP)
    type = Column(String)
