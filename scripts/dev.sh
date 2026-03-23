#!/usr/bin/env bash
set -euo pipefail

# 本地开发启动脚本，默认绑定到 0.0.0.0 便于容器外访问。
npm run dev -- --hostname 0.0.0.0 --port "${PORT:-3000}"
