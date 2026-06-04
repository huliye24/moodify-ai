#!/usr/bin/env bash
# Moodify Studio OS Alpha — Dev Server Deploy Script
# Usage: ./deploy/deploy.sh [dev|prod]
#   dev:  systemd service on localhost (default)
#   prod: Docker container with external port

set -euo pipefail

MODE="${1:-dev}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/.."
SERVICE_NAME="moodify-studio-os"

echo "=== Moodify Studio OS Alpha Deploy ==="
echo "Mode: ${MODE}"
echo "Project: ${PROJECT_ROOT}"
echo ""

# ── Pre-flight checks ────────────────────────────────────────────────

check_deps() {
    echo "Checking dependencies..."
    python3 -c "import fastapi; import uvicorn" 2>/dev/null || {
        echo "ERROR: fastapi/uvicorn not installed. Run: pip install fastapi uvicorn"
        exit 1
    }
    echo "  ✓ Python deps OK"
}

check_tests() {
    echo "Running pre-deploy tests..."
    cd "${PROJECT_ROOT}"
    python3 -m pytest moodify_runtime/tests/ -q --tb=line \
        --ignore=moodify_runtime/tests/test_real_audio.py \
        --ignore=moodify_runtime/tests/test_full_stack_smoke.py 2>&1 | tail -3
    echo "  ✓ Tests OK"
}

# ── Dev deploy (systemd) ──────────────────────────────────────────────

deploy_dev() {
    echo "Deploying as systemd service..."

    local UNIT_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
    local INSTALL_DIR="/opt/moodify"

    if [[ -f "${UNIT_FILE}" ]]; then
        echo "  Unit already installed: ${UNIT_FILE}"
        sudo systemctl daemon-reload
        sudo systemctl restart "${SERVICE_NAME}"
    else
        echo "  Installing to ${INSTALL_DIR}..."
        sudo mkdir -p "${INSTALL_DIR}"
        sudo cp -r "${PROJECT_ROOT}/moodify_runtime" "${INSTALL_DIR}/"
        sudo cp "${SCRIPT_DIR}/moodify-studio-os.service" "${UNIT_FILE}"
        sudo systemctl daemon-reload
        sudo systemctl enable "${SERVICE_NAME}"
        sudo systemctl start "${SERVICE_NAME}"
    fi

    sleep 2
    curl -s http://127.0.0.1:8700/health | python3 -m json.tool
    echo "  ✓ Dev deploy complete"
}

# ── Prod deploy (Docker) ──────────────────────────────────────────────

deploy_prod() {
    echo "Building Docker image..."
    cd "${PROJECT_ROOT}"
    docker build -t moodify-studio-os:alpha -f deploy/Dockerfile . 2>&1 | tail -5

    echo "Starting container..."
    docker rm -f moodify-studio-os 2>/dev/null || true
    docker run -d --name moodify-studio-os \
        -p 8700:8700 \
        -v "$(pwd)/data:/app/data" \
        --restart unless-stopped \
        moodify-studio-os:alpha

    sleep 3
    echo "Health check:"
    curl -s http://127.0.0.1:8700/health | python3 -m json.tool
    echo "  ✓ Prod deploy complete"
}

# ── Main ──────────────────────────────────────────────────────────────

check_deps
check_tests

case "${MODE}" in
    dev)
        deploy_dev
        ;;
    prod)
        deploy_prod
        ;;
    *)
        echo "Usage: $0 [dev|prod]"
        exit 1
        ;;
esac

echo ""
echo "=== Deploy complete ==="
echo "  Console: http://127.0.0.1:8700/operator"
echo "  API:     http://127.0.0.1:8700/health"
echo "  Status:  http://127.0.0.1:8700/studio-os/status"
