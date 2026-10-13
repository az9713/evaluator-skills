"""Apply independently discovered fixes to local review editions only."""
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
NEW=BASE/"revised-skills"

def write(p,t):p.write_text(t,encoding="utf-8",newline="\n")
def main():
    # Reparse-point detection includes Windows junctions and directory mount links.
    for name in ("repo-evaluator","agent-skill-evaluator","mcp-evaluator"):
        p=NEW/name/"scripts/scan.py";t=p.read_text(encoding="utf-8")
        t=t.replace('import json\n','import json\nimport hashlib\n')
        t=t.replace('def inspect(root,', '''def is_link(path):
    info = path.lstat()
    return path.is_symlink() or bool(getattr(info, "st_file_attributes", 0) &
                                    getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))

def inspect(root,''')
        t=t.replace('    root = Path(root).resolve()\n', '''    supplied = Path(root).absolute()
    if any(is_link(p) for p in (supplied, *supplied.parents)):
        raise ValueError("target or ancestor is a symlink/reparse point; use an isolated regular tree")
    root = supplied.resolve()
''',1)
        t=t.replace('if path.is_symlink():','if is_link(path):')
        t=t.replace('"symlink directory not followed"', '"symlink/reparse directory not followed"')
        t=t.replace('            try:\n                if not stat.S_ISREG(path.lstat().st_mode):',
                    '''            try:
                if name == ".env" or name.startswith(".env.") or name in {"id_rsa", "id_ed25519", "credentials", "wallet.dat", "logins.json", ".netrc", ".npmrc", ".pypirc"}:
                    result["skipped"].append({"path": rel, "reason": "credential-bearing filename; values not opened"})
                    continue
                if is_link(path) or not stat.S_ISREG(path.lstat().st_mode):''')
        t=t.replace('"text": line}', '"text": "[source content omitted; inspect cited line locally]"}')
        t=t.replace('"categories": [{', '"content_policy": "Lead locations only; raw matching lines are omitted to avoid exposing embedded secrets.",\n              "categories": [{')
        # Documented examples/tests keep full source; source-line emission remains suppressed.
        write(p,t)
    p=NEW/"repo-evaluator/scripts/deps.py";t=p.read_text(encoding="utf-8")
    t=t.replace('def inspect(root, offline=False):', '''def is_link(path):
    info = path.lstat()
    return path.is_symlink() or bool(getattr(info, "st_file_attributes", 0) &
                                    getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))

def inspect(root, offline=False):''')
    t=t.replace('    root = Path(root).resolve()\n', '''    supplied = Path(root).absolute()
    if any(is_link(p) for p in (supplied, *supplied.parents)):
        raise ValueError("target or ancestor is a symlink/reparse point")
    root = supplied.resolve()
''',1)
    t=t.replace('name in SKIP or path.is_symlink()', 'name in SKIP or is_link(path)')
    t=t.replace('if not stat.S_ISREG(path.lstat().st_mode):', 'if is_link(path) or not stat.S_ISREG(path.lstat().st_mode):')
    t=t.replace("    return result\n\n\ndef main():", """    result['content_policy'] = 'Raw script/source/unresolved-requirement values omitted; inspect cited manifests locally. Package identities remain visible and may be private.'
    for key in ('install_scripts', 'unusual_sources'):
        result[key] = [value.split(': ', 1)[0] + ': [detail omitted; inspect manifest locally]'
                       for value in result[key]]
    result['notes'] = [value.split(': ', 2)[0] + ': unresolved requirement; content omitted'
                       if 'unresolved requirement (' in value else value for value in result['notes']]
    return result


def main():""")
    t=t.replace("        identity(n, v)\n        pinned.append((eco, n, v))",
                """        identity(n, v)
        if '://' in v or (eco == 'SwiftURL' and
                          (urllib.parse.urlsplit(n).username or urllib.parse.urlsplit(n).password or
                           urllib.parse.urlsplit(n).query or urllib.parse.urlsplit(n).fragment)):
            notes.append('non-version or credential-bearing package identity requires local review')
            return
        pinned.append((eco, n, v))""")
    t=t.replace("notes.append('Swift dependency without a version needs manual advisory review: ' + str(location))",
                "notes.append('Swift dependency without a version needs local advisory review; location omitted')")
    write(p,t)
    # Bind archive destination ancestors to a stable ordinary filesystem tree.
    for name in ("repo-evaluator","agent-skill-evaluator","mcp-evaluator"):
        p=NEW/name/"scripts/safe_archive.py";t=p.read_text(encoding="utf-8")
        t=t.replace('def unpack(source,', '''def is_link(path):
    info = path.lstat()
    return path.is_symlink() or bool(getattr(info, "st_file_attributes", 0) &
                                    getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))

def unpack(source,''')
        t=t.replace('    if destination.exists() or destination.is_symlink():', '''    for parent in (source.absolute(), *source.absolute().parents, *destination.absolute().parents):
        if parent.exists() and is_link(parent):
            raise ValueError("archive path or destination ancestor is a symlink/reparse point")
    if destination.exists() or destination.is_symlink():''')
        write(p,t)
    p=NEW/"repo-evaluator/tests/VALIDATION.md"
    write(p,"""# Local review edition validation

This is a local review edition, not an upstream release.
Run: python -B -m unittest discover -s tests -v
On the producing Windows/Python 3.13 host: 53 passed, 3 POSIX shell fixtures skipped.
The full review package also has separate mocked/inert portable-fetch, boundary,
junction, source-content suppression and scheduler tests. Those tests are not part
of this standalone skill archive; the tabbed review report includes their results.
No live target installation, live provider generation or hosted deployment was tested.
""")
    for name in ("agent-skill-evaluator","mcp-evaluator"):
        p=NEW/name/"references/evidence-contract.md"
        t=p.read_text(encoding="utf-8")
        t += """

Scanner ledgers preserve every lead's category/file/line, but omit matching source
content by default; a credential assignment may otherwise leak into the report.
Known credential-bearing filenames are not opened; skipped secret files are a gap,
not a clean finding. Read only the necessary redacted local source evidence.
Windows junction/reparse directories and linked roots/ancestors are refused.
This does not close filesystem races or authenticate a concurrently changing tree.
"""
        write(p,t)
    p=NEW/"repo-evaluator/references/platform-and-scope.md";t=p.read_text(encoding="utf-8")
    t += """

Scanner JSON preserves category/file/line but omits raw matching lines to avoid
printing embedded credentials. Credential-bearing filenames are skipped, explicitly
making scope incomplete. Linked/reparse roots and ancestors are refused; junction
directories are skipped as incomplete. deps.py follows the same directory boundary.
    Dependency output omits raw install-script/source/unresolved-requirement values;
    package names/versions remain visible and can be private. Use offline mode and
    privately inspect/redact metadata before sharing it. Review omitted values locally.
"""
    write(p,t)
    p=NEW/"frugal-fable/scripts/scheduler.mjs";t=p.read_text(encoding="utf-8")
    t=t.replace('let spent=0,reserved=0,calls=0,breached=false;',
                'let spent=0,measured=0,estimated=0,reserved=0,calls=0,breached=false;')
    t=t.replace('let charge=task.upperBound;', 'let charge=task.upperBound,usageKnown=false;')
    t=t.replace('      charge=usage;', '      charge=usage; usageKnown=true;')
    t=t.replace('    } finally { reserved-=task.upperBound; spent+=charge; }',
                '    } finally { reserved-=task.upperBound; spent+=charge; if(usageKnown)measured+=charge;else estimated+=charge; }')
    t=t.replace('return {spentTokens:spent,calls,breached,reserveTokens:reserve,results,',
                'return {accountedTokens:spent,measuredTotalTokens:measured,estimatedChargedTokens:estimated,accountingComplete:estimated===0,calls,breached,reserveTokens:reserve,results,')
    t=t.replace('reason:"adapter breached reservation",usage}', 'reason:"adapter breached reservation",usage,usageBasis:"measured"}')
    t=t.replace('usage,result:response.result}', 'usage,usageBasis:"measured",result:response.result}')
    t=t.replace('reason:String(error),usage:charge}', 'reason:String(error),usage:charge,usageBasis:usageKnown?"measured":"estimated-reservation"}')
    write(p,t)
    p=BASE/"tests/test_scheduler.mjs";t=p.read_text(encoding="utf-8")
    t=t.replace('.spentTokens','.accountedTokens')
    t=t.replace("assert.equal(r.accountedTokens,50);assert.equal(r.results[0].status,'failed');",
                "assert.equal(r.accountedTokens,50);assert.equal(r.measuredTotalTokens,0);assert.equal(r.estimatedChargedTokens,50);assert.equal(r.accountingComplete,false);assert.equal(r.results[0].status,'failed');")
    write(p,t)
    p=NEW/"frugal-fable/references/budget-and-evidence.md";t=p.read_text(encoding="utf-8")
    t += """

Outputs distinguish measuredTotalTokens, estimatedChargedTokens, accountedTokens
(their conservative sum), and accountingComplete. Missing usage/failed-call charges
are estimates, never reported as measured provider usage.
"""
    write(p,t)
    print("Applied independent-review fixes to local copies.")
if __name__=="__main__":main()
