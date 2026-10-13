"""Check public privacy boundaries, site links, source hashes and ZIP equality."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,re,zipfile
from privacy import private_features
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=[];self.tabs=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if "id" in a:self.ids.append(a["id"])
        if tag=="a" and "href" in a:self.links.append(a["href"])
        self.tabs+=a.get("role")=="tab"
def main():
    bad=[]
    patterns=[r"(?i)[\\/]+Users[\\/]+(?!<)[A-Za-z0-9_.-]+[\\/]",r"file:///"+"C:",r"(?i)gh[opusr]_[A-Za-z0-9]{20,}"]
    for p in ROOT.rglob("*"):
        if not p.is_file() or ".git" in p.parts or "__pycache__" in p.parts or p.suffix in {".png",".zip",".pyc"}:continue
        text=p.read_text(encoding="utf-8")
        if any(re.search(x,text) for x in patterns) or private_features(text):bad.append(p.relative_to(ROOT).as_posix())
    page=Page();page.feed((ROOT/"docs/index.html").read_text(encoding="utf-8"))
    assert page.tabs==5 and len(page.ids)==len(set(page.ids))
    for url in page.links:
        if url.startswith("http"):continue
        if url.startswith("#"):assert url[1:] in page.ids,url
        else:assert (ROOT/"docs"/url).is_file(),url
    for archive in (ROOT/"docs/packages").glob("*.zip"):
        with zipfile.ZipFile(archive) as z:
            for info in z.infolist():
                assert z.read(info)==(ROOT/"jeredblu-tools/skills"/info.filename).read_bytes()
    for archive in ROOT.rglob("*.zip"):
        if ".git" in archive.parts:continue
        with zipfile.ZipFile(archive) as z:
            for info in z.infolist():
                if info.is_dir():continue
                try:content=z.read(info).decode("utf-8")
                except UnicodeDecodeError:continue
                assert not private_features(content),archive.name+" contains personal identifiers"
    for e in json.loads((ROOT/"analysis/evidence/source-manifest.json").read_text(encoding="utf-8")):
        assert hashlib.sha256((ROOT/"analysis/original-snapshot"/e["path"]).read_bytes()).hexdigest()==e["sha256"]
    assert not bad,"Public local-identifier matches: "+str(bad)
    print("PASS: privacy patterns, original hashes, ZIP equality, five tabs, site links.")
if __name__=="__main__":main()
