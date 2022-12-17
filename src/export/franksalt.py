import pandas as pd

from tqdm import tqdm

from helper.fetch import Fetch
from helper.dynamic_scrape import DynamicScrape


class FrankSalt(object):
    source = 'Frank Salt'

    columns = [
        'Reference', 'Town', 'Type',
        'Bedrooms', 'Bathrooms',
        'TotalSqm', 'IntArea', 'ExtArea', 'Price'
    ]

    @staticmethod
    def fetch_data(is_sale: bool) -> pd.DataFrame:
        data = pd.DataFrame()
        proxies = Fetch.load_proxies()

        page_type = 'residential-buy' if is_sale else 'residential-rent'
        page_element = '//div[@class="fra-property-catalog"][last()]/div[@class="property-description"]'
        driver = Fetch.get_dynamic(f'https://franksalt.com.mt/properties?mode={page_type}&pg=1', proxies, page_element)

        x_pages = '//li[contains(@class, "paginationjs-last")]/a'
        pages = int(DynamicScrape.get_text(driver, x_pages))

        for page in tqdm(range(1, pages+1)):
            x_cards = '//div[@class="fra-property-catalog"]'
            cards = DynamicScrape.get_elements(driver, x_cards)

            listing = []

            x_reference = './/span[@class="ref-no"]'
            x_type_town = './/h4[@class="property-address"]'
            x_bedrooms = './/span[@class="bed-count"]'
            x_bathrooms = './/span[@class="bath-count"]'
            x_price = './/span[@class="currency-price-container"]'

            for card in cards:
                reference = DynamicScrape.get_text(card, x_reference).replace('REF. ', '')
                town = None
                type = None

                type_town = DynamicScrape.get_text(card, x_type_town).split(' in ')

                if len(type_town) == 2:
                    town = type_town[1]
                    type = type_town[0]

                bedrooms = DynamicScrape.get_text(card, x_bedrooms)
                bathrooms = DynamicScrape.get_text(card, x_bathrooms)

                total_sqm = None
                int_area = None
                ext_area = None

                price = DynamicScrape.get_text(card, x_price).replace(',', '').replace('/month', '')

                listing.append([
                    reference, town, type,
                    bedrooms, bathrooms,
                    total_sqm, int_area, ext_area, price
                ])

            # Concatenate previous data frame with data of current page
            page_data = pd.DataFrame(listing, columns=FrankSalt.columns)
            data = pd.concat([data, page_data])

            # Click Next Page
            x_next_page = f'//li[contains(@class, "paginationjs-page")]/a[text()="{page+1}"]'
            x_await_page = f'//li[contains(@class, "paginationjs-page active")]/a[text()="{page+1}"]'
            DynamicScrape.click_element(driver, x_next_page, x_await_page)

        # Add source and rename columns
        data.insert(0, 'Is_Sale', is_sale)
        data.insert(1, 'Source', FrankSalt.source)

        # Return the data
        return data

    @staticmethod
    def fetch_res_sale():
        return FrankSalt.fetch_data(True)

    @staticmethod
    def fetch_res_rent():
        return FrankSalt.fetch_data(False)

    @staticmethod
    def fetch_all():
        # Create progress bar
        pbar = tqdm(total=2)

        # Fetching data
        res_sale = FrankSalt.fetch_res_sale()
        pbar.update(1)

        res_rent = FrankSalt.fetch_res_rent()
        pbar.update(1)

        # Close progress bar
        pbar.close()

        # Concatenate Data
        data = pd.concat([res_sale, res_rent])

        # Return Desired Data
        return data
