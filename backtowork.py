# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 15:40:18 2020

@author: hossenbuxs
"""

from timeit import default_timer as timer


import scrapy
import os
os.chdir(r'U:\lavspec\Startup\backtowork')
import sys

sys.path.append(r'U:\Lavspec\Startup\backtowork\backtowork')

from items import NewItem
from urllib.parse import urlparse
import pandas as pd
from scrapy.http import Request
import pandas as pd
import datetime



#%%


class backtowork(scrapy.Spider):
    name = "backtowork"
    allowed_domains = ['www.backtowork24.com']
    start_urls = ['https://www.backtowork24.com/equity-crowdfunding?gclid=EAIaIQobChMI-6SMr9K_5wIVRIXVCh1aKAa3EAAYAiAAEgIPvfD_BwE']



    def parse(self, response):
        
        item = NewItem()
        #in order to use this, name must exist prior to launch the code
        
        
        item['Name'] = [response.xpath('//*[@id="grid-campaign"]/div/div/div[{}]/a/div/div[1]/span[5]/h4/text()'.format(i)).get() for i in range(100)]
        
        
        item['Adesioni']= [response.xpath('//*[@id="grid-campaign"]/div/div/div[{}]/a/div/div[2]/div[4]/div/div/div[1]/h4/text()'.format(i)).get() for i in range(100)]
        
        
        item['Equity']= [response.xpath('//*[@id="grid-campaign"]/div/div/div[{}]/a/div/div[2]/div[4]/div/div/div[2]/h4/text()'.format(i)).get() for i in range(100)]
        
       
        item['Settore']=[response.xpath('//*[@id="grid-campaign"]/div/div/div[{}]/a/div/div[2]/div[4]/div/div/div[3]/h4/text()'.format(i)).get() for i in range(100)]
        
        
        item['description']= [response.xpath('//*[@id="grid-campaign"]/div/div/div[{}]/a/div/div[2]/div[2]/p/text()'.format(i)).get() for i in range(100)]
        
        
        item['status']=[response.xpath('//*[@id="grid-campaign"]/div/div/div[{}]/a/div/div[2]/div[3]/div/div/p/text()'.format(i)).get() for i in range(100)]
        
        item['percent_raised'] = [response.xpath('//*[@id="grid-campaign"]/div/div/div[{}]/a/div/div[2]/div[3]/div/div/div[1]/text()'.format(i)).get() for i in range(100)]
        

        item['date'] = datetime.datetime.now()
        
        item['base_url'] = response.url        
        
        return item
    



#%%        

def main():
    import scrapy
    from scrapy import cmdline
    
    cmdline.execute("scrapy crawl backtowork -o {}.json -t json".format('backtowork_03_19_20').split())  
    
    #cmdline.execute("scrapy crawl backtowork".split())  
    

        
if __name__ =="__main__":    
    main()
    
#%%
import json
with open('backtowork_03_19_20.json', 'r') as f:
    distros_dict = json.load(f)
    
dataframe = pd.DataFrame(distros_dict[0])

dataframe.to_csv('backtowork_03_19_20.csv')


