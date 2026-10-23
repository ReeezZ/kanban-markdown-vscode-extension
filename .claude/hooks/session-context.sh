#!/usr/bin/env bash
# SessionStart hook for a new session, /clear and compaction: hands the fresh
# context a short "where we are" block, since decisions made only in an earlier
# conversation are gone.
# Prints the JSON Claude Code expects; stays silent on any error.
set -euo pipefail
# The scripts next to this one, which may be a different checkout's copy than
# the one this session runs in: a worktree branched before they existed has none.
hooks=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$(git rev-parse --show-toplevel)"

open_specs=$(
  for f in docs/specs/*.md; do
    [ -e "$f" ] || continue
    status=$(awk '/^## Status/ { f = 1; next } f && NF { print; exit }' "$f")
    case "$status" in
      Draft* | Approved*) echo "- $f ($status)" ;;
    esac
  done
)

# `|| true`: if head closes the pipe early, pipefail would otherwise end the hook.
changes=$(git status --short | head -20 || true)

# A failing summary shouldn't cost the rest of the context, but mustn't read as "none".
worktrees=$("$hooks"/worktree-summary.sh) || worktrees="(couldn't be read)"
# Seeds worktree-watch.sh's cache, so its first prompt only reports real changes.
session=$(jq -r '.session_id // "default"' 2>/dev/null || echo default)
"$hooks"/worktree-watch.sh --print-stable >"${TMPDIR:-/tmp}/claude-worktrees-$session" || true

context="Repo state at the start of this context (from the session-context hook):

Branch: $(git branch --show-current)

Uncommitted changes:
${changes:-(clean)}

Recent commits, first-parent (on main a merge commit stands for a whole branch; they record decisions and what was deferred):
$(git log --first-parent --oneline -10)

Specs in progress:
${open_specs:-none}

Other worktrees (another agent may be working there; check before merging or editing the same files):
${worktrees:-none}

If you were mid-task, re-read the relevant spec. If the current approach is unclear, ask the user before continuing."

jq -n --arg ctx "$context" \
  '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $ctx}}'
