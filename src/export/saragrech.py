import pandas as pd

from tqdm import tqdm

from helper.fetch import Fetch
from helper.dynamic_scrape import DynamicScrape


class SaraGrech(object):
    source = 'Sara Grech'

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

        pages = 1
        x_pages = '//div/div[2]/div[last()]/a[last()]/span'

        proxies = Fetch.load_proxies()

        page_type = 'buy' if is_sale else 'rent'
        page_element = '//div[@class="property-grid"]'

        while True:
            driver = Fetch.get_dynamic(f'https://saragrech.com/property/?pg={page+1}&buy-or-rent={page_type}', proxies, page_element)

            if page == 1:
                pages = int(DynamicScrape.get_text(driver, x_pages))

            x_cards = '//div[@class="pod-property "]'
            cards = DynamicScrape.get_elements(driver, x_cards)

            listing = []

            x_reference = './/div[2]/h5[1]'
            x_town = './/h4/span[1]'
            x_type = './/h4/span[3]'
            x_overviews = './/div[@class="flex flex-column mt-2 items-center"]/div'
            x_bedrooms = f'{x_overviews}[1]/span[2]'
            x_bathrooms = f'{x_overviews}[3]/span[2]'
            x_total_sqm = f'{x_overviews}[5]/span[2]'
            x_price = './/div[3]/h5'

            for card in cards:
                reference = DynamicScrape.get_text(card, x_reference).replace('ID. ', '')
                town = DynamicScrape.get_text(card, x_town)
                type = DynamicScrape.get_text(card, x_type)
                latitude = None
                longitude = None

                rooms = None
                bedrooms = None
                bathrooms = None

                total_sqm = None
                int_area = None
                ext_area = None

                overviews = DynamicScrape.get_elements(card, x_overviews)

                if len(overviews) >= 1:
                    total_sqm = DynamicScrape.get_text(card, x_bedrooms)
                    total_sqm = total_sqm.replace('m2', '') if total_sqm else None

                if len(overviews) >= 3:
                    bedrooms = DynamicScrape.get_text(card, x_bedrooms)
                    bathrooms = DynamicScrape.get_text(card, x_bathrooms)

                if len(overviews) >= 5:
                    total_sqm = DynamicScrape.get_text(card, x_total_sqm)
                    total_sqm = total_sqm.replace('m2', '') if total_sqm else None

                price = DynamicScrape.get_text(card, x_price)
                price = price.replace('€', '').replace(',', '').replace('/mo', '')

                listing.append([
                    reference, town, type,
                    latitude, longitude,
                    rooms, bedrooms, bathrooms,
                    total_sqm, int_area, ext_area, price
                ])

            # Print Current Page
            print(f'Source {SaraGrech.source} Type {page_type} Page {page:03d}')

            # Concatenate previous data frame with data of current page
            page_data = pd.DataFrame(listing, columns=SaraGrech.columns)
            data = pd.concat([data, page_data])
            page += 1

            if page == pages:
                break

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
