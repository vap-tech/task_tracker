from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete, desc, Column, Table

from fastapi import Depends

from src.database import get_async_session
from src.config import DEBUG
from src.task.models import Task
from src.employee.models import Employee
from src.employee.schemas import EmployeeCreate
from src.task.schemas import TaskCreate, ObjBase


async def get_free_id(
        table: Table,
        session: AsyncSession = Depends(get_async_session)) -> int:

    """Возвращает следующий свободный id из заданной таблицы."""

    stmt = select(table.c.id).order_by(desc(table.c.id)).limit(1)

    if DEBUG:
        print(stmt)

    obj = (await session.execute(stmt)).first()

    if obj:
        free_id = obj.id + 1
    else:
        free_id = 1

    return free_id


async def check_exists_obj(
        table: Table,
        obj_id: int,
        session: AsyncSession = Depends(get_async_session)) -> bool:

    """Проверяет существование записи по id."""

    stmt = select(table.c.id).where(table.c.id == obj_id)
    if (await session.execute(stmt)).first():
        return True
    return False


async def post_obj(
        table: Table,
        obj: TaskCreate or EmployeeCreate,
        session: AsyncSession = Depends(get_async_session)) -> dict:

    """Вставляет полученный объект в полученную таблицу"""

    free_id = await get_free_id(table, session=session)
    obj.id = free_id

    data = obj.model_dump()

    stmt = insert(table).values(**data)

    if DEBUG:
        print(f'\nЗапрос добавления объекта в БД:\n{stmt}\n')

    await session.execute(stmt)
    await session.commit()

    return {
        "status": "success",
        "data": data,
        "details": "created"
    }


async def get_obj(
        table: Table,
        column: Column,
        scheme: TaskCreate or EmployeeCreate,
        limit: int,
        page: int,
        search: str,
        session: AsyncSession = Depends(get_async_session)) -> dict:

    """Получает объекты из БД с пагинацией и поиском"""

    skip = (page - 1) * limit

    stmt = select(table).filter(column.contains(search)).limit(limit).offset(skip)

    if DEBUG:
        print(f'\nЗапрос объектов:\n{stmt}\n')

    result = (await session.execute(stmt)).all()

    if not result:
        return {
            "status": "error",
            "data": "Ничего не найдено",
            "details": None
        }

    obj = [scheme.model_validate(i, from_attributes=True) for i in result]

    return {
        "status": "success",
        "data": obj,
        "details": None
    }


async def get_obj_by_id(
        object_id: int,
        table: Table,
        scheme: TaskCreate or EmployeeCreate,
        session: AsyncSession = Depends(get_async_session)) -> dict:

    """Получает объект из БД по id"""

    stmt = select(table).where(table.c.id == object_id)

    if DEBUG:
        print(f'\nЗапрос объекта по id:\n{stmt}\n')

    result = (await session.execute(stmt)).first()

    if not result:
        return {
            "status": "error",
            "data": f"id: {object_id} не найден",
            "details": None
        }

    obj = scheme.model_validate(result, from_attributes=True)

    return {
        "status": "success",
        "data": obj,
        "details": None
    }


async def patch_obj(
        table: Table,
        scheme: TaskCreate or EmployeeCreate,
        obj: ObjBase,
        session: AsyncSession = Depends(get_async_session)) -> dict:

    """Обновляет полученный объект в полученной таблице"""

    obj_is_exists = (await check_exists_obj(table, obj.id, session=session))

    if not obj_is_exists:
        return {
            "status": "error",
            "data": f"id: {obj.id} не найден",
            "details": None
        }

    update_data = {}

    for element in obj:
        if element[-1] and element[0] != 'id':
            update_data[element[0]] = element[-1]

    if not update_data:
        return {
            "status": "error",
            "data": f"Нет данных для обновления.",
            "details": None
        }

    stmt = update(table).where(table.c.id == obj.id).values(**update_data)

    if DEBUG:
        print(stmt)

    await session.execute(stmt)
    await session.commit()

    stmt = select(table).where(table.c.id == obj.id)
    data = (await session.execute(stmt)).first()
    data = scheme.model_validate(data, from_attributes=True)

    return {
        "status": "success",
        "data": data,
        "details": "updated"
    }


async def delete_obj(
        obj_id: int,
        table: Table,
        session: AsyncSession = Depends(get_async_session)) -> dict:

    """Удаляет объект из полученной таблицы по полученному id."""

    obj_is_exists = await check_exists_obj(table, obj_id, session=session)

    if not obj_is_exists:
        return {
            "status": "error",
            "data": f"id: {obj_id} не найден",
            "details": None
        }

    stmt = delete(table).where(table.c.id == obj_id)

    if DEBUG:
        print(stmt)

    await session.execute(stmt)
    await session.commit()

    return {
        "status": "success",
        "data": None,
        "details": "deleted"
    }


# specific employee


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
        получая кортеж (id, user) из result."""
        _, user = item
        task_count = user['task_count']
        return task_count

    sorted_result = dict(sorted(result.items(), key=by_task_count))

    return {
        "status": "success",
        "data": sorted_result,
        "details": None
    }


# specific task
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

    result = []

    for i in data:
        result.append(
            {
                'id': i[0],
                'name': i[1]
            }
        )

    return {
        "status": "success",
        "data": result,
        "details": None
    }
