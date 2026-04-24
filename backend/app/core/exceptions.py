from fastapi import HTTPException


class AppException(Exception):
    def __init__(self, status_code: int, error_code: str, message: str):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message


class UnauthorizedException(AppException):
    def __init__(self, message: str = "인증이 필요합니다."):
        super().__init__(401, "UNAUTHORIZED", message)


class ForbiddenException(AppException):
    def __init__(self, message: str = "접근 권한이 없습니다."):
        super().__init__(403, "FORBIDDEN", message)


class NotFoundException(AppException):
    def __init__(self, message: str = "리소스를 찾을 수 없습니다."):
        super().__init__(404, "NOT_FOUND", message)


class ToiletNotFoundException(AppException):
    def __init__(self):
        super().__init__(404, "TOILET_NOT_FOUND", "해당 화장실을 찾을 수 없습니다.")


class ReviewNotFoundException(AppException):
    def __init__(self):
        super().__init__(404, "REVIEW_NOT_FOUND", "해당 리뷰를 찾을 수 없습니다.")


class DuplicateReviewException(AppException):
    def __init__(self):
        super().__init__(409, "DUPLICATE_REVIEW", "이미 이 화장실에 리뷰를 작성하셨습니다.")


class ValidationException(AppException):
    def __init__(self, message: str):
        super().__init__(422, "VALIDATION_ERROR", message)
