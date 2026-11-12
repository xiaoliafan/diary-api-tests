"""新增和编辑日记的表单弹窗对象。"""

from selenium.webdriver.common.by import By

from ui_tests.pages.base_page import BasePage


class DiaryFormModal(BasePage):
    """封装新增/编辑弹窗的填写、提交和校验提示。"""

    MASK = (By.ID, "formMask")
    SUBMITTER_INPUT = (By.ID, "formSubmitter")
    CONTENT_INPUT = (By.ID, "formContent")
    SUBMIT_BUTTON = (By.ID, "formSubmit")
    CANCEL_BUTTON = (By.ID, "formCancel")
    SUBMITTER_ERROR = (By.ID, "submitterError")
    CONTENT_ERROR = (By.ID, "contentError")

    def wait_open(self) -> "DiaryFormModal":
        self.wait_visible(self.MASK)
        return self

    def wait_closed(self) -> None:
        self.wait_invisible(self.MASK)

    def fill(
        self,
        submitter: str | None = None,
        content: str | None = None,
    ) -> "DiaryFormModal":
        if submitter is not None:
            field = self.wait_visible(self.SUBMITTER_INPUT)
            field.clear()
            field.send_keys(submitter)
        if content is not None:
            field = self.wait_visible(self.CONTENT_INPUT)
            field.clear()
            field.send_keys(content)
        return self

    def submit(self) -> None:
        self.wait_clickable(self.SUBMIT_BUTTON).click()

    def cancel(self) -> None:
        self.wait_clickable(self.CANCEL_BUTTON).click()
        self.wait_closed()

    def submitter_error(self) -> str:
        return self.wait_visible(self.SUBMITTER_ERROR).text.strip()

    def content_error(self) -> str:
        return self.wait_visible(self.CONTENT_ERROR).text.strip()
