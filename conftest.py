"""项目级 pytest 全局配置，只放接口测试和 UI 测试共用的内容。"""

import os

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """注册 UI 测试命令行参数。"""
    parser.addoption(
        "--browser",
        action="store",
        default=os.getenv("UI_BROWSER", "chrome"),
        choices=("chrome", "firefox", "edge", "safari"),
        help="UI 测试使用的浏览器，默认 chrome，可用 UI_BROWSER 环境变量覆盖",
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=os.getenv("UI_HEADLESS", "").lower() in {"1", "true", "yes"},
        help="UI 测试以无头模式运行",
    )
    parser.addoption(
        "--base-url",
        action="store",
        default=os.getenv("DIARY_BASE_URL", "http://127.0.0.1:8080"),
        help="被测服务地址，默认 http://127.0.0.1:8080",
    )
