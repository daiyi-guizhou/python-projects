#/bin/bash
which nvidia-smi > /dev/null
if [ $? -eq 0 ]
then
    num=`timeout 10 nvidia-smi | wc -l`    # timeout : if the time of command is longer than 30s, the precess of command "nvidia-smi" will be killed 
    if [ -n $num ];then
        echo $num
    else
        echo 2 
    fi
else
    echo 4
fi




