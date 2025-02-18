#!/bin/bash
#
# Record notifications from Chiadog to event files for parsing by Machinaris
#

event_priority_name="$1"
event_service_name="$2"
event_message="$3"
hostname="$(hostname -s)"
now="$(date +'%Y-%m-%d %H:%M:%S.%3N')"
unique_id="${hostname}_${blockchains}_${now}"
echo "${now} ${hostname} ${event_service_name} ${event_priority_name}: ${event_message}"

now_secs_only=$(echo "${now}" | sed 's/...$//')
cd /root/.chia/machinaris/dbs
sqlite3 -cmd '.timeout 5000' machinaris.db <<EOF
INSERT INTO alerts (unique_id,hostname,blockchain,priority,service,message,created_at) VALUES ('${unique_id}', '${hostname}', '${blockchains}','${event_priority_name//\'/\'\'}','${event_service_name//\'/\'\'}','${event_message//\'/\'\'}', '${now_secs_only}');
EOF
