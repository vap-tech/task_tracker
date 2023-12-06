from sqlalchemy import TIMESTAMP, Column, Integer, String

from ..database import Base


class Task(Base):
    """Задача"""
    __tablename__ = "task"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    parent_task_id = Column(Integer)
    employee_id = Column(Integer)
    date_begin = Column(TIMESTAMP)
    date_end = Column(TIMESTAMP)
    status = Column(String)
