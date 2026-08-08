"""Download all useful data from cloud server before it expires."""
import paramiko
import os

host = os.environ.get("MOODIFY_CLOUD_HOST", "43.156.175.4")
user = os.environ.get("MOODIFY_CLOUD_USER", "ubuntu")
password = os.environ["MOODIFY_CLOUD_PASSWORD"]
repo = "/home/ubuntu/moodify-mainline"
local_dir = os.environ.get("MOODIFY_CLOUD_DATA_DIR", "cloud_data")

os.makedirs(local_dir, exist_ok=True)

import time
import socket

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

for attempt in range(5):
    try:
        print(f"Connection attempt {attempt+1}/5...")
        client.connect(host, port=22, username=user, password=password,
                       timeout=30, banner_timeout=30, auth_timeout=30)
        print("Connected!")
        break
    except (socket.timeout, paramiko.SSHException) as e:
        print(f"  Failed: {e}")
        if attempt < 4:
            time.sleep(10)
        else:
            raise

def run(cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(out)
    if err:
        print(f"  [err]: {err}")

# Step 1: Check sizes of priority directories
print("=" * 60)
print("STEP 1: Size check")
print("=" * 60)
run(f"du -sh {repo}/reports {repo}/logs {repo}/data")
run(f"du -sh {repo}/outputs/tidal_runs {repo}/outputs/pdf_reports {repo}/outputs/nem_* {repo}/outputs/mt001_* {repo}/outputs/full_test_v02 {repo}/outputs/tidal {repo}/outputs/tidal_manual")
run(f"du -sh {repo}/treatment_records {repo}/night")

# Step 2: Also check for important configs
print("\n" + "=" * 60)
print("STEP 2: Configs and scripts check")
print("=" * 60)
run(f"du -sh {repo}/configs {repo}/scripts {repo}/workers")

# Step 3: Create bundle on server
print("\n" + "=" * 60)
print("STEP 3: Creating bundle of priority data")
print("=" * 60)

# Bundle command - tar up the most important stuff
bundle_cmd = f"""
cd {repo} && tar czf /home/ubuntu/moodify_data_backup.tar.gz \
  reports/ \
  logs/ \
  data/ \
  outputs/tidal_runs/ \
  outputs/pdf_reports/ \
  outputs/nem_mrs_002/ \
  outputs/nem_validate_001/ \
  outputs/mt001_smoke/ \
  outputs/mt001_gate3_real_ai/ \
  outputs/full_test_v02/ \
  outputs/manifest.json \
  outputs/metadata.json \
  outputs/MAP_CHAIN_VERSION \
  outputs/validation_report.json \
  outputs/environment.txt \
  treatment_records/ \
  night/ \
  configs/ \
  scripts/ \
  workers/ \
  2>&1
echo "EXIT: $?"
"""
run(bundle_cmd)

# Step 4: Check bundle size
print("\n" + "=" * 60)
print("STEP 4: Bundle size")
print("=" * 60)
run("ls -lh /home/ubuntu/moodify_data_backup.tar.gz")

client.close()
