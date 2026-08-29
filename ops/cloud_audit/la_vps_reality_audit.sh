#!/usr/bin/env bash
# Moodify Cloud Production 001-A — LA VPS (103.144.246.242) Reality Audit
#
# 性质:
#   - 只读 (Read-only audit)
#   - 不修改任何文件 / 服务 / 数据库 / 配置
#   - 不安装任何软件
#   - 不创建 / 删除云资源
#   - 不打印任何 secret / token / AccessKey / password / private key
#
# 使用方式:
#   # 方式 1: 在目标 VPS 上直接运行 (ops SSH 登录后)
#   ssh ops@103.144.246.242
#   bash aliyun_ecs_reality_audit.sh
#
#   # 方式 2: 远程执行 (推荐,零文件传输)
#   ssh ops@103.144.246.242 'bash -s' < aliyun_ecs_reality_audit.sh
#
#   # 方式 3: 通过 GitHub Actions / CI runner 在 VPS 上拉取后运行
#   # (不建议; 直接 SSH 更简单)
#
# 输出:
#   stdout: TS-prefixed 行 → 人工复制到
#     docs/cloud/LA_VPS_REALITY_REPORT_2026-08-24.md
#   无副作用: 不写文件, 不创建日志
#
# 已知约束 (来自本地 probe, 2026-08-24):
#   - moodify-api (:8000) / moodify-music (:3100) / music-bff (:8100)
#     不对外暴露,仅在 127.0.0.1 监听
#     → 审计这些服务必须通过 SSH 进入 VPS 后用 localhost 探测
#   - rongjinwenchuan.xyz 域名解析状态未知
#     → 审计域名路由需独立检查
#
# 参考:
#   - CURRENT_ARCHITECTURE.md §1 (P00 扫描 2026-08-17)
#   - INTERNAL_SYSTEMS.md §3-4 (state machine + 外部能力分类)
#   - docs/cloud/CLOUD_EXECUTION_CHECKLIST.md §5 (触发条件 9 项)
#   - ops/cloud_audit/aliyun_ecs_reality_audit.README.md (通用说明)

set -u

TARGET="${1:-$(hostname 2>/dev/null || echo la-vps)}"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
REPORT_DATE="2026-08-24"

echo "============================================================"
echo " Moodify Cloud Production 001-A — LA VPS Reality Audit"
echo "============================================================"
echo " target          : $TARGET"
echo " target_ip       : 103.144.246.242 (亿速云)"
echo " audit_ts       : $TS"
echo " audit_kind     : read-only (SSH required)"
echo " report_output  : docs/cloud/LA_VPS_REALITY_REPORT_2026-08-24.md"
echo "============================================================"

# secrets 排除模式 (来自 ops/web_origin/scan_secrets.sh)
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
  echo "--- lscpu (summary) ---"
  if command -v lscpu >/dev/null 2>&1; then
    lscpu | grep -E '^(Architecture|CPU\(s\)|Model name|CPU MHz|Cache)' || lscpu | head -20
  else
    echo "lscpu: not installed"
  fi
  echo "--- free -h ---"
  free -h 2>&1 || echo "free: unavailable"
  echo "--- df -h (mounted filesystems) ---"
  df -h 2>&1 || echo "df: unavailable"
  echo "--- /proc/diskstats (disk model) ---"
  if [ -f /proc/diskstats ]; then
    head -5 /proc/diskstats
  fi
}

# ---- Step 2: 系统服务 ----------------------------------------------
step_services() {
  echo ""
  echo "[Step 2] System services (state=running)"
  if command -v systemctl >/dev/null 2>&1; then
    echo "--- running services (total) ---"
    systemctl list-units --type=service --state=running --no-pager 2>&1 | grep -E '(moodify|nginx|docker|cloudflare|mysql|postgres|redis)' || echo "no matching services found"
    echo "--- all running ---"
    systemctl list-units --type=service --state=running --no-pager 2>&1 | wc -l
    echo "--- key service status ---"
    for svc in nginx docker cloudflared mysql mariadb postgres redis-server redis moodify-api moodify-music moodify-worker moodify-data-worker; do
      active=$(systemctl is-active "$svc" 2>/dev/null || true)
      enabled=$(systemctl is-enabled "$svc" 2>/dev/null || true)
      echo "  $svc : active=$active enabled=$enabled"
    done
  else
    echo "systemctl: not available (no systemd)"
    echo "--- ps aux (key processes) ---"
    ps aux 2>/dev/null | grep -E '(nginx|docker|cloudflare|moodify|mysql|postgres|redis)' | grep -v grep | head -20 || true
  fi
}

