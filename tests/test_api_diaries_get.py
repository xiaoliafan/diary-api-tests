"""GET /api/diaries/{id} 单查接口用例。"""

from api.client import DiaryApiClient
from api.schemas import Diary, Message


def test_get_existing_diary(api_client: DiaryApiClient, created_diary: Diary) -> None:
    """按 id 查询已存在的日记，返回内容与创建时一致。"""
    fetched = api_client.get_diary_parsed(created_diary.id)
    assert fetched == created_diary


def test_get_nonexistent_diary_returns_404(api_client: DiaryApiClient) -> None:
    """查询不存在的日记返回 404。"""
    response = api_client.get_diary(999999999)
    assert response.status_code == 404
    Message.model_validate(response.json())
