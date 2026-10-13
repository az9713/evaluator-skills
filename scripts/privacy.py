"""Public-evidence minimization. Emails and intentional public source URLs are retained."""
from pathlib import Path
import json
import os
import re
ROOT=Path(__file__).resolve().parents[1]
PROFILE=re.compile(r"(?i)[A-Z]:Users[^\s\"'<>]+")
ZONE=re.compile(r"\bAmerica/[A-Za-z_]+\b")
EMAIL=re.compile(r"[A-Za-z0-9.!#$%&'*+/=?^_\x60{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PUBLIC_URL=re.compile(r"https?://(?:github\.com|[A-Za-z0-9-]+\.github\.io)[^\s<>\"']*")

def without_allowed_identity(text):
    return PUBLIC_URL.sub("[public-url]",EMAIL.sub("[email]",text))

def scrub_text(text):
    retained=[]
    def hold(match):
        retained.append(match[0])
        return "PUBLICIDENTITYPLACEHOLDER"+str(len(retained)-1)+"END"
    text=PUBLIC_URL.sub(hold,EMAIL.sub(hold,text))
    for prefix in (str(ROOT),str(Path.home())):
        for form in (prefix,prefix.replace("\\","\\\\"),prefix.replace("\\","/"),
                     prefix.replace("\\","")):
            text=re.sub(re.escape(form),"<local-path>",text,flags=re.I)
    text=PROFILE.sub("<local-path>",text)
    local_name=Path.home().name
    if len(local_name)>=4 and local_name not in {"root","runner","user","test"}:
        text=re.sub(r"\b"+re.escape(local_name)+r"\b","[redacted]",text,flags=re.I)
    text=ZONE.sub("location omitted",text)
    text=re.sub(r"(?i)Windows-\d+-\d+\.\d+\.\d+-[A-Za-z0-9]+","Windows",text)
    text=re.sub(r'file:///+<local-path>[^\s"<]*',"local-preview",text)
    for index,value in enumerate(retained):
        text=text.replace("PUBLICIDENTITYPLACEHOLDER"+str(index)+"END",value)
    return text

def clean_json(value):
    if isinstance(value,list):return [clean_json(v) for v in value]
    if isinstance(value,dict):
        result={k:clean_json(v) for k,v in value.items()
                if k not in {"timezone","initial_live_commit"}}
        if "platform" in result and isinstance(result["platform"],str):
            result["platform"]=result["platform"].split("-")[0]
        if "python" in result and isinstance(result["python"],str):
            m=re.match(r"(\d+\.\d+)",result["python"])
            if m:result["python"]=m[1]
        if isinstance(result.get("command"),list):
            command=result["command"]
            if command and str(command[0]).lower().endswith(("python.exe","python","python3")):
                command[0]="python"
            result["command"]=[re.sub(r"^<local-path>[\\/]+","",str(v)).replace("\\","/") for v in command]
        if isinstance(result.get("url"),str) and result["url"].startswith("local-preview"):
            result["url"]="Local report preview (path omitted)"
        return result
    if isinstance(value,str):return scrub_text(value)
    return value

def private_features(text):
    text=without_allowed_identity(text)
    result=[]
    if PROFILE.search(text):result.append("collapsed local profile path")
    if re.search(r"(?i)[\\/]+Users[\\/]+(?!<)[A-Za-z0-9_.-]+[\\/]",text):
        result.append("user profile path")
    local_name=Path.home().name
    if len(local_name)>=4 and local_name not in {"root","runner","user","test"} and re.search(r"\b"+re.escape(local_name)+r"\b",text,re.I):
        result.append("local username")
    if ZONE.search(text):result.append("personal timezone")
    if re.search(r"Windows-\d+-\d+\.\d+\.\d+",text):result.append("machine build fingerprint")
    if re.search(r"(?i)gh[opusr]_[A-Za-z0-9]{20,}",text):result.append("credential token")
    return result

def scrub_evidence():
    for base in (ROOT/"analysis/evidence",ROOT/"docs/evidence"):
        for p in base.glob("*"):
            if not p.is_file() or p.suffix not in {".json",".txt",".md"}:continue
            text=p.read_text(encoding="utf-8")
            if p.suffix==".json":
                cleaned=json.dumps(clean_json(json.loads(text)),indent=2)+"\n"
            else:cleaned=scrub_text(text)
            p.write_text(cleaned,encoding="utf-8",newline="\n")

if __name__=="__main__":
    scrub_evidence()
    print("Public evidence minimized; emails and public URLs retained.")
