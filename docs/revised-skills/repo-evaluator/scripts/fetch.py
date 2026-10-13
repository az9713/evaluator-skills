#!/usr/bin/env python3
"""Public GitHub fetch for static review. Never executes target code; no private auth."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit

def parse_spec(spec):
    if "://" in spec:
        u = urlsplit(spec)
        if u.scheme != "https" or u.netloc.lower() != "github.com" or u.query or u.fragment:
            raise ValueError("use an exact public https://github.com/owner/repo URL")
        spec = u.path.strip("/")
    spec = spec.removesuffix(".git")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", spec):
        raise ValueError("expected owner/repo; select branch separately")
    if any(p in {".", ".."} or p.startswith("-") for p in spec.split("/")):
        raise ValueError("invalid repository component")
    return spec

def git_env():
    env = {k:v for k,v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_CONFIG_COUNT="0", GIT_TERMINAL_PROMPT="0", GIT_LFS_SKIP_SMUDGE="1")
    return env

def fetch(spec, depth=300, ref=None):
    spec = parse_spec(spec)
    if type(depth) is not int or not 1 <= depth <= 10000:
        raise ValueError("depth must be 1..10000")
    if ref and (ref.startswith("-") or any(ord(c)<32 for c in ref)):
        raise ValueError("invalid branch/tag")
    work = Path(tempfile.mkdtemp(prefix="repo-eval."))
    checkout = work/"src"
    base = ["git", "-c", "init.templateDir=", "-c", "core.hooksPath="+os.devnull,
            "-c", "core.fsmonitor=false", "-c", "protocol.file.allow=never",
            "-c", "submodule.recurse=false", "-c", "credential.helper="]
    command = base + ["clone", "--quiet", "--depth", str(depth), "--single-branch",
                      "--no-recurse-submodules"]
    if ref:
        command += ["--branch", ref]
    command += ["https://github.com/"+spec+".git", str(checkout)]
    def run(cmd):
        return subprocess.run(cmd, env=git_env(), capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=120, check=True)
    try:
        run(command)
        revision = run(base+["-C", str(checkout), "rev-parse", "HEAD"]).stdout.strip()
        if not re.fullmatch("[0-9a-f]{40}", revision):
            raise ValueError("could not verify commit")
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        raise ValueError("fetch failed; preserve this partial temp directory for inspection: "+
                         str(work)+": "+str(exc)) from exc
    return {"repository":spec, "commit":revision, "workdir":str(work),
            "checkout":str(checkout), "submodules_fetched":False, "lfs_fetched":False}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("spec"); p.add_argument("--depth", type=int, default=300); p.add_argument("--ref")
    a=p.parse_args()
    try:
        print(json.dumps(fetch(a.spec,a.depth,a.ref),indent=2)); return 0
    except ValueError as exc:
        print(str(exc),file=sys.stderr); return 2
if __name__ == "__main__": sys.exit(main())
