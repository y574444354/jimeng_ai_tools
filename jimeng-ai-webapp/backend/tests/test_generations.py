"""
接口验证: 图片生成相关API端点
- POST /api/v1/generations/text2img
- POST /api/v1/generations/img2img
- POST /api/v1/generations/inpainting
- GET  /api/v1/generations/{id}/status
- GET  /api/v1/generations/{id}
- GET  /api/v1/generations
- DELETE /api/v1/generations/{id}

使用 mock 雪桥AI客户端隔离外部依赖
"""
import pytest


# ==================== 文生图 POST /api/v1/generations/text2img ====================

class TestText2Img:
    """文生图接口验证"""

    MINIMAL_REQUEST = {
        "prompt": "一只可爱的猫咪",
        "image_size": "1024x1024",
    }

    def test_text2img_with_minimal_request(self, app_with_mocks):
        """验证：最小参数请求返回200"""
        response = app_with_mocks.post("/api/v1/generations/text2img", json=self.MINIMAL_REQUEST)
        assert response.status_code == 200, f"期望200，实际{response.status_code}，响应: {response.text}"

    def test_text2img_response_envelope_format(self, app_with_mocks):
        """验证：响应包含统一信封格式"""
        response = app_with_mocks.post("/api/v1/generations/text2img", json=self.MINIMAL_REQUEST)
        body = response.json()
        assert body["code"] == 0
        assert "message" in body
        assert "data" in body

    def test_text2img_data_contains_required_fields(self, app_with_mocks):
        """验证：data 包含生成记录的完整字段"""
        response = app_with_mocks.post("/api/v1/generations/text2img", json=self.MINIMAL_REQUEST)
        data = response.json()["data"]
        required_fields = [
            "id", "task_type", "prompt", "image_size", "status",
            "created_at", "updated_at", "images",
        ]
        for field in required_fields:
            assert field in data, f"缺少字段: {field}"

    def test_text2img_status_is_completed(self, app_with_mocks):
        """验证：mock下任务status为completed"""
        response = app_with_mocks.post("/api/v1/generations/text2img", json=self.MINIMAL_REQUEST)
        assert response.json()["data"]["status"] == "completed"

    def test_text2img_task_type_is_text2img(self, app_with_mocks):
        """验证：task_type字段值为 text2img"""
        response = app_with_mocks.post("/api/v1/generations/text2img", json=self.MINIMAL_REQUEST)
        assert response.json()["data"]["task_type"] == "text2img"

    # ---- 请求校验测试 ----

    def test_text2img_missing_prompt_returns_422(self, app_with_mocks):
        """验证：缺少必填字段prompt返回422"""
        response = app_with_mocks.post("/api/v1/generations/text2img", json={"image_size": "1024x1024"})
        assert response.status_code == 422

    def test_text2img_invalid_image_size_format(self, app_with_mocks):
        """验证：无效的image_size格式返回422"""
        response = app_with_mocks.post("/api/v1/generations/text2img", json={
            "prompt": "test", "image_size": "invalid"
        })
        assert response.status_code == 422

    def test_text2img_prompt_max_length(self, app_with_mocks):
        """验证：prompt超过1000字符时返回422"""
        long_prompt = "测" * 1001
        response = app_with_mocks.post("/api/v1/generations/text2img", json={
            "prompt": long_prompt, "image_size": "1024x1024"
        })
        assert response.status_code == 422

    def test_text2img_cfg_scale_out_of_range(self, app_with_mocks):
        """验证：cfg_scale超出1.0~20.0范围返回422"""
        response = app_with_mocks.post("/api/v1/generations/text2img", json={
            "prompt": "test", "image_size": "1024x1024", "cfg_scale": 0.5
        })
        assert response.status_code == 422

        response = app_with_mocks.post("/api/v1/generations/text2img", json={
            "prompt": "test", "image_size": "1024x1024", "cfg_scale": 21.0
        })
        assert response.status_code == 422

    def test_text2img_image_count_out_of_range(self, app_with_mocks):
        """验证：image_count超出1~4范围返回422"""
        response = app_with_mocks.post("/api/v1/generations/text2img", json={
            "prompt": "test", "image_size": "1024x1024", "image_count": 5
        })
        assert response.status_code == 422

        response = app_with_mocks.post("/api/v1/generations/text2img", json={
            "prompt": "test", "image_size": "1024x1024", "image_count": 0
        })
        assert response.status_code == 422

    # ---- 可选参数测试 ----

    def test_text2img_with_all_optional_params(self, app_with_mocks):
        """验证：所有可选参数都可正常提交并正确返回"""
        full_request = {
            "prompt": "一只可爱的猫咪，高清画质",
            "negative_prompt": "模糊，变形，低质量",
            "image_size": "768x1024",
            "style": "写实风格",
            "cfg_scale": 10.0,
            "seed": 42,
            "image_count": 2,
        }
        response = app_with_mocks.post("/api/v1/generations/text2img", json=full_request)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["negative_prompt"] == full_request["negative_prompt"]
        assert data["cfg_scale"] == 10.0
        assert data["seed"] == 42
        assert data["image_count"] == 2


