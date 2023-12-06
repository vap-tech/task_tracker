import smtplib
from email.message import EmailMessage

from celery import Celery

from src.config import SMTP_HOST, SMTP_PORT, SMTP_PASSWORD, SMTP_USER, REDIS_HOST, REDIS_PORT

# Инициализируем Celery
celery = Celery('tasks', broker=f'redis://{REDIS_HOST}:{REDIS_PORT}')


def get_email_template_dashboard(username: str) -> EmailMessage:
    """
    Собирает email
    :param username: Адрес для email
    :return: Объект класса EmailMessage
    """
    email = EmailMessage()
    email['Subject'] = 'Отчет о задачах'
    email['From'] = SMTP_USER
    email['To'] = SMTP_USER

    email.set_content(
        '<div>'
        f'<h1 style="color: red;">Здравствуйте, {username}, а вот и ваш отчет. Enjoy 😊</h1>'
        '<img src="https://v-petrenko.ru/dashboard.jpg" width="600">'
        '</div>',
        subtype='html'
    )
    return email


@celery.task
def send_email_report_dashboard(username: str):
    """
    Задача отправки email
    :param username: Адрес для email
    :return:
    """
    email = get_email_template_dashboard(username)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(email)
