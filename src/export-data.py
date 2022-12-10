import numpy as np
import pandas as pd

from tqdm import tqdm

from export.remax import Remax
from export.dhalia import Dhalia
from helper.mappings import Mappings


if __name__ == "__main__":
    remax_path = "data/remax.csv"
    dhalia_path = "data/dhalia.csv"

    # ===================================
    # Create Progress Bar
    # ===================================

    pbar = tqdm(total=3)

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
    # Process a common Dataset
    # ===================================

    remax = pd.read_csv(remax_path)
    dhalia = pd.read_csv(dhalia_path)

    dataset = pd.concat([remax, dhalia])
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
        dataset['Bedrooms'].notnull() &
        pd.to_numeric(dataset['Price'], errors='coerce').notnull()
    ]

    # Saving Dataset
    dataset.to_csv("data/dataset.csv", index=False)
    pbar.update(1)

    # ===================================
    # Close Progress Bar
    # ===================================

    pbar.close()
