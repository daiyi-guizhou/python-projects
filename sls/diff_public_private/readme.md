## 目录文件说明
2019.11.13.HH.mm.SS_diff  
    src                               时间2019xxxx， public 与 专有云-master分支 对比而得
        
        unilateral_dirs                 不一样的文件目录 （有 与 无）,单边目录，只有一边有
        unilateral_files                不一样的文件 （有 与 无）,单边文件，只有一边有
        sums_same_filename            文件路径一样，文件内容不一样的文件路径
        diff_contents_same_filename   文件路径一样，文件内容不一样的具体体现
        common_file_list              相同的文件路径（debug 模式才生成）
    以下各文件 均有 src 中 文件 与 already_known_diff 中同名文件对比所得，diff后的结果放在fixed 下 同名文件内。
    fixed    
        unilateral_dirs
        unilateral_files
        sums_same_filename
        diff_contents_same_filename                
        common_file_list
<br/>
<br/>
#### 原始版  时间20191104， public 与 专有云-master分支 对比而得, 最原始版
**already_known_diff**        
    unilateral_dirs                     不一样的文件目录
    unilateral_files                    不一样的文件
    sums_same_filename            文件路径一样，文件内容不一样的文件路径
    diff_contents_same_filename         文件路径一样，文件内容不一样的具体体现
    common_file_list                  相同的文件路径
<br/>
<br/>
<br/>
## 操作说明
```
python diff_all.py
--tianji_access_key_id=“xxxxx”  
--tianji_access_key_secret="xxxxx"
--tianji_endpoint="xxxx"
--tianji_project="xxxx"
--public_service_name="xxxx"
--private_git_name="xxxx"
--public_template_name="xxxx"
--private_template_name="xxxx"
--private_git_repo="xxxx"
```
示例：
`python diff_all.py
--tianji_access_key_id=“xxxxx”  --tianji_access_key_secret="xxxxx"`
得到 sls-backend-server 下 public 与 私有云 master 的 diff.