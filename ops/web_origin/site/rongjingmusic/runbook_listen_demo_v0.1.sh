#!/usr/bin/env bash
# runbook_listen_demo_v0.1.sh — Listen Demo v0.1 部署运行手册
#
# 用途:
#   把 Cadeau10 5 首原声跑 MoodifyDSPChain → 落 wav 到 LA 媒体根
#   → 产生公开 manifest sidecar → 部署 → 验证 5 个公开 URL 返回 206
#
# 这是 ops 一次性的端到端执行清单;非自动循环、非后台运行。
# 整个流程需要人工耳机会话(Step 5),不可绕过。
#
# 与 existing tools 的关系:
#   - assets/cadeau10-album1.json     原声 manifest (in git)
#   - assets/cadeau10-album1-moodify.json  Moodify manifest sidecar (此 runbook 生成)
#   - scripts/listen_demo_render.py     离线 DSP 渲染(此 runbook 调用)
#   - PRODUCTION_TOPOLOGY.md §21        LA 媒体根 / nginx alias
#   - soak_probe.sh                     持续健康探针(可选用)
#
# 用法:
#   bash ops/web_origin/site/rongjingmusic/runbook_listen_demo_v0.1.sh
#
# 风险点:
#   - Step 5 不能跳过。若 < 80% 命中,Profile v0.1 必须先调才能进入 Step 6。
#   - wav 进 LA 媒体根后,撤销必须靠 gift/重生成,不可 git 撤销(wav 不进 git)。
#   - /opt/moodify 是 ops 唯一真实部署路径,一切路径假设以此为准。
#
# 此 runbook 不修改 git 状态;所有 git 命令需 ops 手工确认。

set -u

REPO_ROOT="${MOODIFY_REPO_ROOT:-/opt/moodify}"
MEDIA_ROOT="${MOODIFY_MEDIA_ROOT:-/opt/moodify/music-media/audio}"
PUBLIC_BASE_URL="${MOODIFY_PUBLIC_BASE_URL:-https://play.rongjingmusic.com/audio/cadeau10-album1-moodify}"

ORIG_DIR="$MEDIA_ROOT/cadeau10-album1"
MOOD_DIR="$MEDIA_ROOT/cadeau10-album1-moodify"

MANIFEST_IN="$REPO_ROOT/apps/web/assets/cadeau10-album1.json"
MANIFEST_OUT="$REPO_ROOT/apps/web/assets/cadeau10-album1-moodify.json"

# ---- 打印人类可读 banner ---------------------------------------------------
echo "============================================================"
echo " Listen Demo v0.1 — ops runbook"
echo "============================================================"
echo " repo root         : $REPO_ROOT"
echo " media root        : $MEDIA_ROOT"
echo " original audio dir: $ORIG_DIR"
echo " moodify audio dir : $MOOD_DIR"
echo " public base url   : $PUBLIC_BASE_URL"
echo "============================================================"

# ---- Step 1 ----------------------------------------------------------------
echo "[step 1] cd $REPO_ROOT && git pull --rebase origin main"
(
  cd "$REPO_ROOT" || { echo "FATAL: cannot cd $REPO_ROOT"; exit 1; }
  git pull --rebase origin main || { echo "FATAL: git pull failed"; exit 1; }
)

# ---- Step 2 ----------------------------------------------------------------
echo "[step 2] verify original audio manifest"
[ -f "$MANIFEST_IN" ] || { echo "FATAL: $MANIFEST_IN missing"; exit 1; }
[ -d "$ORIG_DIR" ] || { echo "FATAL: $ORIG_DIR missing"; exit 1; }
echo " manifest: $MANIFEST_IN"
echo " original dir: $ORIG_DIR"
echo " contents:"
ls -la "$ORIG_DIR" | sed 's/^/   /'

# ---- Step 3 ----------------------------------------------------------------
echo "[step 3] prepare moodify audio dir"
mkdir -p "$MOOD_DIR"
echo " moodify dir: $MOOD_DIR"

# ---- Step 4 ----------------------------------------------------------------
echo "[step 4] render 5 tracks via moodify-core-package"
(
  cd "$REPO_ROOT" || { echo "FATAL: cannot cd $REPO_ROOT"; exit 1; }
  python moodify-core-package/scripts/listen_demo_render.py \
    --input-dir      "$ORIG_DIR" \
    --output-dir     "$MOOD_DIR" \
    --manifest-input "$MANIFEST_IN" \
    --manifest-output "$MANIFEST_OUT" \
    --public-base-url "$PUBLIC_BASE_URL" || { echo "FATAL: render failed"; exit 1; }
)
echo " rendered files:"
ls -la "$MOOD_DIR" | sed 's/^/   /'

