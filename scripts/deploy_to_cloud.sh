#!/usr/bin/env bash
# ===========================================================================
# Moodify Night Worker — 腾讯云一键部署脚本
#
# 用法 (在你本地执行):
#   bash scripts/deploy_to_cloud.sh
#
# 前提:
#   1. 腾讯云服务器已开机
#   2. SSH 可达: ssh ubuntu@139.199.186.106
#   3. 服务器上已有 moodify-o3is 项目
# ===========================================================================
set -e

CLOUD_HOST="ubuntu@139.199.186.106"
CLOUD_PROJECT="/home/ubuntu/moodify-o3is"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "============================================"
echo "  Moodify Night Worker — 云端部署"
echo "============================================"
echo ""

# ── 1. 连接检查 ────────────────────────────────
echo -n "检查云端连接... "
if ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no $CLOUD_HOST "echo ok" 2>/dev/null; then
    echo -e "${RED}失败${NC}"
    echo "无法连接 $CLOUD_HOST"
    echo "请确认:"
    echo "  1. 服务器已开机"
    echo "  2. SSH 端口 22 可达"
    echo "  3. 密钥已配置"
    exit 1
fi
echo -e "${GREEN}在线${NC}"

# ── 2. 检查远端项目 ─────────────────────────────
echo -n "检查远端项目... "
if ! ssh $CLOUD_HOST "test -d $CLOUD_PROJECT" 2>/dev/null; then
    echo -e "${RED}不存在${NC}"
    echo "远端 $CLOUD_PROJECT 不存在, 需要先 clone 项目"
    exit 1
fi
echo -e "${GREEN}存在${NC}"

# ── 3. 同步 Night Worker 文件 ──────────────────
echo "同步 Night Worker 文件..."
rsync -avz --progress \
    "$PROJECT_ROOT/workers/" \
    "$CLOUD_HOST:$CLOUD_PROJECT/workers/"

rsync -avz --progress \
    "$PROJECT_ROOT/configs/" \
    "$CLOUD_HOST:$CLOUD_PROJECT/configs/"

rsync -avz --progress \
    "$PROJECT_ROOT/scripts/run_night.sh" \
    "$PROJECT_ROOT/scripts/monitor_night.sh" \
    "$PROJECT_ROOT/scripts/stop_night.sh" \
    "$CLOUD_HOST:$CLOUD_PROJECT/scripts/"

# 设置可执行权限
ssh $CLOUD_HOST "chmod +x $CLOUD_PROJECT/scripts/run_night.sh $CLOUD_PROJECT/scripts/monitor_night.sh $CLOUD_PROJECT/scripts/stop_night.sh"

echo -e "${GREEN}文件同步完成${NC}"

# ── 4. 验证部署 ─────────────────────────────────
echo ""
echo "验证部署..."
ssh $CLOUD_HOST "cd $CLOUD_PROJECT && echo 'workers:' && ls workers/ && echo '' && echo 'configs:' && ls configs/ && echo '' && echo 'scripts:' && ls scripts/run_night.sh scripts/monitor_night.sh scripts/stop_night.sh"

# ── 5. 环境检查 ─────────────────────────────────
echo ""
echo "远端环境检查..."
ssh $CLOUD_HOST "cd $CLOUD_PROJECT && echo 'Python:' && python3 --version && echo '' && echo 'Memory:' && free -h | head -2 && echo '' && echo 'Disk:' && df -h / | tail -1"

# ── 6. Dry-run ──────────────────────────────────
echo ""
echo "远端 Dry-run..."
ssh $CLOUD_HOST "cd $CLOUD_PROJECT && python3 workers/night_worker.py --dry-run"

echo ""
echo "============================================"
echo -e "${GREEN}  部署完成${NC}"
echo "============================================"
echo ""
echo "下一步:"
echo "  ssh $CLOUD_HOST"
echo "  cd $CLOUD_PROJECT"
echo "  bash scripts/run_night.sh"
echo ""
