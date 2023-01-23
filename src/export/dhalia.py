import datetime
import pandas as pd

from helper.fetch import Fetch
from helper.dynamic_scrape import DynamicScrape
from helper.property_helper import PropertyHelper


class Dhalia(object):
    source = 'Dhalia'

    columns = [
        'Reference', 'Town', 'Type', 'Stage',
        'Bedrooms', 'Bathrooms',
        'TotalSqm', 'IntArea', 'ExtArea', 'Price'
    ]

    @staticmethod
    def fetch_data(is_sale: bool) -> pd.DataFrame:
        data = pd.DataFrame()
        proxies = Fetch.load_proxies()

        page_type = 'buy' if is_sale else 'rent'
        page_element = f'//div[@class="searchForm searchForm--quick-search page-{page_type}"]'
        driver = Fetch.get_dynamic(f'https://www.dhalia.com/{page_type}/?pageIndex=1', proxies, page_element, True)

        x_pages = '//li[@class="pager__last"]/a'
        DynamicScrape.await_element(driver, x_pages)
        pages = int(DynamicScrape.get_link(driver, x_pages).split('=')[1])

        for page in range(1, pages+1):
            x_links = '//a[@class="propertybox"]'
            links = DynamicScrape.get_links(driver, x_links)

            listing = []

            x_features = './/div[@class="property-top__col__part property-top__col__part--others"]/span'
            x_type_town = './/div[@class="property-top__col"]/h1'
            x_description = './/div[@class="description write-up"]'
            x_price = './/div[@class="property-top__col__part property-top__col__part--price"]'

            for i, link in enumerate(links):
                page_element = '//section[@class="property-detail-wrapper"]'
                successful = DynamicScrape.open_tab_link(driver, link, page_element)

                if successful:
                    features = DynamicScrape.get_texts(driver, x_features)

                    reference = [feature for feature in features if 'Ref: ' in feature]
                    reference = reference[0].replace('Ref: ', '').strip() if len(reference) else None

                    type_town = DynamicScrape.get_text(driver, x_type_town)

                    town = type_town.split(' in ')[1].strip()
                    type = type_town.split(' in ')[0].strip()

                    stage = PropertyHelper.determine_stage(driver, x_description, is_sale)

                    bedrooms = [side_info for side_info in features if 'Bedrooms' in side_info]
                    bedrooms = bedrooms[0].replace('Bedrooms', '') if len(bedrooms) else None

                    bathrooms = [side_info for side_info in features if 'Bathrooms' in side_info]
                    bathrooms = bathrooms[0].replace('Bathrooms', '') if len(bathrooms) else None

                    area = [side_info for side_info in features if 'm²' in side_info]
                    area = area[0].replace('m²', '').split('/') if len(area) else None

                    total_sqm = area[0] if area else None
                    int_area = area[1] if area else None
                    ext_area = area[2] if area else None

                    price = DynamicScrape.get_text(driver, x_price)
                    price = price.replace('€', '').replace(',', '')

                    try:
                        if ' daily' in price:
                            price = int(price.replace(' daily', '')) * 30
                        elif ' monthly' in price:
                            price = int(price.replace(' monthly', ''))
                        elif ' yearly' in price:
                            price = round(int(price.replace(' yearly', '')) / 12)
                    except ValueError:
                        price = None

                    listing.append([
                        reference, town, type, stage,
                        bedrooms, bathrooms,
                        total_sqm, int_area, ext_area, price
                    ])

                DynamicScrape.close_tab_link(driver)

                print(
                    '%s\t %s\t Page %03d of %03d\t Entry %03d of %03d' %
                    (datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), Dhalia.source + ' ' + page_type.title(), page, pages, i+1, len(links))
                )

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

        # Close Driver
        Fetch.dynamic_close_browser(driver)

        # Return the data
        return data

    @staticmethod
    def fetch_res_sale():
        return Dhalia.fetch_data(True)

    @staticmethod
    def fetch_res_rent():
        return Dhalia.fetch_data(False)

    @staticmethod
    def fetch_all(file_path: str) -> None:
        # Fetching data
        res_sale = Dhalia.fetch_res_sale()
        res_rent = Dhalia.fetch_res_rent()

        # Concatenate Data
        data = pd.concat([res_sale, res_rent])

        # Save data frame to CSV file
        data.to_csv(file_path, index=False)
