"""日记列表页对象。"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from ui_tests.pages.base_page import BasePage


class DiaryListPage(BasePage):
    """封装列表页的查询、分页和行操作。"""

    TITLE = (By.CSS_SELECTOR, ".page-head h1")
    SUBMITTER_FILTER = (By.ID, "fSubmitter")
    CONTENT_FILTER = (By.ID, "fContent")
    SEARCH_BUTTON = (By.ID, "btnSearch")
    RESET_BUTTON = (By.ID, "btnReset")
    ADD_BUTTON = (By.ID, "btnAdd")
    TABLE_BODY = (By.ID, "diaryBody")
    TABLE_ROWS = (By.CSS_SELECTOR, "#diaryBody tr")
    TOAST = (By.ID, "toast")

    def open(self) -> None:
        super().open("/")
        self.wait_visible(self.TABLE_BODY)
        self.wait_for_table_loaded()

    def title(self) -> str:
        return self.wait_visible(self.TITLE).text.strip()

    def wait_for_table_loaded(self) -> None:
        self.wait.until(
            lambda _: "加载中..." not in self.driver.find_element(*self.TABLE_BODY).text
        )#循环获取表格的文字，当文本里没有加载中时代表加载完成了 返回True 停止等待
        # 上面常量区有定义TABLE_BODY

    def table_text(self) -> str:
        self.wait_for_table_loaded()
        return self.driver.find_element(*self.TABLE_BODY).text

    def search_by_submitter(self, submitter: str) -> None:
        field = self.wait_visible(self.SUBMITTER_FILTER)
        field.clear()
        field.send_keys(submitter)
        self.wait_clickable(self.SEARCH_BUTTON).click()
        self.wait_for_table_loaded()

    def reset_filters(self) -> None:
        self.wait_clickable(self.RESET_BUTTON).click()
        self.wait_for_table_loaded()

    def click_add(self) -> None:
        self.wait_clickable(self.ADD_BUTTON).click()

    def rows(self) -> list[WebElement]:
        self.wait_for_table_loaded()
        return self.driver.find_elements(*self.TABLE_ROWS)

    def find_row_by_submitter(self, submitter: str) -> WebElement | None:
        for row in self.driver.find_elements(*self.TABLE_ROWS):
            cells = row.find_elements(By.TAG_NAME, "td")
            if cells and cells[0].text.strip() == submitter:
                return row
        return None

    def wait_for_row(self, submitter: str) -> WebElement:
        return self.wait.until(lambda _: self.find_row_by_submitter(submitter))

    def wait_for_row_absent(self, submitter: str) -> None:
        self.wait.until(lambda _: self.find_row_by_submitter(submitter) is None)

    def row_text(self, submitter: str) -> str:
        return self.wait_for_row(submitter).text

    def click_action(self, submitter: str, action: str) -> None:
        row = self.wait_for_row(submitter)
        button = row.find_element(By.CSS_SELECTOR, f"button[data-action='{action}']")
        self.wait.until(lambda _: button.is_enabled())
        button.click()

    def wait_for_toast(self, text: str | None = None):
        """等待 toast 显示；页面元素一直存在，所以必须等待 show 样式。"""

        def _toast_visible(_):
            toast = self.driver.find_element(*self.TOAST)
            classes = (toast.get_attribute("class") or "").split()
            if "show" not in classes:
                return False
            if text is not None and toast.text.strip() != text:
                return False
            return toast

        return self.wait.until(_toast_visible)
