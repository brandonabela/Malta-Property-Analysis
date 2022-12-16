import numpy as np
import pandas as pd

from tqdm import tqdm
from scipy.stats import zscore

from export.remax import Remax
from export.dhalia import Dhalia
from export.saragrech import SaraGrech
from export.alliance import Alliance
from export.franksalt import FrankSalt
from export.benestates import BenEstates
from export.belair import Belair
from helper.configuration import Configuration


if __name__ == "__main__":
    remax_path = 'data/remax.csv'
    dhalia_path = 'data/dhalia.csv'
    saragrech_path = 'data/saragrech.csv'
    alliance_path = 'data/alliance.csv'
    franksalt_path = 'data/franksalt.csv'
    benestates_path = 'data/benestates.csv'
    belair_path = 'data/belair.csv'

    # ===================================
    # Create Progress Bar
    # ===================================

    pbar = tqdm(total=8)

    # # ===================================
    # # Fetch Remax Data
    # # ===================================

    # remax = Remax.fetch_all()
    # remax.to_csv(remax_path, index=False)
    # pbar.update(1)

    # # ===================================
    # # Fetch Dhalia Data
    # # ===================================

    # dhalia = Dhalia.fetch_all()
    # dhalia.to_csv(dhalia_path, index=False)
    # pbar.update(1)

    # # ===================================
    # # Fetch Sara Grech Data
    # # ===================================

    # saragrech = SaraGrech.fetch_all()
    # saragrech.to_csv(saragrech_path, index=False)
    # pbar.update(1)

    # # ===================================
    # # Fetch Alliance Data
    # # ===================================

    # alliance = Alliance.fetch_all()
    # alliance.to_csv(alliance_path, index=False)
    # pbar.update(1)

    # # ===================================
    # # Fetch Frank Salt Data
    # # ===================================

    # franksalt = FrankSalt.fetch_all()
    # franksalt.to_csv(franksalt_path, index=False)
    # pbar.update(1)

    # # ===================================
    # # Fetch Ben Estate Data
    # # ===================================

    # benestates = BenEstates.fetch_all()
    # benestates.to_csv(benestates_path, index=False)
    # pbar.update(1)

    # # ===================================
    # # Fetch Belair Data
    # # ===================================

    # belair = Belair.fetch_all()
    # belair.to_csv(belair_path, index=False)
    # pbar.update(1)

    # ===================================
    # Process a common Dataset
    # ===================================

    remax = pd.read_csv(remax_path)
    dhalia = pd.read_csv(dhalia_path)
    saragrech = pd.read_csv(saragrech_path)
    alliance = pd.read_csv(alliance_path)
    franksalt = pd.read_csv(franksalt_path)
    benestates = pd.read_csv(benestates_path)
    belair = pd.read_csv(belair_path)

    dataset = pd.concat([remax, dhalia, saragrech, alliance, franksalt, benestates, belair])

    exclude_types = Configuration.exclude_types()
    exclude_towns = Configuration.exclude_towns()

    mapping_types = Configuration.mapping_types()
    mapping_towns = Configuration.mapping_towns()
    imply_province = Configuration.imply_province()

    # Exclude Type and Town
    dataset = dataset[~ dataset['Type'].isin(exclude_types)]
    dataset = dataset[~ dataset['Town'].isin(exclude_towns)]

    # Standardise Type and Town Names
    dataset['Type'] = dataset['Type'].replace(mapping_types)
    dataset['Town'] = dataset['Town'].replace(mapping_towns)

    # Determining Regions
    dataset = dataset.merge(imply_province, on='Town', how='left')

    # Replace 0 as NAN
    dataset[['Rooms', 'Bedrooms', 'Bathrooms']] = dataset[['Rooms', 'Bedrooms', 'Bathrooms']].replace(0, np.nan)

    # Exclude invalid entries
    dataset = dataset[
        pd.to_numeric(dataset['Bedrooms'], errors='coerce').notnull() &
        pd.to_numeric(dataset['Price'], errors='coerce').notnull()
    ]

    dataset = dataset.dropna(subset=dataset.columns[:5])

    dataset['Price'] = pd.to_numeric(dataset['Price'])

    # Exclude anomaly values
    dataset = dataset[dataset.groupby(['Type', 'Town', 'Bedrooms'])['Price'].transform(zscore).abs() < 2]

    # Saving Dataset
    dataset.to_csv('data/dataset.csv', index=False)
    pbar.update(1)

    # Save Unmapped Towns
    variant_types = dataset['Type'].value_counts()
    variant_types.to_csv('data/variant_types.csv')

    # Save Unmapped Towns
    unmapped_towns = dataset[dataset['Province'].isnull()]['Town'].value_counts()
    unmapped_towns.to_csv('data/unmapped_towns.csv')

    # ===================================
    # Close Progress Bar
    # ===================================

    pbar.close()
