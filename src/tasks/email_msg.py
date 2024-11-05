import smtplib
from datetime import datetime
from typing import Union
from email.message import EmailMessage
from celery import Celery

from config import setting


SMTP_HOST="smtp.gmail.com"
SMTP_PORT=465

celery = Celery('tasks', broker='redis://localhost:6379')

@celery.task
def send_email(email_content: str) -> None:
    email = EmailMessage()
    email['Subject'] = email_content['Subject']
    email['From'] = email_content['From']
    email['To'] = email_content['To']
    email.set_content(email_content['Content'], subtype='html')
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(setting.SMTP_USER, setting.SMTP_PASS)
        server.send_message(email)

def after_reg(user_email: str, user_name: str) -> None:
    email = {
        'Subject': 'Registration successful',
        'From': setting.SMTP_USER,
        'To': user_email,
        'Content': (
            '<div>'
            f'<h1 style="color: red;">Здравствуйте, {user_name}, '
            'Аккаунт успешно создан 😊</h1>'
            '</div>'
        )
    }
    send_email.delay(email)

def verify_account(user_email: str, link: str, user_name: str):
    email = {
        'Subject': 'Verify ur account',
        'From': setting.SMTP_USER,
        'To': user_email,
        'Content': (
            '<div>'
            f'<h1 style="color: red;">Здравствуйте, {user_name}, '
            f'Please verify your account by clicking on the link: {link} 😊</h1>'
            '</div>'
        )
    }
    send_email.delay(email)

def after_verify(user_email: str, user_name: str):
    email = {
        'Subject': 'Account was verified',
        'From': setting.SMTP_USER,
        'To': user_email,
        'Content': (
            '<div>'
            f'<h1 style="color: red;">Здравствуйте, {user_name}, '
            f'Your account was verified in {datetime.now().strftime("%H:%M:%S")}😊</h1>'
            '</div>'
        )
    }
    send_email.delay(email)