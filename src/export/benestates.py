import datetime
import pandas as pd

from helper.fetch import Fetch
from helper.dynamic_scrape import DynamicScrape


class BenEstates(object):
    source = 'Ben Estate'

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

        page_type = 'Buy' if is_sale else 'Rent'
        page_element = '//div[@class="pgl-property"][last()]'
        driver = Fetch.get_dynamic(f'https://www.benestates.com/{"for-sale" if is_sale else "to-let"}', proxies, page_element, True)

        x_cookies = '//*[@id="cc_dialog"]/div/div[2]/button[1]'
        DynamicScrape.get_element(driver, x_cookies).click()

        x_flt_res_com = '//aside[1]//div[@class="row"]//button[contains(@class, "dropdown-toggle")]'
        x_flt_com_value = '//aside[1]//div[@class="row"]//ul/li[5]'
        x_flt_search = '//aside[1]//button[@type="submit"]'
        x_modal = '//div[@class="modal-dialog"]'
        DynamicScrape.get_element(driver, x_flt_res_com).click()
        DynamicScrape.get_element(driver, x_flt_com_value).click()
        DynamicScrape.click_element(driver, x_flt_search, x_modal)

        x_modal_close = '//div[@class="modal-dialog"]//div[@class="modal-footer"]/button[1]'
        DynamicScrape.click_element(driver, x_modal_close)

        x_sort = '//*[@id="sort_options_chosen"]'
        x_sort_latest = '//*[@id="sort_options_chosen"]//li[6]'
        DynamicScrape.await_element(driver, x_sort)
        DynamicScrape.get_element(driver, x_sort).click()
        DynamicScrape.await_element(driver, x_sort_latest)
        DynamicScrape.click_element(driver, x_sort_latest, page_element)

        while True:
            x_links = '//div[@class="col-xs-4 animation"]/a'
            links = DynamicScrape.get_links(driver, x_links)

            listing = []

            x_features = './/ul[@class="list-unstyled amenities amenities-detail"]/li'
            x_type_town = './/div[@class="pgl-detail"]//h1'
            x_price = './/ul[@class="slides"]/li[1]//span[@class="label price"]'

            for i, link in enumerate(links):
                page_element = '//div[@class="pgl-detail"]'
                successful = DynamicScrape.open_tab_link(driver, link, page_element)

                if successful:
                    features = DynamicScrape.get_texts(driver, x_features)
                    features = [feature for feature in features if 'Form: ' not in feature]

                    reference = [feature for feature in features if 'Reference: ' in feature]
                    reference = reference[0].replace('Reference: ', '') if len(reference) else None

                    type_town = DynamicScrape.get_text(driver, x_type_town)
                    town = type_town.split(' IN ')[1].strip().title()
                    type = type_town.split(' IN ')[0].strip().title()

                    stage = [feature for feature in features if 'Form: ' in feature]
                    stage = stage[0].replace('Form: ', '') if len(stage) else 'Unclassified'

                    bedrooms = [feature for feature in features if ' Bedrooms' in feature]
                    bedrooms = bedrooms[0].replace(': ', '').replace(' Bedrooms', '') if len(bedrooms) else None

                    bathrooms = [feature for feature in features if ' Bathrooms' in feature]
                    bathrooms = bathrooms[0].replace(': ', '').replace(' Bathrooms', '') if len(bathrooms) else None

                    total_sqm = [feature for feature in features if 'Plot Area: ' in feature]
                    total_sqm = total_sqm[0].replace('Plot Area: ', '').replace('m2', '') if len(total_sqm) else None

                    int_area = [feature for feature in features if 'Inside Area: ' in feature]
                    int_area = int_area[0].replace('Inside Area: ', '').replace('m2', '') if len(int_area) else None

                    ext_area = [feature for feature in features if 'Outside Area: ' in feature]
                    ext_area = ext_area[0].replace('Outside Area: ', '').replace('m2', '') if len(ext_area) else None

                    price = DynamicScrape.get_text(driver, x_price).replace('€', '').replace(',', '').strip()

                    try:
                        if ' p/day' in price:
                            price = int(price.replace(' p/day', '')) * 30
                        if ' p/week' in price:
                            price = int(price.replace(' p/week', '')) * 4
                        elif ' p/month' in price:
                            price = int(price.replace(' p/month', ''))
                        elif ' p/year' in price:
                            price = round(int(price.replace(' p/year', '')) / 12)
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
                    (datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), BenEstates.source + ' ' + page_type.title(), page, i+1, len(links))
                )

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

        # Close Driver
        Fetch.dynamic_close_browser(driver)

        # Return the data
        return data

    @staticmethod
    def fetch_res_sale():
        return BenEstates.fetch_data(True)

    @staticmethod
    def fetch_res_rent():
        return BenEstates.fetch_data(False)

    @staticmethod
    def fetch_all(file_path: str) -> None:
        # Fetching data
        res_sale = BenEstates.fetch_res_sale()
        res_rent = BenEstates.fetch_res_rent()

        # Concatenate Data
        data = pd.concat([res_sale, res_rent])

        # Save data frame to CSV file
        data.to_csv(file_path, index=False)
