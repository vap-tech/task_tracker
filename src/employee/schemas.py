from typing import Any

from src.task.schemas import ObjBase, NaiveDatetime, TaskCreate


class EmployeeBase(ObjBase):
    telegram: str = None
    date_end: NaiveDatetime = None


class EmployeeCreate(EmployeeBase):
    id: int = None
    full_name: str
    position: str
    date_begin: NaiveDatetime


class EmployeeUpdate(EmployeeBase):
    full_name: str = None
    position: str = None
    date_begin: NaiveDatetime = None


class EmployeeGet(ObjBase):
    full_name: str
    position: str
    date_begin: NaiveDatetime
    date_end: Any
    telegram: Any
