import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.ensemble import GradientBoostingClassifier

class GradientBooster():
    
    
    def __init__(self, df_agg_data):
        '''Initialize with feature set data'''
        self.rawdata = df_agg_data
        self.model = []
        self.folds = []

    
    def classification_setup(self, var = 'toxin_a', gap = 20000, chr_events = 50000):
        '''
        Method to make a classification setup with X_data, y_data, and a
        chronological test set
        
        Inputs: self.data (modified by this method)
                variable (Pollutant to modify)
                gap (chronological gap between training and test data)
                chr_events (number of events to use as a test set)
        Outputs: self.X_data
                 self.y_data
                 self.features (features for classification)
        '''
        self.rawdata = (self.rawdata.reset_index()
                            .dropna()
                            .sort_values(by = 'timestamp'))
        self.cvdata = self.rawdata.tail(chr_events+gap).tail(chr_events)
        self.train_test = self.rawdata.head(len(self.rawdata) - chr_events)
        self.X_data = self.train_test
        self.y_data = self.train_test[var + '_cutoff']
    
        self.X_cv = self.cvdata
        self.y_cv = self.cvdata[var + '_cutoff']
    
        #Only include features for specific time series
        self.features = (self.X_data.columns[self.X_data.columns.str.contains(var)]
                            .tolist())

        #Add Weather Features
        self.features += self.X_data.columns[self.X_data.columns.str.contains('tempe')].tolist()
        self.features += self.X_data.columns[self.X_data.columns.str.contains('humidi')].tolist()
        self.features += self.X_data.columns[self.X_data.columns.str.contains('wind')].tolist()
        self.features += self.X_data.columns[self.X_data.columns.str.contains('precip')].tolist()
        self.features += self.X_data.columns[self.X_data.columns.str.contains('dew')].tolist()
        self.features += ['day', 'time_of_day']
        
        #Remove data leakage features
        self.features.remove(var + '_cutoff')
        self.features.remove(var + '_future_max')
    
    
    
    def under_sample_kfold(self, var = 'toxin_a', n_folds = 10):
        '''
        Method to create undersampled data for an ensemble model
        
        Inputs: self.data
                variable (default)
                n_folds (number of undersampled folds)
        Outputs: self.folds (class balanced folds of train and test data)
        '''
        pos_events = self.X_data[self.X_data[var + '_cutoff'] == 1]
        neg_events = self.X_data[self.X_data[var + '_cutoff'] == 0]
    
        #Randomize and pick same n number of events
        number_pos_events = len(pos_events)

        for fold in range(0, n_folds):
            pos_events = pos_events.reindex(np.random.permutation(pos_events.index))
            neg_events = neg_events.reindex(np.random.permutation(neg_events.index))
            undersampled_events = pd.concat([neg_events.head(number_pos_events), pos_events])
            X_data_u, y_data_u = undersampled_events, undersampled_events[var + '_cutoff']
            X_train_u, X_test_u, y_train_u, y_test_u = train_test_split(X_data_u, y_data_u, test_size=0.3)
            self.folds.append([X_train_u, X_test_u, y_train_u, y_test_u])    
    
    
    def make_model(self):
        '''
        Method to make models from self.folds
        Inputs:  self.folds
        Outputs: self.model (set of models to ensemble)
        '''
        for fold in range(0, len(self.folds)):
            X_train, X_test, y_train, y_test = (self.folds[fold][0], 
                                                self.folds[fold][1],
                                                self.folds[fold][2],
                                                self.folds[fold][3])
            clf = GradientBoostingClassifier(n_estimators = 200, max_depth = 5)
            clf.fit(X_train[self.features].head(100000), y_train.head(100000))
            self.model.append(clf)


    def add_fold_predictions(self, var = 'toxin_a', e_cutoff = 7):
        '''
        Method to add predictions for each model to the self.X_cv data
        Inputs: self.X_cv
                self.model
                var (default)
                e_cutoff: ensemble voting cutoff for a Class 1 prediction
        Outputs: self.X_cv with added prediction columns
        '''
        for fold in range(0, len(self.model)):
            self.X_cv.loc[:, var + '_prediction_' + str(fold)] = self.model[fold].predict(self.X_cv[self.features])
            self.X_cv.loc[:, var + '_result_' + str(fold)] = 2*self.X_cv[var + '_prediction_' + str(fold)] - self.X_cv[var + '_cutoff']
    
        self.X_cv.loc[:, var + '_ensemble_score'] = self.X_cv[[var + '_prediction_' + str(i) for i in range(0, len(self.model))]].sum(axis = 1)
        self.X_cv.loc[:, var + '_ensemble_pred'] = (self.X_cv[var + '_ensemble_score'] > e_cutoff).astype(int)
        self.X_cv.loc[:, var + '_ensemble_result'] = 2*self.X_cv[var + '_ensemble_pred'] - self.X_cv[var + '_cutoff']
        
    
    def time_series_eval(self, var = 'toxin_a'):
        '''
        Method to determine the distance between the model's first prediction 
        and the start of the 8 hour forecast
        
        Input:  self.X_cv (stored fold predictions required)
                var (default, make sure to change depending on which model)
        Output: self.pred_offset_dist (Distance of model from all test events)
        '''
        self.X_cv = (self.X_cv.reset_index()
                    .set_index(['device_uuid', 'timestamp'])
                    .sort_index(axis=0, level=0))
        self.pred_offset_dist = self.X_cv.groupby(level=0).apply(self.prediction_time_offset, var)
        self.pred_offset_dist = [item for sublist in self.pred_offset_dist for item in sublist]


    def prediction_time_offset(self, df, var):
        '''
        Groupby method to track the distance between the start of the forecast
        and the start of predictions from the model
        '''
        cutoffs = pd.DataFrame(np.where(df[var + '_cutoff'] == 1)[0])
        cutoffs['offset'] = cutoffs.loc[:,0] - cutoffs.loc[:,0].shift(1)
        pred_offset_dist = []
        
        for cutoff in cutoffs[cutoffs['offset'] != 1].loc[:,0]:
            single_event = df.iloc[cutoff:,:].copy()
            single_event[var + '_cutoff_cum_sum'] = single_event[var + '_cutoff'].cumsum()
            single_event[var + '_chrono_result'] = single_event[var + '_cutoff_cum_sum'] * single_event[var + '_ensemble_result']
            try:
                prediction_offset = np.where(single_event[var + '_chrono_result'] > 0)[0][0]
            except:
                #Put in 8 hours if completely missed
                prediction_offset = 32
            pred_offset_dist.append(prediction_offset)
        return pred_offset_dist
  
    
    def pred_offset_to_cdf(self, ls_offsets):
        '''
        Plots a Normalized Cumulative Probability Density for Forecasted
        Predictions with respect to time-till-positive class
        '''
    
        df_offsets = pd.DataFrame(ls_offsets)
        df_offsets = pd.DataFrame(df_offsets.iloc[:,0].value_counts().sort_index())
        df_offsets['cum_pred'] = df_offsets.iloc[:,0].cumsum()
        df_offsets['cum_pred'] = df_offsets['cum_pred']/df_offsets['cum_pred'].max() * 100 
    
        #Adjust index to be time till it changes classes
        df_offsets.index = [(32-x)/float(4) for x in df_offsets.index]
        df_offsets['cum_pred'].plot(fontsize = 20)