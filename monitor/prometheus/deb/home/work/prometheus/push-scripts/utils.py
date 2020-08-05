import netifaces
import logging
from logging.handlers import TimedRotatingFileHandler

def getMacAddress():
    for interface in sorted(netifaces.interfaces()):
        if interface.startswith("en") or interface.startswith("eth"):
            mac = netifaces.ifaddresses(
                interface)[netifaces.AF_LINK][0]['addr']
            macStr = mac.replace(":", "-").upper()
            return macStr
    raise Exception("No mac address got")

def get_logger(loggerName):
    logfilePath = "/var/log/{}.log".format(loggerName)
    myLogger = logging.getLogger(loggerName)
    myLogger.setLevel(logging.INFO)
    prometheus_logHandler = TimedRotatingFileHandler(logfilePath, when='midnight', interval=1, backupCount=7)
    logFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    prometheus_logHandler.setFormatter(logFormatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(logFormatter)
    streamHandler.setLevel(logging.WARNING)
    myLogger.propagate = False
    myLogger.addHandler(streamHandler)
    myLogger.addHandler(prometheus_logHandler)
    return myLogger