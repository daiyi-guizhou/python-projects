#!/bin/bash
i=`grep 'useRemoteTfServer: 1' /opt/flaw_checker/config.yaml | wc -l`
#echo $i
if [ $i == 1 ];then
	echo 1
	systemctl enable daiyi-gpu-alive.service
	systemctl restart daiyi-gpu-alive.service
else
	echo 0
fi
