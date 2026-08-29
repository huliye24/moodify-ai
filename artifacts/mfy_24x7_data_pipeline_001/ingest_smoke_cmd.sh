set -x
# 1) staging file must be ignored
echo "partial-data" > /var/lib/moodify/staging/staging_test.wav.part
# 2) young inbox file must be ignored (min age 120s)
echo "young-data" > /var/lib/moodify/inbox/young_test.wav
# 3) old-enough inbox file must be ingested
echo "old-enough-data" > /var/lib/moodify/inbox/old_test.wav
touch -d "5 minutes ago" /var/lib/moodify/inbox/old_test.wav
# 4) duplicate of an already-ingested source must NOT be enqueued again
cp /var/lib/moodify/inbox/old_test.wav /var/lib/moodify/inbox/dup_test.wav
touch -d "5 minutes ago" /var/lib/moodify/inbox/dup_test.wav

BEFORE=$(/opt/moodify/.venv/bin/moodify-node status | /opt/moodify/.venv/bin/python -c "import json,sys; print(json.load(sys.stdin)['QUEUED']+json.load(sys.stdin)['RUNNING']+json.load(sys.stdin)['SUCCEEDED'])")

sudo -u moodify /opt/moodify/.venv/bin/python /opt/moodify/ops/data_node/inbox_ingest.py --inbox /var/lib/moodify/inbox --source-store /var/lib/moodify/sources --ledger-db /var/lib/moodify/ops/ingest.sqlite3 --node-cli /opt/moodify/.venv/bin/moodify-node --min-age-seconds 120 2>&1

echo "--- staging/young still present ---"
ls -la /var/lib/moodify/staging/ /var/lib/moodify/inbox/
echo "--- source store ---"
find /var/lib/moodify/sources -name "old_test.wav" -o -name "dup_test.wav" 2>/dev/null
echo "--- ledger ---"
/opt/moodify/.venv/bin/python -c "import sqlite3;con=sqlite3.connect('/var/lib/moodify/ops/ingest.sqlite3');[print(r) for r in con.execute('select source_sha256,substr(original_path,-20),substr(stored_path,-30),job_id from ingested_sources order by first_seen_at desc limit 3')]"
echo "--- queue delta ---"
AFTER=$(/opt/moodify/.venv/bin/moodify-node status | /opt/moodify/.venv/bin/python -c "import json,sys; print(json.load(sys.stdin)['QUEUED']+json.load(sys.stdin)['RUNNING']+json.load(sys.stdin)['SUCCEEDED'])")
echo "BEFORE=$BEFORE AFTER=$AFTER"
