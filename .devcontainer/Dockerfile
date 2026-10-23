FROM mcr.microsoft.com/devcontainers/typescript-node:1-22-bookworm

# xvfb and the Electron libraries for the integration tests (`xvfb-run -a pnpm run test:integration`),
# as in .github/workflows/ci.yml; bookworm names libasound2t64 libasound2. xauth is needed by xvfb-run.
# jq is used by the Claude Code hooks.
RUN apt-get update \
  && export DEBIAN_FRONTEND=noninteractive \
  && apt-get install -y --no-install-recommends \
    xvfb xauth \
    libnspr4 libnss3 libatk1.0-0 libatk-bridge2.0-0 libgtk-3-0 libglib2.0-0 libgbm1 \
    libxkbcommon0 libasound2 libxss1 libsecret-1-0 \
    jq \
  && rm -rf /var/lib/apt/lists/*
