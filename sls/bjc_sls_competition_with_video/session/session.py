# -*- coding: utf-8 -*-

import os
import json
import redis
from flask import Flask, session, make_response
from datetime import timedelta
from flask_cors import CORS
from functools import lru_cache



app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}},supports_credentials=True, methods=["GET","POST","OPTIONS"],allow_headers="*")
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)  # 配置7天有效


@lru_cache()
def conn_rds():
    r = redis.StrictRedis(host='127.0.0.1', password="123456", port=6379, db=0)
    return r


def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = 'http://10.100.254.149:8000'
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp

app.after_request(after_request)

# 设置session
@app.route('/set')
def set():
    session['username'] = 'evan'  # 设置“字典”键值对
    session.permanent = True  # 设置session的有效时间，长期有效，一个月的时间有效，
    conn = conn_rds()
    conn.set("username",json.dumps({"evan":"sign_in"}))
    return json.dumps({"result":"set_session_success"})


# 读取session
@app.route('/get')
def get():
    if not session.get('username'):
        conn = conn_rds()
        if conn.get("username"):
            return "sucess"
        else:
            return "未登录，无session信息"

    return json.dumps({"result":session.get('username')})


@app.route("/")
def welcome():
    return "welcome"

@app.route("/get_status")
def get_status():
    conn = conn_rds()
    username = conn.get("username")
    if username:
        return {"status":json.loads(username)["evan"]}
    else:
        return "未获得状态"




# 清除session中所有数据
@app.route('/clear')
def clear():
    session.clear()
    return 'success'


@app.route('/test')
def test():
    a = {"cors":"success"}
    return json.dumps(a)



if __name__ == '__main__':
    app.run(host="0.0.0.0",port="5000")

