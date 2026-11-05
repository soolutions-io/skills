#!/usr/bin/env python3
"""Aggiorna le skill del plugin `portal` da quelle pubblicate dal portale.

La fonte di verità è il gestionale: le skill descrivono la CLI che gira in
produzione, e il portale le serve già (`/downloads/SKILL*.md`) insieme a un
manifest con versione e sha256. Questo script:

  1. scarica il manifest e ogni skill;
  2. verifica lo sha256 di ciascun file contro il manifest (un file diverso da
     quello dichiarato non entra);
  3. scrive le skill in `plugins/portal/skills/<dir>/SKILL.md`;
  4. allinea `version` del plugin alla versione della CLI.

Uso:  python3 scripts/sync_from_portal.py [--base-url URL] [--check]
      --check: non scrive niente, esce 1 se il repo è indietro rispetto al portale.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "portal"

# variante del manifest → cartella della skill nel plugin
VARIANT_DIRS = {"portal-cli": "portal-cli", "partner": "portal-partner"}
MAX_BYTES = 64 * 1024


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "soolutions-skills-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 (URL fisso https)
        body = r.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise SystemExit(f"{url}: oltre {MAX_BYTES} byte, rifiutato")
    return body


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="https://customers.soolutions.io")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    base = args.base_url.rstrip("/")
    if not base.startswith("https://"):
        raise SystemExit("--base-url deve essere https")

    manifest = json.loads(fetch(f"{base}/downloads/cli-manifest.json"))
    version = manifest["version"]
    stale: list[str] = []

    for entry in manifest["skills"]:
        folder = VARIANT_DIRS.get(entry["variant"])
        if not folder:
            print(f"! variante sconosciuta «{entry['variant']}»: ignorata (aggiorna VARIANT_DIRS)")
            continue
        body = fetch(f"{base}/downloads/{entry['file']}")
        digest = hashlib.sha256(body).hexdigest()
        if digest != entry["sha256"]:
            raise SystemExit(f"{entry['file']}: sha256 {digest} ≠ manifest {entry['sha256']}")
        dest = PLUGIN / "skills" / folder / "SKILL.md"
        if not dest.exists() or dest.read_bytes() != body:
            stale.append(str(dest.relative_to(ROOT)))
            if not args.check:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(body)

    pj_path = PLUGIN / ".claude-plugin" / "plugin.json"
    pj = json.loads(pj_path.read_text())
    if pj.get("version") != version:
        stale.append(f"{pj_path.relative_to(ROOT)} (version {pj.get('version')} → {version})")
        if not args.check:
            pj["version"] = version
            pj_path.write_text(json.dumps(pj, indent=2, ensure_ascii=False) + "\n")

    if not stale:
        print(f"Allineato alla CLI {version}.")
        return 0
    print(("Indietro rispetto al portale" if args.check else "Aggiornato") + f" (CLI {version}):")
    for s in stale:
        print(f"  - {s}")
    return 1 if args.check else 0


if __name__ == "__main__":
    sys.exit(main())
