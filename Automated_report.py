# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 11:43:24 2019

@author: hossenbuxs
"""
#Importing relevant modules
import scrapy
import os
import sys
import pandas as pd
import statsmodels.formula as smf
import numpy as np
from linearmodels import PanelOLS

#%%

#adding the directory in order to easiy store and import modules
sys.path.append(r"xx")

#changing main directory to indicate where to obtain and create files
os.chdir(r"xx")

#Importing the file containing the independent variable
pd.ExcelFile("xx.xlsx").sheet_names


'''
Adding the value of the macro economic variable to the mix 
'''

df = pd.read_excel("xx.xlsx", "fin_macro")

df.columns=df.columns.str.strip()

#df.set_index(['area','ANNO'],inplace=True)


#%%

'''
Importing the independent variables for demography
'''

pop2 = pd.read_excel(r"xx.xlsx", sheet_name = 'Sheet2').dropna(how = 'all')



pop2=pop2.melt(id_vars=["ANNO", "vars"], 
        var_name="region", 
        value_name="Value")


pop2 = pop2.set_index(["ANNO","region"]).pivot(columns='vars')['Value'].dropna(how = 'all').reset_index()

pop2['region'] = pop2['region'].apply(lambda x: x.strip())

pop2['region'] =    np.where(pop2['region'] == 'Barletta Andria', 'Barletta-Andria-Trani', pop2['region'])

pop2['region'] =    np.where(pop2['region'] == 'Monza Brianza', 'Monza e della Brianza', pop2['region'])

pop2['region'] =    np.where(pop2['region'] == 'Pesaro Urbino', 'Pesaro e Urbino', pop2['region'])

pop2['region'] =    np.where(pop2['region'] == 'Verbania', 'Verbano-Cusio-Ossola', pop2['region'])

pop2['region'] =    np.where(pop2['region'] == "Forli'", 'Forlì', pop2['region'])

pop2['region'] =    np.where(pop2['region'] == "Massa-Carrara", 'Massa Carrara', pop2['region'])

pop2['region'] =    np.where(pop2['region'] == "Ascoli Piceno", 'Ascoli P.', pop2['region'])

pop2['region'] =    np.where(pop2['region'] == "Reggio di Calabria", 'Reggio Calabria', pop2['region'])

pop2['region'] =    np.where(pop2['region'] == "Reggio nell'Emilia", 'Reggio E.', pop2['region'])


#%%

pop2['area']=np.where(pop2.region=='Nord-est','NE','')
pop2['area']=np.where(pop2.region=='Nord-ovest','NO',pop2['area'])
pop2['area']=np.where(pop2.region=='Mezzogiorno','S',pop2['area'])
pop2['area']=np.where(pop2.region=='Centro','C',pop2['area'])
#pop2['area']=np.where(pop2.region=='ISOLE','S',pop2['area'])




#%%



df = df.merge(pop2,how = 'left',left_on=['ANNO','area'] , right_on=["ANNO","area"])

df['65 anni e oltre']=df['65 anni e oltre'].astype('float64')

#df['Indice di dipendenza anziani']=df['Indice di dipendenza anziani'].astype('float64')


df=df[(df.ANNO>=2011) & (df.ANNO<=2020)]


#%%
'''
obtaining constraint for x_2
'''
df.reset_index(inplace = True)

df.set_index(['area','ANNO'], inplace = True)

df['y'] = np.log(df['xx']/df['xx'])

df['x_1']= np.log(df['xx']/df['xx'])

df['x_2']= np.log(df['xx']/df['xx'])



modr = PanelOLS.from_formula('y ~ x_1 + x_2 + 1', df)
resr = modr.fit(cov_type='clustered', cluster_entity=True)


print(resr.summary)

constraint = resr.params[2]




#%%

'''
obtaining new coefficients while contraining x_2
'''

df['y'] = np.log(df['xx']/df['xx']) - constraint*df['x_2']

df['x_1']= np.log(df['xx']/df['xx'])

df['x_2']= np.log(df['xx']/df['xx'])

#df['x_3']= np.log(df['Indice di dipendenza anziani'])

df['x_3']= np.log(df['xx'])


model = PanelOLS.from_formula('y ~ x_1 + x_3 + 1', df)
panel = model.fit(cov_type='clustered', cluster_entity=True)


print(panel.summary)


#%%

'''
Fitting data back to the regional data.
'''

pop2.reset_index(inplace=True)

#pop2.set_index(['region','ANNO'],inplace=True, drop = True )


df2 = pd.read_excel("xx.xlsx", "fin_prov")

df2.columns=df2.columns.str.strip()

df2.set_index(['xx','xx'],inplace=True, drop = True )



final2 = pd.merge(df2, pop2, how='left', left_index= True, right_on= ['xx','xx']).sort_index()


#%%

#final2['y'] = np.log(final2['Volumi']/final2['POPCR'])

final2.replace(['..','*','...','…'],np.nan,inplace = True)

final2['Prezzi']=final2['Prezzi'].astype('float64')
final2['totprice']=final2['totprice'].astype('float64')
final2['65 anni e oltre']=final2['65 anni e oltre'].astype('float64')
#%%
'''
reconstructing missing values in the final 2 dataframe using the region as a barometer for the price index

prior trials used population and income
'''

#think about what this is doing to our 2019 values, is that a fair thing
final2= final2[(final2.ANNO>=2011) & (final2.ANNO<=2020)].sort_values(['ANNO','REGIO']).ffill()

'''
Reconstructing the variable volumi based on the coefficients gathered and the data at a provincial level
'''
final2['x_1']= np.log(final2['xx']/final2['xx'])

final2['x_2']= np.log(final2['xx']/final2['xx'])

final2['x_3']= np.log(final2['x x e xx'])

final2['y_est'] =(resr.params[0]+resr.params[1]*final2['x_1'] + constraint*final2['x_2'] + resr.params[2]*final2['x_3']) + np.log(final2['POPCR'])

#%%

'''
removing the natural log to obtain the nominal value of volumi
'''

final2['xx']= np.exp(final2['xx'])

final2['xx'] = final2['xx']*final2.Prezzi

#%%

'''
Adding the macro value of volumi to final2 so as to compare the estimated provincial values at a macro level with the observed values at the macro level
'''

comp1 = pd.DataFrame(final2.groupby(['xx','xx']).sum()['xx'])






