import requests
import json


def push(dmid, name, gauge):
    headers = {
        'Content-Type': 'application/json',
        'cache-control': 'no-cache'
    }
    data = {
        "DetectionMachineId": str(dmid),
        "Metrics": [{"Name": str(name),
                     "Gauge": int(gauge)
                     }]
    }
    urls = "https://prometheus.yyyy.com/metrics"
    try:
        r = requests.post(urls, headers=headers, data=json.dumps(data))
    except Exception as e:
        return "Error:", e
