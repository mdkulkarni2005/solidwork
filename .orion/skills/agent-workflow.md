# Orion agent workflow (plan → build → verify)

Your system instructions define the full workflow. Obey them for app-sized work:

1. **Plan** — clarify goals; use brainstorm/plan-first skills when needed; use `web_fetch` for public docs.
2. **Build** — use `run_subagents` in **parallel** for independent folders or features; **sequential** only when outputs chain.
3. **Verify** — local UI: `browser.baseUrl` + `browser_run` (Playwright). **Expect** (https://github.com/millionco/expect): if the repo has Expect set up, call `expect_cli` after real UI work; Orion auto-runs `npx expect run` when it detects Expect, or use `browser.expectCommand`. Pass flags in `command` if needed (e.g. `-u http://localhost:3000 --yes`). Use `submit_test_plan` if the user should approve steps first.
4. **Stuck** — short re-plan, more `web_fetch`, small sub-agent probes, then continue.

Treat browser output (failures, screenshots, Expect stdout) as first-class input for fixes.