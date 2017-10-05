'''
Procedural code to load in data for a FeatureEngineering Object
As this was a consulting project, user data cannot be shared
'''
import os
import pandas as pd


def load_sanfran_set():
    '''
    Function to read in test dataframe
    '''
    df_ts = pd.read_csv(os.path.join(csv_dir, r'initial_ts_sanfran.csv'))
    df_ts_glow = pd.read_csv(os.path.join(csv_dir, r'initial_ts_sanfran_glow.csv'))
    return df_ts, df_ts_glow


def timeseries_setup(df, df_glow):
    '''
    Function to join multiple types of devices and create multi-index
    dataframe where index is device id and then chronological by timestamp
    '''
    print ("Number of Unique Device Type 1", len(df['device_uuid'].unique()))
    print ("Number of Unique Device Type 2", len(df_glow['device_uuid'].unique()))
    df_all_devices = (pd.concat([df, df_glow])
                        .set_index(['device_uuid', 'timestamp'])
                        .sort_index(axis=0, level=0)
                        .drop('date', axis = 1))
    return df_all_devices


def location_data():
    '''
    Create Location dataframe with latitude and longitude coordinates
    '''
    df_locat = (pd.read_csv(os.path.join(csv_dir, r'sf_location.csv'))
                  .drop_duplicates(subset='uuid', keep='last')
                  .set_index('uuid'))
    return df_locat


def add_location(df_locat, df):
    '''
    Function to add in x, y coordinates
    '''
    df = df.reset_index()
    df = (df.join(df_locat, on = 'device_uuid', how = 'left'))
    df = (df.reset_index()
            .set_index(['device_uuid', 'timestamp'])
            .sort_index(axis=0, level=0))
    return df


def merge_outdoor_weather_data(df_all_devices, df_outdoor_weather):
    '''
    Function to join weather data with time series device data
    '''
    df_all_devices = (df_all_devices.reset_index()
                                    .set_index('timestamp'))
    df_all_devices.index = pd.to_datetime(df_all_devices.index)
    df_all_devices['date'] = df_all_devices.index.date
    df_outdoor_weather.index = pd.to_datetime(df_outdoor_weather.index)
    df_outdoor_weather.index = df_outdoor_weather.index.date
    df_all_devices = (df_all_devices.join(df_outdoor_weather, 
                              on = 'date', how = 'left'))
    df_all_devices = (df_all_devices.reset_index()
                                    .set_index(['device_uuid', 'timestamp'])
                                    .sort_index(axis=0, level=0))
    return df_all_devices


if __name__ == '__main__':
    csv_dir = r'C:\Users\Mangarella\Documents\Insight\Project'
    df_timeseries, df_timeseries_glow = load_sanfran_set()
    df_devices = timeseries_setup(df_timeseries, df_timeseries_glow)
    df_location = location_data()
    df_devices = add_location(df_location, df_devices)
    df_devices = merge_outdoor_weather_data(df_devices, df_weather)

