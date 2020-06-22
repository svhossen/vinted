# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 18:04:44 2020

@author: hossenbuxs
"""
#%%
'''
run metric before running this code
'''

#%% import libraries/modules

import pandas as pd
#from __future__ import print_function
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.iolib.summary2 import summary_col
import numpy as np
import os
from datetime import datetime
#%% Working directory

os.chdir(r'C:\Users\hossenbuxs\Desktop\JOB\vinted\vinted')


#%% Investigating potential variables 

descriptive_statistics = ['mean', 'median', 'std','var']

data.listing_quality_string.unique()

data.brand_is_verified.describe()#unique()

data.loc[:,'days_unsold'] = (data.loc[:,'days_unsold']).astype(float)

country_code = data.groupby('country_code').agg({'days_unsold': descriptive_statistics})

listing_quality_string = data.groupby('listing_quality_string').agg({'days_unsold': descriptive_statistics})

listings_in_first_7days_detailed = data.groupby('listings_in_first_7days_detailed').agg({'days_unsold': descriptive_statistics})

brand_is_verified = data.groupby('brand_is_verified').agg({'days_unsold': descriptive_statistics})

listing_platform = data.groupby('listing_platform').agg({'days_unsold': descriptive_statistics})

status =data.groupby('status').agg({'days_unsold': descriptive_statistics})

#%%concatenating the summary tables

summary_stats = pd.concat([country_code,listing_quality_string,listings_in_first_7days_detailed,brand_is_verified,listing_platform,status],keys = ['country_code','listing_quality_string','listings_in_first_7days_detailed','brand_is_verified','listing_platform','status'])



#%%model trial 1
'''
Potential model: ZeroInflatedNegativeBinomialP

This model is adequate for categrical datasets with a relatively high frequency of zeros in the dependant variable
'''
# import statsmodels
# data['endog'] = data.loc[:,'days_unsold']

# data_onehot = pd.get_dummies(data['listing_quality_string'])

# mod_nb = statsmodels.discrete.count_model.ZeroInflatedNegativeBinomialP(data['endog'],data_onehot).fit()

# print(mod_nb.summary())

# mod_ols = sm.NegativeBinomial(data.days_unsold , data_onehot , data=data)
# res_ols = mod_ols.fit(disp=False)
# print(res_ols.summary())

# mod_ols = sm.GLM(data.days_unsold , data_onehot , data=data)
# res_ols = mod_ols.fit(disp=False)
# print(res_ols.summary())

# mod_nbin = sm.NegativeBinomial.from_formula('days_unsold ~ C(country_code) + C(listing_platform)+ C(brand_is_verified) + C(listing_quality_string) + C(status) + gmv_eur_fixed ', data=data)
# res_nbin = mod_nbin.fit(disp=False)
# print(res_nbin.summary())

#%%model 2


# mod_ols = sm.OLS.from_formula(formula = 'days_unsold ~ C(country_code) + C(listing_platform)+ C(brand_is_verified) + C(listing_quality_string) + window_items_sold + catalog_code_1 +status', data=data)
'''
This model automatically create dummies for categorical data: C()

'''


mod_ols = sm.OLS.from_formula(formula = 'days_unsold ~ C(country_code) + C(listing_platform)+ C(brand_is_verified)  + window_items_sold + (catalog_code_1) +  C(listing_quality_string)+C(status) + listing_price_eur_fixed', data=data)

print(mod_ols.fit().params)


print(mod_ols.fit().summary())
     
# Note that tables is a list. The table at index 1 is the "core" table. Additionally, read_html puts dfs in a list, so we want index 0
results_as_html = mod_ols.fit().summary().tables[1].as_html()
test = pd.read_html(results_as_html, header=0, index_col=0)[0]

#%%exporting results to an xlsx file

# writer = pd.ExcelWriter('Report_python.xlsx', engine='xlsxwriter')
# data_daily.to_excel(writer, 'data_daily')
# data_group_unsold.to_excel(writer, 'data_group_unsold')
# test.to_excel(writer, 'Regression_results')
# summary_stats.to_excel(writer, 'summary_stats')

# writer.save()


  #%%
# =============================================================================
# data_nonan = data.dropna()
# 
# 
# Y = data_nonan['days_unsold']
# 
# X = data_nonan[['country_code','listing_platform','brand_is_verified','listing_quality_string','catalog_code_1','status']]
# 
# X = pd.get_dummies(data=X, drop_first=True)
# 
# mod_bin = sm.NegativeBinomial(Y, X , data=data_nonan)
# res_bin = mod_bin.fit(disp=False)
# print(res_bin.summary())
# 
# 
# 
# 
# from sklearn import linear_model
# from sklearn.model_selection import train_test_split
# X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = .20, random_state = 40)
# regr = linear_model.LinearRegression() # Do not use fit_intercept = False if you have removed 1 column after dummy encoding
# regr.fit(X_train, Y_train)
# predicted = regr.predict(X_test)
# =============================================================================





