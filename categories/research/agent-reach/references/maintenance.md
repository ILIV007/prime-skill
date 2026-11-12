# Maintenance

Read this when updates fail, the browser won't start, a channel errors, or the user wants to uninstall.

- Updates: `agent-reach update` upgrades Agent Reach, the tools of added channels, and the skill; `agent-reach update --check` only checks whether a new version exists. Only run after the user agrees.
- Status: `agent-reach doctor --text` reads local status without going online; `agent-reach check <channel> --text` tests live once (`--search` tests only search/jobs). A successful install does not equal a passed live test.
- Browser: `agent-reach browser status` shows status, `browser setup` prepares the engine and extensions, `browser stop` closes; if CloakBrowser download fails, fix the network and run `browser setup --retry-cloak`.
- Tell failure stages apart: dependency download, browser connection, login, page loading, and platform rate limiting are separate things; do not call a network timeout a login failure.
- When an upstream tool errors: record the error and version, and after the user agrees run `agent-reach update` once; do not modify the upstream tool's install files, do not retry in a loop.
- `PLATFORM_BLOCKED`, `RATE_LIMITED`, `NEED_LOGIN`, `BUSY` stop the current attempt; wait for the user to deal with it before continuing, do not keep opening windows.
- Keys and proxies: `agent-reach configure groq-key | openai-key | proxy | github-token` — values are provided by the user personally.
- Port conflicts (`Port <n> belongs to an unmanaged browser`): another program occupies the dedicated browser's port (default 9222). Do not close the user's program; after the user agrees, run `agent-reach configure browser-port <free port>`.
- Uninstall: first run `agent-reach uninstall --dry-run` to show the user the scope, then `agent-reach uninstall` after confirmation. Only delete what Reach itself installed; the user's other files and browsers are kept.
