#!/usr/bin/python3
import subprocess
import logging
from logging.handlers import TimedRotatingFileHandler
from os import system
import time
from workstatus import *

topLogFilePath = "/var/log/top.log"
topLogger = logging.getLogger("top")
topLogger.setLevel(logging.INFO)
tophandler = TimedRotatingFileHandler(
    topLogFilePath, when='W5', interval=1, backupCount=6)
topformatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
tophandler.setFormatter(topformatter)
topLogger.addHandler(tophandler)

count_alarm = 0
default_tags = {"cluster":"detection"}


def used_mem_cpu():
    sta2, used_mem = subprocess.getstatusoutput(
        "top -n 1 -b | grep 'Mem :' | awk '{print $8 / $4 * 100}'")
    mem_used = float(used_mem)
    sta3, cpu_id = subprocess.getstatusoutput(
        "top -n 1 -b | grep Cpu | awk -F' ' '{print $8}' ")
    cpu_used = 100 - float(cpu_id)
    return mem_used, cpu_used


def used_df():
    status, used_df_str = subprocess.getstatusoutput(
        "df | grep '/$' | awk '{print $3 / ($4 + $3) * 100}'")
    return float(used_df_str)


def echo_in_log(metric, threshold):
    top1_info = subprocess.Popen(
        ["top", "-o", "%MEM", "-n", "1", "-b"], stdout=subprocess.PIPE)
    top_info = subprocess.Popen(
        ["head", "-n", "30"], stdin=top1_info.stdout, stdout=subprocess.PIPE)
    out, err = top_info.communicate()
    # output info get from console has many unicode escape character ,such as \x1b(B\x1b[m\x1b[39;49m\x1b[K\n\x1b(B\x1b[m
    # use decode('unicode-escape') to process
    out_info = out.decode('unicode-escape')
    #print("log will print2")
    topLogger.info("now this {metric} is lower than the threshold{threshold}, now top_info is {top_info}".format(
        metric=metric, threshold=threshold, top_info=out_info))


def judge(valueslist, threshold):
    lookup_end = 10
    lookup_start = 8
    if len(valueslist) < lookup_end:
        alarm_is_ok = False
        return alarm_is_ok
    elif len(valueslist) == lookup_end:
        count_alarm = 0
        for value in valueslist:
            if value >= threshold:
                count_alarm = count_alarm + 1
            # print(count_alarm)
        if count_alarm >= lookup_start:
            alarm_is_ok = True
            del valueslist[0]
            return alarm_is_ok
        else:
            alarm_is_ok = False
            del valueslist[0]
            return alarm_is_ok
    else:
        init = len(valueslist) - lookup_end
        valueslist = valueslist[init:]
        alarm_is_ok = False
        return alarm_is_ok



threshold = 70
mem_metric = "mem_used"
cpu_metric = "cpu_used"
mem_used_valueslist = []
cpu_used_valueslist = []
def main():
    mem_used, cpu_used = used_mem_cpu()
    disk_used = used_df()
    push_one("mem_used", mem_used, default_tags)
    push_one("cpu_used", cpu_used, default_tags)
    push_one("disk_used", disk_used, default_tags)
    mem_used_valueslist.append(mem_used)
    cpu_used_valueslist.append(cpu_used)
    alarm_is_ok1 = judge(mem_used_valueslist, threshold)
    if alarm_is_ok1:
        print("log will print")
        echo_in_log(mem_metric, threshold)
    alarm_is_ok2 = judge(cpu_used_valueslist, threshold)
    if alarm_is_ok2:
        print("log will print")
        echo_in_log(cpu_metric, threshold)
            