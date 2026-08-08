"""Check what data/outputs exist on cloud server."""
import os

import paramiko

host = os.environ.get("MOODIFY_CLOUD_HOST", "43.156.175.4")
user = os.environ.get("MOODIFY_CLOUD_USER", "ubuntu")
password = os.environ["MOODIFY_CLOUD_PASSWORD"]

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=22, username=user, password=password)

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(out)
    if err:
        print(f"[stderr]: {err}")

print("=" * 60)
print("DATA DIRECTORY SIZES (mainline)")
print("=" * 60)
run('cd /home/ubuntu/moodify-mainline && du -sh data/ outputs/ reports/ logs/ runs/ 2>/dev/null')

print("\n" + "=" * 60)
print("DATA/ CONTENTS")
print("=" * 60)
run('ls -la /home/ubuntu/moodify-mainline/data/')

print("\n" + "=" * 60)
print("OUTPUTS/ CONTENTS")
print("=" * 60)
run('ls -la /home/ubuntu/moodify-mainline/outputs/')

print("\n" + "=" * 60)
print("REPORTS/ CONTENTS (top level)")
print("=" * 60)
run('ls -la /home/ubuntu/moodify-mainline/reports/')

print("\n" + "=" * 60)
print("LOGS/ CONTENTS")
print("=" * 60)
run('ls -la /home/ubuntu/moodify-mainline/logs/')

print("\n" + "=" * 60)
print("RUNS/ (if exists)")
print("=" * 60)
run('ls -la /home/ubuntu/moodify-mainline/runs/ 2>/dev/null || echo "runs/ NOT FOUND"')

print("\n" + "=" * 60)
print("LATEST OUTPUT SUBDIRS")
print("=" * 60)
run('ls -lt /home/ubuntu/moodify-mainline/outputs/ | head -20')

print("\n" + "=" * 60)
print("O3IS DATA FOR COMPARISON")
print("=" * 60)
run('cd /home/ubuntu/moodify-o3is && du -sh data/ outputs/ reports/ logs/ 2>/dev/null')

print("\n" + "=" * 60)
print("O3IS OUTPUTS SUBDIRS")
print("=" * 60)
run('ls -lt /home/ubuntu/moodify-o3is/outputs/ 2>/dev/null | head -15')

print("\n" + "=" * 60)
print("TOTAL SIZE PER DIR (mainline, 2 levels)")
print("=" * 60)
run('cd /home/ubuntu/moodify-mainline && du -sh outputs/*/ 2>/dev/null | sort -rh | head -15')

print("\n" + "=" * 60)
print("NIGHT DIRECTORY")
print("=" * 60)
run('ls -la /home/ubuntu/moodify-mainline/night/ && echo "---" && du -sh /home/ubuntu/moodify-mainline/night/')

print("\n" + "=" * 60)
print("TREATMENT RECORDS COUNT")
print("=" * 60)
run('cd /home/ubuntu/moodify-mainline && find treatment_records -type f | wc -l && echo "---" && ls treatment_records/')

print("\n" + "=" * 60)
print("ZIP FILES IN HOME")
print("=" * 60)
run('ls -lh /home/ubuntu/*.zip /home/ubuntu/*.tar.gz 2>/dev/null')

client.close()
