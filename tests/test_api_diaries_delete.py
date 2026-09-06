"""DELETE /api/diaries/{id} 删除接口用例。"""

from collections.abc import Callable

from api.client import DiaryApiClient
from api.schemas import Diary, Message


def test_delete_diary_and_verify_gone(api_client: DiaryApiClient, created_diary: Diary) -> None:
    """删除成功，删除后再查询返回 404。"""
    response = api_client.delete_diary(created_diary.id)
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    get_response = api_client.get_diary(created_diary.id)
    assert get_response.status_code == 404
    Message.model_validate(get_response.json())


def test_query_zhou_yu_then_delete(
    api_client: DiaryApiClient,
    diary_id_by_submitter: Callable[[str], int],
    unique_tag: str,
) -> None:
    """先创建一条 submitter=周雨 的临时日记，再按提交人查 id 并删除。"""
    response = api_client.create_diary(submitter="周雨", content=f"待删除-{unique_tag}")
    assert response.status_code == 201
    created = Diary.model_validate(response.json())

    target_id = diary_id_by_submitter("周雨")
    assert target_id == created.id

    delete_response = api_client.delete_diary(target_id)
    assert delete_response.status_code == 200
    assert delete_response.json() == {"ok": True}

    get_response = api_client.get_diary(target_id)
    assert get_response.status_code == 404
    Message.model_validate(get_response.json())
