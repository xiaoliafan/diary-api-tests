"""pytest 公共夹具：接口客户端、唯一标识、测试数据等。"""

import os
import uuid
from collections.abc import Callable

import allure
import pytest

from api.client import DiaryApiClient
from api.schemas import Diary


@pytest.fixture(autouse=True)
def allure_labels(request: pytest.FixtureRequest) -> None:
    """为所有接口用例补充 Allure 的 feature 和 story 标签。"""
    allure.dynamic.feature("日记平台接口")
    allure.dynamic.story(request.module.__name__.rsplit(".", 1)[-1])


@pytest.fixture(scope="session")
def api_client() -> DiaryApiClient:
    """连接日记平台后端，可通 DIARY_API_BASE_URL 覆盖默认地址。"""
    base_url = os.getenv("DIARY_API_BASE_URL", "http://127.0.0.1:8080")
    client = DiaryApiClient(base_url)
    response = client.list_diaries(page=1, pageSize=1)
    assert response.status_code == 200, (
        f"日记平台不可用：{base_url} 返回 {response.status_code}，请先启动后端服务"
    )
    yield client
    client.close()


@pytest.fixture
def unique_tag() -> str:
    """生成每次运行唯一的短标识，避免测试数据相互干扰。"""
    return uuid.uuid4().hex[:8]


@pytest.fixture  #管理测试的前置和后置操作
def created_diary(api_client: DiaryApiClient, unique_tag: str) -> Diary:
    """创建一条测试日记，并在用例结束后清理。"""
    response = api_client.create_diary(
        submitter=f"测试用户-{unique_tag}",
        content=f"接口自动化演示-{unique_tag}",
    )
    assert response.status_code == 201
    diary = Diary.model_validate(response.json())
    yield diary
    api_client.delete_diary(diary.id)


@pytest.fixture
def diary_id_by_submitter(api_client: DiaryApiClient) -> Callable[[str], int]:
    """工厂夹具：按提交人查询最新一条日记 id，供各接口用例串联复用。"""

    def _query(submitter: str) -> int:
        page = api_client.list_diaries_parsed(submitter=submitter, pageSize=1)
        assert page.total >= 1, f"未找到 submitter={submitter} 的日记"
        return page.items[0].id

    return _query
