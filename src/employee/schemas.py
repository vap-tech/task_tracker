from typing import Any

from src.task.schemas import ObjBase, NaiveDatetime


class EmployeeBase(ObjBase):
    telegram: str = None


class EmployeeCreate(EmployeeBase):
    full_name: str
    position: str
    date_begin: NaiveDatetime
    task_count: int


class EmployeeUpdate(EmployeeBase):
    full_name: str = None
    position: str = None


class EmployeeGet(ObjBase):
    full_name: str
    position: str
    date_begin: NaiveDatetime
    task_count: int
    date_end: Any
    telegram: Any
