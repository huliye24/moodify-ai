#!/usr/bin/env bash
# Moodify Cloud Production 001-A — Aliyun ECS Reality Audit
#
# 目标:
#   在目标 ECS (杭州 120.55.191.146 或 LA 103.144.246.242 或其他)
#   上一次性只读扫描真实运行时状态,作为 Cloud Production Implementation
#   触发条件 (CLOUD_EXECUTION_CHECKLIST.md §5) 的事实基础。
#
# 性质:
#   - 只读 (Read-only audit)
#   - 不修改任何文件 / 服务 / 数据库 / 配置
#   - 不安装任何软件
#   - 不创建 / 删除云资源
#   - 不打印任何 secret / token / AccessKey / password / private key
#
# 触发:
#   由 ops 工程师通过 SSH 在目标 ECS 上运行。
#   不通过本仓库的任何 CI 自动触发。
#
# 参考:
#   - docs/cloud/CLOUD_PRODUCTION_V0.1.md
#   - docs/cloud/CLOUD_EXECUTION_CHECKLIST.md §5
#   - docs/cloud/REALITY_AUDIT_RUNBOOK.md
#   - docs/reduction/REDUCTION_EXECUTION_001_REPORT.md
#   - CURRENT_ARCHITECTURE.md §1 (历史快照, 本审计独立验证)
#   - INTERNAL_SYSTEMS.md §4 (外部能力分类)
#
# 既有 ops 模板模式:
#   - ops/web_origin/probe_resources.sh  (set -u, TS-prefixed 输出)
#   - ops/ear_batch/remote/remote_preflight.sh (set -euo pipefail)
#   - ops/web_origin/scan_secrets.sh (PATTERNS + EXCLUDE)
#
# 输出:
#   - stdout: TS-prefixed 行, 由 ops 工程师人工复制到
#     docs/cloud/ALIYUN_ECS_REALITY_REPORT_2026-08-24.md
#   - 不写文件 (本脚本本身无副作用; 不创建日志目录)
#
# 用法:
#   ssh ops@<target-ecs>
#   bash aliyun_ecs_reality_audit.sh [target_label]
#     target_label 默认 = 当前 hostname
#   # 或远程:
#   ssh ops@<target-ecs> 'bash -s' < aliyun_ecs_reality_audit.sh <target_label>

set -u
# 注意: 不开 -e (某些命令失败是预期的, 比如未安装的命令; 我们只报告)
# 注意: 不开 -o pipefail (某些管道失败不影响整体审计)

TARGET="${1:-$(hostname 2>/dev/null || echo unknown)}"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "============================================================"
echo " Moodify Cloud Production 001-A — Aliyun ECS Reality Audit"
echo "============================================================"
echo " target_label : $TARGET"
echo " audit_ts     : $TS"
echo " audit_kind   : read-only"
echo "============================================================"

# 复用既有 secrets 排除模式 (来自 ops/web_origin/scan_secrets.sh)
SECRET_REDACT_PATTERN='(PRIVATE KEY|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|sk-[A-Za-z0-9]{20,}|xox[baprs]-|MOODIFY_BFF_SESSION_SECRET|MOODIFY_INTERNAL_API_KEY|MOODIFY_HANGZHOU_KEY|MOODIFY_DB_PASSWORD)'

# ---- Step 1: 基础信息 ----------------------------------------------
step_basic() {
  echo ""
  echo "[Step 1] Basic server info"
  echo "--- uname ---"
  uname -a 2>&1 || echo "uname: unavailable"
  echo "--- /etc/os-release ---"
  if [ -f /etc/os-release ]; then
    cat /etc/os-release
  else
    echo "/etc/os-release: not found"
  fi
  echo "--- hostname ---"
  hostname 2>&1 || echo "hostname: unavailable"
  echo "--- uptime ---"
  uptime 2>&1 || echo "uptime: unavailable"
  echo "--- lscpu (cores) ---"
  if command -v lscpu >/dev/null 2>&1; then
    lscpu | grep -E '^(Architecture|CPU\(s\)|Model name|CPU MHz)' || lscpu | head -20
  else
    echo "lscpu: not installed"
  fi
  echo "--- free -h ---"
  free -h 2>&1 || echo "free: unavailable"
  echo "--- df -h ---"
  df -h 2>&1 || echo "df: unavailable"
}

# ---- Step 2: 系统服务 ----------------------------------------------
step_services() {
  echo ""
  echo "[Step 2] System services (state=running)"
  if command -v systemctl >/dev/null 2>&1; then
    systemctl list-units --type=service --state=running --no-pager 2>&1 | head -60
  else
    echo "systemctl: not available (no systemd?)"
    echo "--- service --status-all ---"
    service --status-all 2>&1 | head -40 || true
  fi
  echo "--- key services ---"
  for svc in nginx docker cloudflared mysql postgres redis-server redis moodify-api moodify-music moodify-worker moodify-data-worker; do
    if command -v systemctl >/dev/null 2>&1; then
      status=$(systemctl is-active "$svc" 2>&1 || true)
      enabled=$(systemctl is-enabled "$svc" 2>&1 || true)
      echo "  $svc : active=$status enabled=$enabled"
    else
      echo "  $svc : systemctl unavailable"
    fi
  done
}

# ---- Step 3: Docker 环境 -------------------------------------------
step_docker() {
  echo ""
  echo "[Step 3] Docker environment"
  if command -v docker >/dev/null 2>&1; then
    echo "--- docker version ---"
    docker version 2>&1 | head -20 || true
    echo "--- docker ps -a ---"
    docker ps -a 2>&1 || echo "docker ps: failed"
    echo "--- docker images ---"
    docker images 2>&1 || echo "docker images: failed"
    echo "--- docker volume ls ---"
    docker volume ls 2>&1 || echo "docker volume ls: failed"
    echo "--- docker network ls ---"
    docker network ls 2>&1 || echo "docker network ls: failed"
  else
    echo "docker: not installed"
  fi
}

