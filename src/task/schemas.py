from datetime import datetime

from pydantic import BaseModel


class TaskCreate(BaseModel):
    """Задача"""

    id: int
    name: str
    parent_task_id: int
    employee_id: int
    date_begin: datetime
    date_end: datetime
    status: str
