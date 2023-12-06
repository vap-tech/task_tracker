from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from .models import Employee
from .schemas import EmployeeCreate, EmployeeUpdate, EmployeeGet
from .functions import get_employee_with_tasks, get_free_employee, assign_task_to_emp
from src.function.crud_object import get_obj, get_obj_by_id, post_obj, patch_obj, delete_obj

router = APIRouter(
    prefix="/employee",
    tags=["Employee"]
)


@router.post("")
async def add_employee(new_employee: EmployeeCreate, session: AsyncSession = Depends(get_async_session)):

    """
    Добавляет нового сотрудника в БД.\n
    id: required, auto set\n
    task_count: required, auto set\n
    full_name: required\n
    position: required\n
    date_begin: required
    """

    new_employee.task_count = 0

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
    Обновляет сотрудника в БД.\n
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


@router.post('/assign_task/')
async def assign_task_to_employee(
        task_id: int,
        emp_id: int,
        emp_tc: int = 0,
        session: AsyncSession = Depends(get_async_session)
):

    """Присваивает задачу сотруднику"""

    response = await assign_task_to_emp(
        task_id,
        emp_id,
        emp_tc,
        session=session
    )

    return response


@router.get('/employee_with_tasks/')
async def employee_with_tasks(
        full_name: str = '',
        task: str = '',
        session: AsyncSession = Depends(get_async_session)):

    """
    Получает из БД список сотрудников и их задачи,
    отсортированный по количеству активных задач.\n
    Максимальное произведение количества сотрудников на количество задач равно 999.\n
    В случае ошибки по превышению, пожалуйста, используйте критерии поиска.
    """

    response = await get_employee_with_tasks(
        full_name,
        task,
        session=session
    )

    return response


@router.get('/free_employee/')
async def free_employee(task_id: int, session: AsyncSession = Depends(get_async_session)):

    """
    Ищет сотрудника, который может взять важную задачу.\n
    Это будет наименее загруженный сотрудник или сотрудник выполняющий родительскую задачу\n
    если ему назначено максимум на 2 задачи больше, чем у наименее загруженного сотрудника.
    """

    response = await get_free_employee(
        task_id,
        session=session
    )

    return response
