"""Write the build receipt: which tools turned which exact bytes into which outputs.

`python -m analysis.build_receipt <output>...` prints JSON to stdout. The
receipt is the input to the PROV-O projection in `provenance/`; it names
every input and output by SHA-256 and by RFC 6920 `ni:` URI.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT_GLOBS = (
    "paper.yaml",
    "manuscript/*.md",
    "manuscript/build.yaml",
    "manuscript/filters/*.lua",
    "references/references.yaml",
    "references/*.csl",
    "figures/*.svg",
    "data/records/*.json",
    "data/derived/*",
    "analysis/*.py",
)


def identify(path: Path) -> dict:
    data = path.read_bytes()
    digest = hashlib.sha256(data).digest()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(data),
        "sha256": digest.hex(),
        "ni": "ni:///sha-256;" + base64.urlsafe_b64encode(digest).decode().rstrip("="),
    }


def version(command: list[str]) -> str | None:
    try:
        return subprocess.run(command, capture_output=True, text=True, check=True).stdout.splitlines()[0].strip()
    except (OSError, subprocess.CalledProcessError, IndexError):
        return None


def git(*args: str) -> str | None:
    return version(["git", "-C", str(ROOT), *args])


def receipt(outputs: list[str]) -> dict:
    inputs = sorted({p for pattern in INPUT_GLOBS for p in ROOT.glob(pattern) if p.is_file()})
    return {
        "kind": "lenticule.research-build-receipt.v1",
        "paper": "white-repopulation",
        "source": {"repository": git("config", "--get", "remote.origin.url"), "revision": git("rev-parse", "HEAD"),
                   "dirty": bool(version(["git", "-C", str(ROOT), "status", "--porcelain", "--", "."]))},
        "sourceDateEpoch": os.environ.get("SOURCE_DATE_EPOCH"),
        "toolchain": {
            "pandoc": version(["pandoc", "--version"]),
            "lualatex": version(["lualatex", "--version"]),
            "rsvg-convert": version(["rsvg-convert", "--version"]),
            "python": sys.version.split()[0],
        },
        "inputs": [identify(p) for p in inputs],
        "outputs": [identify(ROOT / o) for o in outputs],
    }


if __name__ == "__main__":
    json.dump(receipt(sys.argv[1:]), sys.stdout, indent=2)
    sys.stdout.write("\n")
