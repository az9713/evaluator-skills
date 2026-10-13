"""Structure check for the constrained frontmatter used in this package."""
from pathlib import Path
import re,sys
def main():
    p=Path(sys.argv[1]);t=(p/"SKILL.md").read_text(encoding="utf-8")
    m=re.match(r"^---\n(.*?)\n---\n",t,re.S)
    if not m:raise ValueError("missing frontmatter")
    name=re.search(r"^name: ([a-z0-9]+(?:-[a-z0-9]+)*)$",m[1],re.M)
    desc=re.search(r"^description: (.+)$",m[1],re.M)
    if not name or name[1]!=p.name or len(name[1])>=64:raise ValueError("invalid name")
    if not desc or len(desc[1])>1024:raise ValueError("invalid description")
    if not re.search(r'^  version: "[^"]+"$',m[1],re.M):raise ValueError("missing version")
    print("Structure valid; not behavior certification.")
if __name__=="__main__":main()
