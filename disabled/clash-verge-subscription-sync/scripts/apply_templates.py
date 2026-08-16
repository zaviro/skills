#!/usr/bin/env python3
"""Apply stable Clash Verge rules/merge templates to a remote subscription profile.

This script updates the profile-enhancement template files referenced by a
selected remote subscription in:
  ~/.local/share/io.github.clash-verge-rev.clash-verge-rev/profiles.yaml
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ProfileItem:
    uid: str
    type: Optional[str] = None
    file: Optional[str] = None
    name: Optional[str] = None
    option: Dict[str, str] = field(default_factory=dict)


def _strip_quotes(value: str) -> str:
    text = value.strip()
    if (text.startswith("'") and text.endswith("'")) or (
        text.startswith('"') and text.endswith('"')
    ):
        return text[1:-1]
    return text


def parse_profiles_yaml(path: Path) -> tuple[Optional[str], List[ProfileItem]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    current: Optional[str] = None
    items: List[ProfileItem] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if line.startswith("current:"):
            current = _strip_quotes(line.split(":", 1)[1])
            i += 1
            continue

        if line.startswith("- uid:"):
            uid = _strip_quotes(line.split(":", 1)[1])
            item = ProfileItem(uid=uid)
            i += 1
            while i < len(lines) and not lines[i].startswith("- uid:"):
                sub = lines[i]
                sub_stripped = sub.strip()

                if sub.startswith("  type:"):
                    item.type = _strip_quotes(sub.split(":", 1)[1])
                elif sub.startswith("  file:"):
                    item.file = _strip_quotes(sub.split(":", 1)[1])
                elif sub.startswith("  name:"):
                    item.name = _strip_quotes(sub.split(":", 1)[1])
                elif sub.startswith("  option:"):
                    i += 1
                    while i < len(lines) and lines[i].startswith("    "):
                        opt = lines[i].strip()
                        if ":" in opt:
                            key, value = opt.split(":", 1)
                            item.option[key.strip()] = _strip_quotes(value)
                        i += 1
                    continue

                if sub_stripped == "":
                    pass
                i += 1

            items.append(item)
            continue

        i += 1

    return current, items


def find_primary_group_name(remote_yaml: Path) -> str:
    text = remote_yaml.read_text(encoding="utf-8", errors="replace")
    in_proxy_groups = False

    for line in text.splitlines():
        if not in_proxy_groups:
            if line.startswith("proxy-groups:"):
                in_proxy_groups = True
            continue

        # stop at next top-level section
        if line and not line.startswith(" ") and line.endswith(":"):
            break

        m = re.match(r"^\s*name:\s*(.+?)\s*$", line)
        if m:
            return _strip_quotes(m.group(1))

    raise RuntimeError(f"Cannot find first proxy group name in {remote_yaml}")


def render_rules_template(main_group: str) -> str:
    return f"""# Profile Enhancement Rules Template for Clash Verge

prepend:
  - DOMAIN,localhost,DIRECT
  - DOMAIN-SUFFIX,local,DIRECT
  - IP-CIDR,127.0.0.0/8,DIRECT,no-resolve
  - IP-CIDR,10.0.0.0/8,DIRECT,no-resolve
  - IP-CIDR,172.16.0.0/12,DIRECT,no-resolve
  - IP-CIDR,192.168.0.0/16,DIRECT,no-resolve
  - IP-CIDR,100.64.0.0/10,DIRECT,no-resolve
  - IP-CIDR,100.100.100.100/32,DIRECT,no-resolve
  - IP-CIDR6,fd7a:115c:a1e0::/48,DIRECT,no-resolve
  - IP-CIDR,169.254.0.0/16,DIRECT,no-resolve
  - IP-CIDR6,::1/128,DIRECT,no-resolve
  - IP-CIDR6,fc00::/7,DIRECT,no-resolve
  - IP-CIDR6,fe80::/10,DIRECT,no-resolve
  - DOMAIN-SUFFIX,ts.net,DIRECT
  - DOMAIN-SUFFIX,tailscale.com,DIRECT
  - DST-PORT,22,DIRECT
  - SRC-PORT,22,DIRECT
  - DOMAIN-SUFFIX,cn,DIRECT
  - GEOSITE,CN,DIRECT
  - GEOIP,CN,DIRECT
  - GEOSITE,geolocation-!cn,{main_group}
  - IP-CIDR,17.0.0.0/8,{main_group},no-resolve
  - MATCH,{main_group}