# ---- Step 5 (gated, NOT skip-able) -----------------------------------------
echo "============================================================"
echo " [step 5] HUMAN GATE: real-ear A/B review"
echo "============================================================"
echo " Required: 5 tracks × (Original, Moodify)  blind A/B review."
echo " Tooling: headphones + ABX switcher."
echo " Pass criterion: >= 80% of 5 trials auditor can identify difference."
echo ""
echo " If PASS  -> continue to Step 6."
echo " If FAIL  -> edit moodify-core-package/scripts/listen_demo_render.py"
echo "             LISTEN_DEMO_PROFILE_V1 to a conservative variant,"
echo "             then rerun from Step 4."
echo ""
read -r -p " Proceed? (type 'yes' to continue, anything else to abort): " GATE
[ "$GATE" = "yes" ] || { echo "ABORTED at human gate."; exit 0; }

# ---- Step 6 ----------------------------------------------------------------
echo "[step 6] commit manifest sidecar"
(
  cd "$REPO_ROOT" || { echo "FATAL: cannot cd $REPO_ROOT"; exit 1; }
  git add apps/web/assets/cadeau10-album1-moodify.json
  git commit -m "listen-demo-v0.1: Cadeau10 public comparison manifest sidecar"
  git push origin main || { echo "FATAL: push failed"; exit 1; }
)

# ---- Step 7 ----------------------------------------------------------------
echo "[step 7] redeploy apps/web"
(
  cd "$REPO_ROOT/apps/web" || { echo "FATAL: cannot cd apps/web"; exit 1; }
  npm ci
  npm run build:self-hosted || { echo "FATAL: build failed"; exit 1; }
)
echo " build done; ops playbook restart Node service is out-of-band."

# ---- Step 8 (verification) --------------------------------------------------
echo "[step 8] Range probe"
FILES=(
  "je-ne-veux-pas-enfermer-ton-aujourdhui.wav"
  "ne-vivons-pas-seulement-de-souvenirs.wav"
  "nous-pouvons-nous-reconnaitre-encore.wav"
  "ou-es-tu-maintenant.wav"
  "vieillir-et-devenir-nouveau-avec-toi.wav"
)
fail=0
for f in "${FILES[@]}"; do
  url="$PUBLIC_BASE_URL/$f"
  echo "   -> $url"
  status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 \
    -H "Range: bytes=0-1023" "$url" || echo "000")
  echo "      HTTP $status"
  [ "$status" = "206" ] || fail=$((fail + 1))
done

if [ "$fail" -ne 0 ]; then
  echo "[step 8] FAIL: $fail of ${#FILES[@]} probes did not return 206."
  echo "  -> check nginx alias /opt/moodify/music-media/audio -> 443"
  echo "  -> see PRODUCTION_TOPOLOGY.md §21"
  exit 1
fi

echo "[step 8] OK: all 5 audio origins return 206 with Range header"

# ---- Step 9 (link awareness, manual) ---------------------------------------
echo "============================================================"
echo " [step 9] Brand Home /listen link awareness"
echo "============================================================"
echo " Brand Home index.html Listen section points to"
echo "   https://play.rongjingmusic.com/listen"
echo " If nginx does not route /listen to apps/web, fall back:"
echo "   edit ops/web_origin/site/rongjingmusic/index.html"
echo "   replace <a href=\"https://play.rongjingmusic.com/listen\">"
echo "   with    <a href=\"/#listen\">"
echo "============================================================"

# ---- Step 10 (copy edit, manual) -------------------------------------------
echo "============================================================"
echo " [step 10] Brand Home Listen copy edit (separate PR)"
echo "============================================================"
echo " Replace in ops/web_origin/site/rongjingmusic/index.html"
echo "   <p class=\"note\">Coming soon — Verified audio examples are being prepared.</p>"
echo " with"
echo "   <p class=\"note\">Press Play. The same song, first as the artist delivered it, then as Moodify hears it.</p>"
echo "============================================================"

echo ""
echo " DONE — Listen Demo v0.1 deployed."
echo " Final responsibility:"
echo "   - audio binaries: /opt/moodify/music-media/audio/cadeau10-album1-moodify/"
echo "   - manifest sidecar: apps/web/assets/cadeau10-album1-moodify.json (in git)"
echo "   - /listen page: 5 real src, EmptyState fallback per-track"
echo "   - Brand Home Listen section: copy edit pending Step 10"
