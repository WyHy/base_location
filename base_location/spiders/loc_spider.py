# -*- coding: utf-8 -*- 
import sys
sys.path.append("..")

import scrapy
import json
import re
from scrapy.http import Request
from base_location.items import BaseLocationItem
from base_location.util import LogUtil
import logging
        
class Spider_loc(scrapy.Spider):
    name = "cellocation"
    allowed_domains = ["cellocation.com"]
    handle_httpstatus_list = [404, 403, 503, 504, 10060, 10061]
    start_urls = [
            "http://api.cellocation.com/cell/",
        ]

    def parse(self, response):
        data = open("lac.txt").readlines()
        logging.info("DATE LENGTH ==> " + str(len(data)))
        for item in data[:10]:
            (lac, cid) = re.findall(r'(\w*[0-9]+)\w*', item)
            url = "http://api.cellocation.com/cell/?mcc=460&mnc=1&lac=%s&ci=%s&output=json" % (lac, cid)
            logging.info(LogUtil.get_time_now() + url)
            yield Request(url=url, callback=self.parse_item, meta={"lac":lac, "cid":cid}) 
        
    def parse_item(self, response):
        print response.body
        if response.status == 200:
            lac = response.meta['lac']
            cid = response.meta['cid']
            data = response.body
            data = json.loads(data)
            item = BaseLocationItem()
            
            #errcode
            #0: 成功
            #10000: 参数错误
            #10001: 无查询结果
            
            item['errcode'] = data['errcode']
            item['lac'] = lac
            item['cid'] = cid
             
            if data['errcode'] == 0:
                item['lat'] = data['lat']
                item['lon'] = data['lon']
                item['address'] = data['address']
            else:
                item['lat'] = 0
                item['lon'] = 0
                item['address'] = None
                
            print item
                 
            yield item
        
if __name__ == '__main__':
    data = open("lac.txt").readlines()
    for item in data[19280:20000]:
        (lac, cid) = re.findall(r'(\w*[0-9]+)\w*', item)
        print lac, cid