# ==================== 图生图 POST /api/v1/generations/img2img ====================

class TestImg2Img:
    """图生图接口验证"""

    def test_img2img_with_minimal_request(self, app_with_mocks, temp_image_file):
        """验证：最小参数请求返回200"""
        request = {
            "prompt": "一只可爱的猫咪",
            "image_size": "1024x1024",
            "reference_image_path": temp_image_file,
        }
        response = app_with_mocks.post("/api/v1/generations/img2img", json=request)
        assert response.status_code == 200, f"期望200，实际{response.status_code}，响应: {response.text}"

    def test_img2img_response_envelope_format(self, app_with_mocks, temp_image_file):
        """验证：响应包含统一信封格式"""
        response = app_with_mocks.post("/api/v1/generations/img2img", json={
            "prompt": "猫", "image_size": "1024x1024",
            "reference_image_path": temp_image_file,
        })
        body = response.json()
        assert body["code"] == 0
        assert body["message"] in ("图生图生成完成", "success")

    def test_img2img_task_type_is_img2img(self, app_with_mocks, temp_image_file):
        """验证：task_type字段值为 img2img"""
        response = app_with_mocks.post("/api/v1/generations/img2img", json={
            "prompt": "猫", "image_size": "1024x1024",
            "reference_image_path": temp_image_file,
        })
        assert response.json()["data"]["task_type"] == "img2img"

    def test_img2img_missing_reference_image_path(self, app_with_mocks):
        """验证：缺少reference_image_path返回422"""
        response = app_with_mocks.post("/api/v1/generations/img2img", json={
            "prompt": "test", "image_size": "1024x1024"
        })
        assert response.status_code == 422

    def test_img2img_data_contains_images_array(self, app_with_mocks, temp_image_file):
        """验证：响应data中包含images数组"""
        response = app_with_mocks.post("/api/v1/generations/img2img", json={
            "prompt": "猫", "image_size": "1024x1024",
            "reference_image_path": temp_image_file,
        })
        data = response.json()["data"]
        assert "images" in data
        assert isinstance(data["images"], list)
        assert len(data["images"]) > 0, "mock应返回至少1张图片"


# ==================== 局部重绘 POST /api/v1/generations/inpainting ====================

class TestInpainting:
    """局部重绘接口验证"""

    def test_inpainting_with_minimal_request(self, app_with_mocks, temp_image_file, temp_mask_file):
        """验证：最小参数请求返回200"""
        request = {
            "prompt": "一只可爱的猫咪",
            "image_size": "1024x1024",
            "reference_image_path": temp_image_file,
            "mask_image_path": temp_mask_file,
        }
        response = app_with_mocks.post("/api/v1/generations/inpainting", json=request)
        assert response.status_code == 200, f"期望200，实际{response.status_code}，响应: {response.text}"

    def test_inpainting_task_type_is_inpainting(self, app_with_mocks, temp_image_file, temp_mask_file):
        """验证：task_type字段值为 inpainting"""
        response = app_with_mocks.post("/api/v1/generations/inpainting", json={
            "prompt": "猫", "image_size": "1024x1024",
            "reference_image_path": temp_image_file,
            "mask_image_path": temp_mask_file,
        })
        assert response.json()["data"]["task_type"] == "inpainting"

    def test_inpainting_missing_mask_image_path(self, app_with_mocks, temp_image_file):
        """验证：缺少mask_image_path返回422"""
        response = app_with_mocks.post("/api/v1/generations/inpainting", json={
            "prompt": "test",
            "image_size": "1024x1024",
            "reference_image_path": temp_image_file,
        })
        assert response.status_code == 422

    def test_inpainting_missing_both_images(self, app_with_mocks):
        """验证：缺少两个图片路径返回422"""
        response = app_with_mocks.post("/api/v1/generations/inpainting", json={
            "prompt": "test", "image_size": "1024x1024"
        })
        assert response.status_code == 422

    def test_inpainting_status_is_completed(self, app_with_mocks, temp_image_file, temp_mask_file):
        """验证：mock下任务status为completed"""
        response = app_with_mocks.post("/api/v1/generations/inpainting", json={
            "prompt": "猫", "image_size": "1024x1024",
            "reference_image_path": temp_image_file,
            "mask_image_path": temp_mask_file,
        })
        assert response.json()["data"]["status"] == "completed"


