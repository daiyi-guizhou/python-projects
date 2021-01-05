
# 快速开始：

## 安装依赖：
```sh
pip install redis
pip install pymysql
pip instal flask
```

## redis 和 mysql  设置

* 本地创建一个 redis 数据库，db 为 0  密码为123456 `redis.StrictRedis(host='127.0.0.1', password="123456", port=6379, db=0)`

* 创建一个mysql 数据库，database 名称为:evan_test,  然后账号密码就和上面一样。`pymysql.connect(host='127.0.0.1', port=3306,user="root",passwd="123456",database="evan_test")`
数据库创建表:
```sql
CREATE TABLE orders(
    id int not null primary key,
    name char(20)
);
```

# 启动程序:
 `python3 orders.py`



# 调试
请在自己电脑安装 Jmeter 用来模拟请求，详情请参照短视频。

当启动服务后，测试api 为tabke_orders 
请在浏览器输入 http://10.100.254.149:5000/take_orders?orders_id=1234
进行高并发下单测试，每次测试请更改 orders_id 参数
测试完成后，可以通过 select * from orders; 查看数据库订单是否重复。

