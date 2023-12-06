from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import Depends

from ..database import get_async_session
from .schemas import TaskGetMinimal
from .models import Task
from ..config import DEBUG
from ..employee.models import Employee


async def get_important_tasks(task: str, session: AsyncSession = Depends(get_async_session)):

    """
    Получает из БД задачи не взятые в работу, от которых
    зависят другие задачи, взятые в работу.
    """

    stmt = select(
        Task.__table__.c.id,
        Task.__table__.c.name
    ).where(
        Task.__table__.c.parent_task_id > 0,
        Task.__table__.c.employee_id == 0
    ).filter(
        Task.__table__.c.name.contains(task)
    ).limit(
        1000
    )

    if DEBUG:
        print(stmt)

    data = (await session.execute(stmt)).all()

    if len(data) == 1000:
        return {
            "status": "error",
            "data": None,
            "details": "Слишком много данных, уточните запрос!"
        }

    if not data:
        return {
            "status": "success",
            "data": None,
            "details": "Важные задачи отсутствуют."
        }

    result = [TaskGetMinimal.model_validate(
        row,
        from_attributes=True) for row in data]

    return {
        "status": "success",
        "data": result,
        "details": None
    }


async def get_important_tasks_and_emp(
        task: str,
        session: AsyncSession = Depends(get_async_session)):

    """
    Возвращает Список объектов [{Важная задача, Срок, [ФИО сотрудника]}]
    """

    stmt = select(
        Task.id,
        Task.name,
        Task.date_end,
        Employee.id,
        Employee.full_name
    ).filter(Task.parent_task_id > 0).join(
        Employee, Employee.id == Task.employee_id
    )

    if DEBUG:
        print(stmt)

    result = (await session.execute(stmt)).all()

    response = []

    for i in result:
        response.append(
            {
                'id': i[0],
                'task': i[1],
                'date_end': i[2],
                'employee': [
                    f'id: {i[3]}, ФИО: {i[4]}'
                ]
            }
        )

    return {
        "status": "success",
        "data": response,
        "details": None
    }
