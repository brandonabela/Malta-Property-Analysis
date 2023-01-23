import datetime
import pandas as pd

from helper.fetch import Fetch
from helper.dynamic_scrape import DynamicScrape
from helper.property_helper import PropertyHelper


class QuickLets(object):
    source = 'QuickLets'

    columns = [
        'Reference', 'Town', 'Type', 'Stage',
        'Bedrooms', 'Bathrooms',
        'TotalSqm', 'IntArea', 'ExtArea', 'Price'
    ]

    @staticmethod
    def fetch_data(is_sale: bool) -> pd.DataFrame:
        page = 1
        data = pd.DataFrame()
        proxies = Fetch.load_proxies()

        page_element = '//div[@class="properties-holder filter-box-holder"]'
        driver = Fetch.get_dynamic('https://www.quicklets.com.mt/long-let-malta', proxies, page_element, True)

        while True:
            x_links = '//div[@class="properties-item filtration-box"]//div[@class="bg-hide"]/a'
            links = DynamicScrape.get_links(driver, x_links)

            listing = []

            x_features = './/div[@class="info-holder"]//div[@class="pro-info"]/dl'
            x_town_type = './/div[@class="slider-head"]/h1'
            x_description = './/div[@class="description"]/div'
            x_price = './/div[@class="info-holder"]//div[@class="price"]'

            for i, link in enumerate(links):
                page_element = '//div[@class="main-info"]'
                successful = DynamicScrape.open_tab_link(driver, link, page_element)

                if successful:
                    features = DynamicScrape.get_texts(driver, x_features)

                    reference = [feature for feature in features if 'Ref No.:\n' in feature]
                    reference = reference[0].replace('Ref No.:\n', '') if len(reference) else None

                    town_type = DynamicScrape.get_text(driver, x_town_type).split(' - ')

                    town = ' '.join(town_type[:-1]).strip()
                    type = town_type[-1].strip()

                    stage = PropertyHelper.determine_stage(driver, x_description, is_sale)

                    bedrooms = [side_info for side_info in features if 'Bedrooms:\n' in side_info]
                    bedrooms = bedrooms[0].replace('Bedrooms:\n', '') if len(bedrooms) else None

                    bathrooms = [side_info for side_info in features if 'Bathrooms:\n' in side_info]
                    bathrooms = bathrooms[0].replace('Bathrooms:\n', '') if len(bathrooms) else None

                    total_sqm = [side_info for side_info in features if 'SQM:\n' in side_info]
                    total_sqm = total_sqm[0].replace('SQM:\n', '') if len(total_sqm) else None

                    int_area = None
                    ext_area = None

                    price = DynamicScrape.get_text(driver, x_price)
                    price = price.replace('€', '').replace(',', '')

                    try:
                        if ' / Daily' in price:
                            price = int(price.replace(' / Daily', '')) * 30
                        if ' / Weekly' in price:
                            price = int(price.replace(' / Weekly', '')) * 4
                        elif ' / Monthly' in price:
                            price = int(price.replace(' / Monthly', ''))
                        elif ' / Yearly' in price:
                            price = round(int(price.replace(' / Yearly', '')) / 12)
                    except ValueError:
                        price = None

                    listing.append([
                        reference, town, type, stage,
                        bedrooms, bathrooms,
                        total_sqm, int_area, ext_area, price
                    ])

                DynamicScrape.close_tab_link(driver)

                print(
                    '%s\t %s\t Page %03d of XXX\t Entry %03d of %03d' %
                    (datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), QuickLets.source + ' Rent', page, i+1, len(links))
                )

            # Concatenate previous data frame with data of current page
            page_data = pd.DataFrame(listing, columns=QuickLets.columns)
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
        data.insert(1, 'Source', QuickLets.source)

        # Close Driver
        Fetch.dynamic_close_browser(driver)

        # Return the data
        return data

    @staticmethod
    def fetch_res_rent():
        return QuickLets.fetch_data(False)

    @staticmethod
    def fetch_all(file_path: str) -> None:
        # Fetching data
        res_rent = QuickLets.fetch_res_rent()

        # Concatenate Data
        data = pd.concat([res_rent])

        # Save data frame to CSV file
        data.to_csv(file_path, index=False)
