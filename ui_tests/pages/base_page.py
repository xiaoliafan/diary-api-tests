"""页面对象基类。"""

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

Locator = tuple[str, str]


class BasePage:
    """封装浏览器和显式等待，供各页面对象复用。"""

    def __init__(self, driver: WebDriver, base_url: str, timeout: float = 10.0) -> None:
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, timeout)

    def open(self, path: str = "/") -> None:
        self.driver.get(f"{self.base_url}{path}")

    def wait_visible(self, locator: Locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_clickable(self, locator: Locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def wait_invisible(self, locator: Locator):
        return self.wait.until(EC.invisibility_of_element_located(locator))
