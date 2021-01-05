# -*- coding: utf-8 -*-
import redis
import pymysql
from flask import Flask, request
from functools import lru_cache

# 建表语句:
"""
CREATE TABLE orders(
    id int not null primary key,
    name char(20)
);
"""


app = Flask(__name__)

@lru_cache()
def conn_rds():
    r = redis.StrictRedis(host='127.0.0.1', password="123456", port=6379, db=0)
    return r


@lru_cache()
def conn_mysql():
    conn = pymysql.connect(host='127.0.0.1', port=3306,user="root",passwd="123456",database="evan_test")
    conn.autocommit(True)
    cursor = conn.cursor()
    return cursor


@app.route("/")
def hello():
    return "welcome"

@app.route("/take_orders",methods=["GET"])
def take_orders():
    order_id = request.args.get("orders_id")
    rds = redis.StrictRedis(host="127.0.0.1", password="123456", port=6379, db=0)
    rds.incr(order_id, 1)

    if rds.get(order_id) > b"1":
        print("已经下单成功，重复订单cache")
        return "already sucess"
    else:
        cursor = conn_mysql()
        sql = "insert into orders(id) values('%s')" % order_id
        cursor.execute(sql)
        print("订单写入数据库成功")
    return "sucess"


@app.errorhandler(Exception)
def all_exception_handler(e):
    return 'request Error'


if __name__ == "__main__":
    app.run("0.0.0.0",port=5000,threaded=True)

