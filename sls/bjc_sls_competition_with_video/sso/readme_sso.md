快速开始：

    安装依赖：
    pip install flask
    pip install pyjwt


启动程序:
    python3 sso.py


原理说明:
    1. 使用jwt 加密，服务端存储了统一的秘钥匙，无论nginx 转发到哪个服务器上，因为后端秘钥相同，
       所以都可以解析出来用户状态。

    2. 通过 flask 的 before_request 功能，把用户权限写入到jwt秘串中，每次接口收到请求前，都会解析并验证权限，
       刷新权限，就将新的权限回写到token中，下次请求，解析jwt，就能拿到最新权限，做到权限及时变更。


使用说明:
    1. 首先访问http://10.100.254.149:5000/ 接口，会返回未校验，验证失败，
    2. 访问 http://10.100.254.149:5000/login 进行登录， 单点JWT登录成功。
    3. 访问 /test , / ,  /test2 接口，均可正常登录返回
    4. 访问 http://10.100.254.149:5000/flush 刷新权限
    5. 访问 http://10.100.254.149:5000/test2 接口，返回无权限，权限快速更新已经成功。


redis 和 mysql  设置

* 本地创建一个 redis 数据库，db 为 0  密码为123456 `redis.StrictRedis(host='127.0.0.1', password="123456", port=6379, db=0)`
* 创建一个mysql 数据库，database 名称为:evan_test,  然后账号密码就和上面一样。`pymysql.connect(host='127.0.0.1', port=3306,user="root",passwd="123456",database="evan_test")`