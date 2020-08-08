#!/home/tops/bin/python
# -*- coding:utf-8 -*-
import json
import logging.config
import os
import subprocess
import sys
from optparse import OptionParser
import requests
def get_options():
    usage = "usage: sudo /home/tops/bin/python  %prog --cluster_name= --service_name= --mode="
    parser = OptionParser(usage=usage)
    parser.add_option("--cluster_name",
                      dest="cluster_name",
                      default="",
                      help="cluster_name")
    parser.add_option("--service_name",
                      dest="service_name",
                      default="",
                      help="service_name")
    parser.add_option(
        "--mode",
        dest="mode",
        default="check",
        help=
        'there are two mode. "check","delete"; \n"--mode=check" : just check the logtail_config_detail;\n "--mode=delete" : just delete logtail_config_detail.'
    )
    (options, args) = parser.parse_args()
    return options
def get_logger(name=None, save_dir="log"):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    conf_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             "logger.conf")
    logging.config.fileConfig(conf_path)
    return logging.getLogger(name)
def exec_cmd(cmd, throw=True):
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    stdout = stdout.strip("\n")
    stderr = stderr.strip("\n")
    if p.returncode:
        if throw:
            raise Exception("ERROR", cmd, p.returncode, stdout, stderr)
    return p.returncode, stdout, stderr
class OldLogtailVersion(object):
    # global logger
    def __init__(self):
        options = get_options()
        self.cluster_name = options.cluster_name
        self.service_name = options.service_name
        self.mode_flag = options.mode
        self.logger = get_logger()
    def search_db_resource(self, db_name):
        try:
            vip_url = "http://yyyy:8888/api/kkkkk/service.res.*"
            payload = {
                'service.res.service': self.service_name,
                'service.res.name': db_name,
                'service.res.type': 'db'
            }
            db_results = requests.get(vip_url, params=payload)
            return db_results.json() if db_results.status_code == 200 else None
        except Exception as e:
            print e
            sys.exit(1)
    def common(self, db_res_list):
        self.logger.info("Prepare to get resource of slscmc_inr db")
        for _db_res in db_res_list:
            if self.cluster_name == _db_res['service.res.cluster']:
                db_res = _db_res
        assert db_res, "ERROR, can find the cluster info . please check the cluster name : %s" % self.cluster_name
        conf_json = json.loads(db_res["service.res.result"])
        sls_db_scmc_db = conf_json["db_name"]
        sls_db_scmc_host = conf_json["db_host"]
        sls_db_scmc_password = conf_json["db_password"]
        sls_db_scmc_port = conf_json["db_port"]
        sls_db_scmc_user = conf_json["user"]
        self.logger.info(
            "the resource of slscmc_inr db is host=%s, port=%s, user=%s, passwd=%s, database=%s"
            % (sls_db_scmc_host, sls_db_scmc_port, sls_db_scmc_user,
               sls_db_scmc_password, sls_db_scmc_db))
        mysql_cmd_tmplate = "/usr/bin/mysql -h {sls_scmc_db_host} -P {sls_scmc_db_port} -u {sls_scmc_db_user} -p{sls_scmc_db_passwd} {sls_scmc_db_database}".format(
            sls_scmc_db_host=sls_db_scmc_host,
            sls_scmc_db_port=sls_db_scmc_port,
            sls_scmc_db_user=sls_db_scmc_user,
            sls_scmc_db_passwd=sls_db_scmc_password,
            sls_scmc_db_database=sls_db_scmc_db)
        mysql_cmd_config_count = ' -e "select project_name, config_name, max(version) as mv, count(*) as total from logtail_config_detail where deleted_flag = 0 group by project_name, config_name order by total desc limit 400;" | sed "s/\t/,/g" | grep -v "project_name,config_name,mv"'
        cmd = mysql_cmd_tmplate + mysql_cmd_config_count
        self.logger.info("Prepare to get mysql_config, the cmd :  %s" % cmd)
        _, config_str, _ = exec_cmd(cmd)
        config_list = config_str.split('\n')
        return config_list, mysql_cmd_tmplate
## 11111
    def check_sql(self, config_list):
        _max_num = 0
        for i in config_list:
            _num = i.split(',')[3]
            _max_num = _max_num + int(_num)
        if _max_num >= 10000:
            print "=======" * 10
            print '     '
            self.logger.info(
                "All max_version sum  now is  %s, potential to cause slow sql, it is time to clear it "
                % _max_num)
            print '     '
            print "=======" * 10
        else:
            print "=======" * 10
            print '     '
            self.logger.info(
                "All max_version sum  now is %s, normal ,it is ok ," %
                _max_num)
            print '     '
            print "=======" * 10
    def delete_sql(self, config_list, mysql_cmd_tmplate):
        delete_sql = """ -e 'delete from logtail_config_detail where project_name = "{project}" and config_name = "{config}" and version < {version};'"""
        for i in config_list:
            project, config, version = i.split(',')[0], i.split(
                ',')[1], i.split(',')[2]
            _cmd = delete_sql.format(project=project,
                                     config=config,
                                     version=version)
            cmd = mysql_cmd_tmplate + _cmd
            self.logger.info(cmd)
            exec_cmd(cmd)
        print "=======" * 10
        print '     '
        self.logger.info("OK, All Done!")
        print '     '
        print "=======" * 10
    def main(self):
        self.logger.info("Prepare to get resource of slscmc_inr db")
        if self.service_name == "sls-backend-server":
            db_name_scmc = "slsscmc"
        elif self.service_name == "sls-common":
            db_name_scmc = "slsscmc_inr"
        else:
            self.logger.info("ERROR, the service_name  %s is wrong " %
                             self.service_name)
            sys.exit(1)
        db_res_list_scmc = self.search_db_resource(db_name_scmc)
        config_list, mysql_cmd_tmplate = self.common(db_res_list_scmc)
        if self.mode_flag == "check":
            self.check_sql(config_list)
        elif self.mode_flag == "delete":
            self.delete_sql(config_list, mysql_cmd_tmplate)
        else:
            self.logger.info("ERROR, the mode  %s is wrong " % self.mode_flag)
            sys.exit(1)
if __name__ == "__main__":
    client = OldLogtailVersion()
    client.main()