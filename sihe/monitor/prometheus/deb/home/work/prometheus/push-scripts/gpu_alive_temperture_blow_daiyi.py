import netifaces
import requests
import subprocess
from workstatus import *
import logging
from logging.handlers import TimedRotatingFileHandler
from os import system
import os
import time

gpuRebootLogFilePath = "/var/log/gpuReboot.log"
gpuRebootLogger = logging.getLogger("gpuReboot")
gpuRebootLogger.setLevel(logging.INFO)
gpuReboothandler = TimedRotatingFileHandler(
    gpuRebootLogFilePath, when='W5', interval=1, backupCount=6)
gpuRebootformatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s')
gpuReboothandler.setFormatter(gpuRebootformatter)
gpuRebootLogger.addHandler(gpuReboothandler)

default_tags = {"cluster":"detection"}


alarm_count = 0
sucess_count = 0


# 2019.3.14  wo use "timeout 1 nvidia-smi",  give up "gpu_reboot",by He Yuxuan.   2019.3.29  start to reboot by He Yuxuan.
def gpu_reboot(tem1, ts):
    global alarm_count
    global sucess_count
    if tem1 < 10:
        alarm_count += 1
        sucess_count = 0
    else:
        alarm_count = 0
        sucess_count += 1
    if alarm_count >= 3:
        if os.path.exists('/var/log/gpuReboot.log'):
            try:
                status_alarm, last_alarm = subprocess.getstatusoutput(
                    "grep 'is not alive' /var/log/gpuReboot.log | tail -n 1 | awk -F'at' '{print $2}'")
            except Exception as e:
                gpuRebootLogger.error(str(e))
        else:
            last_alarm = ""
        if last_alarm == "":
            last_alarm = "0"
            last_reboot_time = int(last_alarm)
        else:
            last_reboot_time = int(last_alarm)
        next_reboot_time_threshold = last_reboot_time + 1800
        if ts >= next_reboot_time_threshold:
            try:
                gpuRebootLogger.info(
                    "gpu is not alive,auto reboot at {}".format(ts))
                print("it is time to reboot")
                system('reboot')
            except Exception as e:
                gpuRebootLogger.error(str(e))
        else:
            print("it is not time to reboot")


def gpu_start_rule():
    start = False
    try:
        config = loadOpenCvYaml(yamlPath)
        if 'useRemoteTfServer' in config:
            if config['useRemoteTfServer'] == 1:
                start = True
    except:
        pass
    return start


def gpu_alive():
    start = gpu_start_rule()
    if start:
        status1, tem1 = subprocess.getstatusoutput(
            "bash /home/work/prometheus/push-scripts/detect-gpu-alive.sh")
        tem1 = int(tem1)
        metrics = "gpu_alive"
        push_one(metrics, tem1, default_tags)
        ts = getTimeStamp()  # 2019.3.14  wo use "timeout 1 nvidia-smi", give up "gpu_reboot",by He Yuxuan.  2019.3.29  start to reboot by He Yuxuan
        gpu_reboot(tem1, ts)


def gpu_temperture():
    start = gpu_start_rule()
    if start:
        status, tem = subprocess.getstatusoutput(
            "timeout 30 nvidia-smi -q | grep 'GPU Current Temp' | cut -d' ' -f 24")
        tem = int(tem)
        metrics = "gpu_temperature"
        push_one(metrics, tem, default_tags)


def blow_start_rule():
    start = False
    try:
        config = loadOpenCvYaml(yamlPath)
        if 'blows' in config:
            for blow in config['blows']:
                if 'device' in blow:
                    device = blow['device']
                    if device.endswith('0x0006'):
                        start = True
    except:
        pass
    return start


def pushBlowStatus():
    blowData = getBlowStatus()
    payload_list = []
    for record in blowData:
        t = getTimeStamp()
        blowtag = default_tags.copy()
        blowtag['blow'] = record['blow']
        if record['checkFrames']:
            push_one(metrics='blow_checkFrames',
                     values=record['checkFrames'], tag=blowtag)
        for oneChannel in record['channel_data']:
            channeltag = blowtag.copy()
            channeltag['channel'] = oneChannel['channel']
            push_one(metrics='blow_avg',
                     values=oneChannel['avg'], tag=channeltag)
            push_one(metrics='blow_std',
                     values=oneChannel['std'], tag=channeltag)
            push_one(metrics='blow_doubt',
                     values=oneChannel['doubt'], tag=channeltag)


def blow_status():
    start = blow_start_rule()
    if start:
        falconWorkLogger.info('start push blow status msg')
        pushBlowStatus()


init = False


def main():
    global init
    if not init:
        time.sleep(300)
        init = True
    gpu_alive()
    gpu_temperture()