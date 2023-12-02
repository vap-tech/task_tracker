from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_cache.decorator import cache
from sqlalchemy import insert, select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.task.models import Task
from src.task.schemas import TaskCreate
from src.employee.router import get_id

router = APIRouter(
    prefix="/task",
    tags=["Task"]
)


@router.get("/")
@cache(expire=10)
async def get_task(
        limit: int = 10,
        page: int = 1,
        search: str = '',
        session: AsyncSession = Depends(get_async_session),
):
    skip = (page - 1) * limit
    try:
        query = select(Task.__table__).filter(
            Task.__table__.c.full_name.contains(search)).limit(limit).offset(skip)
        result = await session.execute(query)
        result = result.all()

        result = [TaskCreate.model_validate(i, from_attributes=True) for i in result]

        return {
            "status": "success",
            "data": result,
            "details": None
        }
    except Exception:
        # Передать ошибку разработчикам
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
            "status": "error",
            "data": None,
            "details": None
        })


@router.post("")
async def add_task(new_task: TaskCreate, session: AsyncSession = Depends(get_async_session)):

    id_ = await get_id(Task, session=session)
    new_task.id = id_
    stmt = insert(Task).values(**new_task.model_dump())
    await session.execute(stmt)
    await session.commit()
    return {
        "status": "success",
        "data": None,
        "details": None
    }


@router.patch('/{task_id}')
async def update_task(task_id: int, payload: TaskCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Task.__table__).filter(Task.__table__.c.id == task_id)
    result = await session.execute(stmt)
    task = result.first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Задача id: {task_id} не найдена')

    update_data = payload.model_dump(exclude_unset=True)
    stmt = update(Task.__table__).filter(Task.__table__.c.id == task_id).values(**update_data)
    await session.execute(stmt)
    await session.commit()

    return {
        "status": "success",
        "data": None,
        "details": None
    }


@router.get('/{task_id}')
async def get_task(task_id: int, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Task.__table__).filter(Task.__table__.c.id == task_id)
    result = await session.execute(stmt)
    task = result.first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Задача id: {task_id} не найдена")

    task = [TaskCreate.model_validate(row, from_attributes=True) for row in task]

    return {
        "status": "success",
        "data": task,
        "details": None
    }


@router.delete('/{task_id}')
async def delete_task(task_id: int, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Task.__table__).filter(Task.__table__.c.id == task_id)
    result = await session.execute(stmt)
    task = result.first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Задача id: {task_id} не найдена")

    try:
        stmt = delete(Task.__table__).filter(Task.__table__.c.id == task_id)
        await session.execute(stmt)
        await session.commit()

        return {
            "status": "success",
            "data": None,
            "details": None
        }

    except Exception:
        # Передать ошибку разработчикам
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={
            "status": "error",
            "data": None,
            "details": None
        })
