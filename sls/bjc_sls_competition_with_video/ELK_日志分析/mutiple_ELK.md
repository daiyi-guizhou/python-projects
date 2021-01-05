[参考文档](https://blog.csdn.net/amor_leo/article/details/83144739)
[eshead](https://blog.csdn.net/cyooke/article/details/80253214)

## 环境准备
```
# 安装系统依赖
yum install -y yum-utils device-mapper-persistent-data lvm2 

# 添加docker源信息（下载速度比较快）
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo 

# 更新yum缓存
yum makecache fast

# 安装docker-ce
yum -y install docker-ce

# 启动docker后台服务
sudo systemctl start docker

# 配置阿里云镜像加速器（仅建议进行配置, 这里加速器地址仅用于展示，无加速功能，请使用自己的阿里云加速器，教程见百度，加速器免费）
mkdir /etc/docker
sudo cat > /etc/docker/daemon.json <<EOF 
    {"registry-mirrors": ["https://6y4h812t.mirror.aliyuncs.com"]}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
```

# 多节点 ELK 

```



mkdir -p /root/competition_bjc_sls/ELK/e/conf
mkdir -p /root/competition_bjc_sls/ELK/e/data
mkdir -p /root/competition_bjc_sls/ELK/e/plugins/ik
chmod  777 /root/competition_bjc_sls/ELK/e/plugins/ik
chmod  777 /root/competition_bjc_sls/ELK/e/data
chmod  777 /root/competition_bjc_sls/ELK/e/conf

 

cat > /etc/sysctl.conf << EOF

vm.max_map_count=262144
EOF
sysctl -p


cat > /etc/security/limits.conf << EOF
* soft nofile 65536
* hard nofile 65536
* soft nproc 4096
* hard nproc 4096
EOF

cat >> /etc/security/limits.d/20-nproc.conf << EOF

* soft nproc 4096
EOF


cd /root/competition_bjc_sls/ELK/e/conf

cat > es1.yml << EOF
#集群名
cluster.name: ESCluster
 
#节点名
node.name: node-1
 
#设置绑定的ip地址，可以是ipv4或ipv6的，默认为0.0.0.0，
#指绑定这台机器的任何一个ip
network.bind_host: 0.0.0.0
 
#设置其它节点和该节点交互的ip地址，如果不设置它会自动判断，
#值必须是个真实的ip地址  
network.publish_host: 10.100.254.143
  
#设置对外服务的http端口，默认为9200
http.port: 9201
 
#设置节点之间交互的tcp端口，默认是9300
transport.tcp.port: 9301
 
#是否允许跨域REST请求
http.cors.enabled: true

#允许 REST 请求来自何处
http.cors.allow-origin: "*"

#节点角色设置
node.master: true 
node.data: true

#有成为主节点资格的节点列表
#discovery.zen.ping.unicast.hosts: ["0.0.0.0:9303","192.168.0.112:9300","192.168.0.113:9300"]
discovery.zen.ping.unicast.hosts: ["10.100.254.143:9303","10.100.254.143:9302","10.100.254.143:9301"]

#集群中一直正常运行的，有成为master节点资格的最少节点数（默认为1）
# (totalnumber of master-eligible nodes / 2 + 1) 
discovery.zen.minimum_master_nodes: 2

EOF

cd /root/competition_bjc_sls/ELK/e/conf

cat > es2.yml << EOF
#集群名
cluster.name: ESCluster
 
#节点名
node.name: node-2
 
#设置绑定的ip地址，可以是ipv4或ipv6的，默认为0.0.0.0，
#指绑定这台机器的任何一个ip
network.bind_host: 0.0.0.0
 
#设置其它节点和该节点交互的ip地址，如果不设置它会自动判断，
#值必须是个真实的ip地址  
network.publish_host: 10.100.254.143
  
#设置对外服务的http端口，默认为9200
http.port: 9202
 
#设置节点之间交互的tcp端口，默认是9300
transport.tcp.port: 9302
 
#是否允许跨域REST请求
http.cors.enabled: true

#允许 REST 请求来自何处
http.cors.allow-origin: "*"

#节点角色设置
node.master: true 
node.data: true

#有成为主节点资格的节点列表
#discovery.zen.ping.unicast.hosts: ["0.0.0.0:9303","192.168.0.112:9300","192.168.0.113:9300"]
discovery.zen.ping.unicast.hosts: ["10.100.254.143:9303","10.100.254.143:9302","10.100.254.143:9301"]

#集群中一直正常运行的，有成为master节点资格的最少节点数（默认为1）
# (totalnumber of master-eligible nodes / 2 + 1) 
discovery.zen.minimum_master_nodes: 2

EOF

cd /root/competition_bjc_sls/ELK/e/conf

cat > es3.yml << EOF
#集群名
cluster.name: ESCluster
 
#节点名
node.name: node-3
network.bind_host: 0.0.0.0
network.publish_host: 10.100.254.143
http.port: 9203
 

http.cors.enabled: true
http.cors.allow-origin: "*"

node.master: true 
node.data: true

discovery.zen.ping.unicast.hosts: ["10.100.254.143:9303","10.100.254.143:9302","10.100.254.143:9301"] 
discovery.zen.minimum_master_nodes: 2

EOF



firewall-cmd --zone=public --add-port=9201/tcp --add-port=9202/tcp --add-port=9203/tcp --add-port=9301/tcp --add-port=9302/tcp --add-port=9302/tcp --permanent
firewall-cmd --reload

docker pull logstash:6.7.1 && docker pull kibana:6.7.1 && docker pull elasticsearch:6.7.1

docker pull docker.io/jeanberu/elasticsearch-head

docker run --name eshead  --restart=always -e ES_JAVA_OPTS="-Xms128m -Xmx128m -Duser.timezone=Asia/Shanghai" --net=host --privileged=true -p 9100:9100  -d  docker.io/jeanberu/elasticsearch-head
<!-- http://ip:9100/ -->


cd /root/competition_bjc_sls/ELK/e/conf

docker run -d --name es1 -p 9201:9201 -p 9301:9301  -v /root/competition_bjc_sls/ELK/e/conf/es1.yml:/usr/share/elasticsearch/config/elasticsearch.yml -v /root/competition_bjc_sls/ELK/e/data/d1:/usr/share/elasticsearch/data  -v /root/competition_bjc_sls/ELK/e/plugins/p1:/usr/share/elasticsearch/plugins  --restart=always  -e ES_JAVA_OPTS="-Xms128m -Xmx128m -Duser.timezone=Asia/Shanghai" --net=host --privileged=true  elasticsearch:6.7.1

docker run -d --name es2 -p 9202:9202 -p 9302:9302  -v /root/competition_bjc_sls/ELK/e/conf/es2.yml:/usr/share/elasticsearch/config/elasticsearch.yml -v /root/competition_bjc_sls/ELK/e/data/d2:/usr/share/elasticsearch/data  -v /root/competition_bjc_sls/ELK/e/plugins/p2:/usr/share/elasticsearch/plugins  --restart=always -e ES_JAVA_OPTS="-Xms128m -Xmx128m -Duser.timezone=Asia/Shanghai" --net=host --privileged=true  elasticsearch:6.7.1

docker run -d --name es3 -p 9203:9203 -p 9303:9303  -v /root/competition_bjc_sls/ELK/e/conf/es3.yml:/usr/share/elasticsearch/config/elasticsearch.yml -v /root/competition_bjc_sls/ELK/e/data/d3:/usr/share/elasticsearch/data  -v /root/competition_bjc_sls/ELK/e/plugins/p3:/usr/share/elasticsearch/plugins --restart=always -e ES_JAVA_OPTS="-Xms128m -Xmx128m -Duser.timezone=Asia/Shanghai" --net=host --privileged=true  elasticsearch:6.7.1

docker run -d --name es4 -p 9204:9204 -p 9304:9304  -v /root/competition_bjc_sls/ELK/e/conf/es4.yml:/usr/share/elasticsearch/config/elasticsearch.yml -v /root/competition_bjc_sls/ELK/e/data/d4:/usr/share/elasticsearch/data  -v /root/competition_bjc_sls/ELK/e/plugins/p4:/usr/share/elasticsearch/plugins --restart=always -e ES_JAVA_OPTS="-Xms128m -Xmx128m -Duser.timezone=Asia/Shanghai" --net=host --privileged=true  elasticsearch:6.7.1


 <!-- docker stop eshead es1 es3 es2;docker rm eshead es1 es3 es2 -->
 <!--  -->

 /var/lib/docker/overlay2/ceee5e31455b0bc4c9bccab4afd27cd896e91943dcb0d2bba0baffd103e19193/diff/usr/share/elasticsearch
/var/lib/docker/overlay2/0511398230c36373486f4a2f2ea2ff904cfdf14213fcde28b567fb536790e332/diff/usr/share/elasticsearch
/var/lib/docker/overlay2/7a9de74387b16eb2825a468ccd9f402a3712fe87fc4d599baa3675c7c707b070/diff/usr/share/elasticsearch
```

## eshead  --localinstall
```bash

wget https://github.com/mobz/elasticsearch-head/archive/master.zip

unzip master.zip
curl -sL https://rpm.nodesource.com/setup_14.x | bash -
yum install -y nodejs

cd elasticsearch-head-master/
npm install grunt --save-dev
npm install    
``` 

vim Gruntfile.js文件：增加hostname属性，设置为*； `hostname: '*',`
```
            },

                connect: {
                        server: {
                                options: {
                                        hostname: '*',
                                        port: 9100,
                                        base: '.',
                                        keepalive: true
                                }
                        }
                }

        });

```
vim _site/app.js 文件：修改head的连接地址:，如图所示:在js文件的最下面，我是找了蛮久，ip地址改为你的es所在服务器的ip
`this.base_uri = this.config.base_uri || this.prefs.get("app-base_uri") || "http;//localhost:9203" || "http;//localhost:9202" || "http;//localhost:9201" ;`
```
 services.Cluster = ux.Class.extend({
                defaults: {
                        base_uri: null
                },
                init: function() {
                        this.base_uri = this.config.base_uri || this.prefs.get("app-base_uri") || "http;//localhost:9203" || "http;//localhost:9202" || "http;//localhost:9201" ;
                },
                setVersion: function( v ) {
                        this.version = v;
                        this._version_parts = parse_version( v );
                },
```
启动命令： `npm run start &`
网络访问： http://ip:9100/