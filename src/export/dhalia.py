import pandas as pd

from tqdm import tqdm
from selenium.webdriver.common.by import By

from helper.scrape import Scrape


class Dhalia(object):
    url_buy = 'https://www.dhalia.com/buy/?pageIndex='
    url_rent = 'https://www.dhalia.com/rent/?pageIndex='

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

        url = Dhalia.url_buy if is_sale else Dhalia.url_rent
        proxies = Scrape.load_proxies()

        page_type = 'buy' if is_sale else 'rent'
        page_element = f'//div[@class="searchForm searchForm--quick-search page-{page_type}"]'

        while True:
            driver = Scrape.get_dynamic(f'{url}{page}', proxies, page_element)

            x_cards = '//div[@class="ItemContent"]'
            cards = driver.find_elements(By.XPATH, x_cards)

            listing = []

            x_reference = './/span[@class="propertybox__ref-link"]'
            x_town = './/div[@class="propertybox__left-col"]/h2'
            x_type = './/div[@class="propertybox__left-col"]/h3'
            x_bedrooms = './/div[@class="propertybox__footer"]'
            x_price = './/span[@class="propertybox__price"]'

            for card in cards:
                reference = card.find_element(By.XPATH, x_reference).text
                town = card.find_element(By.XPATH, x_town).text
                type = card.find_element(By.XPATH, x_type).text
                latitude = None
                longitude = None

                rooms = None

                bedrooms = card.find_element(By.XPATH, x_bedrooms).text.replace('Sole Agency', '')
                bedrooms = bedrooms.split(' ')[1].replace('\n', '') if bedrooms else None

                bathrooms = None

                total_sqm = None
                int_area = None
                ext_area = None

                price = card.find_element(By.XPATH, x_price).text
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
            page += 1

            # Break loop if last page
            x_last_pager = '//li[@class="pager__last"]'
            is_last_pager = Scrape.await_element(driver, x_last_pager, 3)

            if not is_last_pager:
                break

        # Add source and rename columns
        data.insert(0, 'Is_Sale', is_sale)
        data.insert(1, 'Source', 'Dhalia')

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
