---
id: "sandbox-network-allowlist"
status: "backlog"
priority: "low"
assignee: null
epic: "04 Publish"
dueDate: null
created: "2026-10-23T17:11:58.000Z"
modified: "2026-10-23T17:11:58.000Z"
completedAt: null
labels: ["chore", "workflow"]
order: "aH"
---
# Network allowlist for the Bash sandbox

The sandbox only blocks a few known hosts, so a sandboxed command can send what it reads anywhere else. `sandbox.network.allowedDomains` (npm registry, GitHub, the VS Code update server) would turn that around.

Open: the full list of hosts the checks, the e2e and the installs need, and how many prompts new domains cause in practice.
