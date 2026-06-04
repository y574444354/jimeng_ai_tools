from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import Request
from starlette.status import HTTP_200_OK, HTTP_201_CREATED


# 创建主路由
api_router = APIRouter(prefix="/api/v1")


def success_response(data=None, message: str = "success", status_code: int = HTTP_200_OK):
    """统一成功响应"""
    return JSONResponse(
        status_code=status_code,
        content={
            "code": 0,
            "message": message,
            "data": data,
        },
    )


def page_response(items: list, total: int, page: int, page_size: int):
    """统一分页响应"""
    return JSONResponse(
        status_code=HTTP_200_OK,
        content={
            "code": 0,
            "message": "success",
            "data": {
                "list": items,
                "total": total,
                "page": page,
                "pageSize": page_size,
            },
        },
    )