# ---- Step 4: Moodify 目录扫描 (无 secrets) -------------------------
step_moodify_dirs() {
  echo ""
  echo "[Step 4] Moodify directory scan (secrets redacted)"
  for base in /opt /home /root /var/www /var/lib; do
    if [ -d "$base" ]; then
      echo "--- $base ---"
      find "$base" -maxdepth 3 -type d \( -name 'moodify*' -o -name 'docker-compose*' \) 2>/dev/null | head -20 || true
      find "$base" -maxdepth 4 -type f \( -name 'docker-compose.yml' -o -name 'docker-compose.yaml' -o -name '.env' \) 2>/dev/null | head -10 | while read -r f; do
        echo "  found: $f"
        echo "    (content redacted — secrets and full config not printed in audit)"
      done
    fi
  done
  echo "--- running processes ---"
  ps -ef 2>/dev/null | grep -E '(moodify|python|uvicorn|gunicorn|node|fworker)' | grep -v grep | head -20 || true
}

# ---- Step 5: 网络监听 ---------------------------------------------
step_network() {
  echo ""
  echo "[Step 5] Listening ports"
  if command -v ss >/dev/null 2>&1; then
    ss -tulpn 2>&1 | head -40 || true
  elif command -v netstat >/dev/null 2>&1; then
    netstat -tulpn 2>&1 | head -40 || true
  else
    echo "ss / netstat: not available"
    cat /proc/net/tcp 2>/dev/null | head -10 || true
  fi
  echo "--- key port reachability (loopback) ---"
  for port in 80 443 8000 8100 3100 18080; do
    if timeout 2 bash -c "</dev/tcp/127.0.0.1/$port" 2>/dev/null; then
      echo "  port $port : LISTENING (loopback open)"
    else
      echo "  port $port : not listening on loopback"
    fi
  done
}

# ---- Step 6: 数据库状态 (只读) --------------------------------------
step_databases() {
  echo ""
  echo "[Step 6] Database state (read-only)"
  echo "--- mysql ---"
  if command -v mysql >/dev/null 2>&1; then
    mysql --version 2>&1 || true
    echo "(skip list of databases — requires auth; record credentials separately, never in this output)"
  else
    echo "mysql client: not installed"
  fi
  echo "--- psql ---"
  if command -v psql >/dev/null 2>&1; then
    psql --version 2>&1 || true
    echo "(skip database list — requires auth)"
  else
    echo "psql client: not installed"
  fi
  echo "--- redis-cli ---"
  if command -v redis-cli >/dev/null 2>&1; then
    redis-cli --version 2>&1 || true
  else
    echo "redis-cli: not installed"
  fi
  echo "--- local SQLite files (moodify related) ---"
  find /var/lib /opt /home /root -maxdepth 6 -type f -name '*.db' 2>/dev/null | grep -iE '(moodify|ear|music|qa)' | head -20 || true
  echo "  (Do NOT open or copy these — list only)"
}

# ---- Step 7: 阿里云工具 --------------------------------------------
step_aliyun_tools() {
  echo ""
  echo "[Step 7] Aliyun tooling"
  if command -v aliyun >/dev/null 2>&1; then
    aliyun version 2>&1 | head -5 || true
    echo "  (configured profile names: aliyun configure list 2>&1 | head -5 — DO NOT print AccessKey)"
  else
    echo "aliyun cli: not installed"
  fi
  if command -v ossutil >/dev/null 2>&1; then
    ossutil --version 2>&1 | head -3 || true
    echo "  (DO NOT print AccessKey / SecretKey / configured bucket credentials)"
  else
    echo "ossutil: not installed"
  fi
  echo "--- ALIYUN_* environment variables (values redacted) ---"
  env 2>/dev/null | grep -E '^(ALIYUN_|ALIBABA_|OSS_|AK_)' | sed -E 's/=(.{0,4}).*/=\1***REDACTED***/' | head -20 || true
  echo "  (values above are first-4-chars preview only; full values never printed)"
}

# ---- Step 8: 输出说明 -----------------------------------------------
step_summary() {
  echo ""
  echo "============================================================"
  echo " Audit complete."
  echo "============================================================"
  echo ""
  echo " Next steps for ops:"
  echo ""
  echo " 1. Copy the output above (without secrets) into:"
  echo "      docs/cloud/ALIYUN_ECS_REALITY_REPORT_2026-08-24.md"
  echo ""
  echo " 2. Fill in the corresponding section headers in that file."
  echo ""
  echo " 3. Confirm or refute each existing item from"
  echo "      CURRENT_ARCHITECTURE.md §1"
  echo ""
  echo " 4. Do NOT commit any credential, AccessKey, or password."
  echo ""
  echo " 5. After report is filed, the report answers:"
  echo "      Does this target ECS satisfy the Cloud Production"
  echo "      Implementation 001 triggers from"
  echo "      docs/cloud/CLOUD_EXECUTION_CHECKLIST.md §5 ?"
  echo ""
  echo " 6. Submit the report to owner for sign-off before any"
  echo "    provisioning action."
  echo ""
  echo " Audit script does NOT alter the target system."
  echo " If you observe any side effect, stop and file a bug."
}

# ---- main ----------------------------------------------------------
step_basic
step_services
step_docker
step_moodify_dirs
step_network
step_databases
step_aliyun_tools
step_summary

exit 0