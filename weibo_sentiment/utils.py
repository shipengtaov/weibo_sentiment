#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging

def get_logger(name=None, level=logging.DEBUG):
    logger = logging.getLogger(name or __name__)
    logger.setLevel(level)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(
                fmt='%(asctime)s %(levelname)-8s %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(stream_handler)
    return logger

def format_weibo_time(time):
    time_format = '%a %b %d %H:%M:%S +0800 %Y'
    now = datetime.datetime.now()
    date = datetime.datetime.strptime(time, time_format)
    if date.year == now.year:
        if date.month == now.month:
            if date.day == now.day:
                res_format = '%H:%M'
            else:
                res_format = '%m-%d %H:%M'
        else:
            res_format = '%m-%d %H:%S'
    else:
        res_format = '%Y-%m-%d %H:%S'
    return date.strftime(res_format)
