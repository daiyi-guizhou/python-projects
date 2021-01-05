我们 利用了 ELK 来做日志分析
主要安装了 ELK 三个容器。
<!-- TOC -->

- [competion](#competion)
    - [冷热节点](#冷热节点)
    - [业务痛点](#业务痛点)
    - [冷热节点的结构](#冷热节点的结构)
    - [冷热节点的优势](#冷热节点的优势)
    - [技术实现](#技术实现)
        - [如何实现数据从hot节点迁移到老的cold节点?](#如何实现数据从hot节点迁移到老的cold节点)

<!-- /TOC -->

[es 字段说明](https://www.zhihu.com/question/26446020)

# competion

相同类型的日志尽可能使用一个解析规则、以天为单位使用一个 Elasticsearch 索引存储，最终通过不同的Tag来区分不用应用日志，假如日志量非常大或者业务方明确提出单独存储需求，再拆分成不同的 kafka topic 以及 Elasticsearch 存储索引。
目前达达的Elasticsearch的集群由最初的5个节点逐步演变成15个热节点和5个冷节点
热节点机器主要承担实时日志写入以及最近3天日志的日志搜索查询，对于查询频次较低的3天以前的日志则全部迁移到冷节点。
冷热节点共存的方式运行一段时间后，我们发现冷节点的CPU利用率一直非常低，只在数据迁移以及数据查询时有磁盘IO的开销，其他时间段内几乎都是处于闲置状态。
我们决定使用基于Kubernetes部署Elasticsearch冷节点，物理机部署热节点的混合部方式，以达到充分利用这些CPU利用率峰值3%左右的冷节点资源
使用Kubernetes的Statefullset的模式部署冷节点以及Host网络模式来保证Elasticsearch集群的网络互通
为充分利用这些计算资源，我们使用Go重构了Java技术栈的日志解析逻辑
假如遇到大促等这样日质量暴涨的场景，可以使用公有云服务器扩容Kubernetes的Node资源以满足日志解析需要的计算资源

## 冷热节点

[blog](https://www.qedev.com/bigdata/63911.html)
[blog_practice](https://blog.csdn.net/mushao999/article/details/103520079?utm_medium=distribute.pc_relevant.none-task-blog-OPENSEARCH-6.not_use_machine_learn_pai&depth_1-utm_source=distribute.pc_relevant.none-task-blog-OPENSEARCH-6.not_use_machine_learn_pai)

[real_practice](https://blog.csdn.net/weixin_34361881/article/details/86131416?utm_medium=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-4.control&depth_1-utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-4.control)


[blog_vedio](https://blog.csdn.net/weixin_33554121/article/details/106513369?utm_medium=distribute.pc_relevant.none-task-blog-searchFromBaidu-3.not_use_machine_learn_pai&depth_1-utm_source=distribute.pc_relevant.none-task-blog-searchFromBaidu-3.not_use_machine_learn_pai)
[vedio](https://edu.csdn.net/course/play/26124?spm=1001.2101.3001.4101&utm_source=137528677)
1.  有x台机器tag设置为hot
2. 有y台机器tag设置为stale
3. hot集群中只存最近两天的.
4. 有一个定时任务每天将前一天的索引标记为stale
5. es看到有新的标记就会将这个索引迁移到冷集群中, 这都是es自动完成的.



[冷热节点 文档参考](https://blog.csdn.net/weixin_34361881/article/details/86131416?utm_medium%3Ddistribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-4.control%26depth_1-utm_source%3Ddistribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-4.control)
## 业务痛点


## 冷热节点的结构
热节点机器主要承担实时日志写入以及最近3天日志的日志搜索查询，对于查询频次较低的3天以前的日志则全部迁移到冷节点,冷热节点共存的方式运行一段时间后，我们发现冷节点的CPU利用率一直非常低，只在数据迁移以及数据查询时有磁盘IO的开销，其他时间段内几乎都是处于闲置状态。
我们决定使用基于Kubernetes部署Elasticsearch冷节点，物理机部署热节点的混合部方式，以达到充分利用这些CPU利用率峰值3%左右的冷节点资源。

## 冷热节点的优势

hot集群只保留最近三天数据， 查询比较快
引入Elasticsearch的冷热节点架构构建了一个满足日志高速写入同时保证了300T的存储空间的集群，同时引入Kubernetes部署冷节点，方便架构弹性，解决了冷节点的CPU利用率低的问题。


## 技术实现
配置文件在 `/root/elasticsearch/conf/`
es1.yml 为 master
es2.yml 为 hot 
es3.yml 为 cold 




### 如何实现数据从hot节点迁移到老的cold节点?
以test—bjc-2020.12.27索引为例,将它从hot节点迁移到cold节点

kibana里操作:
```
PUT /test—bjc-2020.12.27/_settings 
{ 
  "settings": { 
    "index.routing.allocation.require.box_type": "cold"
  } 
}
```

竞品对比:
     自建ELK  VS 阿里云 日志服务 
	1.	性能
	◦	同样性能，使用LogSearch/Analytics与ELK（SSD）费用比为 13.6%
	2.	 

	2.	规模
	◦	日志服务
	3.	
	◦	SLS 一天可以索引PB级数据，一次查询可以在秒级过几十TB规模数据，在数据规模上可以做到弹性伸缩与水平扩展
	4.	
	◦	SLS 没有扩展性方面的问题，每个shard都是分布式存储。并且当吞吐率增加时，可以动态分裂shard，达到处理能力水平扩展 
	5.	 

	3.