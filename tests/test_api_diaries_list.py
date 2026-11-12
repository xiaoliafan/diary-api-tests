"""GET /api/diaries 查询接口用例：YAML 数据驱动 + Python 动态场景。"""

import allure
import pytest

from api.client import DiaryApiClient
from api.schemas import Diary, DiaryPage
from api.yaml_loader import QueryCase, load_query_cases

pytestmark = pytest.mark.api

LIST_CASES = load_query_cases("diaries_list.yaml")


@pytest.mark.parametrize("case", LIST_CASES, ids=[case.id for case in LIST_CASES])
def test_list_query_cases(api_client: DiaryApiClient, case: QueryCase) -> None:
    """执行 YAML 中的稳定查询入参，验证状态码和简单预期字段。"""
    allure.dynamic.title(case.title)

    with allure.step("发送查询请求"):
        response = api_client.list_diaries(**case.params)

    with allure.step("校验状态码"):
        assert response.status_code == case.expected_status

    with allure.step("校验响应模型和预期字段"):
        page = DiaryPage.model_validate(response.json())
        for field_name, expected_value in case.expected_fields.items():
            assert getattr(page, field_name) == expected_value
        assert page.total >= len(page.items)
        assert len(page.items) <= page.pageSize


def test_list_filter_by_submitter(
    api_client: DiaryApiClient,
    created_diary: Diary,
) -> None:
    """按提交人关键字筛选。"""
    allure.dynamic.title("按提交人筛选日记")
    keyword = created_diary.submitter.rsplit("-", 1)[-1]

    with allure.step(f"查询提交人关键字 {keyword}"):
        page = api_client.list_diaries_parsed(submitter=keyword)

    with allure.step("校验筛选结果"):
        assert page.total >= 1
        assert all(keyword in item.submitter for item in page.items)


def test_list_filter_by_content(
    api_client: DiaryApiClient,
    created_diary: Diary,
) -> None:
    """按内容关键字筛选。"""
    allure.dynamic.title("按内容筛选日记")
    keyword = created_diary.content.rsplit("-", 1)[-1]

    with allure.step(f"查询内容关键字 {keyword}"):
        page = api_client.list_diaries_parsed(content=keyword)

    with allure.step("校验筛选结果"):
        assert page.total >= 1
        assert all(keyword in item.content for item in page.items)


def test_list_filter_by_submit_time_range(
    api_client: DiaryApiClient,
    created_diary: Diary,
) -> None:
    """按提交时间区间筛选。"""
    allure.dynamic.title("按提交时间区间筛选日记")
    start = created_diary.submitTime - 1
    end = created_diary.submitTime + 1

    with allure.step("查询提交时间区间"):
        page = api_client.list_diaries_parsed(submitStart=start, submitEnd=end)

    with allure.step("校验目标日记在结果中"):
        assert page.total >= 1
        assert any(item.id == created_diary.id for item in page.items)


def test_list_filter_by_modify_time_range(
    api_client: DiaryApiClient,
    created_diary: Diary,
) -> None:
    """按修改时间区间筛选。"""
    allure.dynamic.title("按修改时间区间筛选日记")
    start = created_diary.modifyTime - 1
    end = created_diary.modifyTime + 1

    with allure.step("查询修改时间区间"):
        page = api_client.list_diaries_parsed(modifyStart=start, modifyEnd=end)

    with allure.step("校验目标日记在结果中"):
        assert page.total >= 1
        assert any(item.id == created_diary.id for item in page.items)


def test_list_combine_filters(
    api_client: DiaryApiClient,
    created_diary: Diary,
) -> None:
    """提交人、内容、时间区间组合筛选。"""
    allure.dynamic.title("组合条件筛选日记")
    keyword = created_diary.submitter.rsplit("-", 1)[-1]

    with allure.step("发送组合条件查询"):
        page = api_client.list_diaries_parsed(
            submitter=keyword,
            content=keyword,
            submitStart=created_diary.submitTime - 1,
            submitEnd=created_diary.submitTime + 1,
            pageSize=100,
        )

    with allure.step("校验仅命中目标日记"):
        assert page.total >= 1
        assert all(item.id == created_diary.id for item in page.items)
