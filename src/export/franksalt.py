import datetime
import pandas as pd

from helper.fetch import Fetch
from helper.dynamic_scrape import DynamicScrape
from helper.property_helper import PropertyHelper


class FrankSalt(object):
    source = 'Frank Salt'

    columns = [
        'Reference', 'Town', 'Type', 'Stage',
        'Bedrooms', 'Bathrooms',
        'TotalSqm', 'IntArea', 'ExtArea', 'Price'
    ]

    @staticmethod
    def fetch_data(is_sale: bool) -> pd.DataFrame:
        data = pd.DataFrame()
        proxies = Fetch.load_proxies()

        page_type = 'Buy' if is_sale else 'Rent'
        page_element = '//div[@class="fra-property-catalog"][last()]/div[@class="property-description"]'
        driver = Fetch.get_dynamic(f'https://franksalt.com.mt/properties?mode={"residential-buy" if is_sale else "residential-rent"}&pg=1', proxies, page_element, True)

        x_pages = '//li[contains(@class, "paginationjs-last")]/a'
        pages = int(DynamicScrape.get_text(driver, x_pages))

        for page in range(1, pages+1):
            x_links = '//div[@class="fra-property-catalog"]/div[@class="fra-button-block"]/a'
            links = DynamicScrape.get_links(driver, x_links)

            listing = []

            x_reference = './/section[3]//div[2]//p'
            x_type_town = './/section[2]//div[2]/div/h2'
            x_description = './/section[7]/div/div/div[1]/div/div/div[3]/div/div'
            x_bedrooms = './/div[@class="sub-tags"]/ul/li[@class="bedrooms"]'
            x_bathrooms = './/div[@class="sub-tags"]/ul/li[@class="bathrooms"]'
            x_total_sqm = './/div[@class="sub-tags"]/ul/li[@class="total_area"]'
            x_price = './/section[3]//div[1]/div/p/span[2]'

            for i, link in enumerate(links):
                page_element = '//div[@class="property-features-container"]'
                successful = DynamicScrape.open_tab_link(driver, link, page_element)

                if successful:
                    reference = DynamicScrape.get_text(driver, x_reference).replace('REF: ', '')

                    type_town = DynamicScrape.get_text(driver, x_type_town).split(' in ')
                    town = None
                    type = None

                    if len(type_town) == 2:
                        town = type_town[1]
                        type = type_town[0]

                    stage = PropertyHelper.determine_stage(driver, x_description, is_sale)

                    bedrooms = DynamicScrape.get_text(driver, x_bedrooms).replace(' Bedrooms', '').replace(' Bedroom', '')
                    bathrooms = DynamicScrape.get_text(driver, x_bathrooms).replace(' Bathrooms', '').replace(' Bathroom', '')

                    total_sqm = DynamicScrape.get_text(driver, x_total_sqm).replace('sq mt', '').strip()
                    int_area = None
                    ext_area = None

                    price = DynamicScrape.get_text(driver, x_price).replace(',', '').replace('/month', '')

                    listing.append([
                        reference, town, type, stage,
                        bedrooms, bathrooms,
                        total_sqm, int_area, ext_area, price
                    ])

                DynamicScrape.close_tab_link(driver)

                print(
                    '%s\t %s\t Page %03d of %03d\t Entry %03d of %03d' %
                    (datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), FrankSalt.source + ' ' + page_type.title(), page, pages, i+1, len(links))
                )

            # Concatenate previous data frame with data of current page
            page_data = pd.DataFrame(listing, columns=FrankSalt.columns)
            data = pd.concat([data, page_data])

            # Click Next Page
            x_next_page = f'//li[contains(@class, "paginationjs-page")]/a[text()="{page+1}"]'
            x_await_page = f'//li[contains(@class, "paginationjs-page active")]/a[text()="{page+1}"]'
            DynamicScrape.click_element(driver, x_next_page, x_await_page)

            x_loader = '//div[@class="loader-container"]'
            DynamicScrape.await_no_element(driver, x_loader)

        # Add source and rename columns
        data.insert(0, 'Is_Sale', is_sale)
        data.insert(1, 'Source', FrankSalt.source)

        # Close Driver
        Fetch.dynamic_close_browser(driver)

        # Return the data
        return data

    @staticmethod
    def fetch_res_sale():
        return FrankSalt.fetch_data(True)

    @staticmethod
    def fetch_res_rent():
        return FrankSalt.fetch_data(False)

    @staticmethod
    def fetch_all(file_path: str) -> None:
        # Fetching data
        res_sale = FrankSalt.fetch_res_sale()
        res_rent = FrankSalt.fetch_res_rent()

        # Concatenate Data
        data = pd.concat([res_sale, res_rent])

        # Save data frame to CSV file
        data.to_csv(file_path, index=False)
