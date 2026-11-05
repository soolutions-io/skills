#!/usr/bin/env python3
"""Coerenza del marketplace pubblico. Gira in CI su ogni push e pull request.

Controlla:
  - marketplace.json ↔ cartelle plugins/: ogni plugin registrato esiste e viceversa;
  - plugin.json: name = cartella, version semver;
  - ogni SKILL.md: frontmatter con name = cartella e description < 1024 caratteri;
  - nessun path assoluto di una macchina (/Users/…, /home/…, C:\\Users\\…);
  - tripwire dei segreti (la scansione vera è gitleaks; questo è il primo filtro).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
ABS_PATH = re.compile(r"(/Users/[a-z]|/home/[a-z]|[A-Z]:\\\\Users\\\\)")
SECRETS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),  # AWS access key
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),  # GitHub token
    re.compile(r"sk-[A-Za-z0-9_-]{30,}"),  # chiavi API stile OpenAI/Anthropic
    re.compile(r"\b[a-zA-Z0-9]{8,}_[A-Za-z0-9]{40,}\b"),  # token CLI del portale (prefisso_segreto)
]


def frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    out: dict[str, str] = {}
    key = None
    for line in m.group(1).splitlines():
        kv = re.match(r"^([a-zA-Z_-]+):\s*(.*)$", line)
        if kv:
            key, val = kv.group(1), kv.group(2).strip()
            out[key] = "" if val in (">", "|") else val
        elif key:
            out[key] = (out[key] + " " + line.strip()).strip()
    return out


def main() -> int:
    mk = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    registered = {p["name"]: p for p in mk["plugins"]}
    on_disk = {p.name for p in (ROOT / "plugins").iterdir() if p.is_dir()}
    for name in registered.keys() - on_disk:
        err(f"marketplace: plugin «{name}» registrato ma plugins/{name} non esiste")
    for name in on_disk - registered.keys():
        err(f"plugins/{name}: non registrato in marketplace.json")

    for name in on_disk & registered.keys():
        pdir = ROOT / "plugins" / name
        if registered[name].get("source") != f"./plugins/{name}":
            err(f"marketplace: source di «{name}» deve essere ./plugins/{name}")
        pj = json.loads((pdir / ".claude-plugin" / "plugin.json").read_text())
        if pj.get("name") != name:
            err(f"plugins/{name}/plugin.json: name «{pj.get('name')}» ≠ cartella")
        if not SEMVER.match(str(pj.get("version", ""))):
            err(f"plugins/{name}/plugin.json: version non semver")
        skills = pdir / "skills"
        for sdir in sorted(p for p in skills.iterdir() if p.is_dir()):
            f = sdir / "SKILL.md"
            if not f.exists():
                err(f"{sdir.relative_to(ROOT)}: manca SKILL.md")
                continue
            fm = frontmatter(f.read_text())
            if fm.get("name") != sdir.name:
                err(f"{f.relative_to(ROOT)}: name «{fm.get('name')}» ≠ cartella «{sdir.name}»")
            desc = fm.get("description", "")
            if not desc:
                err(f"{f.relative_to(ROOT)}: description mancante")
            elif len(desc) >= 1024:
                err(f"{f.relative_to(ROOT)}: description di {len(desc)} caratteri (max 1023)")

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix not in {".md", ".json", ".py", ".sh", ".yml", ".yaml"}:
            continue
        if path == Path(__file__).resolve():
            continue
        text = path.read_text(errors="replace")
        rel = path.relative_to(ROOT)
        if ABS_PATH.search(text):
            err(f"{rel}: contiene un path assoluto di una macchina")
        for rx in SECRETS:
            if rx.search(text):
                err(f"{rel}: sembra contenere un segreto ({rx.pattern[:24]}…)")

    if errors:
        print("Lint FALLITO:")
        for e in errors:
            print(f"  ✗ {e}")
        return 1
    print(f"Lint ok: {len(on_disk)} plugin.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
