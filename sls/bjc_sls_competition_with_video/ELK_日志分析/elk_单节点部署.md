<!-- TOC -->

    - [images](#images)
    - [elasticsearch](#elasticsearch)
    - [kibana](#kibana)
    - [logstash](#logstash)
    - [开端口](#开端口)
- [插入数据](#插入数据)

<!-- /TOC -->


## images

三者版本 要一致。
```sh
[root@localhost elasticsearch_docker]# docker ps
CONTAINER ID        IMAGE                 COMMAND                  CREATED             STATUS              PORTS               NAMES
6d7284db06ae        logstash:6.7.1        "/usr/local/bin/do..."   2 days ago          Up 24 hours                             logstash
0c4b4c70d89e        kibana:6.7.1          "/usr/local/bin/ki..."   3 days ago          Up 26 hours                             kibana
873e145e7f00        elasticsearch:6.7.1   "/usr/local/bin/do..."   3 days ago          Up 26 hours                             elasticsearch
[root@localhost elasticsearch_docker]# 
```


## elasticsearch
```sh
docker run \
--name elasticsearch \
--restart=always \
--net=host \
-p 9200:9200 \
-p 9300:9300 \
-e "discovery.type=single-node" \
-e ES_JAVA_OPTS="-Xms64m -Xmx128m -Duser.timezone=Asia/Shanghai" \
-v /opt/elasticsearch_docker/config/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml \
-v /opt/elasticsearch_docker/data:/usr/share/elasticsearch/data \
-v /opt/elasticsearch_docker/plugins:/usr/share/elasticsearch/plugins \
-d elasticsearch:6.7.1
```

 /opt/elasticsearch_docker/config/elasticsearch.yml
```yml
# network.bind_host: ["192.168.122.1","10.100.254.149"]
# network.publish_host: 192.168.122.1
# http.host: 0.0.0.0
# http.host: 10.100.254.149


network.bind_host: 0.0.0.0
network.publish_host: 10.100.254.149
http.port: 9200
transport.tcp.port: 9300
http.cors.enabled: true
http.cors.allow-origin: "*"

http.host: 0.0.0.0
```


## kibana
```sh
docker run --net=host --name kibana -e ELASTICSEARCH_URL=http://10.100.254.149:9200 -p 5601:5601 -d kibana:6.7.1

```

```sh
bash-4.2$ cat config/kibana.yml
#
# ** THIS IS AN AUTO-GENERATED FILE **
#

# Default Kibana configuration for docker target
server.name: kibana
server.host: "10.100.254.149"
elasticsearch.hosts: [ "http://10.100.254.149:9200" ]
xpack.monitoring.ui.container.elasticsearch.enabled: true
```

## logstash

```sh 
docker run -d -p 5000:5000 --name logstash --net=host  -v /root/logstash/config/logstash.yml:/usr/share/logstash/config/logstash.yml -v /root/logstash/conf.d/:/usr/share/logstash/conf.d/ logstash:6.7.1
```
配置文件 
```sh
bash-4.2$ cat config/logstash.yml
http.host: "0.0.0.0"
xpack.monitoring.elasticsearch.url: http://10.100.254.149:9200
xpack.monitoring.enabled: true
path.config: /usr/share/logstash/confd/logstash.conf


bash-4.2$ cat /usr/share/logstash/confd/logstash.conf
input {
  file {
    path => "/usr/share/logstash/bin/*log"
    type => "testlog"
    start_position => "beginning"
    stat_interval => "3"
  }
}

output {
   if [type] == "testlog" {
      elasticsearch {
         hosts => ["10.100.254.149:9200"]
         index => "test-log-%{+YYYY.MM.dd}"
      }
   }
}


bash-4.2$ ls /usr/share/logstash/bin/*log
/usr/share/logstash/bin/aa.log      /usr/share/logstash/bin/logTest.log
/usr/share/logstash/bin/bb.log      /usr/share/logstash/bin/testlog
/usr/share/logstash/bin/logger.log
```

写日志  
`cat /usr/share/logstash/bin/print_log.py`
```py

import logging
import time

logging.basicConfig(filename='test-log', format='%(asctime)s - %(levelname)s - %(message)s',level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
filehandler = logging.FileHandler("logTest.log")
filehandler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
filehandler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)

logger.addHandler(filehandler)
logger.addHandler(console)

logger.info("Start log")
logger.debug("Do something")
logger.warning("Something fail.")
logger.info("Finish")

def fun():
    logger.info('this is a test log')
    import random
    time.sleep(random.randint(0,5))

if __name__=='__main__':
    for i in range(10):
        logger.info('step {}'.format(i))
    while True:
        fun()


```

## 开端口

重启防火墙
```
firewall-cmd --add-port=80/tcp --add-port=8000/tcp --add-port=9300/tcp --add-port=9200/tcp --add-port=5000/tcp  --add-port=5601/tcp --permanent
systemctl restart firewalld
systemctl stop firewalld
```


# 插入数据  

此处 _id  为 shard_id, 默认 shard 为 5 个。 0.1.2.3.4
```
POST /_bulk

{ "create": { "_index": "test_daiyi", "_type": "test_daiyi", "_id" : "1" } }
{"name": "song40","age":30}
{ "create": { "_index": "test_daiyi", "_type": "test_daiyi", "_id" : "2" } }
{"name": "song41","age":31}
{ "create": { "_index": "test_daiyi", "_type": "test_daiyi", "_id" : "3" } }
{"name": "song42","age":32}
{ "create": { "_index": "test_daiyi", "_type": "test_daiyi", "_id" : "0" } }
{"name": "song44","age":34}

```


[move_allocation] can't move 3, from {node-2} to , since its not allowed, 
reason: [YES(shard has no previous failures)][YES(shard is primary and can be allocated)]
[YES(explicitly ignoring any disabling of allocation due to manual allocation commands via the reroute API)]
[YES(can relocate primary shard from a node with version [6.7.1] to a node with equal-or-newer version [6.7.1])]
[YES(no snapshots are currently running)][YES(ignored as shard is not being recovered from a snapshot)]
[NO(node does not match index setting [index.routing.allocation.include] filters [zone:\"hot\"])]
[NO(the shard cannot be allocated to the same node on which a copy of the shard already exists [[test_daiyi][3], node[4OlFyLToRoqvU6Muf7p_zg], [R], s[STARTED], a[id=eMRzYBQuRO2wko2283pRZw]])]
[YES(enough disk for shard on node, free: [28.5gb], shard size: [3.6kb], free after allocating shard: [28.5gb])]
[YES(below shard recovery limit of outgoing: [0 < 2] incoming: [0 < 2])
][YES(total shard limits are disabled: [index: -1, cluster: -1] <= 0)]
[YES(allocation awareness is not enabled, set cluster setting [cluster.routing.allocation.awareness.attributes] to enable it)]