append: []

delete: []
"""


def render_merge_template() -> str:
    return """# Profile Enhancement Merge Template for Clash Verge

tun:
  strict-route: true
  route-exclude-address:
    - 100.64.0.0/10
    - fd7a:115c:a1e0::/48

dns:
  listen: 127.0.0.1:1053
  respect-rules: true
  default-nameserver:
    - 223.5.5.5
    - 119.29.29.29
  nameserver:
    - https://dns.alidns.com/dns-query
    - https://doh.pub/dns-query
  fallback:
    - https://1.1.1.1/dns-query
    - https://8.8.8.8/dns-query
  proxy-server-nameserver:
    - https://dns.alidns.com/dns-query
    - https://doh.pub/dns-query
  fallback-filter:
    geoip: true
    geoip-code: CN
  nameserver-policy:
    "*.ts.net": 100.100.100.100
    "*.tailscale.com": 100.100.100.100
    "controlplane.tailscale.com": 100.100.100.100
    "login.tailscale.com": 100.100.100.100
"""


def write_with_backup(path: Path, content: str) -> None:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    if path.exists():
        backup = path.with_suffix(path.suffix + f".bak.{ts}")
        shutil.copy2(path, backup)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply stable rules/merge templates to Clash Verge subscription."
    )
    parser.add_argument(
        "--base-dir",
        default="~/.local/share/io.github.clash-verge-rev.clash-verge-rev",
        help="Clash Verge data directory",
    )
    parser.add_argument(
        "--remote-uid",
        default=None,
        help="Remote subscription uid in profiles.yaml (default: current)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print targets and detected main group without writing files",
    )
    args = parser.parse_args()

    base_dir = Path(args.base_dir).expanduser().resolve()
    profiles_yaml = base_dir / "profiles.yaml"
    profiles_dir = base_dir / "profiles"

    if not profiles_yaml.exists():
        print(f"[ERR] profiles.yaml not found: {profiles_yaml}", file=sys.stderr)
        return 1
    if not profiles_dir.exists():
        print(f"[ERR] profiles dir not found: {profiles_dir}", file=sys.stderr)
        return 1

    current_uid, items = parse_profiles_yaml(profiles_yaml)
    uid_to_item: Dict[str, ProfileItem] = {item.uid: item for item in items}

    target_uid = args.remote_uid or current_uid
    if not target_uid:
        print("[ERR] cannot determine target remote uid", file=sys.stderr)
        return 1

    remote = uid_to_item.get(target_uid)
    if not remote or remote.type != "remote":
        print(f"[ERR] uid {target_uid!r} is not a remote profile", file=sys.stderr)
        return 1

    merge_uid = remote.option.get("merge")
    rules_uid = remote.option.get("rules")
    if not merge_uid or not rules_uid:
        print(f"[ERR] remote {target_uid} missing merge/rules references", file=sys.stderr)
        return 1

    merge_item = uid_to_item.get(merge_uid)
    rules_item = uid_to_item.get(rules_uid)
    if not merge_item or not merge_item.file:
        print(f"[ERR] merge profile not found for uid {merge_uid}", file=sys.stderr)
        return 1
    if not rules_item or not rules_item.file:
        print(f"[ERR] rules profile not found for uid {rules_uid}", file=sys.stderr)
        return 1

    if not remote.file:
        print(f"[ERR] remote profile file missing for uid {target_uid}", file=sys.stderr)
        return 1

    remote_file = profiles_dir / remote.file
    merge_file = profiles_dir / merge_item.file
    rules_file = profiles_dir / rules_item.file

    if not remote_file.exists():
        print(f"[ERR] remote file not found: {remote_file}", file=sys.stderr)
        return 1

    main_group = find_primary_group_name(remote_file)

    print(f"target remote uid: {target_uid}")
    print(f"remote file      : {remote_file}")
    print(f"main group       : {main_group}")
    print(f"rules template   : {rules_file}")
    print(f"merge template   : {merge_file}")

    if args.dry_run:
        print("[DRY-RUN] no files were modified")
        return 0

    write_with_backup(rules_file, render_rules_template(main_group))
    write_with_backup(merge_file, render_merge_template())

    print("[OK] templates updated")
    print("next: refresh this subscription in Clash Verge UI, then run cdiag")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
