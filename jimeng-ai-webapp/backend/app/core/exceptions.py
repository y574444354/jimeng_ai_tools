from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi import Request
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR


class AppException(Exception):
    """业务异常基类"""
    def __init__(self, code: int, message: str, status_code: int = HTTP_400_BAD_REQUEST):
        self.code = code
        self.message = message
        self.status_code = status_code


class APIException(AppException):
    """API调用异常"""
    def __init__(self, message: str, code: int = 10001):
        super().__init__(code=code, message=message, status_code=HTTP_400_BAD_REQUEST)


class AuthException(AppException):
    """鉴权异常"""
    def __init__(self, message: str = "API密钥配置无效或未配置"):
        super().__init__(code=10002, message=message, status_code=HTTP_401_UNAUTHORIZED)


class NotFoundException(AppException):
    """资源未找到异常"""
    def __init__(self, message: str = "请求的资源不存在"):
        super().__init__(code=10003, message=message, status_code=HTTP_404_NOT_FOUND)


class FileException(AppException):
    """文件处理异常"""
    def __init__(self, message: str):
        super().__init__(code=10004, message=message, status_code=HTTP_400_BAD_REQUEST)


class ExternalServiceException(AppException):
    """外部服务异常"""
    def __init__(self, message: str = "外部服务调用失败"):
        super().__init__(code=10005, message=message, status_code=HTTP_500_INTERNAL_SERVER_ERROR)


async def app_exception_handler(request: Request, exc: AppException):
    """统一业务异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "data": None,
        },
    )


async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 99999,
            "message": f"服务器内部错误: {str(exc)}",
            "data": None,
        },
    )