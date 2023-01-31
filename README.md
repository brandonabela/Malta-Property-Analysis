# Malta Property Analysis

This project aims to uncover the most profitable real estate opportunities in Malta by comparing and ranking properties for sale against similar rental properties. By analysing key features of each property, we are able to identify those with the highest potential return on investment (ROI).

## Dataset Compilation

For the analysis of the property market to occur, a dataset had to be compiled. The selenium python package was used for this purpose, with the implementation of multithreading to allow for concurrent scraping of multiple websites. The websites ```Alliance```, ```Belair```, ```Ben Estates```, ```Dhalia```, ```Frank Salt```, ```Remax```, ```Sara Grech``` were scraped for properties for sale and rental. In addition, ```Quicklets``` was scraped specifically for rental properties and ```Zanzi``` was scraped for properties for sale.

![Source Distribution](https://user-images.githubusercontent.com/23166383/215691494-a33f8c7a-3f80-44c5-93f2-80055c4457cc.png)


Every data source had its own unique logic to ensure that every feature was at a common baseline, and every data source was saved as a separate ```CSV```. The use of multithreading in the scraping process allowed for efficient and quick compilation of a comprehensive dataset containing information on properties for sale and rental from multiple sources, providing a thorough understanding of the current property market in the area.

The following details highlight the key features extracted from the website sources for both sale and rental properties.
- **Is_Sale**: This feature indicates whether the property is for sale or not. It is a boolean variable (e.g. True or False) where True indicates that the property is for sale and False indicates that it is not.
- **Source**: This feature indicates the source website where the information of the property was scraped from.
- **Reference**: The reference is a unique identifier that is specific to the website source and can be used to easily locate the property within that source.
- **Town**: This feature specifies the city where the property is located.
- **Type**: This feature indicates the type of property. Examples include house, apartment, villa, etc.
- **Stage**: This feature denotes the current stage of development of the property. It can be categorized as on plan, shell, finished, furnished, unconverted, or unclassified.
- **Bedrooms**: This feature indicates the number of bedrooms in the property.
- **Bathrooms**: This feature indicates the number of bathrooms in the property.
- **TotalSqm**: This feature indicates the total area of the property measured in square meters.
- **IntArea**: This feature indicates the internal area of the property measured in square meters.
- **ExtArea**: This feature indicates the external area of the property measured in square meters.
- **Price**: This feature specifies the cost of the property, denoted in Euro currency.

## Dataset Processing

After the data scraping has finished, the data processing starts by loading all the data sources and eliminating the types and towns that are not in the scope. The stage, type and town features are mapped to eliminate variations in wording. The town feature represents the province, latitude and longitude features. If any of the features: Is_Sale, Source, Reference, Town and Type are missing, the entire record is removed.

If the total square meter is not filled but the interior and external areas are provided, the total square meter can be implied. Furthermore, a statistical method of Z-score is applied to eliminate prices that have an absolute value greater than 1 based on the type.

The following are explanations of the implied features:
- **Province**: This feature specifies the region in which the property is located, such as North, East, South, West, Central and Gozo.
- **Latitude**: This feature denotes the geographical position of the town relative to the distance north or south of the equator.
- **Longitude**: This feature measures the town's geographical location in relation to the distance east or west of the Prime Meridian.

## Data Analysis

The dataset contains 86,906 rows and 16 columns. There are 75,291 missing values in the External Area and Internal Area columns, 56,168 missing values in the Total Square meter column, and 4,831 missing values in the Bathrooms column. All missing values in the dataset have been filled with the value ```unclassified```.

![City Plot](https://user-images.githubusercontent.com/23166383/215432109-0221dc71-7e99-4cc7-a3d3-27766bc2ad51.png)

The data reveals that Remax, Frank Salt, and Zanzi have the highest number of properties for sale, while Remax, QuickLets, and Frank Salt have the highest number of rental listings. In regards to property staging, Remax leads in properties on plan, shell, and finished stages. Meanwhile, Frank Salt has the most furnished properties. Additionally, Ben Estate has the largest number of properties without proper classification.

The top 10 towns in terms of combined property listings for sales and rental are ```Sliema```, ```Saint Julian's```, ```Gzira```, ```Swieqi```, ```Marsaskala```, ```Saint Paul's Bay```, ```Msida```, ```Qawra```, ```Mellieha```, and ```Mosta```. ```Saint Paul's Bay``` has the most property listings for sale, while ```Sliema``` has the most property listings for rent. For sale apartments, the 1st quartile is 225K, the median is 265K, and the 3rd quartile is 319K. For rental apartments, the 1st quartile is 900, the median is 1200, and the 3rd quartile is 1500.

![Top 10 Towns](https://user-images.githubusercontent.com/23166383/215691237-85a6c587-75e4-406d-8a6b-539f89f4242c.png)

When analysing the correlation between features and the sale price, it has been determined that the number of bedrooms, bathrooms, and external area are positively correlated with the sale price. This means that as these features increase, the sale price is likely to increase as well. On the other hand, the total square meter and internal area have no correlation with the sale price.

When analysing the relationship between various features and the rent price, no correlation was found. This may be due to a number of other factors playing a significant role in determining the rent price, such as the location of the property and the quality of its finishing. These factors, rather than the features mentioned, are likely to be the primary drivers of rent prices.

## Conclusions

The ```sale_price.csv``` file groups sale listings using the columns ```Type```, ```Province```, ```Town```, ```Bedrooms```, and ```Stage```. The ```rent_price.csv``` file groups rental listings using similar columns as ```sale_price.csv```, but excluding ```Stage```. Both outputs perform the following aggregations for each group:

- **Reference**: count of the number of references or listings in each group.
- **Bathrooms**: median of the number of bathrooms in each group.
- **IntArea**: median of the internal area (in square meters) in each group.
- **ExtArea**: median of the external area (in square meters) in each group.
- **Price**: minimum, maximum, and median of the price in each group.

The aggregations of both ```sale_price.csv``` and ```rent_price.csv``` were combined based on the rental columns, with a requirement for references to be greater than 2 for both sales and rental. This guaranteed that the grouping of properties would be meaningful and not include outliers in their ranking. This resulted in 1868 unique groups. Metrics such as downpayment amount, loan amount, repayment monthly, vacancy monthly, repairs monthly, management monthly, and cash on cash return were computed for each group. The top 5 groups, sorted by cash on cash return, were: penthouse in Kalkara with 3 bedrooms on plan, house of character in Birkirkara with 3 bedrooms unclassified, penthouse in Kalkara with 3 bedrooms finished, apartment in Ta' Xbiex with 3 bedrooms furnished, and apartment in Saint Julians with 3 bedrooms unclassified.

The ranking process of property sales is based on an aggregation per listing and the cash on cash return. The top 5 listings with the highest cash on cash return, ranging from 151 to 63, are as follows:

1. House of Character in Zebbug with 4 bedrooms and 3 bathrooms (unclassified)
2. House of Character in Zejtun with 3 bedrooms and 2 bathrooms (furnished)
3. House of Character in Birkirkara with 3 bedrooms and 2 bathroom (unclassified)
3. House of Character in Birkirkara with 3 bedrooms and 1 bathroom (unclassified)
4. House of Character in Birkirkara with 3 bedrooms and 1 bathroom (furnished)

These properties have been listed based on their cash on cash return, which is a financial metric used to evaluate the potential profitability of a real estate investment. The properties listed above offer a high return on investment, making them attractive options for potential buyers.
