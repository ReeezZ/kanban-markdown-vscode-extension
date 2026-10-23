#!/usr/bin/env bash
# Runs once after the container is created (postCreateCommand in devcontainer.json).
set -euo pipefail

# Named volumes start out owned by root.
sudo chown node:node node_modules /home/node/.claude

# The pnpm version pinned in package.json's packageManager field.
sudo npm install -g "$(node -p "require('./package.json').packageManager")"
pnpm install --frozen-lockfile

# In the system config, not the repo's .git/config: that file is shared with the host through the
# bind mount, and the hooks need the container's bash and node_modules. --global could be
# overwritten by the host .gitconfig VS Code copies in.
sudo git config --system core.hooksPath .githooks

chmod +x .githooks/* .claude/hooks/*.sh scripts/docs_check.py 2>/dev/null || true
