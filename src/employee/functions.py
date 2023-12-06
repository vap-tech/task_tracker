from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from fastapi import Depends

from src.database import get_async_session
from .models import Employee
from ..task.models import Task
from src.config import DEBUG


async def get_employee_with_tasks(
        full_name: str,
        task: str,
        session: AsyncSession = Depends(get_async_session)):

    """
    Получает из БД список сотрудников и их задачи,
    отсортированный по количеству активных задач.
    :full_name * :task < 1000!
    """

    stmt = select(
        Employee.__table__.c.id,
        Employee.__table__.c.full_name,
        Task.__table__.c.id,
        Task.__table__.c.name,
    ).filter(
        Employee.__table__.c.full_name.contains(full_name),
        Task.__table__.c.name.contains(task)
    ).join(
        Task.__table__,
        Task.__table__.c.employee_id == Employee.__table__.c.id,
        isouter=True
    ).limit(1000)

    if DEBUG:
        print(stmt)

    data = (await session.execute(stmt)).all()

    if len(data) == 1000:
        return {
            "status": "error",
            "data": None,
            "details": "Слишком много данных, уточните запрос!"
        }

    result = {}

    for i in data:

        if not result.get(i[0]):

            result[i[0]] = {
                'full_name': i[1],
                'task_count': 1,
                'task': [
                    {
                        'id': i[2],
                        'name': i[3]
                    }
                ]
            }

            continue

        result[i[0]]['task'].append(
            {
                'id': i[2],
                'name': i[3]
            }
        )
        result[i[0]]['task_count'] += 1

    def by_task_count(item):

        """Возвращает количество задач
        получая кортеж (id, user)"""

        _, user = item
        task_count = user['task_count']

        return task_count

    sorted_result = dict(sorted(result.items(), key=by_task_count))

    return {
        "status": "success",
        "data": sorted_result,
        "details": None
    }


async def assign_task_to_emp(
        task_id: int,
        emp_id: int,
        emp_tc: int = None,
        session: AsyncSession = Depends(get_async_session)):

    """Присваивает задачу сотруднику"""

    stmt = update(
        Task.__table__
    ).where(
        Task.__table__.c.id == task_id
    ).values(employee_id=emp_id)

    await session.execute(stmt)

    # Если task_count не передавался
    if not emp_tc:
        stmt = select(
            Employee.__table__.c.id,
            Employee.__table__.c.task_count
        ).where(
            Employee.__table__.c.id == emp_id
        )
        _, emp_tc = (await session.execute(stmt)).first()

    emp_tc += 1

    stmt = update(
        Employee.__table__
    ).where(
        Employee.__table__.c.id == emp_id
    ).values(task_count=emp_tc)

    await session.execute(stmt)
    await session.commit()

    return {
        "status": "success",
        "data": None,
        "details": "assigned"
    }


async def get_free_employee(task_id: int, session: AsyncSession = Depends(get_async_session)):

    """
    Ищет сотрудника, который может взять важную задачу.
    Это будет наименее загруженный сотрудник или сотрудник выполняющий родительскую задачу
    если ему назначено максимум на 2 задачи больше, чем у наименее загруженного сотрудника.
    """

    # Получаем наименее загруженного сотрудника
    stmt = select(
        Employee.__table__.c.id,
        Employee.__table__.c.full_name,
        Employee.__table__.c.task_count
    ).order_by(
        Employee.__table__.c.task_count
    )

    emp_min_id, emp_min_name, emp_min_tc = (await session.execute(stmt)).first()

    # Получаем id родительской задачи
    stmt = select(
        Task.__table__.c.parent_task_id
    ).where(
        Task.__table__.c.id == task_id
    )

    result = (await session.execute(stmt)).first()
    prnt_task_id: int = result[0]

    # Если отсутствует родительская задача
    if not prnt_task_id:

        return {
            "status": "success",
            "data": {
                "id": emp_min_id,
                "full_name": emp_min_name
            },
            "details": "отсутствует родительская задача"
        }

    # Получаем id сотрудника родительской задачи
    stmt = select(
        Task.__table__.c.employee_id
    ).where(
        Task.__table__.c.id == prnt_task_id
    )

    result = (await session.execute(stmt)).first()
    prnt_emp_id: int = result[0]

    # Если родительская задача не назначена
    if not prnt_emp_id:

        return {
            "status": "success",
            "data": {
                "id": emp_min_id,
                "full_name": emp_min_name
            },
            "details": "родительская задача не назначена"
        }

    # Получаем количество задач сотрудника родительской задачи
    stmt = select(
        Employee.__table__.c.full_name,
        Employee.__table__.c.task_count,
    ).where(
        Employee.__table__.c.id == prnt_emp_id
    )

    prnt_emp_fn, prnt_emp_tc = (await session.execute(stmt)).first()

    # Если у родителя больше как минимум на 2
    if prnt_emp_tc - emp_min_tc > 2:

        return {
            "status": "success",
            "data": {
                "id": emp_min_id,
                "full_name": emp_min_name
            },
            "details": "у исполнителя родительской задачи больше как минимум на 2"
        }

    return {
        "status": "success",
        "data": {
                "id": prnt_emp_id,
                "full_name": prnt_emp_fn
            },
        "details": "исполнитель родительской задачи"
    }
