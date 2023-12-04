from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.task.models import Task
from src.task.schemas import TaskCreate, TaskUpdate, TaskGet
from src.function.for_router import get_obj, get_obj_by_id, post_obj, patch_obj, delete_obj, get_important_tasks

router = APIRouter(
    prefix="/task",
    tags=["Task"]
)


@router.post("")
async def add_task(new_task: TaskCreate, session: AsyncSession = Depends(get_async_session)):

    """
    Добавляет новую задачу в БД.\n
    id: no required, auto set\n
    name: required\n
    status: required
    """

    response = await post_obj(
        Task.__table__,
        new_task,
        session=session
    )

    return response


@router.get("/")
@cache(expire=10)
async def get_task(
        limit: int = 10,
        page: int = 1,
        search: str = '',
        session: AsyncSession = Depends(get_async_session),
):

    """Получает список задач с пагинацией."""

    response = await get_obj(
        Task.__table__,
        Task.__table__.c.name,
        TaskGet,
        limit=limit,
        page=page,
        search=search,
        session=session
    )

    return response


@router.get('/{task_id}')
@cache(expire=10)
async def get_task(task_id: int, session: AsyncSession = Depends(get_async_session)):

    """Получает задачу по id."""

    response = await get_obj_by_id(
        task_id,
        Task.__table__,
        TaskGet,
        session=session)

    return response


@router.patch('/')
async def update_task(obj: TaskUpdate, session: AsyncSession = Depends(get_async_session)):

    """
    Обновляет объект в БД.
    \n
    id: required
    """

    response = await patch_obj(
        Task.__table__,
        TaskUpdate,
        obj,
        session=session
    )

    return response


@router.delete('/{task_id}')
async def delete_task(task_id: int, session: AsyncSession = Depends(get_async_session)):

    """Удаляет задачу из БД по полученному id."""

    response = await delete_obj(
        task_id,
        Task.__table__,
        session=session
    )

    return response


@router.get('/important_tasks/')
async def important_tasks(
        task: str = '',
        session: AsyncSession = Depends(get_async_session)):
    """
    Получает из БД задачи не взятые в работу, от которых
    зависят другие задачи, взятые в работу.\n
    Максимально можно получить 999 задач.\n
    В случае ошибки по превышению, пожалуйста, используйте критерии поиска.
    """

    response = await get_important_tasks(
        task,
        session=session
    )

    return response
