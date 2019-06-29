from AiClothClient import AiClothClient
import time
import json
import getpass
from common_filters import *

lastRestartTimeMap = {}

def checkMachinesAndRestart(client):
    global lastRestartTimeMap

    machine_list = client.get_machine_list()
    machine_list = machine_list['machines']

    # supposed_running_machine = filter(
    #     lambda m: m['FlawCheckerStatusString'] == 'active', machine_list)
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

    supposed_running_machine = filter(
        lambda m:isMachineServiceDown(m, machine_alerts,'memfree'), machine_list)
    supposed_running_machine = list(supposed_running_machine)
    print("mem ",len(supposed_running_machine))
    supposed_running_machine = filter(
        lambda m: isMachineNotHaveTagPrefix(m, '摄:18'), supposed_running_machine)

    
    supposed_running_machine = list(supposed_running_machine)
    print('alert machines: ', len(supposed_running_machine))

    machine_id_list = []
    for m in supposed_running_machine:
        machineId = m['Id']
        if machineId in lastRestartTimeMap and time.time() - lastRestartTimeMap[machineId] < 300:
            print('{} is restarted in 5min, skip'.format(machineId))
            continue
        lastRestartTimeMap[machineId] = time.time()
        machine_id_list.append(machineId)
    print('Calling restart for machines:', machine_id_list)
    if len(machine_id_list) > 0:
        # pass
        client.push_shell_command('systemctl restart flawck', machine_id_list)
        
    print('done')


if __name__ == '__main__':
    # client = AiClothClient(base_url='http://localhost:8081')
    client = AiClothClient()
    client.interactive_login()

    while True:
        checkMachinesAndRestart(client)
        time.sleep(10)