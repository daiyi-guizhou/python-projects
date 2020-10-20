#!/home/tops/bin/python
# -*- coding:utf-8 -*-

import json

from command_executor import exec_cmd
from logging_helper import get_logger

logger = get_logger()

SPECIAL_APPS = ["aysls-stg", "aysls-stg-sh", "ayots-sls-ap-southeast-2-hy-pub"]

OTS_TIANJI_CLUSTERS = [
    "AYOTS-AP-SOUTHEAST-2-HY-PUB", "AYOTS-SLS-EU-GER",
    "AYOTS-SLS-JPTOKYO-HYBRID-PUB", "AYOTS-SLS-ME-DUBAI-HYBRID-PUB"
]


def execute_activity(activity):
    try:
        logger.info("Prepare to execute activity, activity=%s" %
                    activity.__name__)
        activity()
        logger.info("Execute activity successfully, activity=%s" %
                    activity.__name__)
    except Exception as e:
        logger.exception("Failed to execute activity, activity=%s, e=%s" %
                         (activity.__name__, e))
        exit(-1)


def get_os_info(ip):
    _, stdout, _ = exec_cmd('ssh %s "uname -r"' % ip)
    return stdout


def is_alios7(ip):
    os_info = get_os_info(ip)
    if os_info.find("alios7") != -1:
        return True
    else:
        return False


def get_tianji_project_type(cluster):
    if cluster in OTS_TIANJI_CLUSTERS:
        return "OTS"
    else:
        return "SLS"


def load_json_from_file(filename):
    with open(filename, "r") as f:
        content = f.read()
        return json.loads(content)
