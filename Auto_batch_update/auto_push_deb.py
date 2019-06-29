import re
import sys
from AiClothClient import AiClothClient, MachineInfo
import time
import json
import getpass
from common_filters import *
from DebAutoPusher import DebAutoPusher
import argparse



def containMk3(target_machines):
    print('m1: ', len(target_machines))
    mk3_target_machines = list(filter(lambda m: isMachineContainsAtLeastOneTag(
        m, ['MK3', 'MK3镜像']), target_machines))
    print('m2: ', len(target_machines))
    return mk3_target_machines


def notContainMk3(target_machines):
    print('m1: ', len(target_machines))
    no_mk3_target_machines = list(
        filter(lambda m: isMachineNotHaveTagPrefix(m, 'MK3'), target_machines))
    print('m2: ', len(target_machines))
    return no_mk3_target_machines


def filterDeb(deb_name, target_machines):
    deb_name = deb_name.lower()
    if "falcon_agent" not in deb_name:
        if "mk3" in deb_name:
            target_machines = containMk3(target_machines)
            return target_machines
        else:
            target_machines = notContainMk3(target_machines)
            return target_machines
    else:
        # don't distinguish mk2/mk3
        return target_machines






def pusherDeb(client, target_machines, target_version, deb_name, deb_head, dry_run, test_tag):
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

    if test_tag:
        test_tag_prefix = str(test_tag)
        pushers = []
        target_machines = list(filter(lambda m: isMachineHaveTagPrefix(m, test_tag_prefix), target_machines))
        target_machines = filterDeb(deb_name, target_machines)
    else:
        test_tag_prefix = tag_config[deb_head]
        pushers = []
        target_machines = list(filter(lambda m: isMachineNotHaveTagPrefix(m, test_tag_prefix), target_machines))
        target_machines = filterDeb(deb_name, target_machines)

    for m in target_machines:
        m = MachineInfo(m)
        print(m.getDisplayName(), ' '.join(m.getTags()))
    print(f'Num machines: {len(target_machines)}. Auto pushing started in 5 seconds...')
    time.sleep(5)

    # 此处为断点
    # sys.exit(0)
    for m in target_machines:
        m = MachineInfo(m)
        machineId = m.getMachineId()
        pusher = DebAutoPusher(
            client, machineId, version_key_config[deb_head], target_version, deb_name, dry_run)
        pusher.start()
        pushers.append(pusher)
    return pushers


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


def waitPushersDone(pushers):
    while True:
        time.sleep(10)
        alive_pushers = 0
        print(time.strftime('%Y-%m-%d %H:%M:%S'), '=' * 100)
        for pusher in pushers:
            if pusher.is_alive():
                alive_pushers += 1
            if pusher.status != DebAutoPusher.STATUS_EXIT_SUCCESS:
                print(pusher.displayName, pusher.status, pusher.errorCount)
        print(f'alive_pushers: {alive_pushers}')
        if alive_pushers == 0:
            break

    for pusher in pushers:
        pusher.join()

    print("All done!")


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

    reg = re.search(r'(.*)\-(\d+\.\d+\.\d+)\-(.*)\.deb', deb_name)
    assert(reg)
    head, o1, o2 = reg.group(1), reg.group(2), reg.group(3)

    target_version = '-'.join([o1, o2])
    print('Target version:', target_version)

    pushers = pusherDeb(client, target_machines,
                        target_version, deb_name, head, args.dry_run, test_tag)
    waitPushersDone(pushers)


if __name__ == '__main__':
    main()
