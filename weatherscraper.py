# -*- coding: utf-8 -*-
"""
Created on Sat Sep 16 16:34:11 2017

@author: Mangarella
"""

import requests
import pandas as pd
import numpy as np
import re
from bs4 import BeautifulSoup


weather_keys = ['Mean Temperature', 'Max Temperature', 
                'Min Temperature', 'Precipitation',
                'Dew Point', 'Average Humidity',
                'Maximum Humidity', 'Minimum Humidity',
                'Wind Speed']


def get_num_days(year, month):
    '''
    A function to determine the number of days in a given month
    for a given year.  
    - Input: year and month (type: int)
    - Output: number of days (type: int)
    '''
    # Is 'year' a leap year?  If so (not), February has 28 (29) days
    leap_year = False
    if (year % 400 == 0) or ((year % 4 == 0) and (year % 100 != 0)):
        leap_year = True
    if month == 2:
        num_days = 28
        if leap_year:
            num_days = 29
    # 30 days hath September, April, June and November.
    elif month in [4, 6, 9, 11]:
        num_days = 30
    # All the rest have 31, excepting February alone, 
    # which is weird and ill-behaved, like this poem.
    else:
        num_days = 31
    return num_days

def scrape_daily_weather_summary(years=range(2016,2018)):
    '''
    Scrape data from weather underground for a given location
    Generally takes 1 second per day
    Input years (preferably in range or list)
    Output dictionary with key = date, value = daily weather
    '''
    
    dict_weather = {}
    
    for year in years:
        for month in range(1, 13):
            num_days = get_num_days(year, month)
            for day in range(1, num_days + 1):
                print (year, month, day)
                url = 'https://www.wunderground.com/history/airport/KSFO/%s/%s/%s/DailyHistory.html' % \
                    (year, month, day)
                page = requests.get(url)
                soup = BeautifulSoup(page.text, 'lxml')
                (mean_temp, max_temp, min_temp, precip, dew_point,
                mean_humid, max_humid, min_humid, wind_speed) = \
                    [soup.find('span', text=text_label).parent.find_next_sibling('td').get_text(strip=True) for 
                     text_label in weather_keys]
                dict_weather[str(month) + "-" + str(day) + "-" + str(year)] = (mean_temp, max_temp, min_temp, 
                            precip, dew_point, mean_humid, max_humid, min_humid, wind_speed)
    return dict_weather


def scraped_data_to_df(weather_dict):
    '''
    Transforms dictionary of scraped weather to a dataframe
    Input = weather_dict from scrape_daily_weather_summary
    Output = time series dataframe for a given location
    '''
    
    df_weather = pd.DataFrame.from_dict(weather_dict, orient = 'index')
    df_weather.index = pd.to_datetime(df_weather.index)
    df_weather = (df_weather.sort_index()
                            .replace('', np.nan)
                            .dropna() #Only drop missing data before conversion
                            .applymap(lambda x: re.sub(r"[^0-9.]+", "", x))
                            .replace('', np.nan)
                            .applymap(float))
    df_weather.columns = [key.lower().replace(' ', '_') for key in weather_keys]
    return df_weather


if __name__ == '__main__':
   dict_weather = scrape_daily_weather_summary()
   df_weather = scraped_data_to_df(dict_weather)
