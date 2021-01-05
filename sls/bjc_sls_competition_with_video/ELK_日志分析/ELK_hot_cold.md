
mkdir -p /root/elasticsearch/conf
mkdir -p /root/elasticsearch/data
mkdir -p /root/elasticsearch/plugins/ik
chmod  777 /root/elasticsearch/plugins/ik -R
chmod  777 /root/elasticsearch/data -R 
chmod  777 /root/elasticsearch/conf -R 

cd /root/elasticsearch/conf


cat > es1.yml << EOF
cluster.name: ESCluster
node.name: node-1

network.bind_host: 0.0.0.0
network.publish_host: 10.100.254.149

http.port: 9201
transport.tcp.port: 9301
 
#是否允许跨域REST请求
transport.tcp.compress: true
http.cors.enabled: true
http.cors.allow-origin: "*"

#节点角色设置
node.master: true 
node.data: false

#有成为主节点资格的节点列表
discovery.zen.ping.unicast.hosts: ["10.100.254.149:9301"]
EOF




cat > es2.yml << EOF
cluster.name: ESCluster
node.name: node-2

network.bind_host: 0.0.0.0
network.publish_host: 10.100.254.149

http.port: 9202
transport.tcp.port: 9302
 
#是否允许跨域REST请求
transport.tcp.compress: true
node.attr.box_type: hot
http.cors.enabled: true
http.cors.allow-origin: "*"

#节点角色设置
node.master: false
node.data: true

#有成为主节点资格的节点列表
discovery.zen.ping.unicast.hosts: ["10.100.254.149:9301"]
EOF




cat > es3.yml << EOF
cluster.name: ESCluster
node.name: node-3

network.bind_host: 0.0.0.0
network.publish_host: 10.100.254.149

http.port: 9203
transport.tcp.port: 9303
 
#是否允许跨域REST请求
transport.tcp.compress: true
node.attr.box_type: cold
http.cors.enabled: true
http.cors.allow-origin: "*"

#节点角色设置
node.master: false
node.data: true

#有成为主节点资格的节点列表
discovery.zen.ping.unicast.hosts: ["10.100.254.149:9301"]
EOF




docker run -d --name es1 -p 9201:9201 -p 9301:9301  -v /root/elasticsearch/conf/es1.yml:/usr/share/elasticsearch/config/elasticsearch.yml -v /root/elasticsearch/data/d1:/usr/share/elasticsearch/data  -v /root/elasticsearch/plugins/p1:/usr/share/elasticsearch/plugins  --restart=always  -e ES_JAVA_OPTS="-Xms128m -Xmx128m -Duser.timezone=Asia/Shanghai" --net=host --privileged=true  elasticsearch:6.7.1

docker run -d --name es2 -p 9202:9202 -p 9302:9302  -v /root/elasticsearch/conf/es2.yml:/usr/share/elasticsearch/config/elasticsearch.yml -v /root/elasticsearch/data/d2:/usr/share/elasticsearch/data  -v /root/elasticsearch/plugins/p2:/usr/share/elasticsearch/plugins  --restart=always -e ES_JAVA_OPTS="-Xms128m -Xmx128m -Duser.timezone=Asia/Shanghai" --net=host --privileged=true  elasticsearch:6.7.1

docker run -d --name es3 -p 9203:9203 -p 9303:9303  -v /root/elasticsearch/conf/es3.yml:/usr/share/elasticsearch/config/elasticsearch.yml -v /root/elasticsearch/data/d3:/usr/share/elasticsearch/data  -v /root/elasticsearch/plugins/p3:/usr/share/elasticsearch/plugins --restart=always -e ES_JAVA_OPTS="-Xms128m -Xmx128m -Duser.timezone=Asia/Shanghai" --net=host --privileged=true  elasticsearch:6.7.1



docker run -d --name es4 -p 9204:9204 -p 9304:9304  -v /root/elasticsearch/conf/es4.yml:/usr/share/elasticsearch/config/elasticsearch.yml -v /root/elasticsearch/data/d4:/usr/share/elasticsearch/data  -v /root/elasticsearch/plugins/p4:/usr/share/elasticsearch/plugins --restart=always -e ES_JAVA_OPTS="-Xms128m -Xmx128m -Duser.timezone=Asia/Shanghai" --net=host --privileged=true  elasticsearch:6.7.1


 docker stop es1 es3 es2;
 docker rm es1 es3 es2;

docker run --net=host --name kibana -e ELASTICSEARCH_URL=http://10.100.254.149:9201 -p 5601:5601 -d kibana:6.7.1
```




cd /root/competition_bjc_sls/ELK/l

cat > config/logstash.yml << EOF

http.host: "0.0.0.0"
xpack.monitoring.elasticsearch.url: http://10.100.254.149:9201
xpack.monitoring.enabled: true
path.config: /usr/share/logstash/confd/logstash.conf

EOF

cat > conf.d/logstash.conf << EOF 
input {
  file {
    path => "/usr/share/logstash/bin_log/cold*log"
    type => "cold_hot_test"
    start_position => "beginning"
    stat_interval => "3"
  }
  file {
    path => "/usr/share/logstash/bin_log/test*log"
    type => "test"
    start_position => "beginning"
    stat_interval => "3"
  }
}

output {
   if [type] == "cold_hot_test" {
      elasticsearch {
         hosts => ["10.100.254.149:9201"]
         index => "test-log-%{+YYYY.MM.dd}"
      }
   }
   if [type] == "test" {
      elasticsearch {
         hosts => ["10.100.254.149:9201"]
         index => "test-log-%{+YYYY.MM.dd}"
      }
   }
}

EOF

docker run -d -p 5000:5000 --name logstash --net=host  -v /root/competition_bjc_sls/ELK/l/config/logstash.yml:/usr/share/logstash/config/logstash.yml -v /root/competition_bjc_sls/ELK/l/conf.d/:/usr/share/logstash/conf.d/ logstash:6.7.1