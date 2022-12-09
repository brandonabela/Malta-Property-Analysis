import unicodedata
import pandas as pd

from tqdm import tqdm

from helper.scrape import Scrape


class Dhalia(object):
    url_buy = 'https://www.dhalia.com/buy/?pageIndex='
    url_rent = 'https://www.dhalia.com/rent/?pageIndex='

    columns = [
        'Reference', 'Town', 'PropertyType',
        'Latitude', 'Longitude',
        'TotalRooms', 'TotalBedrooms', 'TotalBathrooms',
        'TotalSqm', 'TotalIntArea', 'TotalExtArea', 'Price'
    ]

    @staticmethod
    def fetch_data(is_sale: bool) -> pd.DataFrame:
        page = 1
        data = pd.DataFrame()

        url = Dhalia.url_buy if is_sale else Dhalia.url_rent
        proxies = Scrape.load_proxies()

        while True:
            soup = Scrape.get_static(f'{url}{page}', proxies)

            grid = soup.find('div', class_='search-results__wrapper__grid')
            cards = grid.find_all('div', class_='ItemContent')

            listing = []

            for card in cards:
                reference = card.find('span', class_='propertybox__ref-link').text
                town = card.find('div', class_='propertybox__left-col').find('h2').text
                property_type = card.find('div', class_='propertybox__left-col').find('h3').text
                latitude = None
                longitude = None

                total_rooms = None

                total_bedrooms = card.find('div', class_='propertybox__footer').text.replace('Sole Agency', '')
                total_bedrooms = total_bedrooms.split(' ')[1] if total_bedrooms else None

                total_bathrooms = None

                total_sqm = None
                total_int_area = None
                total_ext_area = None

                price = card.find('span', class_='propertybox__price').text
                price = price.split(' ')[0].replace(',', '')

                listing.append([
                    reference, town, property_type,
                    latitude, longitude,
                    total_rooms, total_bedrooms, total_bathrooms,
                    total_sqm, total_int_area, total_ext_area, price
                ])

            # Concatenate previous data frame with data of current page
            page_data = pd.DataFrame(listing, columns=Dhalia.columns)
            data = pd.concat([data, page_data])
            page += 1

            # Break loop if last page
            last_pager = soup.find('li', class_='pager__last')

            if last_pager is None:
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
