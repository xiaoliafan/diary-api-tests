"""GET /api/diaries 查询接口用例：覆盖正常、筛选、边界和异常入参。"""

import pytest

from api.client import DiaryApiClient
from api.schemas import Diary, DiaryPage


def test_list_uses_default_pagination(api_client: DiaryApiClient) -> None:
    """不带参数时使用默认分页 page=1、pageSize=10。"""
    page = api_client.list_diaries_parsed()
    assert page.page == 1
    assert page.pageSize == 10
    assert page.total > 0
    assert len(page.items) <= 10


def test_list_with_custom_page_and_page_size(api_client: DiaryApiClient) -> None:
    """自定义 page/pageSize 后按指定分页返回。"""
    page = api_client.list_diaries_parsed(page=2, pageSize=3)
    assert page.page == 2
    assert page.pageSize == 3
    assert 0 <= len(page.items) <= 3


@pytest.mark.parametrize(
    "params, expected_page, expected_page_size",
    [
        ({"page": 0}, 1, 10),
        ({"page": -2}, 1, 10),
        ({"pageSize": 0}, 1, 10),
        ({"pageSize": -5}, 1, 10),
        ({"page": "abc", "pageSize": "xyz"}, 1, 10),
    ],
)
def test_list_invalid_numbers_fall_back(
    api_client: DiaryApiClient,
    params: dict,
    expected_page: int,
    expected_page_size: int,
) -> None:
    """非法或越界的页码/页大小回退到默认值。"""
    page = api_client.list_diaries_parsed(**params)
    assert page.page == expected_page
    assert page.pageSize == expected_page_size


@pytest.mark.parametrize("page_size", [1, 100])
def test_list_page_size_allowed_boundaries(api_client: DiaryApiClient, page_size: int) -> None:
    """pageSize 最小值和最大值可直接使用。"""
    page = api_client.list_diaries_parsed(pageSize=page_size)
    assert page.pageSize == page_size
    assert len(page.items) <= page_size


def test_list_page_size_over_max_is_clamped(api_client: DiaryApiClient) -> None:
    """pageSize 超过 100 时被钳制到 100。"""
    page = api_client.list_diaries_parsed(pageSize=1000)
    assert page.pageSize == 100
    assert len(page.items) <= 100


def test_list_page_beyond_total_returns_empty_items(api_client: DiaryApiClient) -> None:
    """查询远超数据量的页码时返回空列表。"""
    page = api_client.list_diaries_parsed(page=999999, pageSize=10)
    assert page.page == 999999
    assert page.items == []


def test_list_filter_by_submitter(api_client: DiaryApiClient, created_diary: Diary) -> None:
    """按提交人关键字筛选。"""
    keyword = created_diary.submitter.rsplit("-", 1)[-1]
    page = api_client.list_diaries_parsed(submitter=keyword)
    assert page.total >= 1
    assert all(keyword in item.submitter for item in page.items)


def test_list_filter_by_content(api_client: DiaryApiClient, created_diary: Diary) -> None:
    """按内容关键字筛选。"""
    keyword = created_diary.content.rsplit("-", 1)[-1]
    page = api_client.list_diaries_parsed(content=keyword)
    assert page.total >= 1
    assert all(keyword in item.content for item in page.items)


def test_list_filter_by_submit_time_range(api_client: DiaryApiClient, created_diary: Diary) -> None:
    """按提交时间区间筛选。"""
    start = created_diary.submitTime - 1
    end = created_diary.submitTime + 1
    page = api_client.list_diaries_parsed(submitStart=start, submitEnd=end)
    assert page.total >= 1
    assert any(item.id == created_diary.id for item in page.items)


def test_list_filter_by_modify_time_range(api_client: DiaryApiClient, created_diary: Diary) -> None:
    """按修改时间区间筛选。"""
    start = created_diary.modifyTime - 1
    end = created_diary.modifyTime + 1
    page = api_client.list_diaries_parsed(modifyStart=start, modifyEnd=end)
    assert page.total >= 1
    assert any(item.id == created_diary.id for item in page.items)


def test_list_combine_filters(api_client: DiaryApiClient, created_diary: Diary) -> None:
    """提交人、内容、时间区间组合筛选。"""
    keyword = created_diary.submitter.rsplit("-", 1)[-1]
    page = api_client.list_diaries_parsed(
        submitter=keyword,
        content=keyword,
        submitStart=created_diary.submitTime - 1,
        submitEnd=created_diary.submitTime + 1,
        pageSize=100,
    )
    assert page.total >= 1
    assert all(item.id == created_diary.id for item in page.items)
