---
id: "push-token-scope"
status: "backlog"
priority: "low"
assignee: null
epic: "XX Workflow v2"
dueDate: null
created: "2026-10-23T17:11:58.000Z"
modified: "2026-10-23T17:11:58.000Z"
completedAt: null
labels: ["chore", "infra"]
order: "aG"
---
# Scope of the GitHub token used to push from the container

Pushing from the container's VS Code git UI hands git the Mac's GitHub login through VS Code's askpass socket. That login usually reaches every repo of the account, and any unsandboxed process in the container can ask the socket for it.

Open: push from the Mac again, or use a fine-grained token limited to the fork; and whether `git.terminalAuthentication: false` is worth setting meanwhile.
