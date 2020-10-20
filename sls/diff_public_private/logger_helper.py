#!/home/tops/bin/python
# -*- coding:utf-8 -*-

import logging.config
import os


def get_logger(name=None):
    conf_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             "config", "logging.conf")
    print "conf_path:: ",conf_path
    logging.config.fileConfig(conf_path)
    return logging.getLogger(name)
