#!/usr/bin/env python3
"""Import skill(s) from a source GitHub repo into categories/<category>/.

Usage:
  python3 tools/add_skill.py <repo-url> --path <path-in-repo> --category <cat>
                             [--only name1,name2] [--requires "a;b"]

- Sparse blob-filtered clone at HEAD; the resolved commit is pinned in
  skill.json.
- Copies runtime files only: dev/test folders (tests, __tests__, test,
  .github, node_modules) are excluded at any depth; runtime data is kept.
- License gate: every imported skill folder must end up with a LICENSE file
  (its own, else the source repo's root LICENSE). A skill that fails the
  gate is skipped and reported; the command exits non-zero.
- With --link-only, no files are copied and the license gate does not apply:
  the destination folder holds only skill.json with entry "link-only"
  (for useful skills whose license forbids redistribution). --path must be
  the skill folder itself in this mode.
- Writes skill.json with description/why as TODO for the maintainer.

Stdlib only (plus git on PATH).
"""
import argparse
import datetime
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {"tests", "__tests__", "test", ".github", "node_modules",
                ".git", "__pycache__", ".hg", ".svn"}
LICENSE_NAMES = ("LICENSE", "LICENCE", "COPYING")


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def slug_from_url(url):
    match = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$", url)
    if not match:
        raise SystemExit(f"cannot parse owner/repo from {url}")
    return f"{match.group(1)}/{match.group(2)}"


def api_json(url):
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                                   "User-Agent": "prime-skill-add"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def repo_info(slug):
    try:
        data = api_json(f"https://api.github.com/repos/{slug}")
        return data.get("stargazers_count"), (data.get("license") or {}).get("spdx_id")
    except Exception:
        return None, None


def detect_license(text, spdx):
    if spdx and spdx != "NOASSERTION":
        return spdx
    if not text:
        return "See LICENSE"
    if "MIT License" in text:
        return "MIT"
    if "Apache License" in text and "Version 2.0" in text:
        return "Apache-2.0"
    if "BSD 3-Clause" in text:
        return "BSD-3-Clause"
    if "BSD 2-Clause" in text:
        return "BSD-2-Clause"
    return "See LICENSE"


def find_license_file(folder):
    for path in sorted(folder.iterdir()):
        if path.is_file() and path.name.upper().startswith(LICENSE_NAMES):
            return path
    return None


def copy_runtime(src, dst):
    def ignore(_dir, names):
        return [n for n in names if n in EXCLUDE_DIRS or n == ".DS_Store"]
    shutil.copytree(src, dst, ignore=ignore)


def frontmatter_name(skill_md):
    try:
        text = skill_md.read_text(encoding="utf-8", errors="replace")[:4096]
    except OSError:
        return None
    if not text.startswith("---"):
        return None
    block = text[3:].split("---", 1)[0]
    match = re.search(r"^name:\s*[\"']?([^\"'\n]+)[\"']?\s*$", block, re.M)
    return match.group(1).strip() if match else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--path", required=True, help="skill folder or folder of skills, in-repo path")
    parser.add_argument("--category", required=True)
    parser.add_argument("--only", default="", help="comma-separated skill folder names")
    parser.add_argument("--requires", default="", help="semicolon-separated requirement labels")
    parser.add_argument("--link-only", action="store_true",
                        help="record metadata only (skill.json, entry=link-only); copy no files")
    args = parser.parse_args()

    slug = slug_from_url(args.url)
    only = {n.strip() for n in args.only.split(",") if n.strip()}
    requires = [r.strip() for r in args.requires.split(";") if r.strip()]

    tmp = Path(tempfile.mkdtemp(prefix="prime-skill-import-"))
    try:
        clone = tmp / "repo"
        run(["git", "clone", "--filter=blob:none", "--sparse", "--depth", "1", args.url, str(clone)])
        if args.path not in (".", ""):
            run(["git", "sparse-checkout", "set", args.path], cwd=clone)
        else:
            run(["git", "checkout"], cwd=clone)
        commit = run(["git", "rev-parse", "HEAD"], cwd=clone)
        stars, spdx = repo_info(slug)
        root_license = find_license_file(clone)

        base = clone / args.path
        if not base.is_dir():
            raise SystemExit(f"path not found in repo: {args.path}")
        if (base / "SKILL.md").exists():
            skill_dirs = [base]
            path_of = {base: args.path}
        else:
            skill_dirs = sorted(p for p in base.iterdir()
                                if p.is_dir() and (p / "SKILL.md").exists())
            path_of = {p: f"{args.path.rstrip('/')}/{p.name}" for p in skill_dirs}
        if only:
            skill_dirs = [p for p in skill_dirs if p.name in only]
        if not skill_dirs:
            raise SystemExit("no skill folders found (nothing matched)")

        if args.link_only and not (base / "SKILL.md").exists():
            raise SystemExit("--link-only requires --path to be the skill folder itself")
        failures = []
        imported = []
        for src in skill_dirs:
            name = src.name
            dest = ROOT / "categories" / args.category / name
            if dest.exists():
                failures.append(f"{name}: destination already exists, skipped")
                continue
            if args.link_only:
                dest.mkdir(parents=True)
                license_text = (root_license.read_text(encoding="utf-8", errors="replace")
                                if root_license is not None else "")
                title = frontmatter_name(src / "SKILL.md") or name.replace("-", " ").title()
                meta = {
                    "name": name,
                    "title": title,
                    "description": "TODO",
                    "why": "TODO",
                    "category": args.category,
                    "source": {"repo": slug, "url": f"https://github.com/{slug}",
                               "path": path_of[src], "commit": commit},
                    "license": detect_license(license_text, spdx),
                    "stars_at_import": stars,
                    "added": datetime.date.today().isoformat(),
                    "requires": requires,
                    "entry": "link-only",
                    "adapted": False,
                    "adaptations": "",
                }
                (dest / "skill.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
                                                 encoding="utf-8")
                imported.append(name)
                continue
            copy_runtime(src, dest)
            license_file = find_license_file(dest)
            if license_file is None and root_license is not None:
                shutil.copy2(root_license, dest / root_license.name)
                license_file = dest / root_license.name
            if license_file is None:
                shutil.rmtree(dest)
                failures.append(f"{name}: LICENSE GATE FAILED - no LICENSE in skill folder or repo root")
                continue
            license_text = license_file.read_text(encoding="utf-8", errors="replace")
            title = frontmatter_name(src / "SKILL.md") or name.replace("-", " ").title()
            meta = {
                "name": name,
                "title": title,
                "description": "TODO",
                "why": "TODO",
                "category": args.category,
                "source": {"repo": slug, "url": f"https://github.com/{slug}",
                           "path": path_of[src], "commit": commit},
                "license": detect_license(license_text, spdx),
                "stars_at_import": stars,
                "added": datetime.date.today().isoformat(),
                "requires": requires,
                "entry": "full",
                "adapted": False,
                "adaptations": "",
            }
            (dest / "skill.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
                                             encoding="utf-8")
            imported.append(name)
        print(json.dumps({"source": slug, "commit": commit, "stars": stars,
                          "imported": imported, "failures": failures}, indent=1))
        return 1 if failures else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
