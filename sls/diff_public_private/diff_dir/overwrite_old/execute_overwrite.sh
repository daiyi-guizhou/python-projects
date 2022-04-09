#!/bin/bash
set -e -o errtrace -o pipefail
err() {
    echo "Error occurred:"
    awk 'NR>L-3 && NR<L+3 { printf "%-5d%3s%s\n",NR,(NR==L?">>>":""),$0 }' L=$1 $0
}
trap 'err $LINENO' ERR
function error_exit {
  echo "$1" 1>&2
  exit 1
}
ARGS=`getopt -o h:: --long "src_files:,dest_dir:,remove::" -n 'example.sh' -- "$@"`
if [ $? != 0 ]; then
    echo -e "EROOR, the ADD overwrite option is:  bash overwrite.sh --src_files=XXX --dest_dir=XX \n or the REMOVE overwrite  option is:  bash overwrite.sh --dest_dir=XX --remove"
    exit 1
fi
#echo $ARGS
#将规范化后的命令行参数分配至位置参数（$1,$2,...)
eval set -- "${ARGS}"
while true
do
    case "$1" in
        -h)
            echo -e "the ADD overwrite option is:  bash overwrite.sh --src_files=XXX --dest_dir=XX \n or the REMOVE overwrite  option is:  bash overwrite.sh --dest_dir=XX --remove"
            echo "--src_files is divided by ','"
            echo "--dest_dir is like '/cloud/app/service_a/ServiceRole_b#/app_c/current', it must start with '/cloud/app/service_a/ServiceRole_b#/app_c/' "
            echo "--remove ,when you want to remove overwrite"
            shift
            ;;
        --src_files)
            # echo "--src_files is $2";
            source_files_str=`echo $2 |sed 's/,/ /g'`;
            read -a source_files_list  <<< $source_files_str;
            for source_file in ${source_files_list[*]}
            do
               ( [[ -e $source_file ]] || [[ -d $source_file ]] ) || error_exit "$source_file no exist"
            done
            shift 2
            ;;
        --dest_dir)
            echo $2 | grep ^/cloud/app/ > /dev/null 2>&1 || error_exit "--dest_dir must start with '/cloud/app/'"
            # echo "--dest_dir is $2"
            dest_dir=$2
            shift 2
            ;;
        --remove)
            # echo "### remove overwrite"
            scripts_option="remove"
            shift 2
            ;;
        --)
            shift
            break
            ;;
        *)
            echo -e "EROOR, the ADD overwrite option is:  bash overwrite.sh --src_files=XXX --dest_dir=XX \n or the REMOVE overwrite  option is:  bash overwrite.sh --dest_dir=XX --remove"
            echo "Internal error!"
            exit 1
            ;;
    esac
done
#处理剩余的参数
for arg in $@
do
    echo "processing $arg"
done
write_overwrite_sh () {
## 基础样式
sudo cat > ./overwrite.sh << EOF
#!/bin/sh
current_dir=/cloud/app/service_name/ServiceRole#/app_name
sudo mkdir  -p \$current_dir/1350852_service_name_ServiceRole.overwrite
sudo /cloud/tool/tianji/overwrite add service_name ServiceRole# app_name 1350852_service_name_ServiceRole 30 -f  
sudo cp -pr \$current_dir/1350852_service_name_ServiceRole/* \$current_dir/1350852_service_name_ServiceRole.overwrite/
##### sudo /cloud/tool/tianji/overwrite remove service_name ServiceRole# app_name 1350852_service_name_ServiceRole  
##### sudo rm -rf /cloud/app/service_name/ServiceRole#/app_name/1350852_service_name_ServiceRole.overwrite
# echo '### restart SR '
sudo tjc stop service_name.ServiceRole# > /dev/null 2>&1 && sudo tjc start service_name.ServiceRole#  > /dev/null 2>&1;
EOF
}
get_common_varabiles () {
    ## 获取变量
    eval $(echo $dest_dir|awk -F"/cloud/app" '{print $2}'|awk -F"/" '{printf("Service=%s;SR=%s;APP=%s;",$2,$3,$4)}')
    local_source_dir="/cloud/app/"$Service"/"
    current_dir=`echo $dest_dir|awk -F'current' '{print $1}'`
    alread_install_dir=$current_dir'current/alread_installed'
    overwrite_script=$current_dir'overwrite.sh'
    machine_ip_str=`get_ip_on_ops -ip -r $Service'.'$SR`  ## get ip_list from ops_machine
    read -a machine_ip_list  <<< $machine_ip_str
    echo `ssh -l root ${machine_ip_list[0]} ls -l $current_dir` > BuildID_str
    BuildID=`cat BuildID_str|grep current|awk -F'-> ' '{print $2}'|awk '{print $1}'|sed 's/.overwrite//g'`
    # echo "### buildID:",$BuildID
}
fix_overwrite_sh () {
    ## 修改overwrite.sh 为正确值。
    sudo chmod +x ./overwrite.sh                          
    sudo sed -i "s/1350852_service_name_ServiceRole/$BuildID/g" ./overwrite.sh  # 修改 buildID
    sudo sed -i "s/service_name/$Service/g" ./overwrite.sh             # 修改 service
    sudo sed -i "s/ServiceRole#/$SR/g" ./overwrite.sh             # 修改 SR
    sudo sed -i "s/app_name/$APP/g" ./overwrite.sh  # 修改 application
}
get_remote_varabiles () {
    restart_SR_cmd=`tail -n 1 overwrite.sh`
    remove_overwrite_cmd=`tail -n 5 overwrite.sh|head -n 1|awk -F'##### ' '{print $2}'`
    re_overwrite_dir=`tail -n 4 overwrite.sh|head -n 1|awk -F'##### ' '{print $2}'`
}
build_overwrite () {
    ## scp
    scp_done=`scp -pr ./overwrite.sh   root@$machine_ip:/$current_dir > /dev/null 2>&1 &`
    echo `ssh -l  root $machine_ip sudo bash $overwrite_script`
    for source_file in ${source_files_list[*]}
    do  
        real_source_dir=`echo $source_file|awk -F"$local_source_dir" '{print $2}'`
        scp_done=`scp  -pr $source_file  root@$machine_ip:/$dest_dir/$real_source_dir > /dev/null 2>&1 &`
    done
    ## restart SR
    echo `ssh -l  root $machine_ip  rm -rf $current_dir'current/alread_installed'`  
    echo `ssh -l  root $machine_ip $restart_SR_cmd`  
}
remove_overwrite () {
    echo `ssh -l  root $machine_ip "$remove_overwrite_cmd > /dev/null 2>&1 &"`
    echo `ssh -l  root $machine_ip "$re_overwrite_dir > /dev/null 2>&1 &"`
}
main () {
    for machine_ip in ${machine_ip_list[*]}
    do
        if [ $scripts_option ]
        then
            remove_overwrite
            echo "### Remove overwrite, $Service/$SR/$APP/$BuildID on $machine_ip successfully"
        elif [ $dest_dir ] && [ $source_files_list ]
        then
            build_overwrite
            echo "### Execute overwrite $Service/$SR/$APP/$BuildID on $machine_ip successfully!"
        fi
    done  
}
write_overwrite_sh
get_common_varabiles
fix_overwrite_sh
get_remote_varabiles
main