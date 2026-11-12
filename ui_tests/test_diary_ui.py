"""日记平台 UI 自动化测试。"""

import pytest

from api.client import DiaryApiClient
from ui_tests.pages.confirm_modal import ConfirmModal
from ui_tests.pages.diary_form_modal import DiaryFormModal
from ui_tests.pages.diary_list_page import DiaryListPage

pytestmark = pytest.mark.ui


def _delete_by_submitter(api_client: DiaryApiClient, submitter: str) -> None:
    """按提交人清理 UI 测试产生的数据。"""
    page = api_client.list_diaries_parsed(submitter=submitter, pageSize=100)
    for item in page.items:
        api_client.delete_diary(item.id)


def test_list_page_loads(diary_list_page: DiaryListPage) -> None:
    """列表页可以正常打开并完成异步加载。"""
    #动态等待表格加载完成并获取表格内容
    assert diary_list_page.title() == "日记列表"
    assert "加载中..." not in diary_list_page.table_text()


def test_search_diary_by_submitter(
    diary_list_page: DiaryListPage,
    api_client: DiaryApiClient,
    unique_tag: str,
) -> None:
    """通过页面查询指定提交人，验证只展示匹配数据。"""
    submitter = f"UI查询-{unique_tag}"
    content = f"查询内容-{unique_tag}"
    created = api_client.create_diary_parsed(submitter, content)

    try:
        diary_list_page.search_by_submitter(submitter)
        row_text = diary_list_page.row_text(submitter)
        assert submitter in row_text
        assert content in row_text
    finally:
        api_client.delete_diary(created.id)


def test_create_edit_delete_diary(
    diary_list_page: DiaryListPage,
    diary_form_modal: DiaryFormModal,
    confirm_modal: ConfirmModal,
    api_client: DiaryApiClient,
    unique_tag: str,
) -> None:
    """通过 UI 完成新增、查询、编辑、删除的完整链路。"""
    submitter = f"UI用户-{unique_tag}"
    content = f"UI新增-{unique_tag}"
    updated_content = f"UI修改-{unique_tag}"

    try:
        diary_list_page.click_add()
        diary_form_modal.wait_open().fill(submitter, content).submit()
        diary_list_page.wait_for_toast("新增成功")
        diary_form_modal.wait_closed()

        diary_list_page.search_by_submitter(submitter)
        assert content in diary_list_page.row_text(submitter)

        diary_list_page.click_action(submitter, "edit")
        diary_form_modal.wait_open().fill(content=updated_content).submit()
        diary_list_page.wait_for_toast("修改成功")
        diary_form_modal.wait_closed()

        diary_list_page.search_by_submitter(submitter)
        assert updated_content in diary_list_page.row_text(submitter)

        diary_list_page.click_action(submitter, "delete")
        assert "确定要删除" in confirm_modal.wait_open().text()
        confirm_modal.confirm()
        diary_list_page.wait_for_toast("删除成功")

        diary_list_page.search_by_submitter(submitter)
        diary_list_page.wait_for_row_absent(submitter)
    finally:
        _delete_by_submitter(api_client, submitter)


def test_required_fields_show_errors(
    diary_list_page: DiaryListPage,
    diary_form_modal: DiaryFormModal,
) -> None:
    """提交人或内容为空时，表单展示对应校验提示。"""
    diary_list_page.click_add()
    diary_form_modal.wait_open().submit()

    assert diary_form_modal.submitter_error() == "请输入提交人"
    assert diary_form_modal.content_error() == "请输入提交内容"
    diary_form_modal.cancel()
