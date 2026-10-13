"""Build static Pages files without deploying. Reuse immutable original evidence."""
from pathlib import Path
import re,shutil,subprocess,sys
from privacy import scrub_text, scrub_evidence
ROOT=Path(__file__).resolve().parents[1]
def scrub(t):
    return scrub_text(t)
def copy(source,dest):
    for p in source.rglob("*"):
        if not p.is_file() or "__pycache__" in p.parts or p.suffix==".pyc":continue
        q=dest/p.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True)
        if p.suffix in {".md",".py",".js",".mjs",".sh",".json",".txt",".html",".diff",""}:
                original=p.read_text(encoding="utf-8");sanitized=scrub(original)
                if original==sanitized:shutil.copyfile(p,q)
                else:q.write_text(sanitized,encoding="utf-8")
        else:shutil.copyfile(p,q)
def main():
    subprocess.run([sys.executable,"-B",str(ROOT/"scripts/normalize_editions.py")],check=True)
    subprocess.run([sys.executable,"-B",str(ROOT/"analysis/scripts/build_report.py")],check=True)
    docs=ROOT/"docs";docs.mkdir(exist_ok=True)
    text=(ROOT/"analysis/index.html").read_text(encoding="utf-8")
    text=text.replace("This downloaded directory has no Git metadata", "The reviewed upstream snapshot had no Git metadata")
    text=text.replace("Pixel screenshot inspection was unavailable in this session. No claim of a screenshot-based visual review is made.",
                      "The original review did not obtain a pixel screenshot. Publication subsequently added a headless-Chrome rendered preview; hosted checks are recorded in <a href='evidence/live-browser-validation.json'>live-browser-validation.json</a>.")
    text=text.replace('<header class="mast">','<header class="mast"><p style="font-size:15px"><a href="https://github.com/az9713/evaluator-skills">Repository and modified skills</a> · Clone-derived from <a href="https://github.com/JeredBlu/jeredblu-marketplace">JeredBlu Marketplace</a></p>')
    (docs/"index.html").write_text(scrub(text),encoding="utf-8")
    (docs/".nojekyll").touch()
    for directory in ("evidence","diffs","packages"):
        copy(ROOT/"analysis"/directory,docs/directory)
    copy(ROOT/"analysis/revised-skills",docs/"revised-skills")
    # Canonical install folders match the report/downloads byte for byte.
    copy(ROOT/"analysis/revised-skills",ROOT/"jeredblu-tools/skills")
    (ROOT/"downloads").mkdir(exist_ok=True)
    for z in (ROOT/"analysis/packages").glob("*.zip"):
        if z.name!="revised-skills.zip":shutil.copyfile(z,ROOT/"downloads"/z.name)
    for p in (ROOT/"analysis/evidence").glob("*"):
        if p.is_file() and p.suffix in {".json",".md",".txt"}:
            p.write_text(scrub(p.read_text(encoding="utf-8")),encoding="utf-8")
    scrub_evidence()
    # Avoid workstation-specific archive timestamps and optional metadata.
    import zipfile
    for archive in ROOT.rglob("*.zip"):
        if ".git" in archive.parts:continue
        with zipfile.ZipFile(archive) as old:
            items=[(i.filename,old.read(i)) for i in old.infolist() if not i.is_dir()]
        with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as new:
            for filename,data in items:
                info=zipfile.ZipInfo(filename,date_time=(1980,1,1,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED
                info.create_system=3
                info.external_attr=0o100644<<16
                new.writestr(info,data)
    print("Built docs/index.html; no deployment performed.")
if __name__=="__main__":main()