# ---- Step 3: Docker 环境 -------------------------------------------
step_docker() {
  echo ""
  echo "[Step 3] Docker environment"
  if command -v docker >/dev/null 2>&1; then
    echo "--- docker version ---"
    docker version 2>&1 | grep -E '(Version|API|Go)' | head -10 || true
    echo "--- docker ps -a ---"
    docker ps -a --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" 2>&1
    echo "--- docker images ---"
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" 2>&1 | head -20
    echo "--- docker volume ls ---"
    docker volume ls 2>&1 | head -20
    echo "--- docker network ls ---"
    docker network ls 2>&1 | head -20
    echo "--- moodify-audiolla (if present) ---"
    docker ps -a --filter "name=audiolla" --format "{{.ID}} {{.Status}} {{.Ports}}" 2>&1 || echo "no audiolla container"
    echo "--- docker container inspect (moodify only, keys only) ---"
    for c in $(docker ps --format '{{.Names}}' 2>/dev/null | grep -i moodify | head -10); do
      echo "  container: $c"
      docker inspect "$c" 2>/dev/null | grep -E '"(Image|State|Status|NetworkMode|PortBindings)"' | head -10 || true
    done
  else
    echo "docker: not installed"
  fi
}

# ---- Step 4: Moodify 目录扫描 (无 secrets) -------------------------
step_moodify_dirs() {
  echo ""
  echo "[Step 4] Moodify directories (secrets redacted)"
  echo "--- moodify processes ---"
  ps -ef 2>/dev/null | grep -E '(moodify|python|uvicorn|gunicorn|node|fworker)' | grep -v grep | head -20 || true
  echo "--- moodify dirs ---"
  for base in /opt /home /root /var/www /var/lib /srv; do
    if [ -d "$base" ]; then
      found=$(find "$base" -maxdepth 4 -type d \( -name 'moodify*' -o -name '*.moodify*' \) 2>/dev/null | head -10)
      if [ -n "$found" ]; then
        echo "  $base:"
        echo "$found" | sed 's/^/    /'
      fi
    fi
  done
  echo "--- docker-compose files ---"
  find /opt /home /root /var/www /var/lib -maxdepth 5 -type f \( -name 'docker-compose.yml' -o -name 'docker-compose.yaml' \) 2>/dev/null | head -10 | while read -r f; do
    echo "  found: $f (content not printed — review manually if needed)"
  done
  echo "--- .env files (paths only, no content) ---"
  find /opt /home /root /var/www /var/lib -maxdepth 5 -type f -name '.env' 2>/dev/null | head -10 | while read -r f; do
    echo "  found: $f (content NOT printed — copy to local for review, keep out of git)"
  done
}

# ---- Step 5: 网络监听 ---------------------------------------------
step_network() {
  echo ""
  echo "[Step 5] Listening ports"
  if command -v ss >/dev/null 2>&1; then
    ss -tulpn 2>&1 | head -60
  elif command -v netstat >/dev/null 2>&1; then
    netstat -tulpn 2>&1 | head -60
  else
    echo "ss/netstat: not available"
    cat /proc/net/tcp 2>/dev/null | head -20
  fi
  echo "--- key port check (localhost) ---"
  for port in 80 443 8000 8100 3100 18080 3306 5432 6379; do
    if timeout 2 bash -c "echo >/dev/tcp/127.0.0.1/$port" 2>/dev/null; then
      echo "  port $port : LISTENING"
    else
      echo "  port $port : not listening"
    fi
  done
  echo "--- cloudflared tunnel status ---"
  if command -v systemctl >/dev/null 2>&1; then
    systemctl status cloudflared 2>&1 | head -10 || echo "cloudflared: not found as systemd service"
  fi
  ps aux 2>/dev/null | grep cloudflared | grep -v grep | head -5 || true
}

# ---- Step 6: 数据库状态 (只读) ------------------------------------
step_databases() {
  echo ""
  echo "[Step 6] Database state (read-only, list only)"
  echo "--- mysql ---"
  if command -v mysql >/dev/null 2>&1; then
    mysql --version 2>&1
    echo "(database list: requires auth — use mysql -u root -p or skip)"
    echo "(DO NOT print passwords in audit output)"
  else
    echo "mysql client: not installed"
  fi
  echo "--- mariadb ---"
  if command -v mariadb >/dev/null 2>&1; then
    mariadb --version 2>&1
  else
    echo "mariadb client: not installed"
  fi
  echo "--- psql ---"
  if command -v psql >/dev/null 2>&1; then
    psql --version 2>&1
  else
    echo "psql client: not installed"
  fi
  echo "--- redis-cli ---"
  if command -v redis-cli >/dev/null 2>&1; then
    redis-cli --version 2>&1
  else
    echo "redis-cli: not installed"
  fi
  echo "--- SQLite moodify files (list only) ---"
  find /var/lib /opt /home /root -maxdepth 6 -type f -name '*.db' 2>/dev/null | grep -iE '(moodify|ear|music|qa|data)' | head -20 || true
  echo "  (DO NOT open / copy these files — list only)"
  echo "--- /var/lib/moodify ---"
  if [ -d /var/lib/moodify ]; then
    ls -lh /var/lib/moodify 2>/dev/null | head -20
    du -sh /var/lib/moodify 2>/dev/null || true
  else
    echo "/var/lib/moodify: not found"
  fi
}

