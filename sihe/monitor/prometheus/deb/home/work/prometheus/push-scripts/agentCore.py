from workstatus import *
import cpu_mem_idle_log_daiyi
import flawckProcesses_cpuTemperature_cameraAlive_vsedion_daiyi
import gpu_alive_temperture_blow_daiyi
import new_blow_usb_jiamigou_gaojingsheng
import service_is_active_yisong
import state_frequency_entry_yisong
import camera_alive_daiyi
import prometheus_agent
import time_series_data_agent
from ForeverThread import ForeverThread

allthreads = [
    ForeverThread(target = cpu_mem_idle_log_daiyi.main, timeSleepInSeconds = 60),
    ForeverThread(target = flawckProcesses_cpuTemperature_cameraAlive_vsedion_daiyi.main, timeSleepInSeconds = 60),
    ForeverThread(target = gpu_alive_temperture_blow_daiyi.main, timeSleepInSeconds = 60),
    ForeverThread(target = new_blow_usb_jiamigou_gaojingsheng.main, timeSleepInSeconds = 60),
    ForeverThread(target = service_is_active_yisong.main, timeSleepInSeconds = 60),
    ForeverThread(target = state_frequency_entry_yisong.main, timeSleepInSeconds = 60),
    ForeverThread(target = camera_alive_daiyi.main, timeSleepInSeconds = 60),
    ForeverThread(target = prometheus_agent.uploadToPrometheus, timeSleepInSeconds = 60),
    ForeverThread(target = prometheus_agent.udpServer, timeSleepInSeconds = 60),
    ForeverThread(target=time_series_data_agent.uploadToServer, timeSleepInSeconds = 60),
    ForeverThread(target=time_series_data_agent.udpServer, timeSleepInSeconds = 60),
]


def main():
    initNanoClient(nanoAddr)
    falconWorkLogger.info('init nano, start to push metrics')
    for i in allthreads:
        i.start()


if __name__ == "__main__":
    main()
