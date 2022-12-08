import requests
import pandas as pd

from tqdm import tqdm


class Remax(object):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    }

    @staticmethod
    def fetch_data(is_sale: bool) -> pd.DataFrame:
        page = 1
        data = pd.DataFrame()

        # Loop until an invalid page shows up
        while True:
            # Retrieve data based on dynamically built URL
            url = f'https://remax-malta.com/api/properties?Residential={is_res}&Commercial={not is_res}&ForSale={is_sale}&ForRent={not is_sale}&page={page}&Take=250'
            request = requests.get(url, headers=Remax.header).json()

            # Break loop id data key not found
            if len(request['data']['Properties']) == 0:
                break

            # Create data frame and select specific columns
            page_data = pd.DataFrame(request['data']['Properties'])
            page_data[['Latitude', 'Longitude']] = page_data['Coordinates'].apply(pd.Series)

            page_data = page_data[[
                'MLS', 'Province', 'Town', 'PropertyType',
                'Latitude', 'Longitude',
                'TotalRooms', 'TotalBedrooms', 'TotalBathrooms',
                'TotalSqm', 'TotalIntArea', 'TotalExtArea', 'Price'
            ]]

            # Concatenate previous data frame with data of current page
            data = pd.concat([data, page_data])
            page += 1

            # Update progress bar

        # Add source and rename columns
        data.insert(0, 'Is_Sale', is_sale)
        data.insert(1, 'Source', 'Remax')

        data = data.rename(columns={
            'MLS': 'Reference'
        })

        # Return the data
        return data

    @staticmethod
    def fetch_res_sale():
        return Remax.fetch_data(True)

    @staticmethod
    def fetch_res_rent():
        return Remax.fetch_data(False)

    @staticmethod
    def fetch_all():
        # Create progress bar
        pbar = tqdm(total=2)

        # Fetching data
        res_sale = Remax.fetch_res_sale()
        pbar.update(1)

        res_rent = Remax.fetch_res_rent()
        pbar.update(1)

        # Close progress bar
        pbar.close()

        # Concatenate Data
        data = pd.concat([res_sale, res_rent])

        # Return Desired Data
        return data
