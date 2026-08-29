#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Moodify Core Engine — 一键安装脚本
# ============================================================
# 适用于 Ubuntu 22.04+ / Python 3.10+
# 无需 GPU，CPU 模式可运行
# Usage:
#   bash install.sh          # Install in venv (recommended)
#   bash install.sh --system # Install system-wide (may need sudo)
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_MODE="${1:-venv}"

echo "========================================"
echo "  Moodify Core Engine — Installer"
echo "========================================"
echo ""

# ---- 检查 Python ----
PYTHON=$(command -v python3 || command -v python)
if [ -z "$PYTHON" ]; then
    echo "ERROR: python3 not found. Please install Python 3.10+."
    exit 1
fi

PY_VER=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "[1/3] Python version: $PY_VER"

MAJOR=$($PYTHON -c "import sys; print(sys.version_info.major)")
MINOR=$($PYTHON -c "import sys; print(sys.version_info.minor)")
if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]); then
    echo "ERROR: Python 3.10+ required, found $PY_VER"
    exit 1
fi
echo "  OK"

# ---- 系统依赖 ----
echo "[2/3] Checking system dependencies..."
if command -v apt-get &> /dev/null; then
    if ! dpkg -l 2>/dev/null | grep -q libsndfile1; then
        echo "  Installing libsndfile1 (soundfile backend)..."
        sudo apt-get update -qq && sudo apt-get install -y -qq libsndfile1 2>/dev/null || \
            echo "  WARNING: Could not install libsndfile1"
    else
        echo "  libsndfile1 OK"
    fi
else
    echo "  Skipped (not Debian/Ubuntu)"
fi

# ---- 安装 Python 包 ----
echo "[3/3] Installing Moodify Core Engine..."

if [ "$INSTALL_MODE" = "--system" ]; then
    echo "  System-wide install..."
    pip install -e "$SCRIPT_DIR"
else
    VENV_DIR="$SCRIPT_DIR/.venv"
    if [ ! -d "$VENV_DIR" ]; then
        echo "  Creating virtual environment at $VENV_DIR ..."
        $PYTHON -m venv "$VENV_DIR"
    fi
    source "$VENV_DIR/bin/activate"
    echo "  Activating virtual environment..."
    pip install --upgrade pip -q 2>/dev/null || true
    pip install -e "$SCRIPT_DIR"
fi

echo ""
echo "========================================"
echo "  Installation complete!"
echo "========================================"
echo ""
if [ "$INSTALL_MODE" != "--system" ]; then
    echo "  Activate:  source $SCRIPT_DIR/.venv/bin/activate"
fi
echo "  Quick start:"
echo "    moodify emotions                  # List 8 available emotions"
echo "    moodify analyze <file.wav>        # Diagnose 18 audio parameters"
echo "    moodify process <file.wav> GA     # Process with Gentle Awakening"
echo "    moodify serve                     # Start API on port 8000"
echo ""
echo "  Optional:"
echo "    pip install demucs torch          # Source separation (CPU mode)"
echo ""
