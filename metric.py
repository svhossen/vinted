# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 16:33:22 2020

@author: hossenbuxs
"""
#%% import libraries/modules

import pandas as pd
import numpy as np
import os
from datetime import datetime
import xlsxwriter

#%% Working directory

os.chdir(r'C:\Users\hossenbuxs\Desktop\JOB\vinted')

#%% Importing original file: data

data = pd.read_csv(r'product_ds_hw_data.csv', sep = ',')

#%% Preliminary data investigation

description = data.describe(include = 'all')

list_variables = data.columns

data.created_at.describe() # Note the count of unique values is lower that general count

#%% Processing dates and establishing number of days item remains unsold

data['days_unsold'] = (data['sale_time'].apply(lambda x: np.nan if pd.isnull(x) else datetime.strptime(x, "%m/%d/%Y %H:%M"))- data['created_at'].apply(lambda x: datetime.strptime(x, "%m/%d/%Y %H:%M"))).dt.components['days']


data['hours_unsold'] = (data['sale_time'].apply(lambda x: np.nan if pd.isnull(x) else datetime.strptime(x, "%m/%d/%Y %H:%M"))- data['created_at'].apply(lambda x: datetime.strptime(x, "%m/%d/%Y %H:%M"))) / np.timedelta64(1, 'h')

data_head = data.head(10)
# data = data.loc[np.isnan(data.loc[:,'sale_time'])]

# def days_between(d1, d2, string_format):
#     '''
    
#     Parameters
#     ----------
#     d1 : Start date
#     d2 : end datae
#     string_format: format of the dates 

#     Returns
#     -------
#     TYPE
#         returns the difference in days between the pair of dates inputed.

#     '''
#     d1 = datetime.strptime(d1, string_format)
#     d2 = datetime.strptime(d2, string_format)
#     return abs((d2 - d1).days)

# data['days_unsold'] = days_between(data.loc[9,'created_at'],
#                                    data.loc[9,'sale_time'],
#                                    "%m/%d/%Y %H:%M")

#%% Assessing the percentage of products sold at a certain point of time.
data.columns

# required to include nan(unsold) as a group
#=============================================================================
data['days_unsold'] = data['days_unsold'].astype(str)
#=============================================================================


#grouping by days unsold and totalling the number of items
data_group_unsold =( data.groupby('days_unsold').agg({'id': 'count'})).rename(columns={'id':'number of items'})
#calculating the percentage of number of items on a given day
data_group_unsold['percentage'] = 100 * (data_group_unsold.loc[:,'number of items']  /                                data_group_unsold.loc[:,'number of items'].sum())

data_group_unsold.reset_index(inplace = True)

#%% daily available items and sales
data_daily_add = (data.groupby(data['created_at'].apply(lambda x: datetime.strptime(x, "%m/%d/%Y %H:%M")).dt.date).agg({'id':'count'})).rename(columns = {'id':'number of additions'})

data_daily_sale = (data.groupby(data['sale_time'].apply(lambda x: np.nan if pd.isnull(x) else datetime.strptime(x, "%m/%d/%Y %H:%M")).dt.date).agg({'id':'count'})).rename(columns = {'id':'number of items sold'})

# daily additions and sales
data_daily = data_daily_add.merge(data_daily_sale, how = 'left', left_index = True,right_index = True)




