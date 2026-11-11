"""Build the inline 3x-ui subscription template from the main Mihomo profile."""

import argparse
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
FIELDS = (
    "mode",
    "tcp-concurrent",
    "hosts",
    "dns",
    "proxy-groups",
    "rule-providers",
    "rules",
)
HEADER = (
    "# 3x-ui/Mihomo inline subscription template.\n"
    "# Generated from Clash.yaml by scripts/build-3x-ui-template.py.\n"
    "# The panel supplies each subscriber's nodes; no private subscription URL is needed.\n"
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check that the committed template is up to date.")
    args = parser.parse_args()

    source = yaml.safe_load((ROOT / "Clash.yaml").read_text(encoding="utf-8"))
    template = {key: source[key] for key in FIELDS if key in source}
    for group in template["proxy-groups"]:
        providers = group.pop("use", [])
        if providers:
            if providers != ["subscription"]:
                raise ValueError(f"Unsupported node provider in group {group['name']!r}: {providers!r}")
            group["include-all-proxies"] = True

    output = HEADER + yaml.safe_dump(template, allow_unicode=True, sort_keys=False, width=160)
    target = ROOT / "Clash.3x-ui.yaml"
    if args.check:
        if not target.is_file() or target.read_text(encoding="utf-8") != output:
            raise SystemExit("Clash.3x-ui.yaml is out of date; run python scripts/build-3x-ui-template.py")
        print("Clash.3x-ui.yaml is up to date.")
    else:
        target.write_text(output, encoding="utf-8", newline="\n")
        print("Generated Clash.3x-ui.yaml")


if __name__ == "__main__":
    main()
