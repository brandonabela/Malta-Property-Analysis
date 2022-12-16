import pandas as pd

from tqdm import tqdm

from helper.fetch import Fetch
from helper.dynamic_scrape import DynamicScrape


class BenEstates(object):
    source = 'Ben Estate'

    columns = [
        'Reference', 'Town', 'Type',
        'Latitude', 'Longitude',
        'Rooms', 'Bedrooms', 'Bathrooms',
        'TotalSqm', 'IntArea', 'ExtArea', 'Price'
    ]

    @staticmethod
    def fetch_data(is_sale: bool) -> pd.DataFrame:
        page = 1
        data = pd.DataFrame()
        proxies = Fetch.load_proxies()

        page_type = 'for-sale' if is_sale else 'to-let'
        page_element = '//div[@class="pgl-property"][last()]'
        driver = Fetch.get_dynamic(f'https://www.benestates.com/{page_type}', proxies, page_element)

        while True:
            x_cards = '//div[@class="pgl-property"]'
            cards = DynamicScrape.get_elements(driver, x_cards)

            listing = []

            x_reference = './/div[@class="property-thumb-info-content"]/address'
            x_type_town = './/div[@class="property-thumb-info-content"]/h3'
            x_bedrooms = './/div[@class="amenities clearfix"]//ul[@class="pull-right"]/li[1]'
            x_bathrooms = './/div[@class="amenities clearfix"]//ul[@class="pull-right"]/li[2]'
            x_total_sqm = './/div[@class="amenities clearfix"]//ul[@class="pull-left"]'
            x_price = './/span[@class="label price"]'

            for card in cards:
                reference = DynamicScrape.get_text(card, x_reference).replace('#', '')
                town = None
                type = None

                type_town = DynamicScrape.get_text(card, x_type_town).split(' in ')

                if len(type_town) == 2:
                    town = type_town[1]
                    type = type_town[0]

                latitude = None
                longitude = None

                rooms = None
                bedrooms = DynamicScrape.get_text(card, x_bedrooms)
                bathrooms = DynamicScrape.get_text(card, x_bathrooms)

                total_sqm = DynamicScrape.get_text(card, x_total_sqm).replace('Area:', '').replace('m2', '')
                int_area = None
                ext_area = None

                price = DynamicScrape.get_text(card, x_price).replace('€', '').replace(',', '')
                price = price.replace(' p/day', '').replace(' p/month', '').replace(' p/year', '')

                listing.append([
                    reference, town, type,
                    latitude, longitude,
                    rooms, bedrooms, bathrooms,
                    total_sqm, int_area, ext_area, price
                ])

            # Print Current Page
            print(f'{BenEstates.source} {"Buy" if is_sale else "Rent"} - {page:03d}')

            # Concatenate previous data frame with data of current page
            page_data = pd.DataFrame(listing, columns=BenEstates.columns)
            data = pd.concat([data, page_data])

            # Break loop if last page
            x_last_page = '//ul[@id="srch-pagination"]/li[@class="last"]'
            is_last_page = DynamicScrape.get_element(driver, x_last_page) is None

            if is_last_page:
                break
            else:
                x_next_page = f'//ul[@id="srch-pagination"]/li[@class="page"]/a[text()="{page+1}"]'
                x_await_page = f'//ul[@id="srch-pagination"]/li[@class="page active"]/a[text()="{page+1}"]'
                DynamicScrape.click_element(driver, x_next_page, x_await_page)
                page += 1

        # Add source and rename columns
        data.insert(0, 'Is_Sale', is_sale)
        data.insert(1, 'Source', BenEstates.source)

        # Return the data
        return data

    @staticmethod
    def fetch_res_sale():
        return BenEstates.fetch_data(True)

    @staticmethod
    def fetch_res_rent():
        return BenEstates.fetch_data(False)

    @staticmethod
    def fetch_all():
        # Create progress bar
        pbar = tqdm(total=2)

        # Fetching data
        res_sale = BenEstates.fetch_res_sale()
        pbar.update(1)

        res_rent = BenEstates.fetch_res_rent()
        pbar.update(1)

        # Close progress bar
        pbar.close()

        # Concatenate Data
        data = pd.concat([res_sale, res_rent])

        # Return Desired Data
        return data
