---
id: "card-checks-in-extension"
status: "backlog"
priority: "low"
assignee: null
epic: "XX Future Ideas"
dueDate: null
created: "2026-10-24T12:31:54.000Z"
modified: "2026-10-24T12:31:54.000Z"
completedAt: null
labels: ["idea", "extension"]
order: "aT"
---
# Card checks in the extension

The extension checks the cards itself (frontmatter, `Needs:` ids, links between cards), as `scripts/docs_check.py` does for this repo today, and reports problems as VS Code diagnostics. People see them in the Problems panel, and agents running in VS Code can read diagnostics already, so no MCP server is needed. Open: which checks are general enough for any board and which are this repo's conventions, and whether fixes (like `--fix` writing card links) become quick fixes.
