import pandas as pd

from tqdm import tqdm

from export.remax import Remax


if __name__ == "__main__":
    remax_path = "data/remax.csv"

    # ===================================
    # Create Progress Bar
    # ===================================

    pbar = tqdm(total=2)

    # ===================================
    # Fetching Remix Data
    # ===================================

    remax = Remax.fetch_all()
    remax.to_csv(remax_path, index=False)
    pbar.update(1)

    # ===================================
    # Process a common Dataset
    # ===================================

    remax = pd.read_csv(remax_path)

    dataset = pd.concat([remax])
    dataset = dataset[pd.to_numeric(dataset['Price'], errors='coerce').notnull()]

    dataset.to_csv("dataset.csv", index=False)
    pbar.update(1)

    # ===================================
    # Close Progress Bar
    # ===================================

    pbar.close()
