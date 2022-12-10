import random
import requests

from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.proxy import *
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException

from helper.dynamic_scrape import DynamicScrape


class Fetch(object):
    h_session: requests.Session = requests.Session()
    j_driver: WebDriver = None

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    }

    @staticmethod
    def load_proxies():
        url = 'https://sslproxies.org/'

        response = requests.get(url, headers=Fetch.header)
        soup = BeautifulSoup(response.content, 'lxml')

        https_proxies = filter(lambda item: "yes" in item.text, soup.select("table.table tr"))

        proxies = []

        for item in https_proxies:
            proxies.append('http://%s:%s' % (item.select_one("td").text, item.select_one("td:nth-of-type(2)").text))

        return proxies

    @staticmethod
    def get_static(url, proxies):
        rand = random.randint(0, len(proxies) - 1)
        proxy = {'http': proxies[rand]}

        page = Fetch.h_session.get(url, headers=Fetch.header, proxies=proxy)
        soup = BeautifulSoup(page.text.encode('utf-8').decode('ascii', 'ignore'), 'lxml')

        return soup

    @staticmethod
    def get_dynamic(url: str, proxies, x_path_await_element):
        rand = random.randint(0, len(proxies) - 1)

        if Fetch.j_driver is not None:
            Fetch.j_driver.close()
            Fetch.j_driver.quit()

        options = ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('start-maximized')
        options.add_argument('enable-automation')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-gpu')

        options.proxy = Proxy({
            'proxyType': ProxyType.MANUAL,
            'httpProxy': proxies[rand],
            'sslProxy': proxies[rand],
            'noProxy': ''
        })

        header = Fetch.header[list(Fetch.header.keys())[0]]
        options.add_argument(f'user-agent={header}')

        try:
            chrome_executable = Service(executable_path=ChromeDriverManager().install(), log_path='NUL')
            Fetch.j_driver = Chrome(service=chrome_executable, options=options)
            Fetch.j_driver.get(url)

            valid = DynamicScrape.await_element(Fetch.j_driver, x_path_await_element)

            if not valid:
                return None

            return Fetch.j_driver
        except WebDriverException:
            return None
