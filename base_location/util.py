#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2014-7-23

@author: chen
'''
import datetime

class LogUtil(object):
    @classmethod
    def get_time_now(cls):
        return '\n' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " [CUSTOM INFO]"
                        
