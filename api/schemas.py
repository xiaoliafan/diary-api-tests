"""接口响应模型，使用 Pydantic 校验响应结构和字段类型。"""

from pydantic import BaseModel


class Diary(BaseModel):
    """日记实体。"""

    id: int
    submitter: str
    content: str
    submitTime: int
    modifyTime: int


class DiaryPage(BaseModel):
    """分页查询响应。"""

    total: int
    page: int
    pageSize: int
    items: list[Diary]


class Message(BaseModel):
    """通用消息响应，如错误提示。"""

    error: str
