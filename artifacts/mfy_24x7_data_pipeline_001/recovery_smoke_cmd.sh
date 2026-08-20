set -x
SRC=/var/lib/moodify/sources/sha256/da/da0e1a0666809c503784e9433cb8d079805aacd8d22283b1b9a5a1f4a573f69e/track_0.wav
/opt/moodify/.venv/bin/moodify-node enqueue "$SRC" > /tmp/recovery_enqueue.json
sleep 8
echo "--- before kill ---"
/opt/moodify/.venv/bin/moodify-node status
WPID=$(systemctl show -p MainPID --value moodify-data-worker.service)
echo "worker pid=$WPID"
kill -9 "$WPID"
sleep 2
echo "--- after kill, before restart ---"
/opt/moodify/.venv/bin/moodify-node status
systemctl start moodify-data-worker.service
sleep 5
echo "--- after restart ---"
/opt/moodify/.venv/bin/moodify-node status
sleep 40
echo "--- after drain ---"
/opt/moodify/.venv/bin/moodify-node status
/opt/moodify/.venv/bin/moodify-node jobs 2>/dev/null | /opt/moodify/.venv/bin/python -c "import json,sys; d=json.load(sys.stdin); [print(j['job_id'],j['status'],j['attempts'],j.get('last_error')) for j in d[:2]]"
journalctl -u moodify-data-worker --since '2 minutes ago' --no-pager -o cat | grep -Ei 'recover|started|stopped' | tail -5
