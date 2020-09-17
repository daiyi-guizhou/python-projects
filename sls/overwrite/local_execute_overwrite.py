#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import os
from optparse import OptionParser
def get_options():
    parser = OptionParser()
    parser.add_option("--src_files",
                      dest="src_files",
                      default="",
                      help="src_files")
    parser.add_option("--src_dirs",
                      dest="src_dirs",
                      default="",
                      help="src_dirs")
    parser.add_option("--dest_dir", dest="dest_dir", help="dest_dir")
    parser.add_option("--passwd", dest="passwd", default="", help="passwd")
    parser.add_option("--port", dest="port", default="", help="port")
    parser.add_option("--user", dest="user", default="", help="user")
    parser.add_option("--host", dest="host", default="", help="host")
    parser.add_option("--remove",
                      dest="remove",
                      default="false",
                      help="remove")
    parser.add_option("--timeout",
                      dest="timeout",
                      default=1000,
                      help="ops_time_out")
    (options, args) = parser.parse_args()
    return options
class LocalOverwrite():
    def __init__(self):
        options = get_options()
        self.source_files_str = options.src_files
        self.source_files_list = self.source_files_str.split(",")
        self.source_files_list = [] if self.source_files_list == [
            ''
        ] else self.source_files_list
        self.source_dirs_str = options.src_dirs
        _source_dirs_list = self.source_dirs_str.split(",")
        self.source_dirs_list = []
        for _source_dir in _source_dirs_list:
            dir_refine = _source_dir.rstrip("/")
            self.source_dirs_list.append(dir_refine)
        self.source_dirs_list = [] if self.source_dirs_list == [
            ''
        ] else self.source_dirs_list
        self.ops_dest_dir = options.dest_dir
        self.ops_passwd = options.passwd
        self.ops_port = options.port
        self.ops_user = options.user
        self.ops_host = options.host
        self.ops_remove = options.remove
        self.ops_timeout = options.timeout
    def check_xargs(self):
        # check xargs
        assert self.ops_dest_dir.startswith(
            "/cloud/app"), "### ERROR, dest_dir must start with '/cloud/app'! "
        if self.source_files_list:
            for source_file in self.source_files_list:
                assert os.path.isfile(
                    source_file), "### ERROR, %s doesn't exist! " % source_file
        if self.source_dirs_list:
            for source_dir in self.source_dirs_list:
                assert os.path.isdir(
                    source_dir), "### ERROR, %s doesn't exist! " % source_dir
    def get_variables_common(self):
        # get variables
        _service_name = self.ops_dest_dir.split("/")[3]
        ops_work_dir = '/cloud/app/' + _service_name
        _ops_passwd_cmd = ';expect "(yes/no)" {send "yes\\r"};expect "password:" {send "' + self.ops_passwd + \
            '\\r";set timeout %s;exp_continue};' % self.ops_timeout  # \\r is the escape for \r
        ops_passwd_cmd = _ops_passwd_cmd + "' > out.log 2>&1 && cat out.log >> result.log && grep '###' out.log ;grep 'Error' -A5 out.log"  # >> out.log 2>&1 "
        ops_ssh_cmd_front = "'spawn ssh -p %s %s@%s " % (
            self.ops_port, self.ops_user, self.ops_host)
        return ops_ssh_cmd_front, ops_passwd_cmd, ops_work_dir
    def _get_real_rm_source(self, source_str):
        if "/" in source_str:
            while source_str.count("/") >= 2:
                source_str = source_str[:source_str.rfind("/")]
        return source_str
    def _get_source_cmd(self, ops_work_dir, ops_ssh_cmd_front, ops_passwd_cmd):
        ops_source_rm_file_xarg = " "
        for source_file in (self.source_files_list + self.source_dirs_list):
            _source_file_path = ops_work_dir + '/' + self._get_real_rm_source(
                source_file)
            ops_source_rm_file_xarg = _source_file_path + ' ' + ops_source_rm_file_xarg
        _ops_ssh_to_rm_source = "rm -rf %s/execute_overwrite.sh %s/overwrite.sh %s" % (
            ops_work_dir, ops_work_dir, ops_source_rm_file_xarg)
        def _touch_dir_in_odps(ops_work_dir, sources_sum_list):
            ops_source_file_xarg = " "
            ops_ssh_cmd_end_dirs_list = []
            for source_file in sources_sum_list:
                if "/" in source_file:
                    if source_file.count("/") == 1 and source_file.startswith(
                            "./"):
                        pass
                    else:
                        postive_dir = source_file[:source_file.rfind("/")]
                        _source_file_path_dir = ops_work_dir + '/' + postive_dir
                        _source_file_path_dir_cmd = "mkdir -p %s || echo file_dir exists alreadly." % _source_file_path_dir
                        _source_file_path_dir_cmd = '"' + _source_file_path_dir_cmd + '"'
                        ops_ssh_cmd_end_dirs_list.append(
                            _source_file_path_dir_cmd)
                _source_file_path = ops_work_dir + '/' + source_file
                ops_source_file_xarg = _source_file_path + ',' + ops_source_file_xarg
            return ops_source_file_xarg, ops_ssh_cmd_end_dirs_list
        # get the cmd of scping source_files
        ops_source_file_xarg, ops_ssh_cmd_end_dirs_list = _touch_dir_in_odps(
            ops_work_dir, self.source_dirs_list + self.source_files_list)
        if self.ops_remove != "false":
            _ops_ssh_cmd_end = "bash %s/execute_overwrite.sh  --dest_dir=%s --remove" % (
                ops_work_dir, self.ops_dest_dir)
        else:
            _ops_ssh_cmd_end = "bash %s/execute_overwrite.sh --dest_dir=%s --src_files=%s" % (
                ops_work_dir, self.ops_dest_dir, ops_source_file_xarg)
            _ops_ssh_to_rm_source = _ops_ssh_to_rm_source + ";echo Done"
        ops_ssh_cmd_end = '"' + _ops_ssh_cmd_end + '"'
        ops_ssh_to_rm_source = '"' + _ops_ssh_to_rm_source + '"'
        expect_rm_files_cmd = "expect -c %s%s%s" % (
            ops_ssh_cmd_front, ops_ssh_to_rm_source, ops_passwd_cmd)
        return ops_ssh_cmd_end, expect_rm_files_cmd, ops_ssh_cmd_end_dirs_list
    def expect_excute_cmd(self, ops_passwd_cmd, ops_ssh_cmd_end,
                          ops_ssh_cmd_end_dirs_list, expect_rm_files_cmd,
                          ops_ssh_cmd_front, ops_work_dir):
        # sword_cmd
        _scp_overwrite_cmd = "'spawn scp  -P %s ./execute_overwrite.sh %s@%s:%s " % (
            self.ops_port, self.ops_user, self.ops_host, ops_work_dir)
        expect_cmd_scp_overwrite = "expect -c %s%s" % (_scp_overwrite_cmd,
                                                       ops_passwd_cmd)
        os.system(
            "echo '################### this is the result ################## ' > result.log"
        )
        os.system(expect_cmd_scp_overwrite)
        os.system("echo '### Copy overwrite.sh to %s successfully'" %
                  self.ops_host)
        # touch dir in ops_machine
        if ops_ssh_cmd_end_dirs_list:
            for ops_ssh_cmd_end_dir in ops_ssh_cmd_end_dirs_list:
                expect_cmd_ssh_touch_dir = "expect -c %s%s%s" % (
                    ops_ssh_cmd_front, ops_ssh_cmd_end_dir, ops_passwd_cmd)
                os.system(expect_cmd_ssh_touch_dir)
        # scp dirs
        if self.source_dirs_str:
            for source_dir in self.source_dirs_list:
                ops_work_real_dir = ops_work_dir + '/' + source_dir[:source_dir
                                                                    .rindex("/"
                                                                            )]
                _scp_to_ops_dir_source = "'spawn scp  -P %s -pr %s %s@%s:%s " % (
                    self.ops_port, source_dir, self.ops_user, self.ops_host,
                    ops_work_real_dir)
                expect_cmd_scp_source_dir = "expect -c %s%s" % (
                    _scp_to_ops_dir_source, ops_passwd_cmd)
                os.system(expect_cmd_scp_source_dir)
        # scp files
        if self.source_files_str:
            for source_file in self.source_files_list:
                ops_work_real_dir = ops_work_dir + '/' + source_file
                _scp_to_ops_source = "'spawn scp  -P %s -pr %s %s@%s:%s " % (
                    self.ops_port, source_file, self.ops_user, self.ops_host,
                    ops_work_real_dir)
                expect_cmd_scp_source_file = "expect -c %s%s" % (
                    _scp_to_ops_source, ops_passwd_cmd)
                os.system(expect_cmd_scp_source_file)
        expect_cmd_ssh_excute_overwrite = "expect -c %s%s%s" % (
            ops_ssh_cmd_front, ops_ssh_cmd_end, ops_passwd_cmd)
        os.system("echo '### remove'" if self.ops_remove != "false" else
                  "echo '### Copy %s to %s successfully'" %
                  (self.source_files_str, self.ops_host))
        os.system(expect_cmd_ssh_excute_overwrite)
        os.system(expect_rm_files_cmd)
        os.system("rm -rf out.log")
        os.system("echo '### All Done!'")
    def main(self):
        self.check_xargs()
        ops_ssh_cmd_front, ops_passwd_cmd, ops_work_dir = self.get_variables_common(
        )
        ops_ssh_cmd_end, expect_rm_files_cmd, ops_ssh_cmd_end_dirs_list = self._get_source_cmd(
            ops_work_dir, ops_ssh_cmd_front, ops_passwd_cmd)
        self.expect_excute_cmd(ops_passwd_cmd, ops_ssh_cmd_end,
                               ops_ssh_cmd_end_dirs_list, expect_rm_files_cmd,
                               ops_ssh_cmd_front, ops_work_dir)
if __name__ == '__main__':
    localoverwrite = LocalOverwrite()
    localoverwrite.main()