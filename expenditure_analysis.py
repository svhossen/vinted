# -*- coding: utf-8 -*-
"""
Created on Sun May 10 21:12:11 2020

@author: hossenbuxs
"""
#importing libraries
import pandas as pd
import os

os.chdir(r'C:\Users\hossenbuxs\Desktop\JOB\whatswapp')

#%%Importing dataset

data = pd.read_excel(r'purchases\purchases.xlsx')


#%% exploratory

total_spent_sku = data.groupby('sku')['sku_price'].sum()

data.loc[data['user_id']=='b6c14a101f5a2b41d0f3705ff7848a96',['sku','day']]

#%%before & after subscription

#before subscription
data_1 = data[data['sku'].eq('subscription_1').groupby(data['user_id']).cumsum().eq(0)]

#after subscription
data_2 = data[~data['sku'].eq('subscription_1').groupby(data['user_id']).cumsum().eq(0)]

#%%

total_pre=data_1['sku_price'].sum()

total_post=data_2['sku_price'].sum()

#%% average daily expenditure pre and post subscription_1

AVG_pre = pd.DataFrame(data_1.groupby('day')['sku_price'].sum().describe()).rename(columns={'sku_price':'exp_pre'})

AVG_post = pd.DataFrame(data_2.groupby('day')['sku_price'].sum().describe()).rename(columns={'sku_price':'exp_post'})

#%%merging daily average
merged=AVG_pre.merge(AVG_post,how='left', left_index=True,right_index=True)

#%%
import matplotlib.pyplot as plt
from pandas.plotting import table
import seaborn as sns

desc = merged

#create a subplot without frame
plot = plt.subplot(111, frame_on=False)

#remove axis
plot.xaxis.set_visible(False) 
plot.yaxis.set_visible(False) 

#create the table plot and position it in the upper left corner
table(plot, desc,loc='upper right')

#save the plot as a png file
plt.savefig('desc_plot.png')

#alternative viz
fig = plt.figure(facecolor='w', edgecolor='k')
sns.heatmap(merged, annot=True, cmap='viridis', cbar=False,fmt = '.1f')
plt.title('Daily expenditure pre vs post subscription')
plt.savefig('DataFrame.png')

#%%

import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

objects = ('pre_purchase', 'post_purchase')
y_pos = np.arange(len(objects))
performance = [total_pre,total_post]

plt.bar(y_pos, performance, align='center', alpha=0.5)
plt.xticks(y_pos, objects)
plt.ylabel('Total expenditure')
plt.title('Total expenditure pre vs post subscription_1')

plt.show()
#%% average price
AVG_pre = pd.DataFrame(data_1.groupby('day'))