"""Sync the sibling Shadowrocket checkout into the Mihomo configuration."""

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "Shadowrocket-Rules"
config_path = ROOT / "Clash.yaml"
original = config_path.read_text(encoding="utf-8")
config = yaml.safe_load(original)
source_text = (SOURCE / "Shadowrocket.conf").read_text(encoding="utf-8-sig")
sections = {}
section = None
for raw in source_text.splitlines():
    line = raw.strip()
    if line.startswith("[") and line.endswith("]"):
        section = line[1:-1]
        sections[section] = []
    elif line and not line.startswith("#") and section:
        sections[section].append(line)

groups = [{"name": "PROXY", "type": "select", "use": ["subscription"]}]
for line in sections["Proxy Group"]:
    name, options = line.split(" = ", 1)
    options = options.split(",")
    choices = [option for option in options[1:] if "=" not in option]
    if options[0] == "url-test":
        parameters = dict(option.split("=", 1) for option in options[1:] if "=" in option)
        group = {
            "name": name,
            "type": "url-test",
            "use": ["subscription"],
            "url": parameters["url"],
            "interval": int(parameters["interval"]),
            "tolerance": int(parameters.get("tolerance", 0)),
            "timeout": int(parameters.get("timeout", 5)) * 1000,
            "lazy": False,
            "filter": parameters.get("policy-regex-filter", ".+"),
        }
        groups.append(group)
        continue
    if options[0] != "select":
        raise ValueError(f"Unsupported source group type: {options[0]}")
    selected = next((o.split("=", 1)[1] for o in options if o.startswith("policy-select-name=")), choices[0])
    choices.remove(selected)
    choices.insert(0, selected)
    group = {"name": name, "type": options[0], "proxies": choices}
    if name == "✋ 手动选择":
        group["use"] = ["subscription"]
    groups.append(group)

