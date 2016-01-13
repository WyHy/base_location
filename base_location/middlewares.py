# -*- coding: utf-8 -*-
import random
import mysql.connector
import settings
import traceback
from util import LogUtil
import logging

class RandomUserAgent(object):
    """Randomly rotate user agents based on a list of predefined ones"""
    def __init__(self, agents):
        self.agents = agents
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist('USER_AGENTS'))
    
    def process_request(self, request, spider):
        #print "**************************" + random.choice(self.agents)
        request.headers.setdefault('User-Agent', random.choice(self.agents))

class ProxyMiddleware(object):
    def process_request(self, request, spider):
        print request.meta
        if settings.PROXY:
            if request.meta.has_key('tried'):
                request.meta['tried'] = int(request.meta['tried']) + 1
            else:
                proxy = random.choice(settings.PROXY)
                request.meta['proxy'] = "%s://%s:%s" % (proxy['protocol'], proxy['ip'], proxy['port'])
                request.meta['ip'] = proxy['ip']
                request.meta['port'] = proxy['port']
                request.meta['tried'] = 1

            logging.info(LogUtil.get_time_now() + "use ip: %s proxy: %s, try for %s times" % (request.url, request.meta['proxy'], request.meta['tried']))
        else:
            logging.info('NO PROXY')
    def process_response(self, request, response, spider):
        return response
    
    # 当请求失败并重试后会调用此方法    
    def process_exception(self, request, exception, spider):
        if request.meta.has_key('lac'):
            lac = request.meta['lac']
            cid = request.meta['cid']
            request.meta.clear()
            request.meta['lac'] = lac
            request.meta['cid'] = cid
        else:
            request.meta.clear()
            
#         if request.meta.has_key('ip'):
#             self.disable_ip(request.meta['ip'], request.meta['port'])
        return request
        
    def disable_ip(self, ip, port):
        conn = mysql.connector.connect(host=settings.MYSQL_HOST, user=settings.MYSQL_USER, password=settings.MYSQL_PASSWD, db=settings.MYSQL_PROXY_DBNAME)
        cursor = conn.cursor()
        sqlStr = "update ip_proxy_info i set i.isvalid=0 where i.ip='%s' and i.port='%s'" % (ip, port)
        
        try:
            cursor.execute(sqlStr)    
            logging.info(LogUtil.get_time_now() + 'Disableing ip proxy %s' % ip)
        except:
            print LogUtil.get_time_now(), traceback.print_exc()
            
        conn.commit()
        cursor.close()
        conn.close()