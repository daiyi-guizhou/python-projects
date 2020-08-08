<!-- TOC -->

- [使用说明](#使用说明)
    - [背景](#背景)
    - [执行步骤](#执行步骤)
        - [说明](#说明)
            - [参数](#参数)
        - [示例](#示例)
    - [回滚方案](#回滚方案)

<!-- /TOC -->

# 使用说明
## 背景
* 1. 什么情况下需要使用
    专有云 V2、V3 老版本 config_service 保留了所有的历史版本，如果 logtail_conf 更新比较频繁，数据库中的记录会非常多。导致 meta 加载很慢。
    查看 ConfigService 的日志 /apsara/tubo/TempRoot/sys/NewConfigService/ConfigServiceRole@101c06101.cloud.c07.amtest23/config_service_cache.LOG
    query result num:1922344
    query result num 非常大，且后面不出现新的日志，表明 ConfigService 加载 meta 未结束
* 2. 使用之后对系统造成的影响
    它清除的是 config_server 中 logtail_conf 历史version, 对当前没影响，但是历史的就没有了
## 执行步骤
* 1. 在那台机器上执行（OPS1、Service_bbb.ToolService#），用哪个用户执行（admin/root）
    任一台机器都可以，root
* 2. 解压、执行（脚本中包含参数说明、样例）
### 说明
现在有两种模式，
1   check,
检查当前是否满足 删除  条件
```bash
tar -xzf delete_old_logtail_config.tar.gz  ## 解压
/home/tops/bin/python ./delete_old_logtail_config.py --cluster_name=Cluster_aab --service_name=Service_ccc --mode=check   ## 检查
```
2   delete
当你想要执行  删除  操作时
```bash
tar -xzf delete_old_logtail_config.tar.gz  ## 解压
/home/tops/bin/python delete_old_logtail_config.py --cluster_name=cluster_aaa --service_name=Service_bbb --mode=delete   ## 删除
```
#### 参数
```bash
--cluster_name                      ## 你的集群名字      
--service_name                      ## 你的服务名字   Service_bbb,  Service_ccc 可供选择
--mode                              ## 模式   delete， check  可供选择
```
### 示例
```sh
root@a36f07007.cloud.f07.amtest11 /cloud/app/Service_ccc]#tar -xvf ./delete_old_logtail_config.tar.gz
src/README.md
src/delete_old_logtail_config.py
src/logger.conf
[root@a36f07007.cloud.f07.amtest11 /cloud/app/Service_ccc]
#cd src/
[root@a36f07007.cloud.f07.amtest11 /cloud/app/Service_ccc/src]
#/home/tops/bin/python ./delete_old_logtail_config.py --cluster_name=Cluster_aab --service_name=Service_ccc --mode=check
2020-06-16 11:14:28,792 - 66739 - root - delete_old_logtail_config.main:152 - INFO - Prepare to get resource of slscmc_inr db
2020-06-16 11:14:28,819 - 66739 - root - delete_old_logtail_config.common:78 - INFO - Prepare to get resource of slscmc_inr db
2020-06-16 11:14:28,820 - 66739 - root - delete_old_logtail_config.common:93 - INFO - the resource of slscmc_inr db is host=slsscmc.mysql.minirds.intra.env17e.shuguang.com, port=3125, user=slsscmc, passwd=cqdnkv6ptqsNGai4, database=slsscmc
2020-06-16 11:14:28,820 - 66739 - root - delete_old_logtail_config.common:103 - INFO - Prepare to get mysql_config, the cmd :  /usr/bin/mysql -h slsscmc.mysql.minirds.intra.env17e.shuguang.com -P 3125 -u slsscmc -pcqdnkv6ptqsNGai4 slsscmc -e "select project_name, config_name, max(version) as mv, count(*) as total from logtail_config_detail where deleted_flag = 0 group by project_name, config_name order by total desc limit 400;" | sed "s/,/g" | grep -v "project_name,config_name,mv"
======================================================================
2020-06-16 11:14:28,834 - 66739 - root - delete_old_logtail_config.check_sql:129 - INFO - All max_version sum  now is 228, normal ,it is ok ,
======================================================================
[root@a36f07007.cloud.f07.amtest11 /cloud/app/Service_ccc/src]
```
```bash
[root@vm010139128066 /cloud/app/Service_bbb]
#tar -xvf ./delete_old_logtail_config.tar.gz
src/README.md
src/delete_old_logtail_config.py
src/logger.conf
[root@vm010139128066 /cloud/app/Service_bbb]
#cd src/
[root@vm010139128066 /cloud/app/Service_bbb/src]
#ls
delete_old_logtail_config.py  logger.conf  README.md
[root@vm010139128066 /cloud/app/Service_bbb/src]
#/home/tops/bin/python delete_old_logtail_config.py --cluster_name=cluster_aaa --service_name=Service_bbb --mode=check
2020-06-16 16:23:54,061 - 543 - root - delete_old_logtail_config.main:152 - INFO - Prepare to get resource of slscmc_inr db
2020-06-16 16:23:55,008 - 543 - root - delete_old_logtail_config.common:78 - INFO - Prepare to get resource of slscmc_inr db
2020-06-16 16:23:55,008 - 543 - root - delete_old_logtail_config.common:93 - INFO - the resource of slscmc_inr db is host=slsscmc-inr8a7d.mysql.rds.env8c-inc.com, port=3306, user=slsscmc_inr8a7d, passwd=kvcmu9elIafJgq9l, database=slsscmc_inr
2020-06-16 16:23:55,009 - 543 - root - delete_old_logtail_config.common:103 - INFO - Prepare to get mysql_config, the cmd :  /usr/bin/mysql -h slsscmc-inr8a7d.mysql.rds.env8c-inc.com -P 3306 -u slsscmc_inr8a7d -pkvcmu9elIafJgq9l slsscmc_inr -e "select project_name, config_name, max(version) as mv, count(*) as total from logtail_config_detail where deleted_flag = 0 group by project_name, config_name order by total desc limit 400;" | sed "s/      /,/g" | grep -v "project_name,config_name,mv"
======================================================================
2020-06-16 16:23:55,253 - 543 - root - delete_old_logtail_config.check_sql:129 - INFO - All max_version sum  now is 68, normal ,it is ok ,
======================================================================
[root@vm010139128066 /cloud/app/Service_bbb/src]
```
* 3. 验证手段（脚本自包含，执行成功，显示在控制台上打印 successfully，执行失败显示打印 exception）
    若无报错， 即是执行成功
## 回滚方案
    无