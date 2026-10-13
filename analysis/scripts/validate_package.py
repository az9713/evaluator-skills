"""Validate local skill editions and preserve current evidence; no live provider calls."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
BASE=Path(__file__).resolve().parents[1]
NEW=BASE/"revised-skills"
VALIDATOR=BASE.parent/"scripts/check_skill.py"

def main():
    report={"date":"2026-10-12","platform":platform.system(),
            "python":str(sys.version_info.major)+"."+str(sys.version_info.minor),"tests":{},"skill_frontmatter":[],"syntax":[]}
    checks=[
        ("repo-revision",[sys.executable,"-B","-m","unittest","discover","-s",str(NEW/"repo-evaluator/tests"),"-v"]),
        ("revision",[sys.executable,"-B","-m","unittest","discover","-s",str(BASE/"tests"),"-v"]),
        ("scheduler",["node",str(BASE/"tests/test_scheduler.mjs")]),
    ]
    success=True
    for name,args in checks:
        r=subprocess.run(args,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=60)
        log=r.stdout+r.stderr
        (BASE/"evidence"/(name+"-tests.txt")).write_text(log,encoding="utf-8")
        ran=re.search(r"Ran (\d+) tests",log)
        skipped=re.search(r"skipped=(\d+)",log)
        if name=="scheduler":
            count=json.loads(log.splitlines()[-1])["tests"] if r.returncode==0 else None
        else:count=int(ran[1]) if ran else None
        report["tests"][name]={"command":args,"exit_code":r.returncode,"ran":count,
                               "skipped":int(skipped[1]) if skipped else 0,"log":name+"-tests.txt"}
        success &= r.returncode==0
    for s in sorted(p for p in NEW.iterdir() if p.is_dir()):
        r=subprocess.run([sys.executable,"-X","utf8",str(VALIDATOR),str(s)],capture_output=True,text=True,timeout=20)
        report["skill_frontmatter"].append({"skill":s.name,"exit_code":r.returncode,"output":r.stdout+r.stderr})
        success &= r.returncode==0
    for p in NEW.rglob("*.py"):
        ast.parse(p.read_text(encoding="utf-8"),filename=str(p))
        report["syntax"].append(p.relative_to(NEW).as_posix())
    # Recompute exact diffs after independently discovered fixes.
    changes=[]
    for s in sorted(p for p in NEW.iterdir() if p.is_dir()):
        old=BASE/"original-snapshot"/s.name
        paths=sorted({p.relative_to(old).as_posix() for p in old.rglob("*") if p.is_file()} |
                     {p.relative_to(s).as_posix() for p in s.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix!=".pyc"})
        diff=[]
        for rel in paths:
            a=(old/rel).read_text(encoding="utf-8").splitlines(True) if (old/rel).exists() else []
            b=(s/rel).read_text(encoding="utf-8").splitlines(True) if (s/rel).exists() else []
            if a!=b:
                changes.append({"skill":s.name,"path":rel,"action":"changed" if a and b else "added" if b else "removed"})
                diff.extend(difflib.unified_diff(a,b,fromfile="original/"+s.name+"/"+rel,tofile="revised/"+s.name+"/"+rel))
        (BASE/"diffs"/(s.name+".diff")).write_text("".join(diff),encoding="utf-8")
    (BASE/"evidence/changes.json").write_text(json.dumps(changes,indent=2),encoding="utf-8")
    report["all_passed"]=bool(success)
    report["limits"]=["No live provider adapter, cross-CLI run, hosted MCP deployment or target installation tested.",
                      "Legacy artifact/metadata sampling is documented, not comprehensively rewritten.",
                      "Tests do not establish detection accuracy, empirical scoring calibration or model quality."]
    (BASE/"evidence/validation.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({k:{"ran":v["ran"],"skipped":v["skipped"],"exit_code":v["exit_code"]} for k,v in report["tests"].items()}))
    print("Five skill validator results:",[x["exit_code"] for x in report["skill_frontmatter"]])
    return 0 if success else 1
if __name__=="__main__":sys.exit(main())
