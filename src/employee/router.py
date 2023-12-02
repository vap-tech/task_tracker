from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_cache.decorator import cache
from sqlalchemy import insert, select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.employee.models import Employee
from src.employee.schemas import EmployeeCreate

router = APIRouter(
    prefix="/employee",
    tags=["Employee"]
)


async def get_id(model, session: AsyncSession = Depends(get_async_session)):
    """
    Получает следующий свободный id
    :param model: Класс модели алхимии
    :param session: Сессия
    :return: Свободный id
    """
    query = select(model.__table__).order_by(desc(model.__table__.c.id)).limit(1)
    result = await session.execute(query)
    result = result.all()

    if result:
        id_ = result[0].id + 1
    else:
        id_ = 0

    return id_


@router.get("/")
@cache(expire=10)
async def get_employees(
        limit: int = 10,
        page: int = 1,
        search: str = '',
        session: AsyncSession = Depends(get_async_session),
):
    skip = (page - 1) * limit
    try:
        query = select(Employee.__table__).filter(
            Employee.__table__.c.full_name.contains(search)).limit(limit).offset(skip)
        result = await session.execute(query)
        result = result.all()

        result = [EmployeeCreate.model_validate(i, from_attributes=True) for i in result]

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
async def add_employee(new_employee: EmployeeCreate, session: AsyncSession = Depends(get_async_session)):

    id_ = await get_id(Employee, session=session)
    new_employee.id = id_
    stmt = insert(Employee).values(**new_employee.model_dump())
    await session.execute(stmt)
    await session.commit()
    return {
        "status": "success",
        "data": None,
        "details": None
    }


@router.patch('/{employee_id}')
async def update_employee(employee_id: int, payload: EmployeeCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Employee.__table__).filter(Employee.__table__.c.id == employee_id)
    result = await session.execute(stmt)
    employee = result.first()

    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Сотрудник id: {employee_id} не найден')

    update_data = payload.model_dump(exclude_unset=True)
    stmt = update(Employee.__table__).filter(Employee.__table__.c.id == employee_id).values(**update_data)
    await session.execute(stmt)
    await session.commit()

    return {
        "status": "success",
        "data": None,
        "details": None
    }


@router.get('/{employee_id}')
async def get_employee(employee_id: int, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Employee.__table__).filter(Employee.__table__.c.id == employee_id)
    result = await session.execute(stmt)
    employee = result.first()

    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Сотрудник id: {employee_id} не найден")

    employee = [EmployeeCreate.model_validate(row, from_attributes=True) for row in employee]

    return {
        "status": "success",
        "data": employee,
        "details": None
    }


@router.delete('/{employee_id}')
async def delete_employee(employee_id: int, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Employee.__table__).filter(Employee.__table__.c.id == employee_id)
    result = await session.execute(stmt)
    employee = result.first()

    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Сотрудник id: {employee_id} не найден")

    try:
        query = delete(Employee.__table__).filter(Employee.__table__.c.id == employee_id)
        await session.execute(query)
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
