import socket
import json
import jsonschema
import time
import requests
from ForeverThread import ForeverThread
import sys
import re
from utils import *

# https://github.com/prometheus/client_python/blob/master/prometheus_client/metrics_core.py
METRIC_NAME_RE = re.compile(r'^[a-zA-Z_:][a-zA-Z0-9_:]*$')
METRIC_LABEL_NAME_RE = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

prometheus_send_webserverLogger = get_logger("prometheus_send_webserverLogger")
prometheus_agentLogger = get_logger("prometheus_agentLogger")

ignore_metrics = ['camera_buffer_size']

macAddress = getMacAddress()

metricsSchema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "gauge": {"type": "number"},
            "labelMap": {"type": "object"},
            "name": {"type": "string"},
            "ttlInSeconds": {"type": "number"}
        },
        "required": ["gauge", "labelMap", "name", "ttlInSeconds"]
    }
}

metricsMap = {}


def uploadToPrometheus():
    url = "https://prometheus-exporter.sihe6.com/ai-machine-metrics"

    now = time.time()
    payload = {
        "DetectionMachineId": macAddress,
        "Metrics": [m for m in metricsMap.values() if m['ttlTimestamp'] > now],
    }

    headers = {
        'Content-Type': "application/json",
    }

    response = requests.request(
        "POST", url, data=json.dumps(payload), headers=headers)
    prometheus_send_webserverLogger.info("Post to url: {}, status code: {}, metrics count: {}".format(url, response.status_code,
                                                                                             len(payload['Metrics'])))
    if response.status_code != 200:
        prometheus_send_webserverLogger.info(response.content)


def updateMetric(metric):
    metricName = metric['name']
    if not METRIC_NAME_RE.match(metricName):
        prometheus_agentLogger.warning('Invalid metric name: ' + metricName)
        return

    metricKey = metricName
    sortedItems = sorted(metric['labelMap'].items())
    for k, v in sortedItems:
        if not METRIC_LABEL_NAME_RE.match(k):
            prometheus_agentLogger.warning('Invalid label name: ' + k)
            return

        metricKey += ",{}={}".format(k, v)
        metric['labelMap'][k] = str(v)

    if metric['ttlInSeconds'] < 0:
        metric['ttlInSeconds'] = 1e9

    metric['ttlTimestamp'] = time.time() + metric['ttlInSeconds']
    metricsMap[metricKey] = metric


def udpServer():
    prometheus_agentLogger.warning('Init server...')

    host = '127.0.0.1'
    port = 31234

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    prometheus_agentLogger.warning("Listening on udp %s:%s" % (host, port))
    s.bind((host, port))

    while True:
        (rawData, _) = s.recvfrom(1 << 10)  # 1 K
        try:
            metrics = json.loads(rawData)
            if len(metrics) > 0:
                name = metrics[0]['name']
                if name not in ignore_metrics:
                    prometheus_agentLogger.info(
                        'Received metrics: {0}'.format(metrics))
                jsonschema.validate(metrics, metricsSchema)
        except Exception as e:
            prometheus_agentLogger.warning(
                "Can not parse to json: {}, err: {}".format(rawData, e))
            continue

        for metric in metrics:
            updateMetric(metric)


if __name__ == '__main__':
    allThreads = [
        ForeverThread(target=uploadToPrometheus),
        ForeverThread(target=udpServer),
    ]

    for thread in allThreads:
        thread.start()

    # Test in `bash`, not `zsh`
    # echo '[{"labelMap":{"c":"d", "a": "b"},"gauge":0,"name":"string","ttlInSeconds":90}]' > /dev/udp/127.0.0.1/31234
