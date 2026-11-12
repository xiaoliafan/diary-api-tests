"""UI 测试夹具：浏览器生命周期、页面对象和测试数据。"""

import uuid
from collections.abc import Generator

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver

from api.client import DiaryApiClient
from ui_tests.pages.confirm_modal import ConfirmModal
from ui_tests.pages.diary_form_modal import DiaryFormModal
from ui_tests.pages.diary_list_page import DiaryListPage


def _build_driver(browser: str, headless: bool) -> WebDriver:
    """按浏览器类型创建 WebDriver，由 Selenium Manager 自动匹配驱动。"""
    browser = browser.lower()

    if browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1440,1000")
        options.add_argument("--disable-gpu")
        return webdriver.Chrome(options=options)

    if browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        return webdriver.Firefox(options=options)

    if browser == "edge":
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless=new")
        return webdriver.Edge(options=options)

    if browser == "safari":
        if headless:
            raise pytest.UsageError("Safari 不支持 headless 模式，请去掉 --headless")
        return webdriver.Safari()

    raise pytest.UsageError(f"不支持的浏览器：{browser}")


@pytest.fixture(scope="session")
def base_url(request: pytest.FixtureRequest) -> str:
    """被测服务地址，来自根级 conftest.py 的 --base-url。"""
    return request.config.getoption("--base-url").rstrip("/")


@pytest.fixture
def driver(request: pytest.FixtureRequest) -> Generator[WebDriver, None, None]:
    """创建浏览器，测试结束后无条件执行 quit。"""
    browser = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")
    web_driver = _build_driver(browser, headless)
    web_driver.set_window_size(1440, 1000)
    web_driver.implicitly_wait(0)
    try:
        yield web_driver
    finally:
        web_driver.quit()


@pytest.fixture(scope="session")
def api_client(base_url: str) -> Generator[DiaryApiClient, None, None]:
    """UI 测试独立使用的接口客户端，用于准备和清理测试数据。"""
    client = DiaryApiClient(base_url)
    response = client.list_diaries(page=1, pageSize=1)
    assert response.status_code == 200, (
        f"日记平台不可用：{base_url} 返回 {response.status_code}，请先启动后端服务"
    )
    try:
        yield client
    finally:
        client.close()


@pytest.fixture
def unique_tag() -> str:
    """生成 UI 测试数据唯一标识，避免用例之间互相干扰。"""
    return uuid.uuid4().hex[:8]


@pytest.fixture
def diary_list_page(driver: WebDriver, base_url: str) -> DiaryListPage:
    page = DiaryListPage(driver, base_url)
    page.open()
    return page


@pytest.fixture
def diary_form_modal(driver: WebDriver, base_url: str) -> DiaryFormModal:
    return DiaryFormModal(driver, base_url)


@pytest.fixture
def confirm_modal(driver: WebDriver, base_url: str) -> ConfirmModal:
    return ConfirmModal(driver, base_url)
