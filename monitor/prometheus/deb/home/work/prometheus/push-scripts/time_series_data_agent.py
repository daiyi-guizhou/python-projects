import math
import socket
import json
import jsonschema
import time
import requests
from ForeverThread import ForeverThread
import netifaces
import sys
import datetime
from collections import deque
from utils import *

ts_agent_send_logger = get_logger("ts_agent_send_logger")
ts_agent_logger = get_logger("ts_agent_logger")

macAddress = getMacAddress()

metricsSchema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "floatValues": {"type": "object"},
            "labelMap": {"type": "object"},
            "name": {"type": "string"},
        },
        "required": ["floatValues", "labelMap", "name"]
    }
}

dataPointList = deque()

def formatTimeToMsInt64(t):
    return int("{:%Y%m%d%H%M%S%f}".format(t)[:-3])

def convertToApiData(m):
    return {
        'name': m['name'],
        'labelMap': m['labelMap'],
        'floatValues': m['floatValues'],
        'millisecondsInInt64': formatTimeToMsInt64(m['timestamp']),
    }


def sendPoints(batchCount):
    if len(dataPointList) == 0:
        return
    url = "https://prometheus-exporter.sihe6.com/ai-machine/time-series/float-data"

    batchCount = min(len(dataPointList), batchCount)

    dataToUpload = []
    for idx in range(batchCount):
        dataToUpload.append(convertToApiData(dataPointList[idx]))

    payload = {
        "detectionMachineId": macAddress,
        "floatDataList": dataToUpload,
    }

    headers = {'Content-Type': "application/json"}

    response = requests.request(
        "PUT", url, data=json.dumps(payload), headers=headers)
    ts_agent_send_logger.info("Request to url: {}, status code: {}, metrics count: {}".format(url, response.status_code, batchCount))

    if response.status_code != 200:
        ts_agent_send_logger.warning(response.content)
    for _ in range(batchCount):
        dataPointList.popleft()


def uploadToServer():
    batchSize = 100
    while True:
        sendPoints(batchSize)
        if len(dataPointList) < batchSize:
            # Send next time
            break


def udpServer():
    ts_agent_logger.warning('Init server...')

    host = '127.0.0.1'
    port = 31236

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    ts_agent_logger.warning("Listening on udp %s:%s" % (host, port))
    s.bind((host, port))

    while True:
        (rawData, _) = s.recvfrom(1 << 10)  # 1 K
        now = datetime.datetime.now()
        try:
            metrics = json.loads(rawData)
            if len(metrics) > 0:
                ts_agent_logger.info('Received metrics: {0}'.format(metrics))
                jsonschema.validate(metrics, metricsSchema)
        except Exception as e:
            ts_agent_logger.warning(
                "Can not parse to json: {}, err: {}".format(rawData, e))
            continue

        for metric in metrics:
            metric['timestamp'] = now
            dataPointList.append(metric)


if __name__ == '__main__':
    allThreads = [
        ForeverThread(target=uploadToServer),
        ForeverThread(target=udpServer),
    ]

    for thread in allThreads:
        thread.start()

    # Test in `bash`, not `zsh`
    # echo '[{"labelMap":{},"floatValues":{"status":2},"name":"machine_status"}]' > /dev/udp/127.0.0.1/31236
