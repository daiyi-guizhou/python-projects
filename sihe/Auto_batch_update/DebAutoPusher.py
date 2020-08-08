from AiClothClient import AiClothClient
from threading import Thread
import time
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import os

class DebAutoPusher(Thread):
    MAX_PUSH_TIME = 5
    VERSION_KEY_DAEMON = 'Daemon version'
    VERSION_KEY_FLAWCHECKER = 'FlawChecker version'
    VERSION_KEY_FALCON = 'Falcon version'
    VERSION_KEY_PERIPHERAL = 'Peripheral version'

    STATUS_JUST_STARTED = 'JustStarted'
    STATUS_WAITING_OTHER_COMMANDS_DONE = 'WaitingOtherCommandsDone'
    STATUS_PUSHING_DEB = 'PushingDeb'
    STATUS_EXIT_TOO_MANY_ERRORS = 'ExitTooManyErrors'
    STATUS_EXIT_SUCCESS = 'ExitSuccess'
    STATUS_EXIT_NEED_UPDATE = 'ExitNeedUpdate(DryRun mode)'

    STARTING_SERVICE = 'SendCommandToStartService'

    def __init__(self, client: AiClothClient, machineId: str,
                 check_version_key: str, target_version_value: str, deb_name: str, dry_run : bool):
        super().__init__()
        self.client = client
        self.machineId = machineId
        self.deb_name = deb_name
        self.check_version_key = check_version_key
        self.target_version_value = target_version_value
        self.displayName = client.get_display_name_from_cache(machineId)
        self.status = self.STATUS_JUST_STARTED
        self.errorCount = 0
        self.dry_run = dry_run

        os.makedirs('logs', exist_ok=True)
        self.logger = logging.getLogger('DebAutoPusher_{}.log'.format(machineId))
        self.logger.setLevel(logging.INFO)
        handler = TimedRotatingFileHandler(
            'logs/DebAutoPusher_{}.log'.format(machineId),
            when='midnight', interval=1, backupCount=7)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.propagate = False
        self.logger.addHandler(handler)

        self.logger.info('Started DebAutoPusher %s %s %s %s', machineId, check_version_key, target_version_value, deb_name)

    def is_installing_flawck(self):
        return 'flaw_checker' in self.deb_name

    def run(self):
        while True:
            self.logger.info('Current status: %s', self.status)
            time.sleep(5)
            info = self.client.get_machine_info(self.machineId)
            assert info is not None
            if self.status == self.STATUS_JUST_STARTED:
                # check version match
                current_version = info['AdditionalInfo'].get(self.check_version_key, '')
                if current_version != self.target_version_value:
                    self.logger.info('Version mismatch: %s vs %s', current_version, self.target_version_value)
                    self.status = self.STATUS_WAITING_OTHER_COMMANDS_DONE
                    continue
                else:
                    self.logger.info('Version already match, exit (%s)', current_version)
                    self.status = self.STATUS_EXIT_SUCCESS
                    return
            if self.status == self.STATUS_WAITING_OTHER_COMMANDS_DONE:
                # check pendding commands num
                if info.getPendingCommandsCount() == 0:
                    # ready to push deb
                    # for dry_run mode, just mark it needs update
                    if self.dry_run:
                        self.status = self.STATUS_EXIT_NEED_UPDATE
                        return
                    #判断flaw_ck文件
                    if self.is_installing_flawck():
                        self.last_machine_status = info['FlawCheckerStatusString']
                    result = self.client.push_deb(self.deb_name, [self.machineId]) 
                    self.push_command_id = result['success'][self.machineId]
                    self.status = self.STATUS_PUSHING_DEB
                    time.sleep(15)
                    continue
                else:
                    continue
                    
            elif self.status == self.STATUS_PUSHING_DEB:
                # check pending command's status
                if info.getPendingCommandsCount() != 0:
                    continue
                code, stdout, stderr = self.client.get_finished_command_result(self.machineId, self.push_command_id)
                if code == 0:
                    self.logger.info('Cool! Deb installed successfully, wait and retry to check version.')
                    #if self.is_installing_flawck() and self.last_machine_status == 'active':
                    if self.is_installing_flawck():
                        # we need to start the service
                        # TODO: send command to start service
                        self.client.push_shell_command("systemctl restart flawck", [self.machineId])
                        self.status = self.STARTING_SERVICE
                    time.sleep(20)
                    self.status = self.STATUS_JUST_STARTED
                    continue
                else:
                    self.client.delete_finished_command([self.machineId])
                    self.logger.warning('Deb install failed, code = %s\n stderr=%s', code, stderr)
                    self.errorCount += 1
                    self.logger.warning('errorCount = %d', self.errorCount)
                    if self.errorCount > self.MAX_PUSH_TIME or code == 100:
                        self.status = self.STATUS_EXIT_TOO_MANY_ERRORS
                        self.logger.critical('Deb install failed, code = %d\nstderr=%s', code, stderr)
                        return
                    else:
                        self.status = self.STATUS_JUST_STARTED
                        continue
            elif self.status == self.STARTING_SERVICE:
                # check serive is active
                current_service_status = info['FlawCheckerStatusString']
                if current_service_status == "active":
                    self.logger.info('Cool! Service is started.')
                    self.status = self.STATUS_JUST_STARTED
                    continue
                else:
                    self.logger.info('The service is not started yet, current status: {}'.format(current_service_status))
                    continue


if __name__ == '__main__':
    client = AiClothClient(base_url=AiClothClient.DEV_SERVER_BASE_URL, cookie_path='dev-cookie.txt')
    client.interactive_login()
    
    pushers = []
    # The deb must be uploaded to server
    #deb_name = 'detection-machine-daemon-20190403_173250-1c7c490d-0.3.9-daemon-mk3.deb'
    deb_name = 'flaw_checker-0.9.16-net-camera-MK3-0-g3429257-20190409_040915.deb'
    target_version = '0.9.16-net-camera-MK3-0-g3429257-20190409_040915.deb'
   
    #deb_name = 'flaw_checker-0.9.17-net-camera-MK3-0-g0ddc32d-20190409_084431.deb'
    #target_version = '0.9.17-net-camera-MK3-0-g0ddc32d-20190409_084431.deb'
    # deb_name = 'detection-machine-daemon-20190407_145747-f3544586-0.3.10-daemon-mk3.deb'
    # target_version = '0.3.10-daemon-mk3-20190407_145747-f3544586'
    # MK3测试机
    for machineId in ['0C-9D-92-CA-EC-8C']:
        #pusher = DebAutoPusher(client, machineId, DebAutoPusher.VERSION_KEY_DAEMON, target_version, deb_name, True)
        pusher = DebAutoPusher(client, machineId, DebAutoPusher.VERSION_KEY_FLAWCHECKER, target_version, deb_name, False)
        pusher.start()
        pushers.append(pusher)

    while True:
        time.sleep(10)
        all_pushers_done = True
        print(time.strftime('%Y-%m-%d %H:%M:%S'), '=' * 100)
        for pusher in pushers:
            if pusher.is_alive():
                all_pushers_done = False
            if pusher.status != DebAutoPusher.STATUS_EXIT_SUCCESS:
                print(pusher.displayName, pusher.status, pusher.errorCount)
        if all_pushers_done:
            break    

    for pusher in pushers:
        pusher.join()
