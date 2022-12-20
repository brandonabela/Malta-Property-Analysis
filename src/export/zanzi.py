import pandas as pd

from tqdm import tqdm

from helper.fetch import Fetch
from helper.dynamic_scrape import DynamicScrape


class Zanzi(object):
    source = 'Zanzi'

    columns = [
        'Reference', 'Town', 'Type',
        'Bedrooms', 'Bathrooms',
        'TotalSqm', 'IntArea', 'ExtArea', 'Price'
    ]

    @staticmethod
    def fetch_data(is_sale: bool) -> pd.DataFrame:
        page = 1
        data = pd.DataFrame()
        proxies = Fetch.load_proxies()

        page_element = '//div[@class="properties-holder filter-box-holder"]'
        driver = Fetch.get_dynamic('https://www.zanzihomes.com/property-in-malta', proxies, page_element)

        while True:
            x_cards = '//div[@class="properties-item filtration-box"]'
            cards = DynamicScrape.get_elements(driver, x_cards)

            listing = []

            x_reference = './/div[@class="info-prop"]/span'
            x_town = './/a[@class="city"]/span[2]'
            x_type = './/div[@class="bg-hide"]//span[@class="apart-name"]'
            x_bedrooms = './/div[@class="bg-hide"]//ul[@class="flat-info"]/li[1]'
            x_bathrooms = './/div[@class="bg-hide"]//ul[@class="flat-info"]/li[2]'
            x_total_sqm = './/div[@class="bg-hide"]//div[@class="hide-info-prop"]/span'
            x_price = './/div[@class="price"]/span'

            for card in cards:
                reference = DynamicScrape.get_text(card, x_reference).replace('REF No. ', '')
                town = DynamicScrape.get_text(card, x_town)
                type = DynamicScrape.get_hidden_text(card, x_type)

                bedrooms = DynamicScrape.get_hidden_text(card, x_bedrooms).replace(' Bedrooms', '').strip()
                bathrooms = DynamicScrape.get_hidden_text(card, x_bathrooms).replace(' Bathrooms', '').strip()

                total_sqm = DynamicScrape.get_hidden_text(card, x_total_sqm).replace(' sqm', '')
                int_area = None
                ext_area = None

                price = DynamicScrape.get_text(card, x_price).replace('€', '').replace(',', '')

                listing.append([
                    reference, town, type,
                    bedrooms, bathrooms,
                    total_sqm, int_area, ext_area, price
                ])

            # Print Current Page
            print(f'{Zanzi.source} {"Buy" if is_sale else "Rent"} - {page:03d}')

            # Concatenate previous data frame with data of current page
            page_data = pd.DataFrame(listing, columns=Zanzi.columns)
            data = pd.concat([data, page_data])

            # Break loop if last page
            x_last_page = '//div[@class="paginations"]/a[@class="next pagination_ajax"]'
            is_last_page = DynamicScrape.get_element(driver, x_last_page) is None

            if is_last_page:
                break
            else:
                x_next_page = f'//div[@class="paginations"]/a[normalize-space()="{page+1}"]'
                x_await_page = f'//div[@class="paginations"]/span[normalize-space()="{page+1}"]'
                DynamicScrape.click_element(driver, x_next_page, x_await_page)
                page += 1

        # Add source and rename columns
        data.insert(0, 'Is_Sale', is_sale)
        data.insert(1, 'Source', Zanzi.source)

        # Return the data
        return data

    @staticmethod
    def fetch_res_sale():
        return Zanzi.fetch_data(True)

    @staticmethod
    def fetch_all():
        # Create progress bar
        pbar = tqdm(total=1)

        # Fetching data
        res_sale = Zanzi.fetch_res_sale()
        pbar.update(1)

        # Close progress bar
        pbar.close()

        # Concatenate Data
        data = pd.concat([res_sale])

        # Return Desired Data
        return data
