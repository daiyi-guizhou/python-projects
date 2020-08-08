#!/usr/bin/python
# -*- coding: UTF-8 -*-

from time import time
import threading
import csv

from aliyun.log import LogClient, ListLogstoresRequest, GetLogsRequest, GetProjectLogsRequest

# access_key_id = ""
# access_key_secret = ""
# endpoint = ''
# admin_project_name = ""
# client = LogClient(endpoint, access_key_id, access_key_secret)


# 2600  --- 1 h
# 86400 --- 24 h
# 43200 --- 12 h
# method = 1000
# query = "ProjectName: %s AND Method: GetLogStoreLogs | select DISTINCT Query" % i['projectName']
# GetLogStoreLogs,only it have query.


class myThread (threading.Thread):
    def __init__(self, logclient, project_name, sigle_project, admin_project_name, start_time, end_time, all_projects):
        threading.Thread.__init__(self)
        self.logclient = logclient
        self.project_name = project_name
        self.sigle_project = sigle_project
        self.admin_project_name = admin_project_name
        self.start_time = start_time
        self.end_time = end_time
        self.all_projects = all_projects

    def get_method(self):
        method_query = "ProjectName: %s | select DISTINCT Method limit 1000" % self.project_name
        method_ret = GetLogsRequest(project=self.admin_project_name, logstore="sls_operation_log", fromTime=self.start_time,
                                    toTime=self.end_time, topic='', query=method_query, line=1000, offset=0, reverse=False)
        method_res = self.logclient.get_logs(method_ret)
        method_logs = method_res.get_logs()
        self.sigle_project["method_and_query"] = {}
        self.sigle_project["method_and_query"]["method"] = []
        self.sigle_project["method_and_query"]["query"] = []
        if method_logs:
            self.sigle_project["method_and_query"]["method"] = [
                j.get_contents()['Method'] for j in method_logs if j.get_contents()['Method']]

    def get_query(self):
        query_query = "ProjectName: %s AND Method: GetLogStoreLogs | SELECT COUNT(Distinct Query)" % self.project_name
        query_ret = GetLogsRequest(project=self.admin_project_name, logstore="sls_operation_log", fromTime=self.start_time,
                                   toTime=self.end_time, topic='', query=query_query, line=10, offset=0, reverse=False)
        query_res = self.logclient.get_logs(query_ret)
        assert query_res.is_completed(), "Failed to select DISTINCT Query"

        if query_res.get_logs()[0].get_contents().values() != ["0"]:
            all_count = query_res.get_count()
            all_count = all_count * 2
            query_query2 = "ProjectName: %s AND Method: GetLogStoreLogs | select DISTINCT Query limit %s" % (
                self.project_name, all_count)
            query_ret2 = GetLogsRequest(project=self.admin_project_name, logstore="sls_operation_log", fromTime=self.start_time,
                                        toTime=self.end_time, topic='', query=query_query2, line=10, offset=0, reverse=False)
            query_res2 = self.logclient.get_logs(query_ret2)
            assert query_res2.is_completed(), "Failed to select DISTINCT Query"
            query_logs = query_res2.get_logs()
            self.sigle_project["method_and_query"]["query"] = [
                k.get_contents()['Query'] for k in query_logs if k.get_contents()['Query']] # 列表表达式 [ for i in list[] if value ]

    def run(self):
        self.get_method()
        if self.project_name != self.admin_project_name:
            self.get_query()
        threadLock = threading.Lock() ## 线程锁，对公共资源操作。
        threadLock.acquire()  ## 锁住
        self.all_projects.append(self.sigle_project)
        threadLock.release()  ## 释放锁
        # print("##### sigle_project : ",self.sigle_project)


def main():
    endpoint_3b = ""
    access_key_id_3b = ""
    access_key_secret_3b = ""
    admin_project_name = ""
    client = LogClient(endpoint_3b, access_key_id_3b, access_key_secret_3b)

    # start_time = int(time()-10)
    # end_time = time()
    start_time = "2019-11-25 10:00:00"
    end_time = "2019-11-26 10:00:00"

    res = client.list_project(offset=0, size=int(-1))
    if res.get_total() == res.get_count():
        project_name_list = [project_res['projectName']
                             for project_res in res.get_projects()]
        project_name_list.sort()
        print "## num = %s, the project name is : %s  " % (
            len(project_name_list), project_name_list)

        to_run_projects = []
        all_projects = []
        for project_res in res.get_projects():
            sigle_project = {}
            sigle_project["project_name"] = project_res['projectName']
            sigle_project["method_and_values"] = {}
            to_run_project = myThread(
                client, project_res['projectName'], sigle_project, admin_project_name, start_time, end_time, all_projects)
            to_run_projects.append(to_run_project)

            to_run_project.start()
            while True:
                #判断正在运行的线程数量,如果小于5则退出while循环,
                #进入for循环启动新的进程.否则就一直在while循环进入死循环
                if(len(threading.enumerate()) < 5):
                    break


        for to_run_project in to_run_projects:
            to_run_project.join()  ## 进程结束

        all_projects_sorted = sorted(
            all_projects, key=lambda x: x['project_name'])  ## sorted 排序，lambda 

        with open("daiyi-test-method.csv", "w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["project_name", "method", "query"])
            writer.writerows([sigle_project["project_name"], sigle_project["method_and_query"]["method"],
                              sigle_project["method_and_query"]["query"]] for sigle_project in all_projects_sorted)


main()
