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
    urls = "https://prometheus-exporter.sihe6.com/ai-machine-metrics"
    try:
        r = requests.post(urls, headers=headers, data=json.dumps(data))
    except Exception as e:
        return "Error:", e
