from fastapi import APIRouter, BackgroundTasks, Depends

from src.auth.base_config import current_user

from .report import send_email_report_dashboard

router = APIRouter(
    prefix="/report",
    tags=["Report"]
)


@router.get("/dashboard")
def get_dashboard_report(background_tasks: BackgroundTasks, user=Depends(current_user)):
    """
    Тестируем разные способы обработки долгой задачи
    Первый случай - страничка клиента зависает на время выполнения задачи
    Второй и третий - клиент ничего не ждёт
    :param background_tasks: Встроенный обработчик задач FastAPI
    :param user: Текущий юзер
    :return: Стандартная(чтобы разные структуры не прилетали на фронт) структура ответа
    """
    # 1400 ms - Клиент ждет
    send_email_report_dashboard(user.username)
    # 500 ms - Задача выполняется на фоне FastAPI в event loop'е или в другом потоке
    background_tasks.add_task(send_email_report_dashboard, user.username)
    # 600 ms - Задача выполняется Celery в отдельном процессе
    send_email_report_dashboard.delay(user.username)
    return {
        "status": 200,
        "data": "Письмо отправлено",
        "details": None
    }
