# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi
import MySQLdb.cursors
from util import LogUtil
import traceback
import logging

class BaseLocationPipeline(object):
    def process_item(self, item, spider):
        return item
    
class MySQLPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
                host = settings['MYSQL_HOST'],
                db = settings['MYSQL_LOC_DBNAME'],
                user = settings['MYSQL_USER'],
                passwd = settings['MYSQL_PASSWD'],
                charset = 'utf8',
                cursorclass = MySQLdb.cursors.DictCursor,
                use_unicode = True,
            )

        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):
        d = self.dbpool.runInteraction(self._do_insert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        d.addBoth(lambda _: item)
        return d
    
    def _do_insert(self, conn, item, spider):
        try:
            conn.execute("select * from base_location where lac=%s and cid=%s", (item['lac'], item['cid']))
            ret = conn.fetchone()
            
            if ret:
                logging.info(LogUtil.get_time_now() + "do db update, item ==>" + str(item))
                conn.execute("update base_location set errcode=%s, lat=%s, lon=%s, address=%s, type=%s, update_time=now() where lac=%s and cid=%s", 
                        (item['errcode'], item['lat'], item['lon'], item['address'], self._get_base_type(item['lac'], item['cid']), item['lac'], item['cid']))
            else:
                logging.info(LogUtil.get_time_now() + "do db insert, item ==>" + str(item))
                conn.execute("insert into base_location (errcode, lac, cid, lat, lon, address, type, update_time) values (%s, %s, %s, %s, %s, %s, %s, now())",
                    (item['errcode'], item['lac'], item['cid'], item['lat'], item['lon'], item['address'], self._get_base_type(item['lac'], item['cid'])))
        except:
            logging.info(LogUtil.get_time_now() + traceback.format_exc())
            
    def _handle_error(self, failure, item, spider):
        logging.info(LogUtil.get_time_now(), "Error ==>" + failure)
        
    def _get_base_type(self, lac, cid):
        #LAC(TAC)>=40960 -> 3G基站
        #LAC(TAC)<40960 并且 CELLID(ECI) > 65535 -> 4G基站
        #LAC(TAC)<40960 并且 CELLID(ECI) <= 65535 -> 2G基站
        if lac >= 40960:
            return "3G"
        elif lac < 40960:
            if cid > 65535:
                return "4G"
            elif cid <= 65535:
                return "2G"
        return "-"
