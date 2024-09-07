import smtplib
from email.message import EmailMessage
from urllib.parse import urlencode

from celery import Celery
from celery.exceptions import MaxRetriesExceededError

from src.config import SMTP_USER, SMTP_PASS, BASE_URL, REDIS_URI

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

celery = Celery('tasks', broker=REDIS_URI)
celery.conf.broker_connection_retry_on_startup = True


def get_verification_email_template(email: str, token: str):
    message = EmailMessage()
    message['Subject'] = 'Подтвердите регистрацию'
    message['From'] = SMTP_USER
    message['To'] = email

    params = urlencode({'token': token})
    verify_url = f"{BASE_URL}/auth/verify?{params}"

    message.set_content(
        '<div>'
        f'<h1>Подтвердите вашу регистрацию</h1>'
        f'<p>Для подтверждения вашей регистрации, пожалуйста, нажмите на следующую ссылку:</p>'
        f'<a href="{verify_url}">Подтвердить регистрацию</a>'
        f'<p>Если вы не запрашивали регистрацию, пожалуйста, проигнорируйте это письмо.</p>'
        '</div>',
        subtype='html'
    )
    return message


@celery.task(bind=True, max_retries=3, default_retry_delay=20)
def send_verification_email(self, email: str, token: str):
    try:
        message = get_verification_email_template(email, token)
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(message)
    except Exception as exc:
        try:
            raise self.retry(exc=exc, countdown=self.default_retry_delay)
        except MaxRetriesExceededError:
            print(f"Max retries exceeded for sending verification email to {email}")
