# Code Overview

This was a consulting project for a startup in the indoor air quality market space. As a result, user data cannot be shared publicly. In addition, some features and pollutants have been either removed or anonymized. 

## Modules

1. Weatherscraper - Procedural code to scrape weather from weather underground and input it into a pandas dataframe. Features scraped are humidity, temperature, and dew point. The weather underground API highly limits daily call amounts, so this scraper module was written to circumvent these data limits. 

2. Dataloader - Procedural code to merge users' time series data with outdoor air quality and user location data.

3. Feature Engineering - Object to add rolling statistics, time and day, outdoor air quality features. Classification setup is then created using a Chronological CV setup, and the Pollutant type can be chosen.

4. GradientBooster - Object to create gradient boosted models from undersampled kfolds of the training set. Evaluation can be done using non-sequential (precision/recall) or sequential scoring metrics as outlined in my blog post.

Enjoy!
