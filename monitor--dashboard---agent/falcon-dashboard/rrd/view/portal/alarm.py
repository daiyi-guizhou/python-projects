########################################################-*- coding:utf-8 -*-
# #-*- coding:utf-8 -*-
# Copyright 2017 Xiaomi, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import jsonify, render_template, request, g, abort
from rrd import app
from rrd.model.portal.alarm import Event, EventCase
import json
import collections
import re

@app.route("/portal/alarm-dash/case", methods=["GET", "POST"])
def alarm_dash_case_get():
    global case_delete_metric_ok
    global case_delete_metric_problem
    case_delete_metric_ok=""
    evse_case_delete_metric_ok="gpu.alive/"
    case_delete_metric_problem="tf_server/"
    case_delete_metric_ok_list=''
    evse_case_delete_metric_ok_list=''
    case_delete_metric_problem_list=''
    case_delete_metric_ok_list_point=[]
    evse_case_delete_metric_ok_list_point=[]
    case_delete_metric_problem_list_point=[] 
    if request.method == 'POST':
        case_delete_metric_ok = str(request.form['metric_ok_delete'] or "").strip()
        case_delete_metric_problem = str(request.form['metric_problem_delete'] or "").strip()
        evse_case_delete_metric_ok = str(request.form['evse_metric_ok_delete'] or "").strip()

    event_cases = []
    limit = int(request.args.get("limit") or 50)
    page = int(request.args.get("p") or 1)
    endpoint_q = request.args.get("endpoint_q") or ""
    metric_q = request.args.get("metric_q") or ""
    status = request.args.get("status") or ""

    cases, total = EventCase.query(page, limit, endpoint_q, metric_q, status)
    
    limit2=int(total)
    cases_total, total2 = EventCase.query(page, limit2, endpoint_q, metric_q, status)

    for case in cases_total:        
        caseMetric=re.search(r'.*/',case.metric)
        if caseMetric: 
            case__mertic=caseMetric.group()

            # al_mac_alias=al_cloth_alias() 
            # case_delete_metric_ok_list_point_dict={} 
            # evse_case_delete_metric_ok_list_point_dict={}
            if case.status == "OK":
                if case_delete_metric_ok == case__mertic:
                    if case_delete_metric_ok_list:
                        case_delete_metric_ok_list=case_delete_metric_ok_list+','+ case.id
                    else:
                        case_delete_metric_ok_list=case.id
                    case_delete_metric_ok_list_point.append(str(case.endpoint))
                    # case.endpoint=case.endpoint.upper()
                    # case_delete_metric_ok_list_point_dict[case.id]=al_mac_alias[case.endpoint]
                    
                if evse_case_delete_metric_ok != case__mertic:
                    if evse_case_delete_metric_ok_list:
                        evse_case_delete_metric_ok_list=evse_case_delete_metric_ok_list+','+ case.id
                    else:
                        evse_case_delete_metric_ok_list=case.id
                    evse_case_delete_metric_ok_list_point.append(str(case.endpoint))
                    # case.endpoint=case.endpoint.upper()
                    # # print("*************************case.endpoint",case.endpoint)
                    # evse_case_delete_metric_ok_list_point_dict[case.id]=al_mac_alias[case.endpoint]
                    # print("******************************",evse_case_delete_metric_ok_list_point_dict[case.id])
            # elif case.status == "PROBLEM":
            else:
                if case_delete_metric_problem == case__mertic:
                    if case_delete_metric_problem_list:
                        case_delete_metric_problem_list=case_delete_metric_problem_list+','+ case.id
                    else:
                        case_delete_metric_problem_list=case.id
                    case_delete_metric_problem_list_point.append(str(case.endpoint))
    case_delete_metric_ok_html=case_delete_metric_ok
    case_delete_metric_problem_html=case_delete_metric_problem
    evse_case_delete_metric_ok_html=evse_case_delete_metric_ok
    return render_template("portal/alarm/case.html", **locals())

