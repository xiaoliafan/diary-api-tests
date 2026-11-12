"""YAML 测试数据加载和 Pydantic 校验。"""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

_TEST_DATA_DIR = Path(__file__).resolve().parent.parent / "test_data" / "api"


class QueryCase(BaseModel):
    """查询接口的稳定输入和简单预期字段。"""

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    params: dict[str, Any] = Field(default_factory=dict)
    expected_status: int = 200
    expected_fields: dict[str, Any] = Field(default_factory=dict)


class QueryCaseFile(BaseModel):
    """YAML 文件的顶层结构。"""

    model_config = ConfigDict(extra="forbid")

    cases: list[QueryCase]

    @model_validator(mode="after")
    def validate_unique_ids(self) -> "QueryCaseFile":
        case_ids = [case.id for case in self.cases]
        duplicates = sorted({case_id for case_id in case_ids if case_ids.count(case_id) > 1})
        if duplicates:
            raise ValueError(f"YAML 用例 id 重复：{', '.join(duplicates)}")
        return self


def load_query_cases(filename: str) -> list[QueryCase]:
    """按文件名加载测试数据，并完成 Pydantic 结构校验。"""
    path = _TEST_DATA_DIR / filename
    with path.open("r", encoding="utf-8") as stream:
        raw_data = yaml.safe_load(stream)
    return QueryCaseFile.model_validate(raw_data).cases
