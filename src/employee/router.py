from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.employee.models import Employee
from src.employee.schemas import EmployeeCreate, EmployeeUpdate, EmployeeGet
from src.function.for_router import get_obj, get_obj_by_id, post_obj, patch_obj, delete_obj, get_employee_with_tasks

router = APIRouter(
    prefix="/employee",
    tags=["Employee"]
)


@router.post("")
async def add_employee(new_employee: EmployeeCreate, session: AsyncSession = Depends(get_async_session)):

    """
    Добавляет нового сотрудника в БД.\n
    id: no required, auto set\n
    full_name: required\n
    position: required\n
    date_begin: required
    """

    response = await post_obj(
        Employee.__table__,
        new_employee,
        session=session
    )

    return response


@router.get("/")
@cache(expire=10)
async def get_employees(
        limit: int = 10,
        page: int = 1,
        search: str = '',
        session: AsyncSession = Depends(get_async_session),
):

    """Получает список сотрудников с пагинацией."""

    response = await get_obj(
        Employee.__table__,
        Employee.__table__.c.full_name,
        EmployeeGet,
        limit=limit,
        page=page,
        search=search,
        session=session
    )

    return response


@router.get('/{employee_id}')
@cache(expire=10)
async def get_employee(employee_id: int, session: AsyncSession = Depends(get_async_session)):

    """Получает сотрудника по id."""

    response = await get_obj_by_id(
        employee_id,
        Employee.__table__,
        EmployeeGet,
        session=session
    )

    return response


@router.patch('/')
async def update_employee(obj: EmployeeUpdate, session: AsyncSession = Depends(get_async_session)):

    """
    Обновляет объект в БД.
    \n
    id: required
    """

    response = await patch_obj(
        Employee.__table__,
        EmployeeUpdate,
        obj,
        session=session
    )

    return response


@router.delete('/{employee_id}')
async def delete_employee(employee_id: int, session: AsyncSession = Depends(get_async_session)):
    """Удаляет сотрудника из БД по полученному id."""

    response = await delete_obj(
        employee_id,
        Employee.__table__,
        session=session
    )

    return response


@router.get('/employee_with_tasks/')
async def employee_with_tasks(session: AsyncSession = Depends(get_async_session)):

    """
    Получает из БД список сотрудников и их задачи,
    отсортированный по количеству активных задач.
    """

    response = await get_employee_with_tasks(session=session)

    return response