def page_endpoint(current_page,total,endpoint_list,endpoint_all,endpoint_all_id):
    i = int(total)
    limit = 50   
    if i <= limit:
        endpoint_all_page=endpoint_all
        return endpoint_all_page
    else:
        pages_total = i // limit + 1
        last_page_count = i - limit*pages_total
        pages_without_last = pages_total -1
        if current_page < pages_total:    
            endpoint_all_page={}
            endpoint_all_page=collections.OrderedDict()
            init_num = (current_page-1)*limit 
            final_num = current_page*limit 
            for k in endpoint_list[init_num:final_num]:
                endpoint_all_page[k]=endpoint_all[k]
            return endpoint_all_page
        else:
            endpoint_all_page={}
            endpoint_all_page=collections.OrderedDict()
            init_num = (current_page-1)*limit 
            final_num = total
            for k in endpoint_list[init_num:final_num]:
                endpoint_all_page[k]=endpoint_all[k]
            return endpoint_all_page

def al_cloth_alias():
    # endpoint=re.sub(r'dm/',"",point)
    # endpoint=endpoint.upper()
    import requests
    import json
    import re
    headers={'cookie':'mysession=MTU0NDMzNzMyMHxEdi1CQkFFQ180SUFBUkFCRUFBQV9nRVdfNElBQVFaemRISnBibWNNREFBS1ZYTmxjbE4wWVhSMWN3ZGJYWFZwYm5RNEN2X3lBUF92ZXlKSmMweHZaMmx1SWpwMGNuVmxMQ0pWYzJWeVNXUWlPalUwTENKVmMyVnlUbUZ0WlNJNklubHBMbVJoYVNJc0lsQnlhWFpwYkdWblpYTWlPbnNpVEdGaVpXeHBibWRCWkhaaGJtTmxaQ0k2ZEhKMVpTd2lUR0ZpWld4cGJtZENZWE5wWXlJNmRISjFaU3dpVFdGamFHbHVaVTl3YzBKaGMybGpJanAwY25WbExDSk5ZV05vYVc1bFQzQnpTblZ3ZVhSbGNpSTZkSEoxWlN3aVRXRmphR2x1WlU5d2MxTjVjM1JsYlNJNmRISjFaU3dpVFc5a1pXeFBjSE5NYVhOMElqcDBjblZsTENKTmIyUmxiRTl3YzFkeWFYUmxJanAwY25WbExDSlZjMlZ5VFdGdVlXZGxJanAwY25WbGZYMD18osksH3Hi6whcYQrn8ZsC_fhPBrDNrZGf0OyBdm34VJA='}
    req=requests.get('https://www.yyyy.com/machineAlias/v2',headers=headers)
    reqText=json.loads(req.text)
    al_mac_alias=reqText["AliasMap"]

    # al_mac=al_mac[:-1]
    # al_mac=al_mac[2:]
    al_cloth_alias={}
    # al_mac_alias=eval(al_mac)
    for mac in al_mac_alias.keys():
        endpoint = "DM/" + mac
        al_cloth_alias[endpoint] = al_mac_alias[mac]
        print("#######################al_cloth_alias[endpoint]",al_cloth_alias[endpoint],endpoint,type(al_cloth_alias[endpoint]))
    return al_cloth_alias

@app.route("/portal/alarm-dash-V2/case_todo", methods=["GET", "POST"])
def after_alarm_execute():
    cases_init, total_init = EventCase.query(1, 50, '', "", "PROBLEM")
    limit=int(total_init)
    new_case=[]

    cases, total2 = EventCase.query(1, limit, '', "", "problem")
    for case in cases:
        if case.status == 'PROBLEM':
            if case.metric == "mem.memfree.percent/cluster=detection-machine":
                new_case.append(case)
    return render_template("portal/alarm/case_todo.html", **locals())


