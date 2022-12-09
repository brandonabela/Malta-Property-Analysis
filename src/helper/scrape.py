import random
import requests

from bs4 import BeautifulSoup


class Scrape(object):
    h_session: requests.Session = requests.Session()

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    }

    @staticmethod
    def load_proxies():
        url = 'https://sslproxies.org/'

        response = requests.get(url, headers=Scrape.header)
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

        page = Scrape.h_session.get(url, headers=Scrape.header, proxies=proxy)
        soup = BeautifulSoup(page.text.encode('utf-8').decode('ascii', 'ignore'), 'lxml')

        return soup
