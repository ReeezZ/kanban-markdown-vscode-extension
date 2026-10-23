#!/usr/bin/env bash
# Lists the repo's other worktrees (all but the one this runs in), so an agent
# knows another one may be working in parallel. One entry per worktree:
#
#   - <path>: <branch>, <n> commit(s) ahead of main, <n> uncommitted file(s), last change <time>
#     spec: <spec the branch adds or changes> (<its Status>)
#
# Prints nothing when there are no other worktrees.
# Used by session-context.sh and worktree-watch.sh. `--stable` leaves out the
# last-change time, which moves on every edit, so the watcher can compare runs.
#
# Try it: .claude/hooks/worktree-summary.sh [--stable]
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
this_checkout=$(pwd)
mode=${1:-}

# Prints "<path><tab><branch>" per worktree. `git worktree list --porcelain` gives
# one block per worktree ("worktree <path>", "HEAD <sha>", "branch refs/heads/<name>")
# with a blank line after each block.
all_worktrees() {
  local path="" branch=""
  while IFS= read -r line; do
    case "$line" in
      "worktree "*) path=${line#worktree } branch="detached" ;;
      "branch "*) branch=${line#branch refs/heads/} ;;
      "")
        [ -n "$path" ] && printf '%s\t%s\n' "$path" "$branch"
        path=""
        ;;
    esac
  done < <(
    git worktree list --porcelain
    echo
  )
}
main_checkout=$(all_worktrees | awk 'NR == 1' | cut -f1)

describe_path() {
  case "$1" in
    "$main_checkout") echo "main checkout" ;;
    *) echo "${1#"$main_checkout"/}" ;;
  esac
}

commits_ahead_of_main() {
  git -C "$1" rev-list --count main..HEAD 2>/dev/null || echo "?"
}

# One path per line, untracked files included.
uncommitted_files() {
  git -C "$1" status --porcelain --untracked-files=all | cut -c4-
}

count_lines() {
  grep -c . || true
}

# Newest of the last commit and the uncommitted files' modification times, as
# "YYYY-MM-DD HH:MM". Uncommitted edits count, so an agent that's mid-work
# doesn't look idle.
last_change() {
  local worktree=$1 newest
  newest=$(
    {
      git -C "$worktree" log -1 --format=%ct
      uncommitted_files "$worktree" | while IFS= read -r file; do
        stat -c %Y "$worktree/$file" 2>/dev/null || true
      done
    } | sort -n | tail -1
  )
  date -d "@$newest" '+%Y-%m-%d %H:%M'
}

# Specs the branch adds or changes since it left main (three dots: compared
# with the fork point), plus new ones not committed yet. Specs already on main
# show up in session-context.sh's own list.
specs_on_branch() {
  local worktree=$1
  {
    git -C "$worktree" diff --name-only main... -- 'docs/specs/*.md'
    uncommitted_files "$worktree" | grep '^docs/specs/.*\.md$' || true
  } | sort -u
}

# The line under a spec's "## Status" heading, e.g. "Approved".
spec_status() {
  awk '/^## Status/ { f = 1; next } f && NF { print; exit }' "$1"
}

describe_worktree() {
  local worktree=$1 branch=$2
  local entry
  entry="- $(describe_path "$worktree"): $branch"
  entry+=", $(commits_ahead_of_main "$worktree") commit(s) ahead of main"
  entry+=", $(uncommitted_files "$worktree" | count_lines) uncommitted file(s)"
  [ "$mode" = "--stable" ] || entry+=", last change $(last_change "$worktree")"
  echo "$entry"

  specs_on_branch "$worktree" | while IFS= read -r spec; do
    # A spec the branch deleted shows up in the diff but has no file left.
    [ -f "$worktree/$spec" ] || continue
    echo "  spec: $spec ($(spec_status "$worktree/$spec"))"
  done
}

all_worktrees | while IFS=$'\t' read -r worktree branch; do
  [ "$worktree" = "$this_checkout" ] && continue
  describe_worktree "$worktree" "$branch"
done
