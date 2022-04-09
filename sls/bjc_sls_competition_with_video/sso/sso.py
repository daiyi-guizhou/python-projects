# -*- coding: utf-8 -*-

# 需要安装依赖： pyjwt, flask

import jwt
from jwt import PyJWTError
from flask import Flask,request,make_response
from datetime import datetime, timedelta

app = Flask(__name__)

screct_key = "test"

@app.before_request
def before_request():
    if request.path == "/login":
        pass
    else:
        try:
            token = request.cookies.get("token")
            if not token:
                return "还未登录，校验失败"
            data = jwt.decode(token, key=screct_key, algorithms='HS256')
            print(data)
            if request.path == "/test2":
                print("xixi",data)
                if "POST" not in data["authentication"]:
                    return "权限变更，无法访问"

            print("校验成功")
        except PyJWTError as e:
            print("jwt验证失败: %s" % e)
            return "sso false"
    return


def    (auth=["GET", "POST", "UPDATE"],response="set jwt sucess"):
    payload = {  # jwt设置过期时间的本质 就是在payload中 设置exp字段, 值要求为格林尼治时间
        "user_id": request.args.get("user_id"),
        "authentication": auth,
        'exp': datetime.utcnow() + timedelta(seconds=360)
    }
    resp = make_response(response)  # 设置响应体
    token = jwt.encode(payload, key=screct_key, algorithm='HS256')
    resp.set_cookie("token", token, max_age=3600)
    return resp


@app.route("/login")
def set_toke():
    return jwt_decode()


@app.route("/test")
def test():
    return "sucess"


@app.route("/")
def hello():
    return "welcome"


@app.route("/flush")
def flush():

    return  jwt_decode(auth=["GET"],response="刷新权限成功")

@app.route("/test2")
def test2():
    return "test2 sucess"


if __name__ == "__main__":
    app.run("0.0.0.0",port="5000",threaded=True)