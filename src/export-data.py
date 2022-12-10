import numpy as np
import pandas as pd

from tqdm import tqdm

from export.remax import Remax
from export.dhalia import Dhalia
from export.saragrech import SaraGrech
from helper.mappings import Mappings


if __name__ == "__main__":
    remax_path = "data/remax.csv"
    dhalia_path = "data/dhalia.csv"
    saragrech_path = "data/saragrech.csv"

    # ===================================
    # Create Progress Bar
    # ===================================

    pbar = tqdm(total=4)

    # ===================================
    # Fetching Remax Data
    # ===================================

    remax = Remax.fetch_all()
    remax.to_csv(remax_path, index=False)
    pbar.update(1)

    # ===================================
    # Fetching Dhalia Data
    # ===================================

    dhalia = Dhalia.fetch_all()
    dhalia.to_csv(dhalia_path, index=False)
    pbar.update(1)

    # ===================================
    # Fetching Sara Grech Data
    # ===================================

    saragrech = SaraGrech.fetch_all()
    saragrech.to_csv(saragrech_path, index=False)
    pbar.update(1)

    # ===================================
    # Process a common Dataset
    # ===================================

    remax = pd.read_csv(remax_path)
    dhalia = pd.read_csv(dhalia_path)
    saragrech = pd.read_csv(saragrech_path)

    dataset = pd.concat([remax, dhalia, saragrech])
    towns = Mappings.town_mapping()
    regions = Mappings.region_mapping()

    # Standardise Town Names
    dataset['Town'] = dataset['Town'].replace(towns.values.tolist())

    # Determining Regions
    dataset = dataset.merge(regions, on='Town', how='left')

    # Replace 0 as NAN
    dataset[['Rooms', 'Bedrooms', 'Bathrooms']] = dataset[['Rooms', 'Bedrooms', 'Bathrooms']].replace(0, np.nan)

    # Save Unmapped Towns
    unmapped_towns = dataset[dataset['Province'].isnull()]['Town'].value_counts()
    unmapped_towns.to_csv('data/unmapped_towns.csv')

    # Exclude invalid entries
    dataset = dataset[
        pd.to_numeric(dataset['Bedrooms'], errors='coerce').notnull() &
        pd.to_numeric(dataset['Bathrooms'], errors='coerce').notnull() &
        pd.to_numeric(dataset['Price'], errors='coerce').notnull()
    ]

    dataset = dataset.dropna(subset=dataset.columns[:5])

    # Saving Dataset
    dataset.to_csv('data/dataset.csv', index=False)
    pbar.update(1)

    # ===================================
    # Close Progress Bar
    # ===================================

    pbar.close()
