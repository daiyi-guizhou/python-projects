import time
import nnpy
import socket
import json
import traceback
import logging
import yaml
import netifaces
import requests
import subprocess
import copy
from logging.handlers import TimedRotatingFileHandler

falconWorkLogFilePath = "/var/log/falconWork.log"
falconWorkLogger = logging.getLogger("falconWork")
falconWorkLogger.setLevel(logging.INFO)
falconWorkhandler = TimedRotatingFileHandler(
    falconWorkLogFilePath, when='midnight', interval=1, backupCount=14)
falconWorkformatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s')
falconWorkhandler.setFormatter(falconWorkformatter)
falconWorkLogger.addHandler(falconWorkhandler)

nanoAddr = "tcp://0.0.0.0:5554"
lastUpdateTime = 0
yamlPath = ""





def push_one(metrics, values, tag):
    # for integrate prometheus agent
    promethus_tag = copy.copy(tag)
    del promethus_tag['cluster']
    promethusMetric = [{
        "name":  metrics,
        "labelMap": promethus_tag,
        "gauge": values,
        "ttlInSeconds": 90,
    }]
    try:
        udpMessage = bytes(json.dumps(promethusMetric), "utf-8")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        sock.sendto(udpMessage, ("127.0.0.1", 31234))
        falconWorkLogger.info(
            "push {} {} to promethus".format(metrics, r.text))
    except Exception as e:
        falconWorkLogger.error(str(e))
        falconWorkLogger.error(traceback.format_exc())
        falconWorkLogger.warning(
            'push {} to promethus fail, retry'.format(metrics))


def tryIt(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            falconWorkLogger.error(e)
            falconWorkLogger.error(traceback.format_exc())
            return None

    return wrapper


class NanomsgClient:
    def __init__(self, addr):
        self.socket = nnpy.Socket(nnpy.AF_SP, nnpy.REQ)
        self.socket.connect(addr)
        self.socket.setsockopt(nnpy.SOL_SOCKET, nnpy.SNDTIMEO, 1000)
        self.socket.setsockopt(nnpy.SOL_SOCKET, nnpy.RCVTIMEO, 1000)

    def query(self, request):
        self.socket.send(request)
        reply = json.loads(self.socket.recv())
        return reply


def initNanoClient(addr):
    global nanomsgClient
    nanomsgClient = NanomsgClient(addr)


# return unix timestamp with 'second' precision
def getTimeStamp():
    millis = round(time.time())
    return millis


def getStateHistory():
    request = {"type": "state_history"}
    r = json.dumps(request)
    try:
        result = nanomsgClient.query(r)
        return result["state_history"]
    except:
        return [{'state': -1, 'entrytime': int(time.time() * 1000)}]


# This method will get new state history since the last time it was called.
# new or not is judged by lastUpdateTime
def getUpdatedStateHistory():
    global lastUpdateTime
    new_record = []
    current_request_result = getStateHistory()
    if len(current_request_result) > 0:
        if current_request_result[0]["entrytime"] > lastUpdateTime:
            for single_record in current_request_result:
                if single_record["entrytime"] > lastUpdateTime:
                    new_record.append(single_record)
            lastUpdateTime = current_request_result[0]["entrytime"]
    return new_record


# This method will get two value of several cameras
def getCameraInterFrame():
    request = {"type": "camera_interframe"}
    r = json.dumps(request)
    try:
        result = nanomsgClient.query(r)
        return result["camera_interframe"]
    except:
        return []


def getBlowStatus():
    request = {"type": "blow_alarm_data"}
    r = json.dumps(request)
    try:
        result = nanomsgClient.query(r)
        return result["blow_alarm_data"]
    except:
        return []




def loadOpenCvYaml(filename):
    skip_lines = 2
    with open(filename) as infile:
        for i in range(skip_lines):
            _ = infile.readline()
        fileStr = infile.read()
        fileStr = fileStr.replace('!!opencv-matrix', '')
        data = yaml.load(fileStr)
    return data


def getBlowDevice():
    try:
        config = loadOpenCvYaml(yamlPath)
        if 'blows' in config:
            for blow in config['blows']:
                if 'device' in blow:
                    device = blow['device']
                    if device.endswith('0x0006'):
                        return 6
                    elif device.endswith('0x0005'):
                        return 5
                    elif device.endswith('0x0004'):
                        return 4
    except:
        pass
    return 0


if __name__ == '__main__':
    initNanoClient(nanoAddr)
    # print('--NewHistory--')
    # print(getUpdatedStateHistory())
    # print('--CameraHistory--')
    # print(getCameraInterFrame())
    # print()
    print('--Blow Data--')
    print(getBlowStatus())