@app.route("/portal/alarm-dash-V2/case_point", methods=["GET", "POST"])
def alarm_dash_case_point_get():
    global delete_metric_ok
    global delete_metric_problem
    delete_metric_ok=""
    evse_delete_metric_ok="gpu.alive/"
    delete_metric_problem="tf_server/"
    delete_metric_ok_list=''
    evse_delete_metric_ok_list=''
    delete_metric_problem_list=''
    delete_metric_ok_list_point=[]
    evse_delete_metric_ok_list_point=[]
    delete_metric_problem_list_point=[]
    if request.method == 'POST':
        delete_metric_ok = str(request.form['metric_ok_delete'] or "").strip()
        delete_metric_problem = str(request.form['metric_problem_delete'] or "").strip()
        evse_delete_metric_ok = str(request.form['evse_metric_ok_delete'] or "").strip()

    # delete_metric_ok = str(request.args.get("metric_ok_delete") or "").strip()
    # delete_metric_problem = str(request.args.get("metric_problem_delete") or "").strip()  ### 可以分页，但是接收不到数据
    # print("************************************************mertic for html")
    # print(delete_metric_ok,delete_metric_problem)

    event_cases = []
    total_point = 10
    limit_init = int(request.args.get("limit") or 50)
    page = int(request.args.get("p") or 1)
    endpoint_q = request.args.get("endpoint_q") or ""
    metric_q = request.args.get("metric_q") or ""
    status = request.args.get("status") or ""
    page_init=1

    cases_init, total_init = EventCase.query(page_init, limit_init, endpoint_q, metric_q, status)
    limit=int(total_init)

    cases, total2 = EventCase.query(page_init, limit, endpoint_q, metric_q, status)
    endpoint_all={}
    endpoint_all=collections.OrderedDict()
    endpoint_all_id={}
    endpoint_all_id=collections.OrderedDict()
    endpoint_list=[]
    total_different_endpoint_count=0

    case_operator=[]
    metrics_operator = ['camera.last_update_interval/','net-control.alive/','usb_control.alive/','gpu.alive/','camera.alive/','tf_server/']
    for case in cases:
        caseMetric = case.metric
        caseMetric = re.search(r'.*/',caseMetric)
        # all case.metric are like "camera.last_update_interval/cameraid=11,cluster=detection-machine",they have tags, 
        # but if case.metric is like "netstat.ESTABLISHED" without tag,so caseMetric will NONE.
        if caseMetric:          
            mertic_of_case = caseMetric.group()
            if mertic_of_case in metrics_operator:
                case_operator.append(case)
        else:
            pass
    cases=case_operator

    for case in cases: 
        endpoint_all_list=[]
        for key in endpoint_all.keys():
            endpoint_all_list.append(key)
        if case.endpoint not in endpoint_all_list:
            big_case=str(case.endpoint)
            big_case=[]
            big_case.append(case)
            endpoint_all[case.endpoint]=big_case
            big_case_id=str(case.id)   
            endpoint_all_id[case.endpoint]=big_case_id     
        else:
            endpoint_all[case.endpoint].append(case)
            endpoint_all_id[case.endpoint]=endpoint_all_id[case.endpoint] +','+ case.id
        caseMetric=re.search(r'.*/',case.metric)
        case.mertic=caseMetric.group()

        # al_mac_alias=al_cloth_alias() 
        # delete_metric_ok_list_point_dict={} 
        # evse_delete_metric_ok_list_point_dict={}
        if case.status == "OK":
            if delete_metric_ok == case.metric:
                if delete_metric_ok_list:
                    delete_metric_ok_list=delete_metric_ok_list+','+ case.id
                else:
                    delete_metric_ok_list=case.id
                delete_metric_ok_list_point.append(str(case.endpoint))
                # case.endpoint=case.endpoint.upper()
                # delete_metric_ok_list_point_dict[case.id]=al_mac_alias[case.endpoint]
                
            if evse_delete_metric_ok != case.metric:
                if evse_delete_metric_ok_list:
                    evse_delete_metric_ok_list=evse_delete_metric_ok_list+','+ case.id
                else:
                    evse_delete_metric_ok_list=case.id
                evse_delete_metric_ok_list_point.append(str(case.endpoint))
                # case.endpoint=case.endpoint.upper()
                # # print("*************************case.endpoint",case.endpoint)
                # evse_delete_metric_ok_list_point_dict[case.id]=al_mac_alias[case.endpoint]
                # print("******************************",evse_delete_metric_ok_list_point_dict[case.id])
        # elif case.status == "PROBLEM":
        else:
            if delete_metric_problem == case.metric:
                if delete_metric_problem_list:
                    delete_metric_problem_list=delete_metric_problem_list+','+ case.id
                else:
                    delete_metric_problem_list=case.id
                delete_metric_problem_list_point.append(str(case.endpoint))



    for key in endpoint_all.keys():
        total_different_endpoint_count += 1
        endpoint_list.append(key)
    
    total=total_different_endpoint_count
    current_limit = int(request.args.get("limit") or 50)
    limit = int(request.args.get("limit") or 50)
    current_page = int(request.args.get("p") or 1)
    endpoint_all_page=page_endpoint(current_page,total,endpoint_list,endpoint_all,endpoint_all_id)

    endpoint_all_page_count={}
    endpoint_all_page_ok_count={}   
    endpoint_all_page_problem_count={}
    endpoint_all_ok_id={}
    endpoint_all_problem_id={}
    endpoint_all_ok_metric={}
    endpoint_all_problem_metric={}            
    for key in endpoint_all_page.keys():
        endpoint_all_page_count_num=0
        endpoint_all_page_ok_count_num=0
        endpoint_all_page_problem_count_num=0
        endpoint_all_ok_metric_list=[]
        endpoint_all_problem_metric_list=[]
        for pages_case in endpoint_all_page[key]:
            endpoint_all_page_count_num += 1
            pages_case.metric=re.match(r'.*/',pages_case.metric).group()
            if pages_case.status == "OK":
                endpoint_all_page_ok_count_num += 1
                if endpoint_all_ok_id.has_key(key):
                    endpoint_all_ok_id[key]=endpoint_all_ok_id[key] +','+ pages_case.id
                else:
                    endpoint_all_ok_id[key]=pages_case.id
                if endpoint_all_ok_metric_list:
                    if pages_case.metric in endpoint_all_ok_metric_list:
                        pass
                    else:
                        endpoint_all_ok_metric_list.append(pages_case.metric)
                else:
                    endpoint_all_ok_metric_list.append(pages_case.metric)

            if pages_case.status == "PROBLEM":
                endpoint_all_page_problem_count_num += 1
                if endpoint_all_problem_id.has_key(key):
                    endpoint_all_problem_id[key]=endpoint_all_problem_id[key] +','+ pages_case.id
                else:
                    endpoint_all_problem_id[key]=pages_case.id
                if endpoint_all_problem_metric_list: 
                    if pages_case.metric in endpoint_all_problem_metric_list:
                        pass
                    else:
                        endpoint_all_problem_metric_list.append(pages_case.metric)
                else:
                    endpoint_all_problem_metric_list.append(pages_case.metric)


        endpoint_all_page_count[key]=endpoint_all_page_count_num
        endpoint_all_page_ok_count[key]=endpoint_all_page_ok_count_num
        endpoint_all_page_problem_count[key]=endpoint_all_page_problem_count_num
        endpoint_all_ok_metric[key]=endpoint_all_ok_metric_list
        endpoint_all_problem_metric[key]=endpoint_all_problem_metric_list

    delete_metric_ok_html=delete_metric_ok
    delete_metric_problem_html=delete_metric_problem
    evse_delete_metric_ok_html=evse_delete_metric_ok
    return render_template("portal/alarm/case_point.html", **locals())

            
        
