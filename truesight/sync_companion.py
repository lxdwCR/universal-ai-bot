#!/usr/bin/env python3
"""Sync TrueSight local move observations to GitHub without Roblox-held credentials."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

DEFAULT_REPO = "lxdwCR/universal-ai-bot"
REMOTE_FILE = "truesight/moves/observations.json"
CATEGORIES = {"Parryable", "ParryableBreak", "Blockable", "BlockBreak", "Unblockable", "Unknown"}

def gh(*args, input_text=None):
    try:
        p = subprocess.run(["gh", *args], input=input_text, capture_output=True, text=True,
                           encoding="utf-8", check=False)
    except FileNotFoundError as e:
        raise RuntimeError("Install GitHub CLI and run gh auth login") from e
    if p.returncode:
        raise RuntimeError(p.stderr.strip() or ("gh exited " + str(p.returncode)))
    return p.stdout

def clean_id(raw):
    value = str(raw or "")
    return value if re.fullmatch(r"\d{1,20}", value) else None

def number(raw, low, high):
    try:
        val = float(raw)
        return round(val, 3) if low <= val <= high else None
    except (ValueError, TypeError):
        return None

def normalize(data):
    if not isinstance(data, dict) or data.get("schema_version") != 1 or data.get("game") != "YBA":
        raise ValueError("Unsupported TrueSight export schema")
    observations = {}
    mappings = {}
    for row in (data.get("observations") or [])[:500]:
        if not isinstance(row, dict):
            continue
        ident = clean_id(row.get("animation_id"))
        if not ident:
            continue
        try:
            samples = max(0, min(10000, int(row.get("samples", 0))))
        except (TypeError, ValueError):
            samples = 0
        observations[ident] = {
            "animation_id": ident,
            "label": str(row.get("label") or ("Action " + ident)).replace("\n", " ")[:60],
            "best_repeat_gap_seconds": number(row.get("best_repeat_gap_seconds"), 0.5, 120),
            "samples": samples, "confidence": "observed_unverified"}
    for row in (data.get("mappings") or [])[:500]:
        if not isinstance(row, dict):
            continue
        ident = clean_id(row.get("animation_id"))
        if not ident:
            continue
        category = str(row.get("parry_category") or "Unknown")
        if category not in CATEGORIES:
            category = "Unknown"
        mappings[ident] = {
            "animation_id": ident,
            "name": str(row.get("name") or ("Action " + ident)).replace("\n", " ")[:60],
            "cooldown_seconds": number(row.get("cooldown_seconds"), 0, 180) or 0,
            "reach_studs": number(row.get("reach_studs"), 0, 100) or 0,
            "parry_start_seconds": number(row.get("parry_start_seconds"), 0, 5) or 0,
            "parry_end_seconds": number(row.get("parry_end_seconds"), 0, 5) or 0,
            "parry_category": category, "confidence": "user_supplied_unverified"}
    return observations, mappings

def sync(path, repo, dry_run=False):
    incoming = json.loads(path.read_text(encoding="utf-8-sig"))
    observed, mapped = normalize(incoming)
    url = f"repos/{repo}/contents/{REMOTE_FILE}"
    try:
        response = json.loads(gh("api", url))
        current_sha = response["sha"]
        current = json.loads(base64.b64decode(response["content"]).decode("utf-8"))
    except RuntimeError as e:
        if "404" not in str(e) and "Not Found" not in str(e):
            raise
        current_sha = None
        current = {"schema_version": 1, "game": "YBA", "observations": [], "mappings": []}
    if current.get("schema_version") != 1:
        raise ValueError("Refusing to overwrite incompatible remote schema")
    old_observed = {x["animation_id"]: x for x in current.get("observations", [])
                    if isinstance(x, dict) and clean_id(x.get("animation_id"))}
    old_mapped = {x["animation_id"]: x for x in current.get("mappings", [])
                  if isinstance(x, dict) and clean_id(x.get("animation_id"))}
    for ident, value in observed.items():
        previous = old_observed.get(ident)
        if previous:
            gaps = [x for x in (number(previous.get("best_repeat_gap_seconds"), .5, 120),
                                value["best_repeat_gap_seconds"]) if x is not None]
            value["best_repeat_gap_seconds"] = min(gaps) if gaps else None
            value["samples"] = max(int(previous.get("samples", 0)), value["samples"])
        old_observed[ident] = value
    old_mapped.update(mapped)
    result = {"schema_version": 1, "game": "YBA",
              "notice": "UNVERIFIED: observed gaps only bound cooldowns; user-supplied tags need review.",
              "observations": [old_observed[k] for k in sorted(old_observed)][:1500],
              "mappings": [old_mapped[k] for k in sorted(old_mapped)][:1500]}
    if result["observations"] == current.get("observations", []) and result["mappings"] == current.get("mappings", []):
        return
    if dry_run:
        print("Would upload", len(observed), "observations and", len(mapped), "mappings")
        return
    payload = {"message": "Sync TrueSight unverified observations",
               "content": base64.b64encode((json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode()).decode()}
    if current_sha:
        payload["sha"] = current_sha
    gh("api", "-X", "PUT", url, "--input", "-", input_text=json.dumps(payload))
    print("Synced to", f"https://github.com/{repo}/blob/main/{REMOTE_FILE}")

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--repo", default=DEFAULT_REPO)
    ap.add_argument("--interval", type=float, default=30)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--once", action="store_true")
    args = ap.parse_args()
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", args.repo):
        ap.error("Expected GitHub owner/repository")
    gh("auth", "status")
    last_digest = None
    try:
        while True:
            try:
                if args.source.is_file():
                    digest = hashlib.sha256(args.source.read_bytes()).hexdigest()
                    if digest != last_digest:
                        sync(args.source, args.repo, args.dry_run)
                        last_digest = digest
                elif args.once:
                    raise FileNotFoundError(str(args.source))
            except (OSError, RuntimeError, ValueError) as error:
                print("Sync error:", error, file=sys.stderr)
                if args.once:
                    return 1
            if args.once:
                break
            time.sleep(max(10, args.interval))
    except KeyboardInterrupt:
        print("Sync stopped")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
