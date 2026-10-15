#!/usr/bin/env bash
# deploy.sh — 幂等部署 Moodify CPU 节点 worker（在目标机器上运行）
#
# 由 sync.py 把仓库的 ops/cloud_worker/ 送到 /home/ubuntu/moodify-worker/.deploy/，
# 再从 .deploy/ 就位到 worker 根目录。用法：
#
#   bash .deploy/deploy.sh              # 就位全部
#   bash .deploy/deploy.sh --no-pip     # 跳过 awscli 安装（离线或 pypi 不通时）
#
# 设计原则：
#   - 幂等：可反复执行，重复执行不产生副作用（bashrc 追加有 grep 守卫）
#   - 不改运行态：systemd unit 只 install，绝不 enable/start
#     （未冒烟通过时 enable 会 crash loop，把日志和 S3 都打爆）
#   - 增量不删除：只覆盖同名文件，不 --delete（部署目录里有 work/ 与 logs/）
#   - 失败即停：set -euo pipefail，任何一步失败都以非 0 退出，不假装成功
#
# 2026-10-15（W2 布局：worker.py / contract.py / adapters/ / lib/ 都在 worker 根目录）

set -euo pipefail

WORKER_DIR="${MOODIFY_WORKER_DIR:-/home/ubuntu/moodify-worker}"
VENV="${MOODIFY_VENV:-/home/ubuntu/moodify-lab/.venv}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"   # 暂存树 = /home/ubuntu/moodify-worker/.deploy

NO_PIP=0
for arg in "$@"; do
  case "$arg" in
    --no-pip) NO_PIP=1 ;;
    *) echo "未知参数: $arg"; exit 64 ;;
  esac
done

log()  { printf '\033[36m[deploy]\033[0m %s\n' "$*"; }
warn() { printf '\033[33m[warn]\033[0m   %s\n' "$*"; }
die()  { printf '\033[31m[fail]\033[0m   %s\n' "$*" >&2; exit 1; }

[[ -f "$DEPLOY_ROOT/worker.py"      ]] || die "暂存树里没有 worker.py：$DEPLOY_ROOT"
[[ -f "$DEPLOY_ROOT/contract.py"    ]] || die "暂存树里没有 contract.py：$DEPLOY_ROOT"
[[ -d "$DEPLOY_ROOT/schemas/cloud"  ]] || die "暂存树里没有 schemas/cloud：$DEPLOY_ROOT"

log "worker 目录: $WORKER_DIR"
log "暂存树:      $DEPLOY_ROOT"
log "venv:        $VENV"

# ——— 1. 目录骨架 ———
log "1/6 建立目录骨架"
mkdir -p "$WORKER_DIR"/{lib,logs,work,schemas}

# ——— 2. 代码就位（增量、不删除）———
log "2/6 同步代码到 worker 根目录"
tar -C "$DEPLOY_ROOT" \
    --exclude=./.deploy --exclude=./deploy --exclude=./tests --exclude=./scripts \
    --exclude='*/__pycache__' --exclude='./__pycache__' \
    -cf - . | tar -C "$WORKER_DIR" -xf -

# 旧字节码会让改了 .py 之后仍加载缓存
find "$WORKER_DIR" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true

# ——— 2b. 报告旧布局残留（不自动删，交人类决定）———
if [[ -d "$WORKER_DIR/bin" ]]; then
  warn "检测到旧布局目录 $WORKER_DIR/bin（首版把 worker.py 放在 bin/）。"
  warn "  新布局在 worker 根目录，bin/ 已无人使用。确认无引用后可手工删除："
  warn "    rm -rf $WORKER_DIR/bin"
fi

# ——— 3. systemd unit ———
log "3/6 安装 systemd unit（只 install，不 enable）"
sudo install -m 0644 "$DEPLOY_ROOT/deploy/moodify-worker.service" \
     /etc/systemd/system/moodify-worker.service
sudo systemctl daemon-reload
if systemctl is-enabled moodify-worker >/dev/null 2>&1; then
  warn "moodify-worker 当前是 enabled 状态；改 unit 后需要用 restart 让新参数生效"
else
  log "  unit 已装但未 enable —— 符合预期（W3 冒烟通过后再 enable）"
fi

# ——— 4. logrotate ———
log "4/6 安装 logrotate 配置"
sudo install -m 0644 "$DEPLOY_ROOT/deploy/logrotate-moodify-worker" \
     /etc/logrotate.d/moodify-worker
sudo logrotate --debug /etc/logrotate.d/moodify-worker >/dev/null 2>&1 \
  && log "  logrotate 配置语法 OK" \
  || warn "  logrotate --debug 未通过，但不阻断部署"

# ——— 5. shell 别名 ———
log "5/6 安装 shell 别名"
install -m 0644 "$DEPLOY_ROOT/deploy/bashrc.aliases" /home/ubuntu/.moodify_aliases
if ! grep -qF '.moodify_aliases' /home/ubuntu/.bashrc 2>/dev/null; then
  cat >> /home/ubuntu/.bashrc <<'EOF'

# Moodify 宁夏节点快捷命令（由 deploy.sh 自动追加，勿手动改）
[ -f "$HOME/.moodify_aliases" ] && source "$HOME/.moodify_aliases"
EOF
  log "  已向 ~/.bashrc 追加 source 行"
else
  log "  ~/.bashrc 已有 source 行，跳过（幂等）"
fi

# ——— 6. awscli（可选）———
if [[ "$NO_PIP" -eq 1 ]]; then
  log "6/6 跳过 awscli 安装（--no-pip）"
else
  log "6/6 安装/更新 awscli"
  if "$VENV/bin/python" -m pip install -q --disable-pip-version-check awscli 2>/dev/null; then
    log "  awscli 已安装: $("$VENV/bin/aws" --version 2>/dev/null | head -1)"
  else
    warn "  awscli 安装失败（pypi 不通或被拒）—— 不阻断，boto3 路径不受影响"
  fi
fi

# ——— 收尾自检 ———
log "——— 部署后自检 ———"
"$VENV/bin/python" "$WORKER_DIR/node_info.py" || true

cat <<'EOF'

下一步：
  mcheck                                   # 期望 READY
  $MOODIFY_VENV/bin/python .../worker.py --drain 10   # 冒烟：10 个任务
  冒烟全绿后才允许：
    sudo systemctl enable --now moodify-worker
EOF
