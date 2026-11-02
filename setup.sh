#!/usr/bin/env bash
# Installs everything the renderer needs (drawing, music, voice + voice QA). Safe to run repeatedly.
set -e
need_apt=""
python3 -c "import skia" 2>/dev/null || need_apt=1
command -v ffmpeg >/dev/null || need_apt=1
if [ -n "$need_apt" ]; then
  (apt-get install -y -q libegl1 libgl1 libfontconfig1 ffmpeg >/dev/null 2>&1) || \
  (apt-get update -q >/dev/null 2>&1 && apt-get install -y -q libegl1 libgl1 libfontconfig1 ffmpeg >/dev/null 2>&1)
fi
# always install with the SAME interpreter that runs the code (python3 and pip can point at different versions)
PKGS="skia-python scipy requests numpy kokoro-onnx soundfile sherpa-onnx"
python3 -c "import skia, scipy, requests, numpy, kokoro_onnx, soundfile, sherpa_onnx" 2>/dev/null || \
  python3 -m pip install -q $PKGS 2>&1 | grep -v -i "warning\|notice" || \
  python3 -m pip install -q --break-system-packages $PKGS 2>&1 | grep -v -i "warning\|notice" || true
# voice model (Kokoro, ~350 MB) + speech-recognition model for voice QA (~200 MB), both from GitHub releases
python3 -c "import sys; sys.path.insert(0, '$(dirname "$0")'); from engine import voice; voice.ensure_models()"
python3 -c "import skia, scipy, requests, numpy, kokoro_onnx, sherpa_onnx; print('setup ok, skia', skia.__version__, '+ voice')"
