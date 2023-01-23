import datetime
import pandas as pd

from helper.fetch import Fetch
from helper.dynamic_scrape import DynamicScrape
from helper.property_helper import PropertyHelper


class Remax(object):
    source = 'Remax'

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
        page_element = '//section[@class="section--pagination"]'
        driver = Fetch.get_dynamic(f'https://remax-malta.com/listings?Residential=True&Commercial=False&ForSale={is_sale}&ForRent={not is_sale}&page=1', proxies, page_element, True)

        x_pages = '//section[@class="section--pagination"]/div[last()-1]//p'
        pages = int(DynamicScrape.get_text(driver, x_pages))

        for page in range(1, pages+1):
            x_links = '//div[@class="property-card--information"]/div/a'
            links = DynamicScrape.get_links(driver, x_links)

            listing = []

            x_reference = './/div[@class="main-description--location"]/span[@class="leading-none"]'
            x_town = './/div[@class="main-description--location"]/span[1]'
            x_description = './/div[@class="main-description--description"]'

            x_overview_1 = './/div[@class="overview-stats"]/div[1]/div[2]'
            x_overview_2 = './/div[@class="overview-stats"]/div[2]/div[2]'
            x_overview_3 = './/div[@class="overview-stats"]/div[3]/div[2]'

            x_int_area = './/div[@id="property-overview"]/div[2]/div[1]'
            x_ext_area = './/div[@id="property-overview"]/div[2]/div[2]'
            x_price = './/div[@class="price-with-exchange--price"]'

            for i, link in enumerate(links):
                page_element = '//div[@class="property-detailed--main-description"]'
                successful = DynamicScrape.open_tab_link(driver, link, page_element)

                if successful:
                    reference = DynamicScrape.get_text(driver, x_reference).replace('REF-ID: ', '')
                    town = DynamicScrape.get_text(driver, x_town).split(',')[0].strip()
                    type = driver.title.split('-')[0].strip()

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

                        if 'sqm' not in overview_2:
                            bathrooms = overview_2
                        else:
                            total_sqm = overview_2
                    else:
                        if 'sqm' not in overview_1:
                            bedrooms = overview_1
                        else:
                            total_sqm = overview_1

                    bedrooms = bedrooms.replace(' Beds', '') if bedrooms else None
                    bathrooms = bathrooms.replace(' Baths', '') if bathrooms else None
                    total_sqm = total_sqm.replace(' sqm', '') if total_sqm else None

                    int_area = DynamicScrape.get_text(driver, x_int_area)
                    int_area = int_area.replace('Internal Area: ', '').replace(' sqm', '') if 'Internal Area: ' in int_area else None

                    ext_area = DynamicScrape.get_text(driver, x_ext_area)
                    ext_area = ext_area.replace('External Area: ', '').replace(' sqm', '') if 'External Area: ' in ext_area else None

                    price = DynamicScrape.get_text(driver, x_price).replace(',', '')

                    try:
                        if ' Daily' in price:
                            price = int(price.replace(' Daily', '')) * 30
                        if ' Weekly' in price:
                            price = int(price.replace(' Weekly', '')) * 4
                        elif ' Monthly' in price:
                            price = int(price.replace(' Monthly', ''))
                        elif ' Yearly' in price:
                            price = round(int(price.replace(' Yearly', '')) / 12)
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
                    (datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), Remax.source + ' ' + page_type.title(), page, pages, i+1, len(links))
                )

            # Concatenate previous data frame with data of current page
            page_data = pd.DataFrame(listing, columns=Remax.columns)
            data = pd.concat([data, page_data])

            # Click Next Page
            x_next_page = f'//div[@class="pagination--button"]/p[text()="{page+1}"]'
            x_await_page = f'//div[@class="pagination--button pagination--selected"]/p[text()="{page+1}"]'
            DynamicScrape.click_element(driver, x_next_page, x_await_page)

            x_loader = '//div["loader-section"]'
            DynamicScrape.await_no_element(driver, x_loader)

        # Add source and rename columns
        data.insert(0, 'Is_Sale', is_sale)
        data.insert(1, 'Source', Remax.source)

        # Close Driver
        Fetch.dynamic_close_browser(driver)

        # Return the data
        return data

    @staticmethod
    def fetch_res_sale():
        return Remax.fetch_data(True)

    @staticmethod
    def fetch_res_rent():
        return Remax.fetch_data(False)

    @staticmethod
    def fetch_all(file_path: str) -> None:
        # Fetching data
        res_sale = Remax.fetch_res_sale()
        res_rent = Remax.fetch_res_rent()

        # Concatenate Data
        data = pd.concat([res_sale, res_rent])

        # Save data frame to CSV file
        data.to_csv(file_path, index=False)
