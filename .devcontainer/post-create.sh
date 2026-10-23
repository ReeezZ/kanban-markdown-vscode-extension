#!/usr/bin/env bash
# Runs once after the container is created (postCreateCommand in devcontainer.json).
set -euo pipefail

# Named volumes start out owned by root.
sudo chown node:node node_modules /home/node/.claude

# The pnpm version pinned in package.json's packageManager field.
sudo npm install -g "$(node -p "require('./package.json').packageManager")"
pnpm install --frozen-lockfile

git config core.hooksPath .githooks
chmod +x .githooks/* .claude/hooks/*.sh scripts/docs_check.py 2>/dev/null || true