owned = ["Mail", "Google", "AI", "HSBC_HK", "HK_Banks_Direct", "HK_Broker", "ApplePush", "Apple"]
changes = []
counts = Counter()
source_types = Counter()
source_files = {}
for name in owned:
    source_path = SOURCE / f"{name}.list"
    source_files[source_path.name] = hashlib.sha256(source_path.read_bytes()).hexdigest()
    payload = []
    for number, raw in enumerate(source_path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        kind = line.split(",", 1)[0]
        source_types[kind] += 1
        change = {"file": source_path.name, "line": number, "source": line}
        if kind == "USER-AGENT":
            counts["omitted_rules"] += 1
            changes.append({**change, "action": "omitted: Mihomo has no USER-AGENT routing rule"})
            continue
        if kind == "URL-REGEX":
            if line != r"URL-REGEX,^https?://www\.sc\.com/hk/":
                raise ValueError(f"Unmapped URL rule: {line}")
            line = "DOMAIN,www.sc.com"
            counts["modified_rules"] += 1
            changes.append({**change, "output": line, "action": "broadened to host match: Mihomo cannot route by URL path"})
        else:
            if kind not in {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "IP-CIDR", "IP-CIDR6"}:
                raise ValueError(f"Unsupported source rule: {line}")
            counts["unchanged_rules"] += 1
        payload.append(line)
    output = f"# Generated from {name}.list by scripts/sync-shadowrocket.py.\n"
    output += "payload:\n" + "".join("  - '" + rule.replace("'", "''") + "'\n" for rule in payload)
    (ROOT / "rules" / f"{name}.yaml").write_text(output, encoding="utf-8", newline="\n")
    config["rule-providers"][name].update(
        format="yaml",
        url=f"https://raw.githubusercontent.com/yzfh-ty/Clash-Rules/refs/heads/main/rules/{name}.yaml",
        path=f"./providers/{name}.yaml",
    )

rules = []
for line in sections["Rule"]:
    if line.startswith(("RULE-SET,", "DOMAIN-SET,")):
        _, url, policy = line.split(",", 2)
        name = Path(url).stem
        if name not in owned:
            translated = url.replace("/Shadowrocket/", "/Clash/").replace(".list", ".yaml")
            matches = [key for key, value in config["rule-providers"].items() if value["url"] == translated]
            if len(matches) != 1:
                raise ValueError(f"Unmapped provider: {url}")
            name = matches[0]
        line = f"RULE-SET,{name},{policy}"
    line = line.replace("(PROTOCOL,", "(NETWORK,")
    if line.startswith("FINAL,"):
        line = "MATCH," + line.split(",", 1)[1]
    rules.append(line)
# Preserve the existing Clash-specific upstream fix before domestic fallbacks.
if "DOMAIN,dm.wo.com.cn,REJECT" not in rules:
    rules.insert(6, "DOMAIN,dm.wo.com.cn,REJECT")

prefix = original.split("proxy-groups:\n", 1)[0]
prefix = prefix.replace("# PROXY models Shadowrocket's current proxy independently of 节点选择.\n", "")
prefix = prefix.replace("#🚀 节点选择", "#PROXY")
if "    - 255.255.255.255/32" not in prefix:
    prefix = prefix.replace("    - 224.0.0.0/4\n", "    - 224.0.0.0/4\n    - 255.255.255.255/32\n    - 239.255.255.250/32\n")
prefix = prefix.replace("  direct-nameserver:\n    - 223.5.5.5\n    - 119.29.29.29\n", "  direct-nameserver:\n    - system\n")
if "    '+.local': [system]" not in prefix:
    prefix = prefix.replace("  nameserver-policy:\n", "  nameserver-policy:\n    '+.local': [system]\n    '+.in-addr.arpa': [system]\n    '+.ip6.arpa': [system]\n    '+.icloud-content.com': [system]\n    '+.apple-cloudkit.com': [system]\n    '+.cdn-apple.com': [system]\n")
if "    - 'qpic.cn'" not in prefix:
    prefix = prefix.replace("    - '*.qpic.cn'", "    - 'qpic.cn'\n    - '*.qpic.cn'")
    prefix = prefix.replace("    - '*.qlogo.cn'", "    - 'qlogo.cn'\n    - '*.qlogo.cn'")
output = prefix + "# PROXY models Shadowrocket's current proxy independently of 节点选择.\n"
output += yaml.safe_dump({"proxy-groups": groups, "rule-providers": config["rule-providers"], "rules": rules}, allow_unicode=True, sort_keys=False, width=200)
config_path.write_text(output, encoding="utf-8", newline="\n")

report = {
    "target": "Mihomo (Clash.Meta)",
    "source": "yzfh-ty/Shadowrocket-Rules",
    "source_config_sha256": hashlib.sha256((SOURCE / "Shadowrocket.conf").read_bytes()).hexdigest(),
    "source_files_sha256": source_files,
    "source_rules": sum(source_types.values()),
    **counts,
    "source_types": dict(source_types),
    "changes": changes,
    "config_level_changes": [
        f"All {len(groups) - 1} source groups are converted; select groups retain their choices and defaults. PROXY is a separate subscription selector, also available through 手动选择.",
        "Source url-test groups test subscription nodes; timeout seconds become milliseconds, and lazy=false enables periodic checks even when idle.",
        "All source routing rules retain their order; PROTOCOL becomes NETWORK, FINAL becomes MATCH, and source providers map to Mihomo providers.",
        "All eight owned rulesets are converted locally and served from yzfh-ty/Clash-Rules.",
        "The existing dm.wo.com.cn rejection and Xiaohongshu DNS policy are retained.",
        "APNs TCP 5223 remains restricted to Apple IPv4 and four APNs IPv6 ranges; IPv6 remains disabled by default.",
        "Direct DNS uses system; Host server:system suffixes use nameserver-policy and fake-ip-filter.",
        "Cloudflare and Google DoH use PROXY concurrently; this is not Shadowrocket's sequential fallback behavior.",
        "TUN excludes all source IP ranges; dns-hijack retains the Clash setting for all UDP/TCP port 53 traffic.",
        "Shadowrocket skip-proxy and bypass-system are not fully equivalent to Mihomo TUN exclusions and routing rules; client/system-proxy bypass lists may require separate setup.",
        "URL Rewrite and MITM are omitted; Mihomo routing has no equivalent redirect feature.",
        "block-quic=all-proxy and udp-policy-not-supported-behaviour=REJECT have no exact equivalent in this conversion and are not reproduced.",
    ],
}
(ROOT / "conversion-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({"groups": len(groups), "config_rules": len(rules), "source_rules": report["source_rules"], **counts}))
