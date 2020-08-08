#!/home/tops/bin/python
# -*- coding:utf-8 -*-
import os
import time
from common.base import execute_activity
from common.command_executor import exec_cmd
from common.logging_helper import get_logger
from common.tianji.tianji_clt import TianjiAPI, TianjiSDK
from common.tianji.tianji_util import TianjiUtil
from base_diff import diff_catalogue, diff_content, write_dict_into_file, save_diff, diff_new_and_already, get_options, _to_debug, _copy_user_files
logger = get_logger()
options = get_options()
# --tianji_access_key_id="yyyyyy" --tianji_access_key_secret="YYYYYYYY"
TIANJI_ENDPOINT = options.tianji_endpoint
TIANJI_PROJECT_NAME = options.tianji_project
TIANJI_ACCESS_KEY_ID = options.tianji_access_key_id
TIANJI_ACCESS_KEY_SECRET = options.tianji_access_key_secret
PUBLIC_SERVICENAME = options.public_service_name
PRIVATE_GIT_NAME = options.private_git_name
# TEMPLATE_NAME_PUBLIC = options.public_template_name
TEMPLATE_NAME_PUBLIC = "TMPL-SLS-PUBLIC-V001"
TEMPLATE_NAME_PRIVATE = options.private_template_name
PRIVATE_GIT_REPO = options.private_git_repo
DEBUG_FLAG = options.debug_flag
PRIVATE_GIT_NAME_INNER = "service-sls-common"
PRIVATE_GIT_REPO_INNER = "git@gitlab.YYYYYYY.com:YYYYYY/service-sls-common.git"
def get_publice_pub_x86(head_dir_feature):
    tianji = TianjiUtil(TIANJI_ENDPOINT, TIANJI_PROJECT_NAME,
                        TIANJI_ACCESS_KEY_ID, TIANJI_ACCESS_KEY_SECRET)
    template_content = tianji.tj_sdk.GetServiceTemplate(
        PUBLIC_SERVICENAME, TEMPLATE_NAME_PUBLIC, "")
    def write_file_from_dict(dict_content, file_path):
        for file in dict_content.keys():
            file_real_path = os.path.join(file_path, file)
            if isinstance(dict_content[file], str):
                with open(file_real_path, "w+") as f:
                    f.write(str(dict_content[file]))
            if isinstance(dict_content[file], dict):
                if not os.path.exists(file_real_path):
                    exec_cmd("mkdir %s " % file_real_path)
                new_dict = dict_content[file]
                write_file_from_dict(new_dict, file_real_path)
    exec_cmd("rm -rf %s" % head_dir_feature)
    if not os.path.exists(head_dir_feature):
        exec_cmd("mkdir -p %s " % head_dir_feature)
    write_file_from_dict(template_content, head_dir_feature)
    _copy_user_files(head_dir_feature)

def get_private_pub_x86(head_dir_feature):
    exec_cmd(
        "git clone %s " % PRIVATE_GIT_REPO)
    exec_cmd("cd service-sls-backend-server && git checkout -b kk && git pull origin live:live ;git add .;git commit -m 'll' && git checkout live ")
    exec_cmd("rm -rf %s" % head_dir_feature)
    exec_cmd("mv %s/tianji_templates/%s %s ;rm -rf %s" %
             (PRIVATE_GIT_NAME, TEMPLATE_NAME_PRIVATE, head_dir_feature, PRIVATE_GIT_NAME))
    _copy_user_files(head_dir_feature)

def _main_diff(head_dir, local_public_path, local_apsara_path):
    unilateral_dirs, unilateral_files, common_file_list = diff_catalogue(
        local_apsara_path, local_public_path)
    sums_same_filename = diff_content(common_file_list)
    for i, j in zip([unilateral_dirs, unilateral_files, common_file_list, sums_same_filename], [os.path.join(head_dir, i) for i in ["unilateral_dirs", "unilateral_files", "common_file_list", "sums_same_filename"]]):
    # for i, j in zip([unilateral_dirs, unilateral_files, common_file_list, sums_same_filename], ["unilateral_dirs", "unilateral_files", "common_file_list", "sums_same_filename"]):
        write_dict_into_file(i, j)
    _to_debug(DEBUG_FLAG,logger.info, 'order', "Successed ,writing the file_name of diffing into files is done.")
    save_path = str(time.strftime(
        "%Y.%m.%d.%H.%M.%S", time.localtime())) + "_diff"
    save_path = os.path.join(head_dir, save_path)
    save_diff(sums_same_filename, head_dir, save_path)
    
    _to_debug(DEBUG_FLAG, logger.info, 'order', "Successed ,writing the content of diffing into files is done.")
    _to_debug(DEBUG_FLAG, logger.info, 'order', "Prepared to diff the %s and already_known_diff" % save_path)
    diff_new_and_already(save_path, os.path.join(head_dir, "already_known_diff"))
    _to_debug(DEBUG_FLAG, logger.info, 'order', "Successed ,diff the %s and already_known_diff is done." % save_path)
    _to_debug(DEBUG_FLAG, exec_cmd, 'reverse', "rm -rf %s/src/common_file_list %s/fixed/common_file_list" % (save_path, save_path))
    _to_debug(DEBUG_FLAG, exec_cmd, 'reverse', "rm -rf %s %s " % (local_apsara_path, local_public_path))
    
    
def main1():
    head_dir = "Public_vs_Private_pub_x86"
    local_public_path = os.path.join(head_dir, "public")
    local_apsara_path = os.path.join(head_dir, "private")
    get_publice_pub_x86(local_public_path)    ## sls-pub public x86
    get_private_pub_x86(local_apsara_path)        ## sls-pub private x86
    _main_diff(head_dir, local_public_path, local_apsara_path)

    
if __name__ == "__main__":
    # main1()
    # main2()
    # main3()
    main4()
    # main5()