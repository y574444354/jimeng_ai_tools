"""
接口验证: GET /api/v1/health 和 GET /api/v1/health/ready
验证健康检查和就绪检查端点的响应格式、状态码和数据结构
"""
import pytest


class TestHealthCheck:
    """健康检查接口 GET /api/v1/health"""

    def test_health_returns_200(self, app_without_mocks):
        """验证：健康检查返回200状态码"""
        response = app_without_mocks.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_response_envelope_format(self, app_without_mocks):
        """验证：响应包含统一的JSON信封格式 {code, message, data}"""
        response = app_without_mocks.get("/api/v1/health")
        body = response.json()
        assert "code" in body, "响应缺少 code 字段"
        assert "message" in body, "响应缺少 message 字段"
        assert "data" in body, "响应缺少 data 字段"

    def test_health_code_is_zero_on_success(self, app_without_mocks):
        """验证：成功时 code 字段为 0"""
        response = app_without_mocks.get("/api/v1/health")
        assert response.json()["code"] == 0

    def test_health_data_contains_status(self, app_without_mocks):
        """验证：data 中包含 status, service, version 字段"""
        data = app_without_mocks.get("/api/v1/health").json()["data"]
        assert data["status"] == "healthy"
        assert data["service"] == "jimeng-ai"
        assert data["version"] == "1.0.0"

    def test_health_is_idempotent(self, app_without_mocks):
        """验证：多次调用返回相同结果"""
        r1 = app_without_mocks.get("/api/v1/health").json()
        r2 = app_without_mocks.get("/api/v1/health").json()
        assert r1 == r2


class TestHealthReady:
    """就绪检查接口 GET /api/v1/health/ready"""

    def test_ready_returns_200(self, app_without_mocks):
        """验证：就绪检查返回200状态码"""
        response = app_without_mocks.get("/api/v1/health/ready")
        assert response.status_code == 200

    def test_ready_response_envelope_format(self, app_without_mocks):
        """验证：响应包含统一的JSON信封格式"""
        response = app_without_mocks.get("/api/v1/health/ready")
        body = response.json()
        assert "code" in body
        assert "message" in body
        assert "data" in body

    def test_ready_data_contains_required_fields(self, app_without_mocks):
        """验证：data 中包含 status, database, jimeng_client 字段"""
        data = app_without_mocks.get("/api/v1/health/ready").json()["data"]
        assert "status" in data
        assert "database" in data
        assert "jimeng_client" in data

    def test_ready_status_is_ready_or_not_ready(self, app_without_mocks):
        """验证：status 字段值为 'ready' 或 'not_ready'"""
        data = app_without_mocks.get("/api/v1/health/ready").json()["data"]
        assert data["status"] in ("ready", "not_ready")

    def test_ready_content_type_is_json(self, app_without_mocks):
        """验证：响应 Content-Type 为 application/json"""
        response = app_without_mocks.get("/api/v1/health/ready")
        assert "application/json" in response.headers["content-type"]
