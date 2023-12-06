from sqlalchemy import TIMESTAMP, Column, Integer, String

from src.database import Base


class Employee(Base):
    """Сотрудник"""
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    task_count = Column(Integer)
    position = Column(String)
    telegram = Column(String)
    date_begin = Column(TIMESTAMP)
    date_end = Column(TIMESTAMP)
