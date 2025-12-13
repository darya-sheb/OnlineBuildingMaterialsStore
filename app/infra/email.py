import logging
import smtplib
from email.message import EmailMessage

from app.core.settings import settings

log = logging.getLogger(__name__)


def send_order_confirmation(to_email: str, order_id: int) -> None:
    # SMTP не настроен, только логирование для запуска проекта
    if not settings.SMTP_HOST:
        log.info("SMTP не настроен: to_email=%s order_id=%s", to_email, order_id)
        return

    message = EmailMessage()
    message["Subject"] = f"Подтверждение заказа №{order_id}"
    message["From"] = settings.SMTP_FROM
    message["To"] = to_email
    # можно что-то добавить в сообщение
    message.set_content(f"Спасибо за заказ! Номер заказа: {order_id}")

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as s:
        s.starttls()
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        s.send_message(message)