# ---- Step 7: 阿里云 / 亿速云工具 -----------------------------------
step_cloud_tools() {
  echo ""
  echo "[Step 7] Cloud provider tooling"
  echo "--- aliyun cli ---"
  if command -v aliyun >/dev/null 2>&1; then
    aliyun version 2>&1 | head -3 || true
    echo "(DO NOT print AccessKey / SecretKey)"
  else
    echo "aliyun cli: not installed"
  fi
  echo "--- ossutil ---"
  if command -v ossutil >/dev/null 2>&1; then
    ossutil --version 2>&1 | head -3 || true
    echo "(DO NOT print credentials)"
  else
    echo "ossutil: not installed"
  fi
  echo "--- awscli (S3) ---"
  if command -v aws >/dev/null 2>&1; then
    aws --version 2>&1 | head -3 || true
  else
    echo "awscli: not installed"
  fi
  echo "--- cloudflare (cloudflared) ---"
  if command -v cloudflared >/dev/null 2>&1; then
    cloudflared --version 2>&1 | head -3 || true
  else
    echo "cloudflared binary: not in PATH (may be running as systemd service)"
  fi
  echo "--- ALIYUN_* / OSS_* / AWS_* env vars (values redacted) ---"
  env 2>/dev/null | grep -iE '^(ALIYUN|ALIBABA|OSS_|AWS_|AK_|MOODIFY_)' | sed -E 's/=(.{0,4}).*/=\1***REDACTED***/' | head -20 || true
}

# ---- Step 8: 本地 HTTP 探测 (localhost) ----------------------------
step_local_http() {
  echo ""
  echo "[Step 8] Local HTTP health probes (localhost only)"
  echo "--- nginx (localhost:80) ---"
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://127.0.0.1/" 2>/dev/null || echo "FAIL")
  echo "  GET / -> $code"
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://127.0.0.1/healthz" 2>/dev/null || echo "FAIL")
  echo "  GET /healthz -> $code"
  echo "--- moodify-api (localhost:8000) ---"
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://127.0.0.1:8000/health" 2>/dev/null || echo "FAIL")
  echo "  GET localhost:8000/health -> $code"
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://127.0.0.1:8000/ready" 2>/dev/null || echo "FAIL")
  echo "  GET localhost:8000/ready -> $code"
  echo "--- moodify-music (localhost:3100) ---"
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://127.0.0.1:3100/" 2>/dev/null || echo "FAIL")
  echo "  GET localhost:3100/ -> $code"
  echo "--- music-bff (localhost:8100) ---"
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://127.0.0.1:8100/api/v1/music/bootstrap" 2>/dev/null || echo "FAIL")
  echo "  GET localhost:8100/api/v1/music/bootstrap -> $code"
  echo "--- moodify-audiolla (localhost:18080) ---"
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://127.0.0.1:18080/" 2>/dev/null || echo "FAIL")
  echo "  GET localhost:18080/ -> $code"
}

# ---- Step 9: 域名 / DNS 路由检查 -----------------------------------
step_dns_route() {
  echo ""
  echo "[Step 9] Domain routing check"
  echo "--- rongjinwenchuan.xyz NS lookup ---"
  if command -v nslookup >/dev/null 2>&1; then
    nslookup rongjinwenchuan.xyz 2>&1 | head -10 || true
  elif command -v dig >/dev/null 2>&1; then
    dig rongjinwenchuan.xyz 2>&1 | head -15 || true
  else
    echo "nslookup/dig: not available"
  fi
  echo "--- rongjingmusic.com NS lookup ---"
  if command -v nslookup >/dev/null 2>&1; then
    nslookup rongjingmusic.com 2>&1 | head -10 || true
  elif command -v dig >/dev/null 2>&1; then
    dig rongjingmusic.com 2>&1 | head -15 || true
  fi
  echo "--- nginx vhost config (listen 80; domains) ---"
  for conf in /etc/nginx/sites-enabled/ /etc/nginx/conf.d/; do
    if [ -d "$conf" ]; then
      find "$conf" -type f -name '*.conf' 2>/dev/null | head -10 | while read -r f; do
        echo "  $f:"
        grep -E '(server_name|listen 80|listen 443)' "$f" 2>/dev/null | head -10 || true
      done
    fi
  done
}

# ---- main ----------------------------------------------------------
step_basic
step_services
step_docker
step_moodify_dirs
step_network
step_databases
step_cloud_tools
step_local_http
step_dns_route

echo ""
echo "============================================================"
echo " Audit complete."
echo "============================================================"
echo ""
echo " Next steps for ops:"
echo ""
echo " 1. Copy the output above into:"
echo "      docs/cloud/LA_VPS_REALITY_REPORT_2026-08-24.md"
echo "      (replace [PENDING] placeholders with actual values)"
echo ""
echo " 2. Fill in all [PENDING] sections in that report."
echo ""
echo " 3. Answer the §11 Recommendation triggers from"
echo "      docs/cloud/CLOUD_EXECUTION_CHECKLIST.md §5"
echo ""
echo " 4. Have owner sign off."
echo ""
echo " 5. Submit to repo — DO NOT include any credentials,"
echo "    AccessKeys, passwords, or private keys."
echo ""
echo " This script does NOT modify the target system."
echo " If you observe any side effect, stop and file a bug."
echo ""

exit 0