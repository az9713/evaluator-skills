"""Keep executable review editions LF-only; preserve immutable upstream bytes."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for base in (ROOT/"analysis/revised-skills",ROOT/"jeredblu-tools/skills"):
    for p in base.rglob("*"):
        if p.is_file() and p.suffix in {".sh",".py",".mjs",".js",".md",".json",".txt"}:
            p.write_bytes(p.read_bytes().replace(b"\r\n",b"\n"))
for name in ("build_revisions.py","harden_review_editions.py"):
    p=ROOT/"analysis/scripts"/name
    t=p.read_text(encoding="utf-8")
    # write helpers (not readers) explicitly preserve portable newline semantics.
    t=t.replace('path.write_text(textwrap.dedent(text).strip() + "\\n", encoding="utf-8")',
                'path.write_text(textwrap.dedent(text).strip() + "\\n", encoding="utf-8", newline="\\n")')
    t=t.replace('p.write_text(t,encoding="utf-8")','p.write_text(t,encoding="utf-8",newline="\\n")')
    p.write_text(t,encoding="utf-8",newline="\n")
