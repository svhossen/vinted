# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 16:06:31 2020

@author: hossenbuxs
"""

import scrapy
import os
os.chdir(r'U:\Lavspec\Startup\opstart')
import sys
import numpy as np
sys.path.append(r'U:\Lavspec\Startup\opstart\opstart')

from items import NewItem
from urllib.parse import urlparse
import pandas as pd
from scrapy.http import Request
import pandas as pd
import datetime

#%%


class opstart_spider(scrapy.Spider):
    name = "opstart_spider"
    
    start_urls = ['https://www.opstart.it/elenco-progetti/']


    
    
    def parse(self, response):

        
        for link in [response.xpath('//*[@id="content"]/div/div/div/form/div[{}]/div/div[6]/div[3]/a/@href'.format(i)).get() for i in range(200)]:
            
            yield scrapy.Request(response.urljoin(link), callback=self.parse_page)
    

    def parse_page(self, response):
    
    # def parse(self, response):
        
        item = NewItem()
        #in order to use this, name must exist prior to launch the code

        
        item['Name'] = response.xpath('//*[@id="DatiProgetto"]/div/div/h1/text()').get()
        
        item['Adesioni']= response.xpath('//*[@id="DatiProgetto"]/div/div/div/center/span[2]/text()').get()
        
        
        item['minimo']= response.xpath('//*[@id="DatiProgetto"]/div/div/div/div/div/div[2]/text()').get().strip('€').strip()
        
        item['maximo']= response.xpath('//*[@id="DatiProgetto"]/div/div/div/div[1]/div[4]/div[2]/text()').get().strip('€').strip()      
       
        
   
        item['description'] = response.xpath('//*[@id="dettaglioProgetto"]/div/div').get()
        
        
        item['status']= response.xpath('//*[@id="DatiProgetto"]/div/div/div/div[2]/center/span[2]/text()').get()
       
       
        item['collection_information']=response.xpath('//*[@id="DatiProgetto"]/div/div[6]/span/text()').extract()
       
       #tem['valuation']=  response.xpath('//*[@id="DatiProgetto"]/div/div/span/text()').extract()[16].strip('€').strip()
    
        
        item['base_url'] = response.url
        
        item['date'] = datetime.datetime.now()
        
        item['percent_raised'] = response.xpath('//*[@id="DatiProgetto"]/div/div/div/div/div/div/span/text()').get()
        
        
        
        return item
    
#%%
def main():
    import scrapy
    from scrapy import cmdline
    
    cmdline.execute("scrapy crawl opstart_spider -o {}.json -t json".format('opstart_03_19_20').split())  
    
    #cmdline.execute("scrapy crawl crowd_200_spider".split())  
    

        
if __name__ =="__main__":    
    main()
    
#%%
    
dataframe_4 = pd.read_json('opstart_03_19_20.json')

def valutazione(x):
    if "\xa0VALORE PRE MONEY DELL'AZIENDA\xa0" in x:
        print (x)
        return x[x.index("\xa0VALORE PRE MONEY DELL'AZIENDA\xa0") + 2].replace('€ ','').split(',')[0].replace('.',',')

dataframe_4['valuation'] = dataframe_4['collection_information'].apply(lambda x: valutazione(x))

dataframe_4.to_csv(r'opstart_03_19_20.csv')
    