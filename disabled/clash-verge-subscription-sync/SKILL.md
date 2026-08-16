---
name: clash-verge-subscription-sync
description: 'Use when the user asks to "configure extra rules" for a Clash Verge subscription by syncing local profile-enhancement templates (rules/merge) to a target remote (for example: 雪莲Pro).'
---

# Clash Verge Subscription Sync

Created: 2026-03-03

## Overview

Apply a stable profile-enhancement baseline to a target Clash Verge remote subscription by editing its enhancement templates (`option.rules` + `option.merge`):
- keep LAN/local/China traffic direct
- force foreign traffic to the subscription main group
- keep SSH port 22 direct
- set DNS/TUN merge defaults for stability

## Intent Contract (Important)

When user says phrases like:
- "给 X 配置额外规则"
- "按本地规则同步到 X"
- "用 clash skill 给 X 套规则"

Interpret this as:
- update target remote's enhancement templates in `profiles/<rules-uid>.yaml` and `profiles/<merge-uid>.yaml`
- make target behavior consistent with local tuned baseline

Do **not** reinterpret it as:
- changing subscription URL/token
- editing raw remote rules inside `<remote-uid>.yaml`
- modifying unrelated remotes

## When To Use

Use when:
- a new remote subscription appears in `profiles.yaml`
- its enhancement templates are empty
- behavior differs from previously tuned subscriptions
- user explicitly names a target subscription (for example `雪莲Pro`) and wants local-consistent extra rules

Do not use when:
- user explicitly wants different split-routing behavior for that subscription

## One-Command Workflow

```bash
python3 /home/zaviro/ai-rsrc/skills/clash-verge-subscription-sync/scripts/apply_templates.py
```

- default target is `current` remote in `profiles.yaml`
- use `--remote-uid <uid>` to target another remote
- use `--dry-run` to inspect only
- if user gave a subscription **name**, first map name -> uid in `profiles.yaml`, then pass `--remote-uid`
- if user asks "符合我本地", local baseline means currently tuned template behavior (same DIRECT/proxy split and DNS/TUN merge defaults)

## Verification

1. Refresh target subscription in Clash Verge UI.
2. Ensure mode is `rule`.
3. Run:

```bash
cdiag
```

Expectations:
- mode is `rule`
- tun is enabled
- ChatGPT/OpenAI hosts route through proxy chain, not `DIRECT`

## Manual Fallback

If automation is not available:
1. Open `profiles.yaml`, find remote item `option.rules` and `option.merge` uids.
2. Edit corresponding files in `profiles/`.
3. Rules template must include:
- LAN/local/China `DIRECT`
- `DST-PORT,22,DIRECT` and `SRC-PORT,22,DIRECT`
- `GEOSITE,geolocation-!cn,<main-group>`
- `MATCH,<main-group>`
4. Merge template must include:
- `tun.strict-route: true`
- `dns.listen: 127.0.0.1:1053`
- `dns.respect-rules: true`
5. For "match my local setup" requests, copy from an already tuned local subscription template and only replace target main-group tokens.
6. Refresh subscription and verify with `cdiag`.
