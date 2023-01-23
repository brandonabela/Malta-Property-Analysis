import datetime
import pandas as pd

from helper.fetch import Fetch
from helper.dynamic_scrape import DynamicScrape
from helper.property_helper import PropertyHelper


class Belair(object):
    source = 'Belair'

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
        page_element = '//div[@class="grid grid-pad"]'
        driver = Fetch.get_dynamic(f'https://www.belair.com.mt/search-results/?f1=to-{page_type}&pr=1', proxies, page_element, True)

        x_pages = '//ul[@class="pagination"]//li[@class="end"]/a'
        pages = int(DynamicScrape.get_text(driver, x_pages))

        for page in range(1, pages+1):
            x_links = '//div[contains(@class, "property-grid")]//h3/a'
            links = DynamicScrape.get_links(driver, x_links)

            listing = []

            x_features = './/div[@class="col-lg-8 propertyname"]//div[@class="whitetext"]/strong'
            x_reference = './/div[@id="propertyref"]'
            x_type = './/div[@class="col-lg-8 propertyname"]/h1'
            x_description = './/div[@id="property-description"]'
            x_price = './/div[@id="propertyprice"]'

            for i, link in enumerate(links):
                page_element = '//section[@class="content-area col-sm-12 col-lg-8"]'
                successful = DynamicScrape.open_tab_link(driver, link, page_element)

                if successful:
                    features = DynamicScrape.get_texts(driver, x_features)

                    reference = DynamicScrape.get_text(driver, x_reference).replace('Reference No. ', '')
                    town = features[0].title()
                    type = DynamicScrape.get_text(driver, x_type).replace(' For Sale', '').replace(' For Rent', '')
                    stage = PropertyHelper.determine_stage(driver, x_description, is_sale)

                    bedrooms = [features[i-1] for i, feature in enumerate(features) if 'Bedrooms' in feature]
                    bedrooms = bedrooms[0] if len(bedrooms) else None

                    bathrooms = [features[i-1] for i, feature in enumerate(features) if 'Bathrooms' in feature]
                    bathrooms = bathrooms[0] if len(bathrooms) else None

                    total_sqm = [features[i-1] for i, feature in enumerate(features) if 'M2' in feature]
                    total_sqm = total_sqm[0] if len(total_sqm) else None

                    int_area = None
                    ext_area = None

                    price = DynamicScrape.get_text(driver, x_price)
                    price = price.replace('€ ', '').replace(',', '').replace(' monthly', '')

                    listing.append([
                        reference, town, type, stage,
                        bedrooms, bathrooms,
                        total_sqm, int_area, ext_area, price
                    ])

                DynamicScrape.close_tab_link(driver)

                print(
                    '%s\t %s\t Page %03d of %03d\t Entry %03d of %03d' %
                    (datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), Belair.source + ' ' + page_type.title(), page, pages, i+1, len(links))
                )

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

        # Close Driver
        Fetch.dynamic_close_browser(driver)

        # Return the data
        return data

    @staticmethod
    def fetch_res_sale():
        return Belair.fetch_data(True)

    @staticmethod
    def fetch_res_rent():
        return Belair.fetch_data(False)

    @staticmethod
    def fetch_all(file_path: str) -> None:
        # Fetching data
        res_sale = Belair.fetch_res_sale()
        res_rent = Belair.fetch_res_rent()

        # Concatenate Data
        data = pd.concat([res_sale, res_rent])

        # Save data frame to CSV file
        data.to_csv(file_path, index=False)
