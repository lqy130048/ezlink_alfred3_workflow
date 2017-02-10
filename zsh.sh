# ./sudo.sh kill -9 $(ps -ax|grep obfuscated-ssh |awk '{print $1}')
# ./sudo.sh kill -9 $(ps -ax|grep privoxy |awk '{print $1}')

param=""
if  [ -n "$1"  ] ;then
    param=$1
fi

ssh_server=$(echo $param|awk -F '|' '{print $1}')
port=$(echo $param|awk -F '|' '{print $2}')
username=$(echo $param|awk -F '|' '{print $3}')
password=$(echo $param|awk -F '|' '{print $4}')
listen_port=$(echo $param|awk -F '|' '{print $5}')

./bin/sshpass -p $password ./bin/obfuscated-ssh -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -C2TNv -l $username -p $port -D $listen_port $ssh_server -Z usassh
