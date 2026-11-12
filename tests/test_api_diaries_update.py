"""PUT /api/diaries/{id} 编辑接口用例。"""

import allure
import pytest

from api.client import DiaryApiClient
from api.schemas import Diary, Message

pytestmark = pytest.mark.api


def test_update_diary_content(api_client: DiaryApiClient, created_diary: Diary) -> None:
    """编辑日记内容成功，且修改时间不早于提交时间。"""
    allure.dynamic.title("编辑日记内容")
    new_content = f"更新后-{created_diary.id}"

    with allure.step("发送编辑请求"):
        updated = api_client.update_diary_parsed(
            created_diary.id,
            created_diary.submitter,
            new_content,
        )

    with allure.step("校验编辑结果"):
        assert updated.id == created_diary.id
        assert updated.content == new_content
        assert updated.modifyTime >= updated.submitTime


# 数据驱动：覆盖普通内容、特殊字符、空值和长文本
@pytest.mark.parametrize(
    "new_content,expected_status",
    [
        ("普通更新内容", 200),
        ("包含特殊字符@（*¥", 200),
        ("", 400),
        ("非常长的内容" * 100, 200),
    ],
)
def test_update_diary_with_multiple_contents(
    api_client: DiaryApiClient,
    created_diary: Diary,
    new_content: str,
    expected_status: int,
) -> None:
    """使用不同的新内容编辑日记，验证返回状态码和修改结果。"""
    content_preview = new_content[:12] if new_content else "空内容"
    allure.dynamic.title(f"编辑内容：{content_preview}（期望 {expected_status}）")

    with allure.step("发送编辑请求"):
        # 使用原始响应方法，非 2xx 不会提前抛异常，保留 status_code 断言
        response = api_client.update_diary(
            created_diary.id,
            created_diary.submitter,
            new_content,
        )

    with allure.step("校验状态码"):
        assert response.status_code == expected_status

    if expected_status == 200:
        with allure.step("校验编辑后的内容"):
            updated = Diary.model_validate(response.json())
            assert updated.id == created_diary.id
            assert updated.content == new_content
            assert updated.modifyTime >= updated.submitTime
    else:
        with allure.step("校验错误响应"):
            error = Message.model_validate(response.json())
            assert error.error


# 按当前阶段要求，依赖固定 id=15 / submitter=st 的用例暂时停用。
# # 一个不用删除的修改数据
# @pytest.mark.parametrize(
#     "diary_id,submitter,new_content,expected_status",
#     [
#         (15, "st", "自动化修改的数据", 200),
#     ],
# )
# def test_update_diary_sql_contents(
#     api_client: DiaryApiClient,
#     diary_id: int,
#     submitter: str,
#     new_content: str,
#     expected_status: int,
# ) -> None:
#     """调用接口直接更新数据库的数据。"""
#     response = api_client.update_diary(diary_id, submitter, new_content)
#     assert response.status_code == expected_status
#
#     updated = Diary.model_validate(response.json())
#     assert updated.id == diary_id
#     assert updated.content == new_content
#     assert updated.modifyTime >= updated.submitTime


def query_diary_id_by_submitter(api_client: DiaryApiClient, submitter: str) -> int:
    """按提交人查询第一条日记 id，供文件内多个接口用例串联使用。"""
    page = api_client.list_diaries_parsed(submitter=submitter, pageSize=1)
    assert page.total >= 1, f"未找到 submitter={submitter} 的日记"
    return page.items[0].id


def test_query_then_update_diary_content(api_client: DiaryApiClient) -> None:
    """先查询 submitter=st 的日记 id，再把 id 传给编辑接口修改 content。"""
    allure.dynamic.title("先查询日记 id 再修改内容")

    with allure.step("查询 submitter=st 的日记 id"):
        target_id = query_diary_id_by_submitter(api_client, "st")

    new_content = "先查询后修改提交内容"
    with allure.step("使用查询到的 id 编辑内容"):
        response = api_client.update_diary(target_id, "st", new_content)

    with allure.step("校验编辑结果"):
        assert response.status_code == 200
        updated = Diary.model_validate(response.json())
        assert updated.id == target_id
        assert updated.submitter == "st"
        assert updated.content == new_content
        assert updated.modifyTime >= updated.submitTime
