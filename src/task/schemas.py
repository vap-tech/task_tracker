from typing import Any

from pydantic import BaseModel, NaiveDatetime


class ObjBase(BaseModel):
    id: int


class TaskBase(ObjBase):
    """Задача"""
    parent_task_id: int = None
    employee_id: int = None
    date_begin: NaiveDatetime = None
    date_end: NaiveDatetime = None


class TaskCreate(TaskBase):
    """Задача"""
    id: int = None
    name: str
    status: str


class TaskUpdate(TaskBase):
    name: str = None
    status: str = None


class TaskGet(ObjBase):
    name: str
    parent_task_id: Any
    employee_id: Any
    date_begin: Any
    date_end: Any
    status: str
