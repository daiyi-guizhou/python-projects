
# -*- coding:utf-8 -*-

import os
import time

# from base import execute_activity
from command_executor import exec_cmd
from logging_helper import get_logger

from base_diff import diff_catalogue, diff_content, write_dict_into_file, save_diff, diff_new_and_already, get_options, _to_debug

logger = get_logger()

options = get_options()





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

    # _to_debug(DEBUG_FLAG, exec_cmd, 'reverse', "rm -rf %s/src/common_file_list %s/fixed/common_file_list" % (save_path, save_path))
    # _to_debug(DEBUG_FLAG, exec_cmd, 'reverse', "rm -rf %s %s " % (local_apsara_path, local_public_path))



DEBUG_FLAG = False


if __name__ == "__main__":
    # exec_cmd("cp -fr new ./to_diff_dir/")
    # exec_cmd("cp -fr old ./to_diff_dir/")
    head_dir = "diff_dir"
    local_public_path = "diff_dir/overwrite"
    local_apsara_path = "diff_dir/overwrite_old"
    _main_diff(head_dir, local_public_path, local_apsara_path)
