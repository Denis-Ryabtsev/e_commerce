import smtplib
from datetime import datetime

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
        'Subject': 'Registration successfull',
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
            f'Please verify your account by '\
            f'clicking on the link: {link} 😊</h1>'
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
            f'Your account was verified in '\
            f'{datetime.now().strftime("%H:%M:%S")}😊</h1>'
            '</div>'
        )
    }
    send_email.delay(email)

def reset_pass(user_email: str, link: str, user_name: str) -> None:
    email = {
        'Subject': 'Reset pass',
        'From': setting.SMTP_USER,
        'To': user_email,
        'Content': (
            '<div>'
            f'<h1 style="color: red;">Здравствуйте, {user_name}, '
            f'If u need to reset your account password by '\
            f'clicking on the link: {link} 😊</h1>'
            '</div>'
        )
    }
    send_email.delay(email)

def after_reset(user_email: str, user_name: str) -> None:
    email = {
        'Subject': 'Pass was reset',
        'From': setting.SMTP_USER,
        'To': user_email,
        'Content': (
            '<div>'
            f'<h1 style="color: red;">Здравствуйте, {user_name}, '
            f'Your accounts password was recovery in '\
            f'{datetime.now().strftime("%H:%M:%S")}😊</h1>'
            '</div>'
        )
    }
    send_email.delay(email)

def after_delete(user_email: str, user_name: str) -> None:
    email = {
        'Subject': 'Account was deleted',
        'From': setting.SMTP_USER,
        'To': user_email,
        'Content': (
            '<div>'
            f'<h1 style="color: red;">Здравствуйте, {user_name}, '
            f'Your accounts was deleted in '\
            f'{datetime.now().strftime("%H:%M:%S")}😊</h1>'
            '</div>'
        )
    }
    send_email.delay(email)

def seller_order(goods: list[tuple]) -> None:
    
    data_send = {}
    for email, good, count in goods:
        if email not in data_send:
            data_send[email] = []
        data_send[email].append((good, count))

    for email, item in data_send.items():
        obj = ", ".join([f"{temp} (count: {count})" for temp, count in item])

        body = {
        'Subject': 'Good was include in order',
        'From': setting.SMTP_USER,
        'To': email,
        'Content': (
            '<div>'
            f'<h1 style="color: red;">Здравствуйте, '
            f'Your goods: {obj} was include in order in '\
            f'{datetime.now().strftime("%H:%M:%S")}😊</h1>'
            '</div>'
        )
        }
        send_email.delay(body)

def customer_order(goods: list[tuple], email) -> None:
    
    data_send = {}
    for _, good, count in goods:
        if good not in data_send:
            data_send[good] = []
        data_send[good].append(count)
    obj = ", ".join(f"{item} (count: {sum(numb)})" for item, numb in data_send.items())

    body = {
    'Subject': 'Order successful',
    'From': setting.SMTP_USER,
    'To': email,
    'Content': (
        '<div>'
        f'<h1 style="color: red;">Здравствуйте, '
        f'Your goods: {obj} was include in order in '\
        f'{datetime.now().strftime("%H:%M:%S")}😊</h1>'
        '</div>'
    )
    }
    
    send_email.delay(body)