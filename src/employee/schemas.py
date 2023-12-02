from datetime import datetime

from pydantic import BaseModel


class EmployeeCreate(BaseModel):
    id: int
    full_name: str
    position: str
    telegram: str
    date_begin: datetime
    date_end: datetime
