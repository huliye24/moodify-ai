param([string]$EnvironmentPath = ".venv-basic-pitch")

$ErrorActionPreference = "Stop"
$python = Join-Path $EnvironmentPath "Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) { py -3.11 -m venv $EnvironmentPath }
& $python -m pip install --upgrade pip
& $python -m pip install "numpy>=1.24,<2" "scipy>=1.11,<1.14" "librosa>=0.10,<0.11" `
    "mir_eval>=0.8,<0.9" "pretty_midi>=0.2.10,<0.3" "resampy>=0.4,<0.4.3" `
    "scikit-learn>=1.3,<1.6" "typing_extensions>=4.8" "onnxruntime>=1.16,<2"
# Upstream 0.4.0 metadata requires TensorFlow on Python 3.11 even when ONNX is used.
& $python -m pip install --no-deps "basic-pitch==0.4.0"
& $python -m pip install --no-deps -e ".\moodify-core-package"
Write-Host "Moodify transcription installed: $python"
