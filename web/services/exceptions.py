class ServiceException(Exception):
    messages: dict[str, str] = {}


class AuthException(ServiceException):
    ...


class LoginFailed(AuthException):
    messages = {"_details": "아이디 또는 비밀번호가 일치하지 않습니다."}


class CreateSessionFailed(AuthException):
    messages = {"_details": "다시 시도해주세요."}


class VerifySessionFailed(AuthException):
    ...


class UsernameDuplicated(ServiceException):
    messages = {"username": "이미 존재하는 아이디입니다."}
