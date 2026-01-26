#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR/frontend"
npm ci
npm run build

cd "$ROOT_DIR"
mkdir -p plag_checker_app/frontend/dist
cp -R frontend/dist/. plag_checker_app/frontend/dist/

python -m build
