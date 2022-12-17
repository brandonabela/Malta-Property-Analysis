import pandas as pd

from tqdm import tqdm

from helper.fetch import Fetch
from helper.dynamic_scrape import DynamicScrape


class SaraGrech(object):
    source = 'Sara Grech'

    columns = [
        'Reference', 'Town', 'Type',
        'Bedrooms', 'Bathrooms',
        'TotalSqm', 'IntArea', 'ExtArea', 'Price'
    ]

    @staticmethod
    def fetch_data(is_sale: bool) -> pd.DataFrame:
        data = pd.DataFrame()
        proxies = Fetch.load_proxies()

        page_type = 'buy' if is_sale else 'rent'
        page_element = '//div[@class="property-grid"]'
        driver = Fetch.get_dynamic(f'https://saragrech.com/property/?pg=1&buy-or-rent={page_type}', proxies, page_element)

        x_pages = '//div/div[2]/div[last()]/a[last()]/span'
        pages = int(DynamicScrape.get_text(driver, x_pages))

        for page in tqdm(range(1, pages+1)):
            x_cards = '//div[@class="pod-property "]'
            cards = DynamicScrape.get_elements(driver, x_cards)

            listing = []

            x_reference = './/div[2]/h5[1]'
            x_town = './/h4/span[1]'
            x_type = './/h4/span[3]'
            x_overview_1 = './/div[@class="flex flex-column mt-2 items-center"]/div[1]/span[2]'
            x_overview_2 = './/div[@class="flex flex-column mt-2 items-center"]/div[3]/span[2]'
            x_overview_3 = './/div[@class="flex flex-column mt-2 items-center"]/div[5]/span[2]'
            x_price = './/div[3]/h5'

            for card in cards:
                reference = DynamicScrape.get_text(card, x_reference).replace('ID. ', '')
                town = DynamicScrape.get_text(card, x_town)
                type = DynamicScrape.get_text(card, x_type)

                bedrooms = None
                bathrooms = None

                total_sqm = None
                int_area = None
                ext_area = None

                overview_1 = DynamicScrape.get_text(card, x_overview_1)
                overview_2 = DynamicScrape.get_text(card, x_overview_2)
                overview_3 = DynamicScrape.get_text(card, x_overview_3)

                if overview_3:
                    bedrooms = overview_1
                    bathrooms = overview_2
                    total_sqm = overview_3
                elif overview_2:
                    bedrooms = overview_1

                    if 'm2' not in overview_2:
                        bathrooms = overview_2
                    else:
                        total_sqm = overview_2
                else:
                    if 'm2' not in overview_1:
                        bedrooms = overview_1
                    else:
                        total_sqm = overview_1

                total_sqm = total_sqm.replace(',', '').replace('m2', '') if total_sqm else None

                price = DynamicScrape.get_text(card, x_price)
                price = price.replace('€', '').replace(',', '').replace('/mo', '')

                listing.append([
                    reference, town, type,
                    bedrooms, bathrooms,
                    total_sqm, int_area, ext_area, price
                ])

            # Concatenate previous data frame with data of current page
            page_data = pd.DataFrame(listing, columns=SaraGrech.columns)
            data = pd.concat([data, page_data])

            # Click Next Page
            x_next_page = f'//div/div[2]/div[last()]/a/span[text()="{page+1}"]'
            x_await_page = f'//div/div[2]/div[last()]/div/span[text()="{page+1}"]'
            DynamicScrape.click_element(driver, x_next_page, x_await_page)

        # Add source and rename columns
        data.insert(0, 'Is_Sale', is_sale)
        data.insert(1, 'Source', SaraGrech.source)

        # Return the data
        return data

    @staticmethod
    def fetch_res_sale():
        return SaraGrech.fetch_data(True)

    @staticmethod
    def fetch_res_rent():
        return SaraGrech.fetch_data(False)

    @staticmethod
    def fetch_all():
        # Create progress bar
        pbar = tqdm(total=2)

        # Fetching data
        res_sale = SaraGrech.fetch_res_sale()
        pbar.update(1)

        res_rent = SaraGrech.fetch_res_rent()
        pbar.update(1)

        # Close progress bar
        pbar.close()

        # Concatenate Data
        data = pd.concat([res_sale, res_rent])

        # Return Desired Data
        return data
