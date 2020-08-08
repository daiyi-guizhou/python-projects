import time

def isMachineUpdateRecently(machineInfo):
    a = machineInfo['LastUpdate']
    a = a .replace('T', " ")[0:19]
    lastUpdate = time.mktime(time.strptime(a, '%Y-%m-%d %H:%M:%S'))
    return time.time() - lastUpdate < 300 #5min

def isMachineTfServerDown(machineInfo, machine_alerts):
    if machineInfo['Id'] not in machine_alerts:
        return False
    for alert in machine_alerts[machineInfo['Id']]:
        if alert.find('tf_server') > -1:
            return True
    return False

def isMachineNotHaveTagPrefix(machineInfo, tagPrefix):
    tagPrefix = tagPrefix.lower()
    for tag in machineInfo['Tags']:
        tag = tag.lower()
        if tag.startswith(tagPrefix):
            return False
    return True

def isMachineHaveTagPrefix(machineInfo, tagPrefix):
    tagPrefix = tagPrefix.lower()
    for tag in machineInfo['Tags']:
        tag = tag.lower()
        if tag.startswith(tagPrefix):
            return True
    return False

def isMachineContainsAtLeastOneTag(machineInfo, targetTags : list):
    targetTags = set([t.lower() for t in targetTags])
    for tag in machineInfo['Tags']:
        tag = tag.lower()
        if tag in targetTags:
            return True
    return False

#Specify the keyword for the alert
def isMachineServiceDown(machineInfo, machine_alerts, alertkeywords):
    if machineInfo['Id'] not in machine_alerts:
        return False
    for alert in machine_alerts[machineInfo['Id']]:
        if alert.find(alertkeywords) > -1:
            return True
    return False

