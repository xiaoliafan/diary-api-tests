"""POST /api/diaries 新增接口用例。"""

from api.client import DiaryApiClient
from api.schemas import Diary


def test_create_diary_and_read_back(api_client: DiaryApiClient, unique_tag: str) -> None:
    """新增日记成功，且可通过单查接口完整回读。"""
    submitter = f"自动化-{unique_tag}"
    content = f"创建演示-{unique_tag}"

    response = api_client.create_diary(submitter=submitter, content=content)
    assert response.status_code == 201
    created = Diary.model_validate(response.json())
    assert created.submitter == submitter
    assert created.content == content
    assert created.submitTime > 0
    assert created.modifyTime > 0

    try:
        fetched = api_client.get_diary_parsed(created.id)
        assert fetched == created
    finally:
        api_client.delete_diary(created.id)
