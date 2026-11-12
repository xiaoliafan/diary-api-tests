"""基于 requests.Session 的日记平台接口客户端。"""

from typing import Any

import allure
import requests

from api.allure_utils import attach_response
from api.schemas import Diary, DiaryPage


class DiaryApiClient:
    """封装日记平台 REST 接口，统一管理 Session、超时和 Allure 附件。"""

    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def close(self) -> None:
        self.session.close()

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        """统一发送请求，并记录 Allure 请求步骤和响应附件。"""
        kwargs.setdefault("timeout", self.timeout)
        with allure.step(f"请求 {method.upper()} {path}"):
            response = self.session.request(
                method=method.upper(),
                url=f"{self.base_url}{path}",
                **kwargs,
            )
            attach_response(response, name=f"{method.upper()} {path}")
            return response

    def list_diaries(self, **params: Any) -> requests.Response:
        """分页查询日记，支持 page/pageSize/submitter/content 等筛选参数。"""
        return self.request("GET", "/api/diaries", params=params)

    def list_diaries_parsed(self, **params: Any) -> DiaryPage:
        response = self.list_diaries(**params)
        response.raise_for_status()
        return DiaryPage.model_validate(response.json())

    def get_diary(self, diary_id: int) -> requests.Response:
        """查询单条日记。"""
        return self.request("GET", f"/api/diaries/{diary_id}")

    def get_diary_parsed(self, diary_id: int) -> Diary:
        response = self.get_diary(diary_id)
        response.raise_for_status()
        return Diary.model_validate(response.json())

    def create_diary(self, submitter: str, content: str) -> requests.Response:
        """新增日记。"""
        return self.request(
            "POST",
            "/api/diaries",
            json={"submitter": submitter, "content": content},
        )

    def create_diary_parsed(self, submitter: str, content: str) -> Diary:
        response = self.create_diary(submitter, content)
        response.raise_for_status()
        return Diary.model_validate(response.json())

    def update_diary(self, diary_id: int, submitter: str, content: str) -> requests.Response:
        """编辑日记。"""
        return self.request(
            "PUT",
            f"/api/diaries/{diary_id}",
            json={"submitter": submitter, "content": content},
        )

    def update_diary_parsed(self, diary_id: int, submitter: str, content: str) -> Diary:
        response = self.update_diary(diary_id, submitter, content)
        response.raise_for_status()
        return Diary.model_validate(response.json())

    def delete_diary(self, diary_id: int) -> requests.Response:
        """删除日记。"""
        return self.request("DELETE", f"/api/diaries/{diary_id}")
