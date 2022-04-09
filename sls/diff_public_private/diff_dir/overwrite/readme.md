<!-- TOC -->

                    - [](#)
- [操作说明](#操作说明)
    - [添加 overwrite](#添加-overwrite)
    - [移除 overwrite](#移除-overwrite)
- [参数说明](#参数说明)
        - [--src_file](#--src_file)
        - [--src_dirs=./kk_test/,./conf.local/bb/](#--src_dirskk_testconflocalbb)
        - [--dest_dir](#--dest_dir)
        - [--remove](#--remove)
    - [ops 机器信息](#ops-机器信息)
        - [跳板机 的信息](#跳板机-的信息)
- [备注](#备注)

<!-- /TOC -->


ooooooooo
####################
$$$$$$$$$$$$$$$$$$$$$$$$
$$$$$$$$$$$$$$

# 操作说明
## 添加 overwrite
```
python local_execute_overwrite.py --src_files=test.log,./log/aa.txt --src_dirs=./kk_test/,./conf.local/bb/ --dest_dir=/cloud/app/serivce_a/ServiceRole_b#/app_c/current  --passwd=_kkkk_ --port=52501 --user=root --host=10.0.0.1
python local_execute_overwrite.py --src_files=test.log --dest_dir=/cloud/app/serivce_a/ServiceRole_b#/app_c/current/log  --passwd=_kkkk_ --port=52501 --user=root --host=10.0.0.1
python local_execute_overwrite.py --src_files=test.log,aa.txt --dest_dir=/cloud/app/serivce_a/ServiceRole_b#/app_c/current/log  --passwd=_kkkk_ --port=52501 --user=root --host=10.0.0.1
python local_execute_overwrite.py --src_files=test.log,./log/aa.txt --dest_dir=/cloud/app/serivce_a/ServiceRole_b#/app_c/current  --passwd=_kkkk_ --port=52501 --user=root --host=10.0.0.1
python local_execute_overwrite.py --src_dirs=./kk_test/,./conf.local/bb/ --dest_dir=/cloud/app/serivce_a/ServiceRole_b#/app_c/current  --passwd=_kkkk_ --port=52501 --user=root --host=10.0.0.1
```
## 移除 overwrite
```
## --remove= 的值不为 false. 它就会默认都是  remove.
python local_execute_overwrite.py --src_files=test.log --src_dirs=./kk_test/,./conf.local/bb/ --dest_dir=/cloud/app/serivce_a/ServiceRole_b#/app_c/current/log  --passwd=_kkkk_ --port=52501 --user=root --host=10.0.0.1 --remove=99
python local_execute_overwrite.py --src_files=test.log --dest_dir=/cloud/app/serivce_a/ServiceRole_b#/app_c/current/log  --passwd=_kkkk_ --port=52501 --user=root --host=10.0.0.1 --remove=true
python local_execute_overwrite.py --src_dirs=./kk_test/,./conf.local/bb/ --dest_dir=/cloud/app/serivce_a/ServiceRole_b#/app_c/current/log  --passwd=_kkkk_ --port=52501 --user=root --host=10.0.0.1 --remove=99
```
# 参数说明
### --src_file
你要替换的文件， 他会替换到  --dest_dir 目录下  
格式： ` --src_files=YYY --dest_dir=XXX`    
多个文件用`’,‘`逗号分隔。    
` --src_files=YYY,ZZZ,CCC --dest_dir=XXX`  
if you have many src_file; --src_files is divided by ','"    
`python local_execute_overwrite.py  --src_files=test.log,./aa.txt  --dest_dir=/cloud/app/serivce_a/ServiceRole_b#/app_c/current/log  --passwd=_kkkk_ --port=52501 --user=root --host=10.0.0.1 `
### --src_dirs=./kk_test/,./conf.local/bb/
你要替换的文件夹， 他会替换到  --dest_dir 目录下  
格式： ` --src_dirs=YYY --dest_dir=XXX`    
多个文件用`’,‘`逗号分隔。    
` --src_dirs=YYY,ZZZ,CCC --dest_dir=XXX`  
if you have many src_dirs; --src_dirs is divided by ','"    
`python local_execute_overwrite.py  --src_dirs=./kk_test/,./conf.local/bb/  --dest_dir=/cloud/app/serivce_a/ServiceRole_b#/app_c/current/log  --passwd=_kkkk_ --port=52501 --user=root --host=10.0.0.1 `
### --dest_dir
这个 必须 格式严格， /cloud/app/，Service，SR，APP,必须包含  
it must start with `/cloud/app/serivce_a/ServiceRole_b#/sls_web/`  
--dest_dir is like `/cloud/app/serivce_a/ServiceRole_b#/sls_web/current`,
### --remove
默认为 false。
当你要 移除 overwrite  
当你 写了 --remove= ,给它赋值。只要这个指不为空，也不是false. 那么他就默认你要 remove
格式：  `python local_execute_overwrite.py  --src_files=test.log,aa.txt --dest_dir=/cloud/app/serivce_a/ServiceRole_b#/app_c/current/log  --passwd=_kkkk_ --port=52501 --user=root --host=10.0.0.1 --remove=99`
## ops 机器信息
以下几个参数都是ops的机器。
```
--passwd=_kkkk_ --port=52501 --user=root --host=10.0.0.1
```
### 跳板机 的信息
ssh  root@10.0.0.1 -p52501
密码: _kkkk_
# 备注
此脚本 在本机上执行，它先scp 到 ops 跳板机 ,通过跳板机对你的其它机器操作。
result.log  为每次执行的结果。
