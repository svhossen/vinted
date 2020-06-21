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
import numpy as np
import os
from datetime import datetime
#%% Working directory

os.chdir(r'C:\Users\hossenbuxs\Desktop\JOB\vinted')


#%% Investigating potential variables 

descriptive_statistics = ['mean', 'median', 'count', 'sum', 'std','var']

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

#%%
# writer = pd.ExcelWriter('Report_python.xlsx', engine='xlsxwriter')
# data_daily.to_excel(writer, 'data_daily')
# data_group_unsold.to_excel(writer, 'data_group_unsold')

# writer.save()

#%%model trial 1


data['endog'] = data.loc[:,'days_unsold']

data_onehot = pd.get_dummies(data, columns=['country_code'], prefix = ['country'])

mod_nb = sm.OLS.from_formula('days_unsold ~ suggested_price_maximum + C(country_code)', data=data).fit()

print(mod_nb.summary())


#%%


mod_nbin = sm.NegativeBinomial.from_formula('days_unsold ~ suggested_price_maximum + C(country_code)', data=data)
res_nbin = mod_nbin.fit(disp=False)
print(res_nbin.summary())




