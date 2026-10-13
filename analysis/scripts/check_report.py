from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import zipfile
BASE=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.links=[];self.tabs=0;self.panels=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if "id" in a:self.ids.append(a["id"])
        if tag=="a" and "href" in a:self.links.append(a["href"])
        self.tabs+=a.get("role")=="tab"
        self.panels+=a.get("role")=="tabpanel"
def main():
    p=Page();p.feed((BASE/"index.html").read_text(encoding="utf-8"))
    assert len(p.ids)==len(set(p.ids)),"duplicate IDs"
    assert p.tabs==p.panels==5
    for link in p.links:
        if link.startswith("http"):continue
        if link.startswith("#"):assert link[1:] in p.ids,link
        else:assert (BASE/link).is_file(),link
    for name in ("agent-skill-evaluator","mcp-evaluator","repo-evaluator","prd-creator","frugal-fable"):
        with zipfile.ZipFile(BASE/"packages"/(name+".zip")) as z:
            for entry in z.infolist():
                expected=(BASE/"revised-skills"/entry.filename).read_bytes()
                assert z.read(entry)==expected,"package mismatch "+entry.filename
    manifest=json.loads((BASE/"evidence/source-manifest.json").read_text(encoding="utf-8"))
    for e in manifest:
        source=BASE/"original-snapshot"/e["path"]
        assert hashlib.sha256(source.read_bytes()).hexdigest()==e["sha256"],"original changed"
    result={"tabs":p.tabs,"panels":p.panels,"source_files":len(manifest),"source_lines":sum(e["lines"] for e in manifest),
            "anchors_unique":True,"all_local_links_exist":True,"individual_packages_byte_identical":True,
            "original_files_unchanged":True,"links_checked":len(p.links)}
    (BASE/"evidence/artifact-validation.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result))
if __name__=="__main__":main()
