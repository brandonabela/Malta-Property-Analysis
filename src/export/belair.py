import pandas as pd

from tqdm import tqdm

from helper.fetch import Fetch
from helper.dynamic_scrape import DynamicScrape


class Belair(object):
    source = 'Belair'

    columns = [
        'Reference', 'Town', 'Type',
        'Latitude', 'Longitude',
        'Bedrooms', 'Bathrooms',
        'TotalSqm', 'IntArea', 'ExtArea', 'Price'
    ]

    @staticmethod
    def fetch_data(is_sale: bool) -> pd.DataFrame:
        data = pd.DataFrame()
        proxies = Fetch.load_proxies()

        page_type = 'buy' if is_sale else 'rent'
        page_element = '//div[@class="grid grid-pad"]'
        driver = Fetch.get_dynamic(f'https://www.belair.com.mt/search-results/?f1=to-{page_type}&pr=1', proxies, page_element)

        x_pages = '//ul[@class="pagination"]//li[@class="end"]/a'
        pages = int(DynamicScrape.get_text(driver, x_pages))

        for page in tqdm(range(1, pages+1)):
            x_cards = '//div[contains(@class, "property-grid")]'
            cards = DynamicScrape.get_elements(driver, x_cards)

            listing = []

            x_reference = './/div[@class="row web_ref"]/span'
            x_town = './/span[contains(@class, "mega-post-location")]/span'
            x_type = './/h3[contains(@class, "mega-post-title")]'
            x_bedrooms = './/div[@class="greybox row"]/span[contains(@class, "detail-left")]/span'
            x_bathrooms = './/div[@class="greybox row"]/span[contains(@class, "detail-center")]/span'
            x_total_sqm = './/div[@class="greybox row"]/span[contains(@class, "detail-right")]/span'
            x_price = './/span[contains(@class, "mega-post-price")]'

            for card in cards:
                reference = DynamicScrape.get_text(card, x_reference).replace('Ref. ', '')
                town = DynamicScrape.get_text(card, x_town).title()
                type = DynamicScrape.get_text(card, x_type).replace(' For Sale', '').replace(' For Rent', '')
                latitude = None
                longitude = None

                bedrooms = DynamicScrape.get_text(card, x_bedrooms).replace(' Bedrooms', '')
                bathrooms = DynamicScrape.get_text(card, x_bathrooms).replace(' Bathrooms', '')

                total_sqm = DynamicScrape.get_text(card, x_total_sqm)
                total_sqm = total_sqm.replace(' m2', '') if len(total_sqm) > 3 else None
                int_area = None
                ext_area = None

                price = DynamicScrape.get_text(card, x_price)
                price = price.replace('€ ', '').replace(',', '').replace(' monthly', '')

                listing.append([
                    reference, town, type,
                    latitude, longitude,
                    bedrooms, bathrooms,
                    total_sqm, int_area, ext_area, price
                ])

            # Concatenate previous data frame with data of current page
            page_data = pd.DataFrame(listing, columns=Belair.columns)
            data = pd.concat([data, page_data])

            # Click Next Page
            x_next_page = f'//ul[@class="pagination"]//li/a[text()="{page+1}"]'
            x_await_page = f'//ul[@class="pagination"]//li[@class="currentpage"]/a[text()="{page+1}"]'
            DynamicScrape.click_element(driver, x_next_page, x_await_page)

        # Add source and rename columns
        data.insert(0, 'Is_Sale', is_sale)
        data.insert(1, 'Source', Belair.source)

        # Return the data
        return data

    @staticmethod
    def fetch_res_sale():
        return Belair.fetch_data(True)

    @staticmethod
    def fetch_res_rent():
        return Belair.fetch_data(False)

    @staticmethod
    def fetch_all():
        # Create progress bar
        pbar = tqdm(total=2)

        # Fetching data
        res_sale = Belair.fetch_res_sale()
        pbar.update(1)

        res_rent = Belair.fetch_res_rent()
        pbar.update(1)

        # Close progress bar
        pbar.close()

        # Concatenate Data
        data = pd.concat([res_sale, res_rent])

        # Return Desired Data
        return data