# ==================== 查询状态 GET /api/v1/generations/{id}/status ====================

class TestQueryStatus:
    """任务状态查询接口验证"""

    def _create_text2img(self, app):
        resp = app.post("/api/v1/generations/text2img", json={
            "prompt": "test status query", "image_size": "512x512"
        })
        return resp.json()["data"]["id"]

    def test_query_existing_record_status(self, app_with_mocks):
        """验证：查询已存在的记录返回200"""
        record_id = self._create_text2img(app_with_mocks)
        response = app_with_mocks.get(f"/api/v1/generations/{record_id}/status")
        assert response.status_code == 200

    def test_query_status_data_format(self, app_with_mocks):
        """验证：status查询返回generation_id和status字段"""
        record_id = self._create_text2img(app_with_mocks)
        data = app_with_mocks.get(f"/api/v1/generations/{record_id}/status").json()["data"]
        assert "generation_id" in data
        assert "status" in data
        assert data["generation_id"] == record_id
        assert data["status"] in ("pending", "processing", "completed", "failed")

    def test_query_nonexistent_record_returns_404(self, app_with_mocks):
        """验证：查询不存在的记录返回404"""
        response = app_with_mocks.get("/api/v1/generations/nonexistent-id/status")
        assert response.status_code == 404

    def test_query_nonexistent_error_code(self, app_with_mocks):
        """验证：不存在记录的响应包含业务错误码"""
        response = app_with_mocks.get("/api/v1/generations/nonexistent-id/status")
        body = response.json()
        assert body["code"] != 0
        assert body["data"] is None


# ==================== 获取详情 GET /api/v1/generations/{id} ====================

class TestGetGeneration:
    """生成结果详情查询接口验证"""

    def _create_text2img(self, app):
        resp = app.post("/api/v1/generations/text2img", json={
            "prompt": "test get detail", "image_size": "512x512"
        })
        return resp.json()["data"]["id"]

    def test_get_existing_generation(self, app_with_mocks):
        """验证：获取已存在记录返回200"""
        record_id = self._create_text2img(app_with_mocks)
        response = app_with_mocks.get(f"/api/v1/generations/{record_id}")
        assert response.status_code == 200

    def test_get_generation_data_has_images(self, app_with_mocks):
        """验证：记录详情包含images数组"""
        record_id = self._create_text2img(app_with_mocks)
        data = app_with_mocks.get(f"/api/v1/generations/{record_id}").json()["data"]
        assert "images" in data
        assert isinstance(data["images"], list)
        assert len(data["images"]) > 0, "mock应至少返回1张图片"

    def test_get_generation_image_has_file_path(self, app_with_mocks):
        """验证：图片记录包含file_path"""
        record_id = self._create_text2img(app_with_mocks)
        images = app_with_mocks.get(f"/api/v1/generations/{record_id}").json()["data"]["images"]
        assert len(images) > 0
        assert "file_path" in images[0]

    def test_get_nonexistent_generation_returns_404(self, app_with_mocks):
        """验证：获取不存在记录返回404"""
        response = app_with_mocks.get("/api/v1/generations/nonexistent-id")
        assert response.status_code == 404


# ==================== 历史列表 GET /api/v1/generations ====================

