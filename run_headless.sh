#!/bin/bash


## Wait until previous TCP sessions are closed
count=$(netstat -at | grep -c 9000)
if [ $count -gt 0 ]; then
    echo "Waiting for existing TCP connections to end..."
fi 
while [ $count -gt 0 ]
do
    sleep 1
    count=$(netstat -at | grep -c 9000)
done

## Kill existing TCP connections
#ss -K dst 0.0.0.0 dport = 9000
echo "Starting fHDHR-YouTube TV"
export DISPLAY=:99 & xvfb-run --listen-tcp --server-num 99 --auth-file /tmp/xvfb.auth -s "-ac -screen 0 1280x720x24" python3 main.py $1
export DISPLAY=:0
