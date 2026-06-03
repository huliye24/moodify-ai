#!/bin/bash
# ============================================================
# Moodify Cloud Sync — 关机前数据同步脚本
# 从腾讯云拉取所有实验数据和代码变更到本地
# 用法: bash sync_cloud.sh
# ============================================================
set -e

CLOUD_HOST="${MOODIFY_CLOUD_HOST:-ubuntu@43.156.175.4}"
CLOUD_MOODIFY="${MOODIFY_CLOUD_DIR:-/home/ubuntu/moodify-mainline}"
CLOUD_PHYS="${MOODIFY_CLOUD_PHYS_DIR:-/home/ubuntu/phys-lab}"
LOCAL_ROOT="$(cd "$(dirname "$0")" && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SYNC_DIR="$LOCAL_ROOT/outputs/sync_$TIMESTAMP"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}[SYNC]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
fail()  { echo -e "${RED}[FAIL]${NC} $1"; }

# ── 0. 连接检查 ──────────────────────────────────────
info "检查云端连接..."
if ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no $CLOUD_HOST "echo ok" &>/dev/null; then
    fail "无法连接云端，跳过同步"
    exit 1
fi
info "云端在线"

# ── 1. Git 同步 ──────────────────────────────────────
info "Git: 拉取云端 commit..."
cd "$LOCAL_ROOT"

# 先拉云端的新 commit
git fetch tencent main 2>&1 | tail -1

LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse tencent/main 2>/dev/null || echo "none")

if [ "$LOCAL_HASH" != "$REMOTE_HASH" ] && [ "$REMOTE_HASH" != "none" ]; then
    echo "  本地: ${LOCAL_HASH:0:7}"
    echo "  云端: ${REMOTE_HASH:0:7}"
    git merge tencent/main --no-edit 2>&1 | tail -3
    info "Git 同步完成"
else
    info "Git 已是最新"
fi

# ── 2. 实验报告 ──────────────────────────────────────
info "下载实验报告..."
mkdir -p "$SYNC_DIR/reports"
scp -q $CLOUD_HOST:$CLOUD_MOODIFY/outputs/reports/*.md "$SYNC_DIR/reports/" 2>/dev/null && \
    info "  reports/*.md OK" || warn "  无 md 报告"
scp -q $CLOUD_HOST:$CLOUD_MOODIFY/outputs/reports/*.json "$SYNC_DIR/reports/" 2>/dev/null && \
    info "  reports/*.json OK" || warn "  无 json 报告"
scp -q $CLOUD_HOST:$CLOUD_MOODIFY/outputs/reports/*.log "$SYNC_DIR/reports/" 2>/dev/null && \
    info "  reports/*.log OK" || warn "  无 log 文件"

# ── 3. Agent B 结果 ──────────────────────────────────
info "下载 Agent B 验证结果..."
if ssh $CLOUD_HOST "test -d $CLOUD_MOODIFY/moodify-core-package/outputs/phase2_agent_b" 2>/dev/null; then
    mkdir -p "$SYNC_DIR/phase2_agent_b"
    scp -q -r $CLOUD_HOST:$CLOUD_MOODIFY/moodify-core-package/outputs/phase2_agent_b/*.md "$SYNC_DIR/phase2_agent_b/" 2>/dev/null
    scp -q -r $CLOUD_HOST:$CLOUD_MOODIFY/moodify-core-package/outputs/phase2_agent_b/*.json "$SYNC_DIR/phase2_agent_b/" 2>/dev/null
    info "  Agent B reports OK"
else
    warn "  无 Agent B 输出"
fi

# ── 4. B 矩阵数据 ────────────────────────────────────
info "下载 B 矩阵数据..."
if ssh $CLOUD_HOST "test -d $CLOUD_PHYS/outputs/b_matrix" 2>/dev/null; then
    mkdir -p "$SYNC_DIR/b_matrix"
    scp -q $CLOUD_HOST:$CLOUD_PHYS/outputs/b_matrix/*.npy "$SYNC_DIR/b_matrix/" 2>/dev/null
    scp -q $CLOUD_HOST:$CLOUD_PHYS/outputs/b_matrix/*.npz "$SYNC_DIR/b_matrix/" 2>/dev/null
    scp -q $CLOUD_HOST:$CLOUD_PHYS/outputs/b_matrix/*.json "$SYNC_DIR/b_matrix/" 2>/dev/null
    info "  B 矩阵 OK ($(ls "$SYNC_DIR/b_matrix" | wc -l) files)"
else
    warn "  无 B 矩阵数据"
fi

# ── 5. 物理实验结果 ──────────────────────────────────
info "下载 phys-lab 物理实验结果..."
if ssh $CLOUD_HOST "test -d $CLOUD_PHYS/outputs/phys_tencent" 2>/dev/null; then
    mkdir -p "$SYNC_DIR/phys_lab"
    scp -q -r $CLOUD_HOST:$CLOUD_PHYS/outputs/phys_tencent "$SYNC_DIR/phys_lab/" 2>/dev/null
    info "  phys-lab OK"
else
    warn "  无 phys-lab 结果"
fi

# ── 6. 校准状态 ──────────────────────────────────────
info "下载校准状态..."
scp -q $CLOUD_HOST:$CLOUD_MOODIFY/outputs/calibration_state.json "$SYNC_DIR/" 2>/dev/null && \
    info "  calibration_state.json OK" || warn "  无校准状态"
scp -q $CLOUD_HOST:$CLOUD_MOODIFY/outputs/processing_history.jsonl "$SYNC_DIR/" 2>/dev/null && \
    info "  processing_history.jsonl OK" || warn "  无处理历史"

# ── 7. 检查点 ────────────────────────────────────────
info "下载实验检查点..."
if ssh $CLOUD_HOST "test -d $CLOUD_MOODIFY/outputs/checkpoints && ls $CLOUD_MOODIFY/outputs/checkpoints/*/checkpoint.json 2>/dev/null" 2>/dev/null; then
    mkdir -p "$SYNC_DIR/checkpoints"
    scp -q -r $CLOUD_HOST:$CLOUD_MOODIFY/outputs/checkpoints/* "$SYNC_DIR/checkpoints/" 2>/dev/null
    info "  检查点 OK"
else
    warn "  无检查点"
fi

# ── 8. 汇总 ──────────────────────────────────────────
echo ""
echo "========================================="
echo -e "${GREEN}  同步完成${NC}"
echo "========================================="
echo "  时间: $TIMESTAMP"
echo "  目录: $SYNC_DIR"
echo ""
echo "  文件统计:"
find "$SYNC_DIR" -type f | wc -l | xargs echo "    总文件:"
du -sh "$SYNC_DIR" 2>/dev/null | awk '{print "    大小: " $1}'
echo ""
echo "  Git: ${REMOTE_HASH:0:7} (云端) = ${LOCAL_HASH:0:7} (本地)"
echo ""

# 清理超过 7 天的旧同步目录
find "$LOCAL_ROOT/outputs" -maxdepth 1 -name "sync_*" -mtime +7 -exec rm -rf {} \; 2>/dev/null || true