class TestListGenerations:
    """历史记录分页查询接口验证"""

    def _create_records(self, app, count=3):
        for i in range(count):
            app.post("/api/v1/generations/text2img", json={
                "prompt": f"test list item {i}", "image_size": "512x512"
            })

    def test_list_returns_200(self, app_with_mocks):
        """验证：列表查询返回200"""
        self._create_records(app_with_mocks, 2)
        response = app_with_mocks.get("/api/v1/generations")
        assert response.status_code == 200

    def test_list_response_is_page_envelope(self, app_with_mocks):
        """验证：分页响应使用包含list/total/page/pageSize的信封格式"""
        self._create_records(app_with_mocks, 2)
        data = app_with_mocks.get("/api/v1/generations").json()["data"]
        assert "list" in data
        assert "total" in data
        assert "page" in data
        assert "pageSize" in data

    def test_list_total_matches_created_count(self, app_with_mocks):
        """验证：total字段准确反映记录总数"""
        self._create_records(app_with_mocks, 3)
        data = app_with_mocks.get("/api/v1/generations").json()["data"]
        assert data["total"] == 3

    def test_list_items_have_required_fields(self, app_with_mocks):
        """验证：列表中每项包含id/task_type/prompt/status等关键字段"""
        self._create_records(app_with_mocks, 1)
        items = app_with_mocks.get("/api/v1/generations").json()["data"]["list"]
        assert len(items) > 0
        item = items[0]
        for field in ["id", "task_type", "prompt", "status", "image_size", "created_at"]:
            assert field in item, f"列表项缺少字段: {field}"

    def test_list_default_page_params(self, app_with_mocks):
        """验证：默认page=1 pageSize=20"""
        self._create_records(app_with_mocks, 1)
        data = app_with_mocks.get("/api/v1/generations").json()["data"]
        assert data["page"] == 1
        assert data["pageSize"] == 20

    def test_list_custom_pagination(self, app_with_mocks):
        """验证：自定义分页参数正常工作"""
        self._create_records(app_with_mocks, 5)
        data = app_with_mocks.get("/api/v1/generations?page=1&page_size=2").json()["data"]
        assert len(data["list"]) <= 2
        assert data["total"] == 5

    def test_list_page_param_below_1_returns_422(self, app_with_mocks):
        """验证：page小于1返回422"""
        response = app_with_mocks.get("/api/v1/generations?page=0")
        assert response.status_code == 422

    def test_list_empty_result(self, app_with_mocks):
        """验证：无记录时返回空列表（total=0, list=[]）"""
        data = app_with_mocks.get("/api/v1/generations").json()["data"]
        assert data["total"] == 0
        assert data["list"] == []


# ==================== 删除记录 DELETE /api/v1/generations/{id} ====================

class TestDeleteGeneration:
    """历史记录删除接口验证"""

    def _create_text2img(self, app):
        resp = app.post("/api/v1/generations/text2img", json={
            "prompt": "to be deleted", "image_size": "512x512"
        })
        return resp.json()["data"]["id"]

    def test_delete_existing_record(self, app_with_mocks):
        """验证：删除已存在记录返回200"""
        record_id = self._create_text2img(app_with_mocks)
        response = app_with_mocks.delete(f"/api/v1/generations/{record_id}")
        assert response.status_code == 200

    def test_delete_response_message(self, app_with_mocks):
        """验证：删除成功返回'删除成功'消息"""
        record_id = self._create_text2img(app_with_mocks)
        body = app_with_mocks.delete(f"/api/v1/generations/{record_id}").json()
        assert body["code"] == 0
        assert "删除" in body["message"]

    def test_delete_nonexistent_record_returns_404(self, app_with_mocks):
        """验证：删除不存在的记录返回404"""
        response = app_with_mocks.delete("/api/v1/generations/nonexistent-id")
        assert response.status_code == 404

    def test_delete_is_idempotent(self, app_with_mocks):
        """验证：重复删除同一条记录，第二次返回404"""
        record_id = self._create_text2img(app_with_mocks)
        r1 = app_with_mocks.delete(f"/api/v1/generations/{record_id}")
        assert r1.status_code == 200

        r2 = app_with_mocks.delete(f"/api/v1/generations/{record_id}")
        assert r2.status_code == 404

    def test_deleted_record_not_in_list(self, app_with_mocks):
        """验证：删除后记录不出现在列表中"""
        record_id = self._create_text2img(app_with_mocks)
        assert app_with_mocks.delete(f"/api/v1/generations/{record_id}").status_code == 200

        data = app_with_mocks.get("/api/v1/generations").json()["data"]
        ids = [item["id"] for item in data["list"]]
        assert record_id not in ids
