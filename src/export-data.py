import numpy as np
import pandas as pd

from threading import Thread
from scipy.stats import zscore

from export.alliance import Alliance
from export.belair import Belair
from export.benestates import BenEstates
from export.dhalia import Dhalia
from export.franksalt import FrankSalt
from export.remax import Remax
from export.quicklets import QuickLets
from export.saragrech import SaraGrech
from export.zanzi import Zanzi
from helper.configuration import Configuration


if __name__ == "__main__":
    alliance_path = 'raw/alliance.csv'
    belair_path = 'raw/belair.csv'
    benestates_path = 'raw/benestates.csv'
    dhalia_path = 'raw/dhalia.csv'
    franksalt_path = 'raw/franksalt.csv'
    remax_path = 'raw/remax.csv'
    quicklets_path = 'raw/quicklets.csv'
    saragrech_path = 'raw/saragrech.csv'
    zanzi_path = 'raw/zanzi.csv'

    # ===================================
    # Create Threads
    # ===================================

    threads = [
        Thread(target=Alliance.fetch_all, args=(alliance_path,)),
        Thread(target=Belair.fetch_all, args=(belair_path,)),
        Thread(target=BenEstates.fetch_all, args=(benestates_path,)),
        Thread(target=Dhalia.fetch_all, args=(dhalia_path,)),
        Thread(target=FrankSalt.fetch_all, args=(franksalt_path,)),
        Thread(target=QuickLets.fetch_all, args=(quicklets_path,)),
        Thread(target=Remax.fetch_all, args=(remax_path,)),
        Thread(target=SaraGrech.fetch_all, args=(saragrech_path,)),
        Thread(target=Zanzi.fetch_all, args=(zanzi_path,)),
    ]

    # ===================================
    # Start Threads
    # ===================================

    for thread in threads:
        thread.start()

    # ===================================
    # Wait until Threads Finish
    # ===================================

    for thread in threads:
        thread.join()

    # ===================================
    # Process a common Dataset
    # ===================================

    alliance = pd.read_csv(alliance_path)
    belair = pd.read_csv(belair_path)
    benestates = pd.read_csv(benestates_path)
    dhalia = pd.read_csv(dhalia_path)
    franksalt = pd.read_csv(franksalt_path)
    remax = pd.read_csv(remax_path)
    quicklets = pd.read_csv(quicklets_path)
    saragrech = pd.read_csv(saragrech_path)
    zanzi = pd.read_csv(zanzi_path)

    dataset = pd.concat([
        alliance, belair, benestates, dhalia,
        franksalt, remax, quicklets, saragrech, zanzi
    ])

    exclude_types = Configuration.exclude_types()
    exclude_towns = Configuration.exclude_towns()

    mapping_stages = Configuration.mapping_stages()
    mapping_types = Configuration.mapping_types()
    mapping_towns = Configuration.mapping_towns()
    imply_province = Configuration.imply_province()

    # Exclude Type and Town
    dataset = dataset[~ dataset['Type'].isin(exclude_types)]
    dataset = dataset[~ dataset['Town'].isin(exclude_towns)]

    # Standardise Stages, Type and Town Names
    for _, row in mapping_stages.iterrows():
        dataset['Stage'] = dataset['Stage'].replace(row['Variant'], row['Standard'])

    for _, row in mapping_types.iterrows():
        dataset['Type'] = dataset['Type'].replace(row['Variant'], row['Standard'])

    for _, row in mapping_towns.iterrows():
        dataset['Town'] = dataset['Town'].replace(row['Variant'], row['Standard'])

    # Determining Regions
    dataset = dataset.merge(imply_province, on='Town', how='left')

    # Replace 0 as NAN
    dataset[['Bedrooms', 'Bathrooms']] = dataset[['Bedrooms', 'Bathrooms']].replace(0, np.nan)

    # Exclude invalid entries
    dataset = dataset[
        pd.to_numeric(dataset['Bedrooms'], errors='coerce').notnull() &
        pd.to_numeric(dataset['Price'], errors='coerce').notnull()
    ]

    dataset = dataset.dropna(subset=dataset.columns[:5])

    dataset['Price'] = pd.to_numeric(dataset['Price'])

    # Implying Total SQM from Internal and External Area

    sqm_filter = [0, np.nan]

    dataset.loc[
        (dataset['TotalSqm'].isin(sqm_filter) & ~ dataset['IntArea'].isin(sqm_filter) & ~ dataset['ExtArea'].isin(sqm_filter)),
        'TotalSqm'
    ] = dataset['IntArea'] + dataset['ExtArea']

    # Exclude anomaly values
    dataset = dataset[dataset.groupby(['Is_Sale', 'Type'])['Price'].transform(zscore).abs() <= 1]

    # Saving Dataset
    dataset.to_csv('data/dataset.csv', index=False)

    # Save Unmapped Towns
    variant_types = dataset['Type'].value_counts()
    variant_types.to_csv('data/variant_types.csv')

    # Save Unmapped Towns
    unmapped_towns = dataset[dataset['Province'].isnull()]['Town'].value_counts()
    unmapped_towns.to_csv('data/unmapped_towns.csv')
