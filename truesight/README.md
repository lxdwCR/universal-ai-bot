# TrueSight move data and optional cloud synchronization

This folder is independent of the original `aim` script. It does not modify the script you already have in this repository.

## Files

- `moves/observations.json` — **unverified** observed enemy animation replay gaps and user-supplied labels/parry classifications.
- `moves/verified.json` — curated, independently verified entries; intentionally empty until reviewed.

## Cloud Sync (no separate PC application)

Use the **TrueSight v11 Cloud Sync Package** supplied in the ChatGPT conversation. It includes `TrueSight_v11_Cloud_GitHub_AutoSync.lua`, `cloudflare-worker.js`, and `SETUP.md`.

1. Merge this pull request so `observations.json` is available on the `main` branch.
2. Create a Cloudflare Worker in your browser, paste the package's `cloudflare-worker.js` source, then deploy it.
3. Configure the Worker secrets `GITHUB_TOKEN` (fine-grained Contents read/write access **only** for `lxdwCR/universal-ai-bot`) and `SYNC_KEY` (an independent random string of at least 32 characters); set `GITHUB_REPO=lxdwCR/universal-ai-bot` and optionally `GITHUB_BRANCH=main`.
4. In TrueSight v11, open **Combat**, enter the deployed HTTPS endpoint URL ending in `/sync` and your private `SYNC_KEY`, then enable **Cloud GitHub Auto-Sync**.
5. Once TrueSight has learned an interval, it will queue an upload. Use **Sync Learned Moves Now** to test the connection.

Cloud sync is optional. It does not use Python, GitHub CLI, or a companion process on your PC. Your GitHub token stays in the Worker's secret storage, and **must not** be embedded in a public Lua script. The separate `SYNC_KEY` is stored locally as plaintext in the executor's `TrueSightCloudSync.json`: do not share that file.

The repository is public, so synchronized learned move data is public. The schema contains animation IDs, replay intervals, and calibrated move metadata — no usernames, session identifiers, or chat messages. **Observed replay gaps are not verified cooldowns**, and user-supplied parry labels are not confirmed game mechanics. Raw observations are never promoted automatically into `verified.json`.

This cannot guarantee avoiding Roblox anti-cheat or account sanctions. There is no promise that an unsupported executor's HTTP requests will work.
