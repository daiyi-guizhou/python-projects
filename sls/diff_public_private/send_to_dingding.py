#!/usr/bin/python  
# -*- coding: utf-8 -*-
import requests
import json
import os
from base_diff import *
from common.command_executor import exec_cmd
## 舔狗文学组
# url = "https://oapi.dingtalk.com/robot/send?access_token=YYYYYYYYY"
## 专有云
url = "https://oapi.dingtalk.com/robot/send?access_token=YYYYYYYYYYYY"
headers = {'Content-Type': 'application/json'}
## 执行diff
exec_cmd("python diff_all.py --tianji_access_key_id=YYYYYYYY  --tianji_access_key_secret=YYYYYYYYYYYY")
## send_to_dingding
## `diff`是关键字，每次必须都需要包含
all_diff_dict={}
diff_SRs=[]
dirs_list,files_list = get_file_dir_list("sls-backend-server")
for i in dirs_list:
    if i.startswith("2020"):
        new_dir_path = os.path.join("sls-backend-server",i,"src")
        for j in ["diff_dir_list","diff_file_list","content_diff_file_list"]:
            j_path = os.path.join(new_dir_path,j)
            if j == "diff_dir_list":
                exec_cmd("grep sls-backend-server/.*/user/.*/.* %s >> %s" % (j_path,os.path.join(new_dir_path,"diff_file_list")))
            if j == "diff_file_list":
                _,diff_SR,_= exec_cmd("awk -F'/' '{print $4}' %s|uniq" % j_path)
                diff_SRs += diff_SR.split('\n')
                _,all_diff_dict["diff_2_只存在某一方的文件"],_ = exec_cmd("awk -F'sls-backend-server/' '{print $2}' %s" % j_path)
                
            if j == "content_diff_file_list":
                _,diff_SR,_= exec_cmd("awk -F'/' '{print $4}' %s|uniq" % j_path)
                diff_SRs += diff_SR.split('\n')
                _,all_diff_dict["diff_3_两方都有的文件，但内容不一"],_ = exec_cmd("awk -F',' '{print $1}' %s|awk -F'sls-backend-server/private_cloud/' '{print $2}'" % j_path)
        diff_SRs = filter(lambda x : str(x).endswith('#'),diff_SRs)
        all_diff_dict['diff_1_不同的SR'] = list(set(diff_SRs))
        exec_cmd("rm -rf %s " % os.path.join("sls-backend-server",i))
        
with open("test.md","r") as f:
    markdown_data = json.loads(f.read())
for title,text in all_diff_dict.items():
    markdown_data["markdown"]["title"]=title
    markdown_data["markdown"]["text"]= title + '\n\r\n\r' + str(text)
    res = requests.post(url=url,headers=headers,data=json.dumps(markdown_data))
    print(res.text)