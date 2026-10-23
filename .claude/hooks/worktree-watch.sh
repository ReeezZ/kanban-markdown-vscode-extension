#!/usr/bin/env bash
# UserPromptSubmit hook: runs before each user message reaches the agent, and
# tells the agent when the other worktrees changed since it last saw them (a
# worktree added or removed, a branch moved, files changed). Silent when
# nothing changed, so it costs no context on most prompts.
#
# "Last seen" is a cache file per session, which session-context.sh seeds at
# session start (via --print-stable) and this hook updates whenever it reports
# a change.
#
# Try it: echo '{"session_id":"try"}' | .claude/hooks/worktree-watch.sh
# (prints on the first run, nothing on the second; rm /tmp/claude-worktrees-try)
set -euo pipefail
# Sibling scripts by this file's location, not the checkout's: see session-context.sh.
hooks=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$(git rev-parse --show-toplevel)"

# What gets compared: the summary without the last-change time, which moves
# on every edit and would make this report on nearly every prompt.
stable_state() {
  "$hooks"/worktree-summary.sh --stable
}

if [ "${1:-}" = "--print-stable" ]; then
  stable_state
  exit 0
fi

session_id=$(jq -r '.session_id // "default"')
last_seen_file="${TMPDIR:-/tmp}/claude-worktrees-$session_id"

now=$(stable_state)
last_seen=$(cat "$last_seen_file" 2>/dev/null || true)
if [ "$now" = "$last_seen" ]; then
  exit 0
fi
printf '%s\n' "$now" >"$last_seen_file"

worktrees=$("$hooks"/worktree-summary.sh)
context="The other worktrees changed since you last saw them (from the worktree-watch hook):

Other worktrees:
${worktrees:-none}"

jq -n --arg ctx "$context" \
  '{hookSpecificOutput: {hookEventName: "UserPromptSubmit", additionalContext: $ctx}}'
