import time

from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from sqlalchemy import insert, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.operations.models import Operation
from src.operations.schemas import OperationCreate

from src.employee.router import get_id

router = APIRouter(
    prefix="/operations",
    tags=["Operation"]
)


@router.get("/long_operation")
@cache(expire=30)
def get_long_op():
    time.sleep(2)
    return "Много много данных, которые вычислялись сто лет"


@router.get("")
async def get_specific_operations(
        operation_type: str,
        session: AsyncSession = Depends(get_async_session),
):
    try:
        query = select(Operation.__table__).filter(Operation.__table__.c.type == operation_type)
        result = await session.execute(query)
        result = result.all()

        result = [OperationCreate.model_validate(i, from_attributes=True) for i in result]

        return {
            "status": "success",
            "data": result,
            "details": None
        }
    except Exception:
        # Передать ошибку разработчикам
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None
        })


@router.post("")
async def add_specific_operations(new_operation: OperationCreate, session: AsyncSession = Depends(get_async_session)):

    id_ = await get_id(Operation, session=session)
    new_operation.id = id_
    stmt = insert(Operation).values(**new_operation.model_dump())
    await session.execute(stmt)
    await session.commit()
    return {"status": "success"}


@router.get("/main")
async def main(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Operation.__table__))
    result = [OperationCreate.model_validate(row, from_attributes=True) for row in result.all()]
    return result

