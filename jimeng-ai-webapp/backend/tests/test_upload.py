"""
接口验证: 文件上传相关API端点
- POST /api/v1/upload/image
- GET  /api/v1/upload/file/{filename}
"""
import pytest
import io
import os


# ==================== 上传图片 POST /api/v1/upload/image ====================

class TestUploadImage:
    """图片上传接口验证"""

    # 最小有效PNG图片(1x1)
    MINI_PNG = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f'
        b'\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
    )

    def test_upload_valid_png(self, app_with_mocks):
        """验证：上传有效PNG图片返回200"""
        files = {"file": ("test.png", io.BytesIO(self.MINI_PNG), "image/png")}
        response = app_with_mocks.post("/api/v1/upload/image", files=files)
        assert response.status_code == 200, f"期望200，实际{response.status_code}，响应: {response.text}"

    def test_upload_response_envelope_format(self, app_with_mocks):
        """验证：响应包含统一信封格式"""
        files = {"file": ("test.png", io.BytesIO(self.MINI_PNG), "image/png")}
        body = app_with_mocks.post("/api/v1/upload/image", files=files).json()
        assert body["code"] == 0
        assert "message" in body
        assert "data" in body

    def test_upload_data_contains_file_info(self, app_with_mocks):
        """验证：data中含file_path, file_size, original_name"""
        files = {"file": ("my_photo.png", io.BytesIO(self.MINI_PNG), "image/png")}
        data = app_with_mocks.post("/api/v1/upload/image", files=files).json()["data"]
        assert "file_path" in data
        assert "file_size" in data
        assert data["original_name"] == "my_photo.png"

    def test_upload_file_size_matches(self, app_with_mocks):
        """验证：返回的file_size与实际文件大小一致"""
        files = {"file": ("test.png", io.BytesIO(self.MINI_PNG), "image/png")}
        data = app_with_mocks.post("/api/v1/upload/image", files=files).json()["data"]
        assert data["file_size"] == len(self.MINI_PNG)

    def test_upload_valid_jpg(self, app_with_mocks):
        """验证：上传JPG格式图片返回200"""
        jpg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda'
        files = {"file": ("photo.jpg", io.BytesIO(jpg_data), "image/jpeg")}
        response = app_with_mocks.post("/api/v1/upload/image", files=files)
        assert response.status_code == 200, f"期望200，实际{response.status_code}"

    def test_upload_valid_jpeg(self, app_with_mocks):
        """验证：上传JPEG扩展名图片返回200"""
        files = {"file": ("photo.jpeg", io.BytesIO(self.MINI_PNG), "image/jpeg")}
        response = app_with_mocks.post("/api/v1/upload/image", files=files)
        assert response.status_code == 200

    def test_upload_unsupported_extension(self, app_with_mocks):
        """验证：上传GIF（不在允许范围）返回400"""
        files = {"file": ("anim.gif", io.BytesIO(b"fake_gif_data"), "image/gif")}
        response = app_with_mocks.post("/api/v1/upload/image", files=files)
        assert response.status_code == 400
        body = response.json()
        assert body["code"] != 0
        assert "不支持的图片格式" in body["message"]

    def test_upload_no_file_returns_422(self, app_with_mocks):
        """验证：不传文件返回422"""
        response = app_with_mocks.post("/api/v1/upload/image")
        assert response.status_code == 422

    def test_upload_exceeds_size_limit(self, app_with_mocks):
        """验证：超大文件(>20MB)返回400"""
        # 模拟20MB+数据 → 由于设置中有MAX_UPLOAD_SIZE=20MB，
        # 但FastAPI测试客户端没有大小限制，我们需要检查逻辑正确性
        big_data = b"x" * (20 * 1024 * 1024 + 1)
        files = {"file": ("huge.png", io.BytesIO(big_data), "image/png")}
        response = app_with_mocks.post("/api/v1/upload/image", files=files)
        assert response.status_code == 400
        assert "过大" in response.json()["message"]

    def test_upload_message_is_success_text(self, app_with_mocks):
        """验证：上传成功的message为'图片上传成功'"""
        files = {"file": ("test.png", io.BytesIO(self.MINI_PNG), "image/png")}
        body = app_with_mocks.post("/api/v1/upload/image", files=files).json()
        assert body["message"] == "图片上传成功"


# ==================== 获取上传文件 GET /api/v1/upload/file/{filename} ====================

class TestGetUploadedFile:
    """上传文件获取接口验证"""

    def _upload_and_get_path(self, app):
        """上传图片并返回保存路径"""
        mini_png = TestUploadImage.MINI_PNG
        files = {"file": ("test.png", io.BytesIO(mini_png), "image/png")}
        data = app.post("/api/v1/upload/image", files=files).json()["data"]
        return data["file_path"]

    def test_get_uploaded_file_by_full_path(self, app_with_mocks):
        """验证：通过保存的文件路径可以访问到图片"""
        file_path = self._upload_and_get_path(app_with_mocks)
        # 文件路径是完整路径，需要转换为URL路径
        # 上传文件存储在 ./output/_uploads/ 下
        filename = os.path.basename(file_path)
        endpoint = f"/api/v1/upload/file/{filename}"
        response = app_with_mocks.get(endpoint)
        assert response.status_code == 200

    def test_get_uploaded_file_content_type(self, app_with_mocks):
        """验证：返回正确的图片content-type"""
        file_path = self._upload_and_get_path(app_with_mocks)
        filename = os.path.basename(file_path)
        response = app_with_mocks.get(f"/api/v1/upload/file/{filename}")
        # 镜像类型检查
        assert "image" in response.headers.get("content-type", "").lower()

    def test_get_nonexistent_file_returns_404(self, app_with_mocks):
        """验证：访问不存在的文件返回404"""
        response = app_with_mocks.get("/api/v1/upload/file/nonexistent_file.png")
        assert response.status_code == 404
