count1=0
for time in `cat /var/log/syslog | grep  -E  'new_blow read failed' | grep $1 | tail -n 100 | awk '{print $3}'`
do
  d=$(( `date +%s` - `date +%s -d "$time"` ))
  if (( d < (( $2*2 ))  )) ; then
    (( count1 += 1 ))
  fi
done
count2=0
for time in `cat /var/log/syslog | grep  -E  'camera open failed' | grep $1 | tail -n 100 | awk '{print $3}'`
do
  d=$(( `date +%s` - `date +%s -d "$time"` ))
  if (( d < (( $2*2 )) )) ; then
    (( count2 += 1 ))
  fi
done
declare -A dic
dic=(["blow00"]="2f4e:0004" ["blow01"]="2f4e:0005")
if (( `lsusb | grep ${dic[$1]} | wc -l` == 0 )); then
  #echo "usb broken"
  echo -1
elif (( count2 > 0 )); then
  #echo "open failed"
  echo -1
elif (( count1 > 3 )); then
  #echo "read failed"
  echo -3
else
  #echo "test pass"
  echo 1
fi

