"""删除确认弹窗对象。"""

from selenium.webdriver.common.by import By

from ui_tests.pages.base_page import BasePage


class ConfirmModal(BasePage):
    """封装删除确认弹窗。"""

    MASK = (By.ID, "confirmMask")
    TEXT = (By.ID, "confirmText")
    CONFIRM_BUTTON = (By.ID, "confirmOk")
    CANCEL_BUTTON = (By.ID, "confirmCancel")

    def wait_open(self) -> "ConfirmModal":
        self.wait_visible(self.MASK)
        return self

    def confirm(self) -> None:
        self.wait_clickable(self.CONFIRM_BUTTON).click()
        self.wait_invisible(self.MASK)

    def cancel(self) -> None:
        self.wait_clickable(self.CANCEL_BUTTON).click()
        self.wait_invisible(self.MASK)

    def text(self) -> str:
        return self.wait_visible(self.TEXT).text.strip()
