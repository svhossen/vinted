# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 12:55:01 2020

@author: hossenbuxs
"""

import scrapy
import os
os.chdir(r'U:\lavspec\Startup\crowdfundme')
import sys

sys.path.append(r'U:\Lavspec\Startup\crowdfundme\crowdfundme')

from items import NewItem
from urllib.parse import urlparse
import pandas as pd
from scrapy.http import Request
import pandas as pd

import datetime

#%%


class crowdfundme_spider(scrapy.Spider):
    name = "crowdfundme_spider"
    
    start_urls = ['https://www.crowdfundme.it/archivio-progetti-crowdfunding/','https://www.crowdfundme.it/projects/']


    
    
    def parse(self, response):

        
        for link in [response.xpath('/html/body/section[2]/div/div[2]/div[{}]/a/@href'.format(i)).get() for i in range(200)]:
            
            yield scrapy.Request(response.urljoin(link), callback=self.parse_page)
            
            
    

    def parse_page(self, response):
        
        item = NewItem()
        #in order to use this, name must exist prior to launch the code
        
        
        item['Name'] = response.xpath('/html/body/section[1]/div/div/h1/text()').get()
        
        
        
        try:        
            item['Adesioni']= response.xpath('/html/body/section/div/div/div/div/div/div/div/dl/dd/text()').extract()[-1].strip('€').strip()
            
            
            item['Equity']= response.xpath('/html/body/section/div/div/div/div/div/div/div/dl/dd/text()').extract()[0]
            
            item['percent_raised']= response.xpath('/html/body/section/div/div/div/div/div/div/div/span/text()').extract()[0]
            
            item['valuation']= response.xpath('/html/body/section/div/div/div/div/div/div/div/dl/dd/text()').extract()[1].strip('€').strip()
                                                  
                                                        
            item['Settore']=response.xpath('/html/body/section/div/div/div/div/div/dl/dd/text()').extract()[2].strip()
            
        
            
        except:
            
        
            item['Adesioni']=  response.xpath('/html/body/section/div/div/div/div/div/div/dl/dd/text()').extract()[0].strip('€').strip()
           
    
            
            item['Settore']= response.xpath('/html/body/section/div/div/div/div/div/div/dl/dd/text()').extract()[-1].strip('€').strip()
            
    
            
            
            item['valuation']= response.xpath('/html/body/section/div/div/div/div/div/div/dl/dd/text()').extract()[2].strip('€').strip()
                                                
        
    
        pass
        
        
        item['description']=  response.xpath('/html/body/section[1]/div/div/div/p/text()').get()
        
        
        item['status']= response.xpath('/html/body/section/div/div/div/div/div/span/text()').get()
        
        item['base_url'] = response.url
        
        item['date'] = datetime.datetime.now()
        
        return item
    
#%%        

def main():
    import scrapy
    from scrapy import cmdline
    
    cmdline.execute("scrapy crawl crowdfundme_spider -o {}.csv -t csv".format('crowdfundme_03_19_20').split())  
    
    #cmdline.execute("scrapy crawl crowd_200_spider".split())  
    

        
if __name__ =="__main__":    
    main()
    
#%%

dataframe_3 = pd.read_csv(r'crowdfundme_03_19_20.csv')

dataframe_3['Adesioni'] = dataframe_3['Adesioni'].apply(lambda x: str(x).replace(".",","))

dataframe_3['valuation'] = dataframe_3['valuation'].apply(lambda x: str(x).replace(".",","))

dataframe_3.to_csv('crowdfundme_03_19_20_2.csv')
