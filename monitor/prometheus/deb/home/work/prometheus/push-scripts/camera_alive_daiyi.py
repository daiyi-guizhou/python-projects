import netifaces
import requests
import subprocess
from workstatus import *
import re
import socket
import json

default_tags = {"cluster":"detection"}


def get_camera_ip_id():
    status, tem = subprocess.getstatusoutput(
        "awk '/rtsp:/{print a;print}{a= $0}' /opt/flaw_checker/config.yaml")
    # print(tem)
    camera_id = re.findall(r'camera\d+.*', tem)
    camera_ip = re.findall(r'\d+.\d+.\d+.\d+', tem)
    # print(camera_id,camera_ip)
    dict_ip_id = {}
    for i in range(0, len(camera_id)):
        dict_ip_id[camera_ip[i]] = int(re.search(r'\d+', camera_id[i]).group())
    # print(dict_ip_id)
    return(dict_ip_id)


def camera_alive_check():
    dict_ip_id = get_camera_ip_id()
    for i in dict_ip_id.keys():
        ip = str(i)
        ping_cmd = "bash /home/work/prometheus/push-scripts/ping_check.sh "
        ping_cmd = ping_cmd + ip
        # print(ping_cmd)
        state, out = subprocess.getstatusoutput(ping_cmd)
        out = int(out)
        # print(state,out)
        # print(out,dict_ip_id[i])
        tags = default_tags.copy()
        tags['cameraid'] = dict_ip_id[i]
        metrics = "camera_alive"
        push_one(metrics, out, tags)


def main():
    camera_alive_check()

