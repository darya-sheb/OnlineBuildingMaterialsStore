import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from app.core.settings import settings


class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.sender = settings.SMTP_FROM

        if not self.smtp_host:
            raise ValueError("SMTP_HOST is not configured. Email service disabled.")

        template_dir = Path(__file__).parent.parent.parent / "web" / "templates" / "email"
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    async def send_order_confirmation(self, to_email: str, order_id: int) -> None:
        template = self.jinja_env.get_template("order_confirmation.html")
        html_body = template.render(order_id=order_id)

        message = MIMEMultipart("alternative")
        message["Subject"] = f"Ваш заказ №{order_id} подтверждён"
        message["From"] = self.sender
        message["To"] = to_email

        html_part = MIMEText(html_body, "html", "utf-8")
        message.attach(html_part)

        await aiosmtplib.send(
            message,
            hostname=self.smtp_host,
            port=self.smtp_port,
            username=self.smtp_user,
            password=self.smtp_password,
            start_tls=True,
        )