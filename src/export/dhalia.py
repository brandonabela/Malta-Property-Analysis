import pandas as pd

from tqdm import tqdm

from helper.fetch import Fetch
from helper.dynamic_scrape import DynamicScrape


class Dhalia(object):
    source = 'Dhalia'

    columns = [
        'Reference', 'Town', 'Type',
        'Latitude', 'Longitude',
        'Rooms', 'Bedrooms', 'Bathrooms',
        'TotalSqm', 'IntArea', 'ExtArea', 'Price'
    ]

    @staticmethod
    def fetch_data(is_sale: bool) -> pd.DataFrame:
        data = pd.DataFrame()
        proxies = Fetch.load_proxies()

        page_type = 'buy' if is_sale else 'rent'
        page_element = f'//div[@class="searchForm searchForm--quick-search page-{page_type}"]'
        driver = Fetch.get_dynamic(f'https://www.dhalia.com/{page_type}/?pageIndex=1', proxies, page_element)

        x_pages = '//li[@class="pager__last"]/a'
        pages = int(DynamicScrape.get_href(driver, x_pages).split('=')[1])

        for page in tqdm(range(1, pages+1)):
            x_cards = '//div[@class="ItemContent"]'
            cards = DynamicScrape.get_elements(driver, x_cards)

            listing = []

            x_reference = './/span[@class="propertybox__ref-link"]'
            x_town = './/div[@class="propertybox__left-col"]/h2'
            x_type = './/div[@class="propertybox__left-col"]/h3'
            x_bedrooms = './/div[@class="propertybox__footer"]'
            x_price = './/span[@class="propertybox__price"]'

            for card in cards:
                reference = DynamicScrape.get_text(card, x_reference)
                town = DynamicScrape.get_text(card, x_town)
                type = DynamicScrape.get_text(card, x_type)
                latitude = None
                longitude = None

                rooms = None
                bedrooms = DynamicScrape.get_text(card, x_bedrooms).replace('\nSole Agency', '').strip()
                bathrooms = None

                total_sqm = None
                int_area = None
                ext_area = None

                price = DynamicScrape.get_text(card, x_price)
                price = price.split(' ')[0].replace('€', '').replace(',', '')

                listing.append([
                    reference, town, type,
                    latitude, longitude,
                    rooms, bedrooms, bathrooms,
                    total_sqm, int_area, ext_area, price
                ])

            # Concatenate previous data frame with data of current page
            page_data = pd.DataFrame(listing, columns=Dhalia.columns)
            data = pd.concat([data, page_data])

            # Click Next Page
            x_next_page = f'//ul[@class="pager"]/li/a/span[text()="{page+1}"]'
            x_await_page = f'//ul[@class="pager"]/li[@class="pager__current"]/a/span[text()="{page+1}"]'
            DynamicScrape.click_element(driver, x_next_page, x_await_page)

        # Add source and rename columns
        data.insert(0, 'Is_Sale', is_sale)
        data.insert(1, 'Source', Dhalia.source)

        # Return the data
        return data

    @staticmethod
    def fetch_res_sale():
        return Dhalia.fetch_data(True)

    @staticmethod
    def fetch_res_rent():
        return Dhalia.fetch_data(False)

    @staticmethod
    def fetch_all():
        # Create progress bar
        pbar = tqdm(total=2)

        # Fetching data
        res_sale = Dhalia.fetch_res_sale()
        pbar.update(1)

        res_rent = Dhalia.fetch_res_rent()
        pbar.update(1)

        # Close progress bar
        pbar.close()

        # Concatenate Data
        data = pd.concat([res_sale, res_rent])

        # Return Desired Data
        return data
