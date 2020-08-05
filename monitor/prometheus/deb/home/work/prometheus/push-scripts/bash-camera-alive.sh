#!/bin/bash
num=`grep rtsp /opt/flaw_checker/config.yaml|wc -l`
grep rtsp /opt/flaw_checker/config.yaml | awk -F'/' '{ print $3 }'| awk -F':' '{ print $1 }' > /home/work/prometheus/push-scripts/ip_all.txt 

#cat /home/work/prometheus/push-scripts/ip_all.txt 
num_true=0
num_fail=0
#for i in {1..5}
for i in `seq 1 $num`
do
	if ping -c 1 `head -n $i /home/work/prometheus/push-scripts/ip_all.txt | tail -1` >/dev/null 2>&1
	then 
		#echo yes_ping
		num_true=$(($num_true + 1))
	else 
		#echo no_ping;
		#echo $i;
		num_fail=$(($num_fail + 1))
	fi
done

#echo $num_fail

if [ $num_fail == 0 ]
then
	echo 100
else
	echo $((100*$num_true/$num))
fi






