import requests
from http.cookiejar import MozillaCookieJar
from http import HTTPStatus
import os
import time
import json
import logging
from logging.handlers import RotatingFileHandler
import getpass
from datetime import datetime, timedelta
import functools
import re
import urllib



def timed_cache(**timedelta_kwargs):                                              
    def _wrapper(f):                                                              
        update_delta = timedelta(**timedelta_kwargs)                              
        next_update = datetime.utcnow() - update_delta                            
        # Apply @lru_cache to f with no cache size limit                          
        f = functools.lru_cache(None)(f)                                          
        @functools.wraps(f)                                                       
        def _wrapped(*args, **kwargs):                                            
            nonlocal next_update                                                  
            now = datetime.utcnow()                                               
            if now >= next_update:                                                
                f.cache_clear()                                                   
                next_update = now + update_delta                                
            return f(*args, **kwargs)                                             
        return _wrapped                                                           
    return _wrapper

class MachineInfo(dict):
    def getMachineId(self):
        return self['Id']
    def getDisplayName(self):
        return self['DisplayName']
    def getPendingCommandsCount(self):
        return self['PendingCommandsCount']
    def getTags(self):
        return self['Tags']

class AiClothClient:
    DEFAULT_COOKIE_PATH = 'ai-cloth-cookie.txt'
    DEFAULT_BASE_URL = 'https://www.yyyy.com'
    DEV_SERVER_BASE_URL = 'https://https://www.yyyy.com'

    def __init__(self,
                 base_url=DEFAULT_BASE_URL,
                 cookie_path=DEFAULT_COOKIE_PATH):
        self.base_url = base_url
        self.web = requests.session()
        self.cookie_path = cookie_path
        self.display_name_cache = {}
        if os.path.isfile(cookie_path):
            self.web.cookies = MozillaCookieJar(cookie_path)
            self.web.cookies.load()
        else:
            self.web.cookies = MozillaCookieJar()
            self.web.cookies.save(filename=cookie_path)

        self.logger = logging.getLogger("AiClothClient")
        self.logger.setLevel(logging.INFO)
        handler = RotatingFileHandler('client.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.propagate = False
        self.logger.addHandler(handler)

    def is_login(self):
        r = self.web.get('{}/detectionMachine/list'.format(self.base_url))
        return r.status_code == HTTPStatus.OK

    def try_login(self, opt_code, username, password):
        if self.is_login():
            return
        postData = {
            "OtpCode": opt_code,
            "password": password,
            "username": username,
        }
        r = self.web.post('{}/user/login'.format(self.base_url),
                          data=json.dumps(postData))
        obj = r.json()
        if not obj['is_success']:
            raise Exception('Login failed: {}'.format(r.text))
        self.web.cookies.save(filename=self.cookie_path)

    def interactive_login(self):
        if not self.is_login():
            print('Login required. Then the credential will be saved into {}'.format(self.DEFAULT_COOKIE_PATH))
            username = input('Username: ')
            password = getpass.getpass()
            optCode = input('2FA code: ')
            self.try_login(optCode, username, password)
        assert(self.is_login())

    def get_display_name_from_cache(self, machineId):
        if len(self.display_name_cache) == 0:
            self.get_machine_list()
        return self.display_name_cache.get(machineId, machineId)

    def get_machine_alias(self):
        return self.web.get('{}/machineAlias/v2'.format(self.base_url)).json()

    @timed_cache(seconds=2)
    def get_machine_list(self):
        r = self.web.get('{}/detectionMachine/list/v2'.format(self.base_url))
        assert r.status_code == HTTPStatus.OK, '{}'.format(r.status_code)
        machine_list = r.json()
        for m in machine_list['machines']:
            self.display_name_cache[m['Id']] = m['DisplayName']
        return machine_list

    def get_machine_info(self, machineId : str) -> MachineInfo:
        for m in self.get_machine_list()['machines']:
            m  = MachineInfo(m)
            if m.getMachineId() == machineId:
                return m
        return None

    def get_shield_config(self, machineId):
        return self.web.get('{}/detection/machine/{}/shield-config'.format(self.base_url, machineId)).json()

    def get_config_yaml(self, machineId):
        return self.web.get('{}/syncedFile/file/{}_config.yaml'.format(self.base_url, machineId)).json()

    def upload_config_yaml(self, machineId, content):
        assert type(
            content) == str, 'Please call json.dumps(content) and then upload.'
        postData = {
            'FileKey': '{}_config.yaml'.format(machineId),
            'Content': content,
            "UnixTimestamp": int(time.time()),
        }
        r = self.web.post('{}/syncedFile'.format(self.base_url),
                          data=json.dumps(postData))
        assert r.status_code == HTTPStatus.OK, '{}, {}'.format(
            r.status_code, r.text)

    def get_alert_list(self):
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "apitoken": '{"Sig":"default-token-used-in-server-side","Name":"Server-token"}',
            "origin": "https://www.yyyy.com",
            "referer": "https://www.yyyy.com/detectionMachine/list",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 \
                       (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36"
        }
        r = self.web.get(
            'https://falcon-raw.yyyy.com/api/v1/alarm/eventcases?startTime=1466956800&process_status=unresolved&status=PROBLEM', headers=headers)
        assert r.status_code == HTTPStatus.OK
        return r.json()

    def push_shell_command(self, command, machine_list):
        data = {
            'Args': [command],
            'IsControlCmd': False,
            'MachineIds': machine_list
        }
        self.logger.info('{} {}'.format(command, str(machine_list)))
        r = self.web.post('{}/detectionMachine/addCommands'.format(self.base_url),
                          data=json.dumps(data))
        assert r.status_code == HTTPStatus.OK, '{}, {}'.format(
            r.status_code, r.text)

    def push_deb(self, deb_name, machine_list):
        ''' Result json: {"success":{"0C-9D-92-CA-EC-8C":76236}} '''
        data = {
            'Args': ["InstallDeb", "netdiskFile/{}".format(deb_name)],
            'IsControlCmd': True,
            'MachineIds': machine_list
        }
        self.logger.info(json.dumps(data))
        r = self.web.post('{}/detectionMachine/addCommands'.format(self.base_url),
                          data=json.dumps(data))
        assert r.status_code == HTTPStatus.OK, '{}, {}'.format(
            r.status_code, r.text)
        return r.json()

    def _get_finished_commands(self, machineId):
        return self.web.get('{}/detectionMachine/finishedCommands/{}'.format(self.base_url, machineId)).json()

    def get_finished_command_result(self, machineId, commandId : int) -> (int, str, str):
        ''' returns code, stdout, stderr '''
        r = self._get_finished_commands(machineId)
        for c in r['finishedCommands']:
            if c['command']['CommandId'] == commandId:
                return c['code'], c['stdout'], c['stderr']
        return None, None, None

    def get_al_deb(self):
        req = self.web.get('{}/netdiskFile/list'.format(self.base_url))
        assert req.status_code == HTTPStatus.OK, '{}'.format(req.status_code)
        pattern = re.compile(r'href="download/(.*)">Download</a>')
        result = pattern.findall(req.text)
        deb_list=[]
        for i in result:
            j=urllib.parse.unquote(i)
            deb_list.append(j)
        return deb_list
    
    def delete_finished_command(self,mac_list):
        playlod={}
        playlod['MachineIds']=mac_list
    
        r=self.web.post('{}/detectionMachine/confirmFailedCommands'.format(self.base_url), data=json.dumps(playlod))
        assert r.status_code == HTTPStatus.OK, '{}, {}'.format(
            r.status_code, r.text)