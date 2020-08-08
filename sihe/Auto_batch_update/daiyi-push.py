
import re
import sys
from AiClothClient import AiClothClient, MachineInfo
import time
import json
import getpass
from common_filters import *
from DebAutoPusher import DebAutoPusher
import argparse

def loginVerification(env):
    if env == 'prod':
        print('Using prod server!')
        client = AiClothClient()
    else:
        print('Using dev server!')
        client = AiClothClient(base_url=AiClothClient.DEV_SERVER_BASE_URL, cookie_path='dev-cookie.txt')
    client.interactive_login()
    machine_list = client.get_machine_list()
    target_machines = machine_list['machines']
    return client, target_machines

def main():
    parser = argparse.ArgumentParser(prog='auto_push_deb.py')
    parser.add_argument('--dry-run', action='store_true',
                        help='only list machines, but don not push')
    parser.add_argument('--deb', required=True, help='deb name on ai-cloth')
    parser.add_argument('--env', required=True, help='execution environment')
    parser.add_argument('--tag', help='contain test-{tag} machines')
    args = parser.parse_args()
    deb_name = args.deb
    test_tag = args.tag


    client, target_machines = loginVerification(args.env)
    # 5分钟内在线的机器
    target_machines = list(filter(isMachineUpdateRecently, target_machines))
    print('m0: ', len(target_machines))
 
    reg = re.search(r'(.*)\-test-(.*)\.deb', deb_name)
    assert(reg)
    head, mk_num = reg.group(1), reg.group(2)

    pushers = pusherDeb(client, target_machines, deb_name, head, args.dry_run, test_tag)   ### head , 
    waitPushersDone(pushers)

def pusherDeb(client, target_machines, deb_name, deb_head, dry_run, test_tag):
    tag_config = {
        'flaw_checker': 'test-flawck',
        'detection-machine-daemon': 'test-daemon',
        'falcon_agent': 'test-falcon',
        'peripheral-daemon': 'test-peripheral',
    }
    version_key_config = {
        'flaw_checker': DebAutoPusher.VERSION_KEY_FLAWCHECKER,
        'detection-machine-daemon': DebAutoPusher.VERSION_KEY_DAEMON,
        'falcon_agent': DebAutoPusher.VERSION_KEY_FALCON,
        'peripheral-daemon': DebAutoPusher.VERSION_KEY_PERIPHERAL,
    }

    if test_tag:  ### 筛选含有tag的机器.
        test_tag_prefix = str(test_tag)
        target_machines = list(filter(lambda m: isMachineHaveTagPrefix(m, test_tag_prefix), target_machines))
        target_machines = filterDeb(deb_name, target_machines)

    for m in target_machines:
        m = MachineInfo(m)
        print(m.getDisplayName(), ' '.join(m.getTags()))
    print(f'Num machines: {len(target_machines)}. Auto pushing started in 5 seconds...')
    time.sleep(5)

     for m in target_machines:
        m = MachineInfo(m)
        machineId = m.getMachineId()
        pusher = DebAutoPusher(
            client, machineId, version_key_config[deb_head], target_version, deb_name, dry_run)    ####
        pusher.start()
        pushers.append(pusher)
    return pushers


class DebAutoPusher(Thread):
    MAX_PUSH_TIME = 5

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

        self.logger.info('Started DebAutoPusher %s %s', machineId, deb_name)

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

