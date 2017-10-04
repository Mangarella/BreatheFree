import pandas as pd
import numpy as np
import datetime as dt
import os
import gc
from math import cos, asin, sqrt, radians
from geopy import distance


class FeatureEngineering:
    '''Class to engineer statistical features (add_rolling_stats),
    derivative features (add_derivative_stats),
    long term behavior patterns (add_long_term_stats),
    time features (add_time_features),
    generate a forecast based on a cutoff (class_generation),
    and create a class (quick_cutoff)
    '''
    
    def __init__(self, df_agg_data):
        '''
        Initialization method with aggregated weather, location, and
        time series data
        '''
        self.data = df_agg_data
        
    
    def add_rolling_stats(self, times=[4, 16, 32], 
                          labels=['1h', '4h', '8h'],
                          kurt_skew_std = False):
        '''
        Method to add rolling statistics to historical sensor readings
        
        Optional Inputs are:
            
            --times (list):  Custom number of 15 minute segments for 
            --labels (list): Labels should match number of hours or minutes of
                             times variable.
                             
        Output:
            self.data with added rolling stats
        
        Note: I would use a panel for these calculations, but unfortunately 
        that data structure will be deprecated soon :(
        '''
        period = zip(times, labels)
        
        for time, label in period:
            for feat in ['toxin_a', 'toxin_b', 'toxin_c', 'toxin_d', 'toxin_e']:
                self.data[feat + '_roll_mn_' + label] = (self.data[feat]
                                                             .groupby(level=0)
                                .rolling(time).mean().values)
                self.data[feat + '_roll_md_' + label] = (self.data[feat]
                                                             .groupby(level=0)
                                               .rolling(time).median().values)
                self.data[feat + '_roll_std_' + label] = (self.data[feat]
                                                             .groupby(level=0)
                                                   .rolling(time).std().values)
    
    
    def add_deriv_stats(self):
        '''
        Method to add rolling statistics to derivative.
        
        Inputs: Only self
        Outputs: self.data with added rolling statistics on derivative
        '''
        self.data = self.data.groupby(level=0).apply(self.deriv_stats)


    def deriv_stats(self, df):
        '''
        Groupby function called by method add_deriv_stats to add 
        features for each user device
        '''
        for feat in ['toxin_a', 'toxin_b', 'toxin_c', 'toxin_d', 'toxin_e']:
            df[feat + '_1_period_change'] = (df[feat] / df[feat].shift(1) - 1) *100
            df[feat + '_1_period_mn'] = df[feat + '_1_period_change'].rolling(10).mean()
            df[feat + '_1_period_md'] = df[feat + '_1_period_change'].rolling(10).median()
            df[feat + '_1_period_std'] = df[feat + '_1_period_change'].rolling(10).std()
        return df


    def add_long_term_stats(self):
        '''
        Method to add rolling statistics to derivative.
        
        Inputs: Only self
        Outputs: self.data with added rolling max of previous 24h
        '''
        self.data = self.data.groupby(level=0).apply(self.long_stats)
        
        
    def long_stats(self, df):
        '''
        Groupby function called by method long_term_stats to add 
        features for each user device
        '''
        for feat in ['toxin_a', 'toxin_b', 'toxin_c', 'toxin_d', 'toxin_e']:
            df[feat + '_daily_roll_max'] = df[feat].rolling(96).max()
        return df
    
    
    def add_time_features(self):
        '''
        Method to add day of week and time of day features to self.data
        
        Inputs: Only self
        Outputs: self.data with added time of day and day of week features
        '''
        self.data = self.data.reset_index()
        self.data['day'] = self.data['timestamp'].dt.weekday
        self.data['time_of_day'] = self.data['timestamp'].dt.hour
        self.data = self.data.set_index(['device_uuid', 'timestamp'])
    

    def class_generation(self, time = 8):
        '''
        Method to add future rolling max for classification generation
        
        Optional Inputs are:
        --time (hours) = future forecasting time
            
        Outputs: self.data with added future maximal value
        '''
        for feat in ['toxin_a', 'toxin_b', 'toxin_c', 'toxin_d', 'toxin_e']:
            self.data[feat + '_future_max'] = (self.data[feat + '_roll_mn_1h']
                                                        .groupby(level=0)
                                                        .rolling(time*4).max()
                                                        .shift(-time*4).values)


    def quick_cutoff(self):
        '''
        Method to determine class of each time point by future forecasted value
        
        Inputs: Only self
        Outputs: self.data with added future maximal value
        '''
        toxin_a_cutoff, toxin_b_cutoff, toxin_c_cutoff = 1359.64, 2000.0, 37.43
    
        self.data['toxin_a_cutoff'] = (self.data['toxin_a_future_max'] > toxin_a_cutoff).astype(int)
        self.data['toxin_b_cutoff'] = (self.data['toxin_b_future_max'] > toxin_b_cutoff).astype(int)
        self.data['toxin_c_cutoff'] = (self.data['toxin_c_future_max'] > toxin_c_cutoff).astype(int)
        
    
    