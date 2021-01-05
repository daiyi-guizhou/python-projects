
this is our session_跨域 。
用的是 python flask 框架。 具体流程原理 可看图
ession 跨域 readme ：


## 安装依赖 :
```
 pip install flask_cors
 pip install flask
 pip install redis
```

# redis 和 mysql  设置

* 本地创建一个 redis 数据库，db 为 0  密码为123456 `redis.StrictRedis(host='127.0.0.1', password="123456", port=6379, db=0)`
* 创建一个mysql 数据库，database 名称为:evan_test,  然后账号密码就和上面一样。`pymysql.connect(host='127.0.0.1', port=3306,user="root",passwd="123456",database="evan_test")`

 
## 执行
 执行浏览器代码：
   ` python session_browser.py`
    
 执行服务端代码:
   ` python3 session.py `



## 调试方式:
    1.访问10.100.254.149:8000 端口，出现welcome 证明链接服务器已经成功
    2. 访问 10.100.254.149:8000/test 接口，出现页面，下面操作均在页面出现的input输入框中:

** 可以在浏览器中打开检查调试模式观察整个session 跨域过程

    3. 在输入框中输入 /get 点击回车（"点我一下出结果"，下同）； 显示未登录
    4. 在输入框中输入 /get_status 点击回车； 显示没有登录状态
    5. 在输入框中输入 /set 点击回车; 显示session 已经跨域设置成功，可以通过浏览器检查查看，我们是8000端口访问5000，
    可以看到这时候跨域session已经设置成功

    6. 再次输入 /get 回车； /get_status 回车，可以看到从服务端拿到登录状态。
    7. 服务器输入 ps -ef | grep python 找到执行 python3 session.py 的进程杀死.
    8. 重启web服务 python3 session.py 
    9. 再次前端输入框中输入 /get_status, 可以看到依旧获得登录状态。

