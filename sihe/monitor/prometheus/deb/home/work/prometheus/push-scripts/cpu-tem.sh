#!/bin/bash
tem=`sensors | grep -E "Package id 0: |Core *" | awk -F":" '{print $2}' | awk -F"." '{print $1}' | awk -F"+" '{print $2}' | awk '{printf("%s ",$0);}END{print}'`
echo $tem

### grep -E "Package id 0: |Core *"     ##in this command, 'Core *' should be at start without space.