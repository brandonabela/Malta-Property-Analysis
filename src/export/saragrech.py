import datetime
import pandas as pd

from helper.fetch import Fetch
from helper.dynamic_scrape import DynamicScrape
from helper.property_helper import PropertyHelper


class SaraGrech(object):
    source = 'Sara Grech'

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
        page_element = '//div[@class="property-grid"]'
        driver = Fetch.get_dynamic(f'https://saragrech.com/property/?pg=1&buy-or-rent={page_type}', proxies, page_element, True)

        x_pages = '//div/div[2]/div[last()]/a[last()]/span'
        pages = int(DynamicScrape.get_text(driver, x_pages))

        for page in range(1, pages+1):
            x_links = '//div[@class="pod-property "]//a[@class="block"]'
            links = DynamicScrape.get_links(driver, x_links)

            listing = []

            x_town = './/div[@class="lg:sticky top-29 mt-20 lg:mt-0"]//div[@class="font-body text-black text-16 leading-normal font-regular"][1]'
            x_type = './/div[@class="lg:sticky top-29 mt-20 lg:mt-0"]//div[@class="mb-4"]/div/a/span'
            x_description = './/div[@class="mt-6 lg:mt-10"][2]/div'

            x_overview_1 = './/div[@class="lg:sticky top-29 mt-20 lg:mt-0"]//div[@class="text-12 leading-none"][1]'
            x_overview_2 = './/div[@class="lg:sticky top-29 mt-20 lg:mt-0"]//div[@class="text-12 leading-none"][2]'
            x_overview_3 = './/div[@class="lg:sticky top-29 mt-20 lg:mt-0"]//div[@class="text-12 leading-none"][3]'

            x_int_area = './/div[@class="inline-block mr-6 lg:mr-10"][2]/h6'
            x_ext_area = './/div[@class="inline-block mr-6 lg:mr-10"][3]/h6'
            x_price = './/div[@class="col-span-12 lg:col-span-5 content-wrapper px-2 lg:px-3"]//h2'

            for i, link in enumerate(links):
                page_element = '//div[@class="container mx-auto px-4 lg:px-3 relative mt-8 lg:mt-6"]'
                successful = DynamicScrape.open_tab_link(driver, link, page_element)

                if successful:
                    reference = driver.title.split('|')[0].strip()

                    town = DynamicScrape.get_text(driver, x_town)
                    type = DynamicScrape.get_text(driver, x_type)

                    stage = PropertyHelper.determine_stage(driver, x_description, is_sale)

                    bedrooms = None
                    bathrooms = None
                    total_sqm = None

                    overview_1 = DynamicScrape.get_text(driver, x_overview_1)
                    overview_2 = DynamicScrape.get_text(driver, x_overview_2)
                    overview_3 = DynamicScrape.get_text(driver, x_overview_3)

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

                    int_area = DynamicScrape.get_text(driver, x_int_area).replace('m2', '').replace(',', '')
                    ext_area = DynamicScrape.get_text(driver, x_ext_area).replace('m2', '').replace(',', '')

                    price = DynamicScrape.get_text(driver, x_price)
                    price = price.replace('€', '').replace(',', '').replace('/mo', '')

                    listing.append([
                        reference, town, type, stage,
                        bedrooms, bathrooms,
                        total_sqm, int_area, ext_area, price
                    ])

                DynamicScrape.close_tab_link(driver)

                print(
                    '%s\t %s\t Page %03d of %03d\t Entry %03d of %03d' %
                    (datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), SaraGrech.source + ' ' + page_type.title(), page, pages, i+1, len(links))
                )

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

        # Close Driver
        Fetch.dynamic_close_browser(driver)

        # Return the data
        return data

    @staticmethod
    def fetch_res_sale():
        return SaraGrech.fetch_data(True)

    @staticmethod
    def fetch_res_rent():
        return SaraGrech.fetch_data(False)

    @staticmethod
    def fetch_all(file_path: str) -> None:
        # Fetching data
        res_sale = SaraGrech.fetch_res_sale()
        res_rent = SaraGrech.fetch_res_rent()

        # Concatenate Data
        data = pd.concat([res_sale, res_rent])

        # Save data frame to CSV file
        data.to_csv(file_path, index=False)
