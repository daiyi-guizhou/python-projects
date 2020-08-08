import requests
import os
from workstatus import *

default_tags = {"cluster":"detection"}

pushInterval = 60
printPostResult = True
checkList = {
    "blowDeviceController": True,
    "blowStatusUploader": True,
    "buttonMonitor": True,
    "checkConfigUpdate": True,
    "daemon": True,
    "jupyterTitle": True,
    "oss_uploader": True,
    "pingCheck": True,
    "reportRawImageCheckResult": True,
    "snapshotUpload": True,
    "wifi_reconnecting_ifconfig": True,
    "wifi_reconnecting": True
}


def pushServiceState():
    payload = []
    t = getTimeStamp()
    for service, check in checkList.items():
        if not check:
            continue
        cmd = 'systemctl is-active {0}.service'.format(service)
        result = os.popen(cmd).readlines()[0].strip()
        if result == 'active':
            v = 1
        else:
            v = 0
        serviceTag = default_tags.copy()
        serviceTag['name'] = service
        push_one(metrics='service_is_active', values=v,
                 tag=serviceTag)


def pushForCameraInterfram():
    camera_interfram = getCameraInterFrame()
    payload_list = []
    for record in camera_interfram:
        t = getTimeStamp()
        cameratag = default_tags.copy()
        cameratag['cameraid'] = record['camera']
        if record['last_update_interval']:
            push_one(metrics='camera_last_update_interval',
                     values=record['last_update_interval'], tag=cameratag)


def main():
    pushServiceState()
    pushForCameraInterfram()
