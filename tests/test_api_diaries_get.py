"""GET /api/diaries/{id} 单查接口用例。"""

import allure
import pytest

from api.client import DiaryApiClient
from api.schemas import Diary, Message

pytestmark = pytest.mark.api


def test_get_existing_diary(api_client: DiaryApiClient, created_diary: Diary) -> None:
    """按 id 查询已存在的日记，返回内容与创建时一致。"""
    allure.dynamic.title("按 id 查询已存在日记")

    with allure.step("查询目标日记"):
        fetched = api_client.get_diary_parsed(created_diary.id)

    with allure.step("校验返回内容与创建时一致"):
        assert fetched == created_diary


def test_get_nonexistent_diary_returns_404(api_client: DiaryApiClient) -> None:
    """查询不存在的日记返回 404。"""
    allure.dynamic.title("查询不存在的日记返回 404")

    with allure.step("查询不存在的日记 id"):
        response = api_client.get_diary(999999999)

    with allure.step("校验 404 和错误响应模型"):
        assert response.status_code == 404
        Message.model_validate(response.json())
