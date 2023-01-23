from typing import List, Union
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class DynamicScrape(object):
    @staticmethod
    def await_element(driver: WebDriver, x_path: str, seconds: int = 15) -> bool:
        if x_path:
            try:
                WebDriverWait(driver, seconds).until(EC.visibility_of_element_located((By.XPATH, x_path)))
                return True
            except TimeoutException:
                return False

    @staticmethod
    def await_no_element(driver: WebDriver, x_path: str, seconds: int = 10) -> bool:
        if x_path:
            try:
                WebDriverWait(driver, seconds).until(EC.invisibility_of_element_located((By.XPATH, x_path)))
                return True
            except TimeoutException:
                return False

    @staticmethod
    def get_element(driver: WebDriver, x_path: str) -> Union[None, WebElement]:
        try:
            return driver.find_element(By.XPATH, x_path)
        except NoSuchElementException:
            return None

    @staticmethod
    def get_elements(driver: WebDriver, x_path: str) -> Union[None, List[WebElement]]:
        try:
            return driver.find_elements(By.XPATH, x_path)
        except NoSuchElementException:
            return None

    @staticmethod
    def get_text(driver: WebDriver, x_path: str) -> str:
        element = DynamicScrape.get_element(driver, x_path)

        return element.text if element else ''

    @staticmethod
    def get_texts(driver: WebDriver, x_path: str) -> str:
        elements = DynamicScrape.get_elements(driver, x_path)

        return [element.text if elements else '' for element in elements]

    @staticmethod
    def get_hidden_text(driver: WebDriver, x_path: str) -> str:
        element = DynamicScrape.get_element(driver, x_path)

        return element.get_attribute('textContent') if element else ''

    @staticmethod
    def get_link(driver: WebDriver, x_path: str) -> str:
        element = DynamicScrape.get_element(driver, x_path)

        return element.get_attribute('href') if element else ''

    @staticmethod
    def get_links(driver: WebDriver, x_path: str) -> str:
        elements = DynamicScrape.get_elements(driver, x_path)

        return [element.get_attribute('href') if elements else '' for element in elements]

    @staticmethod
    def click_element(driver: WebDriver, x_path: str, x_path_await: str = '') -> bool:
        element = DynamicScrape.get_element(driver, x_path)

        if element:
            driver.execute_script("arguments[0].click();", element)
            return DynamicScrape.await_element(driver, x_path_await)
        else:
            return False

    @staticmethod
    def open_tab_link(driver: WebDriver, url: str, x_path_await_element: str = '') -> bool:
        try:
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(url)

            return DynamicScrape.await_element(driver, x_path_await_element)
        except WebDriverException:
            return False

    @staticmethod
    def close_tab_link(driver: WebDriver, tab_index: int = 0):
        driver.close()
        driver.switch_to.window(driver.window_handles[tab_index])
