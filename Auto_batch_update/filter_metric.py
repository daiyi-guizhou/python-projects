
#Readme:此脚本仅用于临时手动获取红点告警信息

import sys
from AiClothClient import AiClothClient
import time
import json
import getpass
import subprocess
from common_filters import *

lastRestartTimeMap = {}

def checkMachinesAndAlertInfo(client, alertkeywords):
    global lastRestartTimeMap

    machine_list = client.get_machine_list()
    machine_list = machine_list['machines']

    supposed_running_machine = filter(
        lambda m: m['FlawCheckerStatusString'] == 'active', machine_list)
    supposed_running_machine = filter(
        isMachineUpdateRecently, machine_list)
    print('alive machines: ',len(list(supposed_running_machine)))

    alert_list = client.get_alert_list()
    machine_alerts = {}
    for x in alert_list:
        endpoint = x['endpoint']
        if not endpoint.startswith('dm/'):
            continue
        machineId = endpoint[3:].upper()
        if machineId not in machine_alerts:
            machine_alerts[machineId] = []
        machine_alerts[machineId].append(x['metric'])

    supposed_running_machine = filter(lambda m:isMachineServiceDown(m, machine_alerts, alertkeywords), machine_list)
    supposed_running_machine = list(supposed_running_machine)
    print('alert machines: ', len(supposed_running_machine))
    machine_id_list = []
    for m in supposed_running_machine:
        machineAlias = m['aliasName']
        machineId = m['Id']
        if machineId in lastRestartTimeMap and time.time() - lastRestartTimeMap[machineId] < 300:
            print('{} is restarted in 5min, skip'.format(machineId))
            continue
        lastRestartTimeMap[machineId] = time.time()
        alertinfo = machine_alerts[machineId]
        print ("\033[1;31m AliasName: \033[0m {}, \033[1;32mMachineId: \033[0m {}, \033[1;33m AlertInfo: \033[0m {}".format(machineAlias, machineId, alertinfo) )
    #    break
    #    machine_id_list.append(machineId)
    #print('Calling restart for machines:', machine_id_list)
        
    print('done')


if __name__ == '__main__':
    client = AiClothClient()
    #client = AiClothClient(base_url=AiClothClient.DEV_SERVER_BASE_URL, cookie_path='dev-cookie.txt')
    client.interactive_login()
    #alertkeywords is camera\cpu\mem\flaw_checker\frequency
    alertkeywords = sys.argv[1]
    checkMachinesAndAlertInfo(client, alertkeywords)

