import re


email_domain = [
    "@gmail.com",
    "@yahoo.com",
    "@outlook.com",
    "@yandex.ru",
    "@mail.ru",
    "@bk.ru"
]

def validate_email(email: str) -> bool:
    domain = email[email.find("@"):]
    return domain in email_domain

def validate_pass(password: str) -> bool:
    password_regex = re.compile(
        r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{4,}$"
    )
    return (password_regex.fullmatch(password))
    