@app.route("/portal/alarm-dash/case/event")
def alarm_dash_event_get():
    limit = int(request.args.get("limit") or 50)
    page = int(request.args.get("p") or 1)

    case_id = request.args.get("case_id")
    if not case_id:
        abort(400, "no case id")

    _cases = EventCase.select_vs(where='id=%s', params=[case_id], limit=1)
    if len(_cases) == 0:
        abort(400, "no such case where id=%s" %case_id)
    case = _cases[0]

    case_events, total = Event.query(event_caseId=case_id, page=page, limit=limit)
    return render_template("portal/alarm/case_events.html", **locals())


@app.route("/portal/alarm-dash/case/delete", methods=['POST'])
def alarm_dash_case_delete():
    ret = {
        "msg": "",
    }
    ids = request.form.get("ids") or ""
    ids = ids.split(",") or []
    if not ids:
       ret['msg'] = "no case ids" 
       return json.dumps(ret)

    holders = []
    for x in ids:
        holders.append("%s")
    placeholder = ','.join(holders)

    where = 'id in (' + placeholder + ')'
    params = ids
    EventCase.delete(where=where, params=params)
    for x in ids:
        Event.delete(where='event_caseId=%s', params=[x])

    return json.dumps(ret)

@app.route("/portal/alarm-dash/case/event/delete", methods=['POST'])
def alarm_dash_case_event_delete():
    ret = {
        "msg": "",
    }
    ids = request.form.get("ids") or ""
    ids = ids.split(",") or []
    if not ids:
       ret['msg'] = "no case ids" 
       return json.dumps(ret)

    holders = []
    for x in ids:
        holders.append("%s")
    placeholder = ','.join(holders)

    where = 'id in (' + placeholder + ')'
    params = ids
    Event.delete(where=where, params=params)

    return json.dumps(ret)
