#!/usr/bin/env bash
# Installs everything the renderer needs. Safe to run repeatedly.
set -e
need_apt=""
python3 -c "import skia" 2>/dev/null || need_apt=1
command -v ffmpeg >/dev/null || need_apt=1
if [ -n "$need_apt" ]; then
  (apt-get install -y -q libegl1 libgl1 libfontconfig1 ffmpeg >/dev/null 2>&1) || \
  (apt-get update -q >/dev/null 2>&1 && apt-get install -y -q libegl1 libgl1 libfontconfig1 ffmpeg >/dev/null 2>&1)
fi
python3 -c "import skia, scipy, requests, numpy" 2>/dev/null || pip install -q skia-python scipy requests numpy 2>&1 | grep -v WARNING || true
python3 -c "import skia, scipy, requests, numpy; print('setup ok, skia', skia.__version__)"
