"""DELETE /api/diaries/{id} 删除接口用例。"""

from collections.abc import Callable

import allure
import pytest

from api.client import DiaryApiClient
from api.schemas import Diary, Message

pytestmark = pytest.mark.api


def test_delete_diary_and_verify_gone(api_client: DiaryApiClient, created_diary: Diary) -> None:
    """删除成功，删除后再查询返回 404。"""
    allure.dynamic.title("删除日记并验证记录不存在")

    with allure.step("发送删除请求"):
        response = api_client.delete_diary(created_diary.id)

    with allure.step("校验删除响应"):
        assert response.status_code == 200
        assert response.json() == {"ok": True}

    with allure.step("确认删除后查询返回 404"):
        get_response = api_client.get_diary(created_diary.id)
        assert get_response.status_code == 404
        Message.model_validate(get_response.json())


def test_query_zhou_yu_then_delete(
    api_client: DiaryApiClient,
    diary_id_by_submitter: Callable[[str], int],
    unique_tag: str,
) -> None:
    """先创建一条 submitter=周雨 的临时日记，再按提交人查 id 并删除。"""
    allure.dynamic.title("查询提交人周雨的 id 后删除")

    with allure.step("创建临时测试数据"):
        response = api_client.create_diary(submitter="周雨", content=f"待删除-{unique_tag}")
        assert response.status_code == 201
        created = Diary.model_validate(response.json())

    with allure.step("按提交人查询目标 id"):
        target_id = diary_id_by_submitter("周雨")
        assert target_id == created.id

    with allure.step("删除目标日记"):
        delete_response = api_client.delete_diary(target_id)
        assert delete_response.status_code == 200
        assert delete_response.json() == {"ok": True}

    with allure.step("确认删除结果"):
        get_response = api_client.get_diary(target_id)
        assert get_response.status_code == 404
        Message.model_validate(get_response.json())
