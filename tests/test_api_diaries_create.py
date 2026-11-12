"""POST /api/diaries 新增接口用例。"""

import allure
import pytest

from api.client import DiaryApiClient
from api.schemas import Diary

pytestmark = pytest.mark.api


def test_create_diary_and_read_back(api_client: DiaryApiClient, unique_tag: str) -> None:
    """新增日记成功，且可通过单查接口完整回读。"""
    allure.dynamic.title("新增日记并通过单查接口回读")
    submitter = f"自动化-{unique_tag}"
    content = f"创建演示-{unique_tag}"

    with allure.step("发送新增日记请求"):
        response = api_client.create_diary(submitter=submitter, content=content)

    with allure.step("校验新增响应"):
        assert response.status_code == 201
        created = Diary.model_validate(response.json())
        assert created.submitter == submitter
        assert created.content == content
        assert created.submitTime > 0
        assert created.modifyTime > 0

    try:
        with allure.step("通过单查接口回读日记"):
            fetched = api_client.get_diary_parsed(created.id)
        with allure.step("校验回读结果"):
            assert fetched == created
    finally:
        api_client.delete_diary(created.id)
