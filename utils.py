import re


# 8-20 characters long, no _ or . at the beginning, no __ or _. or ._ or .. inside,
# allowed characters, no _ or . at the end
USERNAME_PATTERN = '^(?=.{8,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$'

# Min 1 character, max 25, upper- and lowercase letters only
NAME_PATTER = '^[a-zA-Z ,.\'-]+$'

# Minimum eight characters, at least one letter and one number
PASSWORD_PATTERN = '^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'


error_messages = {
    'nickname': '8-20 characters long, no _ or . at the beginning, no __ or _. or ._ or .. inside, '
        + 'allowed characters, no _ or . at the end',
    'name': 'Min 1 character, max 25, upper- and lowercase letters only',
    'password': 'Minimum eight characters, at least one letter and one number',
}


class UserDataVerifyError(Exception):
    def __init__(self, dataname: str, explanation: str) -> None:
        message = f"{dataname} isn't correct - {explanation}"
        super().__init__(message)


def verify_nickname(nickname: str) -> bool:
    if re.match(USERNAME_PATTERN, nickname):
        return True
    return False


def verify_name(name: str) -> bool:
    if re.match(NAME_PATTER, name):
        return True
    return False


def verify_password(password: str) -> bool:
    if re.match(PASSWORD_PATTERN, password):
        return True
    return False


def verify_user_data(nickname: str, name: str, password: str) -> bool|None:
    results = {
        'nickname': verify_nickname(nickname),
        'name': verify_name(name),
        'password': verify_password(password),
    }
    
    if all(results.values()):
        return True
    
    for data, result in results.items():
        if result == False:
            message = error_messages[data]
            raise UserDataVerifyError(data, message)
