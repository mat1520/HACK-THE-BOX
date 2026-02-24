#!/bin/bash
# PASS1: apt-get install parallel curl -y #
# PASS2: chmod +x CVE-2023-43208.sh #
# FOLLOW ME MY GIT: https://github.com/J4F9S5D2Q7 #
# Dork: title:""Mirth Connect"" or title:""Mirth Connect Administrator"

clear
cat hosts | parallel -j5 'request=$(timeout 10 curl -ksI https://{}/api/server/version | grep -oP "GET, POST, DELETE, PUT" | head -n1)
if [ "$request" == "GET, POST, DELETE, PUT" ]
then
echo -e "{} - VULNERABLE!"
echo -e "{}" >> vulnerables.txt
else
echo -e "{} - FAIL."
fi'
