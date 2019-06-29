#!/usr/bin/python
import netifaces
import requests
import subprocess
from workstatus import *
import time

default_tags = {"cluster":"detection"}


def blow_alive_rule():
    start = False
    try:
        config = loadOpenCvYaml(yamlPath)
        if 'blows' in config:
            for blow in config['blows']:
                if 'device' in blow:
                    device = blow['device']
                    if device.endswith('0x0005') or device.endswith('0x0004'):
                        start = True
    except:
        pass
    return start


def blow00_alive():
    start = blow_alive_rule()
    if start:
        status00, blow00 = subprocess.getstatusoutput(
            "bash /home/work/prometheus/push-scripts/new_blow-gaojingsheng.sh blow00 60")
        blow00 = int(blow00)
        metrics = "blow00_alive"
        push_one(metrics, blow00, default_tags)


def blow01_alive():
    start = blow_alive_rule()
    if start:
        status01, blow01 = subprocess.getstatusoutput(
            "bash /home/work/prometheus/push-scripts/new_blow-gaojingsheng.sh blow01 60")
        blow01 = int(blow01)
        metrics = "blow01_alive"
        push_one(metrics, blow01, default_tags)


def usb_control():
    status1, tem1 = subprocess.getstatusoutput(
        "lsusb | grep 1a86:e010 | wc -l")
    status2, tem2 = subprocess.getstatusoutput(
        "lsusb | grep 2f4e:0002 | wc -l")
    if tem1 + tem2 == 0:
        usb_control_alive = -1
    else:
        usb_control_alive = 1  # online
    # print(usb_control_alive)
    metrics = "usb_control_alive"
    push_one(metrics, usb_control_alive, default_tags)


def jiamigou():
    status1, tem1 = subprocess.getstatusoutput("lsusb | grep 0529:0003|wc -l")
    if tem1 == 0:
        jiamigou_alive = -1
    else:
        jiamigou_alive = 1
    metrics = "jiamigou_alive"
    push_one(metrics, jiamigou_alive, default_tags)


def net_control_push():
    status1, tem1 = subprocess.getstatusoutput("ping -c 1 192.168.8.50")
    if status1 != 0:
        net_control_alive = -1
    else:
        net_control_alive = 1
    metrics = "net_control_alive"
    push_one(metrics, net_control_alive, default_tags)


def net_cotrol():
    status1, tem1 = subprocess.getstatusoutput("lsusb|grep 1a86:e010|wc -l")
    if int(tem1) > 0:
        net_control_push()


init = False


def main():
    global init
    if not init:
        time.sleep(300)
        init = True
    usb_control()
    jiamigou()
    net_cotrol()

