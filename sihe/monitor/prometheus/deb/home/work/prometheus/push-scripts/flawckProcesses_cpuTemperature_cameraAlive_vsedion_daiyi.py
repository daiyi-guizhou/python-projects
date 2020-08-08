import netifaces
import requests
import subprocess
from workstatus import *
import re
import os

default_tags = {"cluster":"detection"}


def tf_server_start_rule():
    start = False
    try:
        config = loadOpenCvYaml(yamlPath)
        if 'useRemoteTfServer' in config:
            if config['useRemoteTfServer'] == 1:
                start = True
    except:
        pass
    return start


def flaw_checker():
    status, tem = subprocess.getstatusoutput(
        "ps -ef | grep -e 'flaw_checker\/flaw_checker' | grep -v color=auto | wc -l")
    tem = int(tem)
    metric_value = 'flaw_checker'
    push_one(metric_value, tem, default_tags)


def tf_server():
    start = tf_server_start_rule()
    if start:
        status, tem = subprocess.getstatusoutput(
            "ps -ef | grep -e 'tf_server.*graph=\/opt\/flaw_checker\/tensorflow\/' | grep -v color=auto | wc -l")
        tem = int(tem)
        metric_value = 'tf_server'
        push_one(metric_value, tem, default_tags)


def camera_process():
    status, tem = subprocess.getstatusoutput(
        "ps -ef | grep -e 'camera_process.*\-\-camera_id' | grep -v color=auto | wc -l")
    tem = int(tem)
    metric_value = 'camera_process'
    push_one(metric_value, tem, default_tags)


def get_cpu_temperature():
    status, tem = subprocess.getstatusoutput(
        "bash /home/work/prometheus/push-scripts/cpu-tem.sh")
    if tem:
        core_id = -1
        tems = re.split(' ', tem)
        for tem in tems:
            if core_id == -1:
                tag = "package_id_0"
            else:
                tag = "core_"+str(core_id)
            tags = default_tags.copy()
            tags['cpuid'] = tag
            temm = int(tem)
            metrics = "cpu_temperature"
            push_one(metrics, temm, tags)
            core_id = core_id + 1


def daemon_version_num():
    if os.path.exists('/opt/detection-machine-daemon/version.txt'):
        with open("/opt/detection-machine-daemon/version.txt", "r") as env:
            date_about_version = "0.0.0"
            for line in env:
                if '-daemon' in line:
                    date_about_version = line.replace("-daemon", "").strip()
    else:
        date_about_version = "0.0.0"
    num = re.compile(r"\d+")
    version = num.findall(date_about_version)
    version_num = int(version[0])*100 + int(version[1])*10 + int(version[2])
    return(version_num)


def falcon_version_num():
    if os.path.exists('/home/work/version.txt'):
        with open("/home/work/version.txt", "r") as env:
            date_about_version = "000.0.0"
            for line in env:
                if 'date' in line:
                    date_about_version = line.replace("date: ", "").strip()
    else:
        date_about_version = "000.0.0"
    num = re.compile(r"\d+")
    version = num.findall(date_about_version)
    version_num = int(version[0][1:])
    return(version_num)


def falcon_version():
    tem1 = falcon_version_num()
    # tem1=int(tem1)
    metrics = "falcon_version"
    push_one(metrics, tem1, default_tags)


def daemon_version():
    tem1 = daemon_version_num()
#   tem1=int(tem1)
    metrics = "daemon_version"
    push_one(metrics, tem1, default_tags)


def flawck_version():
    metrics = "flawck_version"
    status1, tem1 = subprocess.getstatusoutput(
        "cat /opt/flaw_checker/version.txt | tail -1 | awk -F'_' '{ print $1 }'")
    tem1 = tem1[2:]
    tem1 = int(tem1)
    push_one(metrics, tem1, default_tags)


def main():
    flaw_checker()
    tf_server()
    camera_process()
    get_cpu_temperature()

