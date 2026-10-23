# TrueSight learned-move database

This folder is independent of the existing `aim` script.

- `moves/observations.json` — automated captures from client-observed animation replay intervals, plus users' manually entered parry/cooldown mappings. **Unverified.**
- `moves/verified.json` — separately curated entries with validated move IDs, cooldowns, reach and parry timing. Never populate this directly from raw observations.
- `sync_companion.py` — optional PC sync tool for use with GitHub CLI.

## Using the sync

1. Use TrueSight v10, enable Combat > Enemy Cooldown Tracker, then use **Export Learned Moves for GitHub Sync**. The script writes `TrueSightMoveExport.json` in your executor's filesystem.
2. On your PC, install Python 3 and [GitHub CLI](https://cli.github.com/), then run `gh auth login`.
3. Locate the JSON in your executor's workspace and run:

```powershell
py sync_companion.py --source "C:\path\to\executor\workspace\TrueSightMoveExport.json"
```

The companion checks the export periodically and updates the `observations.json` file using your GitHub CLI login. The game script **does not contain or use GitHub credentials**. It can download the public, curated `verified.json` read-only if the executor's HTTP access allows it.

The repository is public: synced move data becomes publicly visible. No usernames, chat content or player/session identifiers are exported. An observed shortest replay interval is **not the actual cooldown**, and user-entered parry categories are **not verified**.
