"""Offline tests of meaningful security/portability invariants; payloads stay inert."""
import importlib.util
from pathlib import Path
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT=Path(__file__).resolve().parents[1]/"revised-skills"
def mod(skill,name):
    spec=importlib.util.spec_from_file_location(skill.replace("-","_")+"_"+name,ROOT/skill/"scripts"/(name+".py"))
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj

fetch=mod("repo-evaluator","fetch")
boundary=mod("mcp-evaluator","boundaries")

class PortableFetchTests(unittest.TestCase):
    def test_exact_origin_validation(self):
        self.assertEqual(fetch.parse_spec("https://github.com/owner/repo.git"),"owner/repo")
        for value in ("http://github.com/o/r","https://github.com.evil/o/r","https://evil/o/r",
                      "https://github.com/o/r/tree/main","o/r;run","../r","-x/r"):
            with self.subTest(value=value),self.assertRaises(ValueError):fetch.parse_spec(value)
    def test_environment_isolated(self):
        with patch.dict(os.environ,{"GIT_CONFIG_PARAMETERS":"evil","GIT_CONFIG_KEY_0":"filter.fake",
                                   "GIT_SSL_NO_VERIFY":"true"},clear=False):
            env=fetch.git_env()
        self.assertNotIn("GIT_CONFIG_PARAMETERS",env)
        self.assertNotIn("GIT_CONFIG_KEY_0",env)
        self.assertNotIn("GIT_SSL_NO_VERIFY",env)
        self.assertEqual(env["GIT_CONFIG_GLOBAL"],os.devnull)
        self.assertEqual(env["GIT_CONFIG_COUNT"],"0")
    def test_mocked_fetch_arguments_and_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            def run(command,**kwargs):
                self.assertFalse(kwargs.get("shell",False))
                self.assertNotIn("cwd",kwargs)
                return subprocess.CompletedProcess(command,0,"a"*40+"\n" if "rev-parse" in command else "","")
            with patch.object(fetch.tempfile,"mkdtemp",return_value=td),patch.object(fetch.subprocess,"run",side_effect=run) as invoke:
                receipt=fetch.fetch("o/r",5,"v1")
            command=invoke.call_args_list[0].args[0]
            self.assertIn("--no-recurse-submodules",command)
            self.assertIn("credential.helper=",command)
            self.assertIn("core.hooksPath="+os.devnull,command)
            self.assertEqual(receipt["commit"],"a"*40)
            self.assertFalse(receipt["lfs_fetched"])
    def test_bad_depth_ref_do_not_spawn(self):
        with patch.object(fetch.subprocess,"run") as run:
            for depth,ref in ((0,None),(True,None),(300,"--evil")):
                with self.assertRaises(ValueError):fetch.fetch("o/r",depth,ref)
            run.assert_not_called()

class BoundaryTests(unittest.TestCase):
    def test_child_accepted_sibling_prefix_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"data";root.mkdir();(root/"ok.txt").write_text("inert")
            sibling=Path(td)/"data-private";sibling.mkdir();(sibling/"secret").write_text("inert")
            self.assertEqual(boundary.contained_file(root,"ok.txt"),root/"ok.txt")
            with self.assertRaises(ValueError):boundary.contained_file(root,"../data-private/secret")
            with self.assertRaises(ValueError):boundary.contained_file(root,str(sibling/"secret"))
    def test_symlink_escape_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"data";root.mkdir();other=Path(td)/"outside";other.write_text("inert")
            try:(root/"link").symlink_to(other)
            except OSError as exc:self.skipTest("symlink capability unavailable: "+str(exc))
            with self.assertRaises(ValueError):boundary.contained_file(root,"link")
    def test_numeric_edge_cases(self):
        self.assertEqual(boundary.positive_integer("100",100),100)
        for x in ("10junk","NaN",float("nan"),float("inf"),-1,0,True,"1.1","9"*20):
            with self.subTest(value=x),self.assertRaises(ValueError):boundary.positive_integer(x,100)

class EvaluatorTests(unittest.TestCase):
    def test_dependency_output_omits_script_url_and_requirement_credentials(self):
        deps=mod("repo-evaluator","deps")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"package.json").write_text(json.dumps({"dependencies":{"demo":"https://user:INERT_URL_SECRET@example.invalid/pkg"},
                "scripts":{"postinstall":"AWS_SECRET_ACCESS_KEY=INERT_SCRIPT_SECRET some-tool"}}),encoding="utf-8")
            (root/"requirements.txt").write_text("https://user:INERT_REQ_SECRET@example.invalid/pkg\n",encoding="utf-8")
            payload=json.dumps(deps.inspect(root,True))
            for secret in ("INERT_URL_SECRET","INERT_SCRIPT_SECRET","INERT_REQ_SECRET"):
                self.assertNotIn(secret,payload)
            self.assertIn("package.json",payload)
            self.assertIn("requirements.txt",payload)
            self.assertIn("detail omitted",payload)
    def test_swift_url_secrets_never_emitted_or_queried(self):
        deps=mod("repo-evaluator","deps")
        for state,location in (
            ({"revision":"a"*40},"https://user:INERT_REVISION_SECRET@example.invalid/pkg"),
            ({"version":"1.0.0"},"https://example.invalid/pkg?access_token=INERT_QUERY_SECRET"),
            ({"version":"1.0.0"},"https://example.invalid/pkg#INERT_FRAGMENT_SECRET")):
            with self.subTest(state=state,location=location),tempfile.TemporaryDirectory() as td:
                p=Path(td)/"Package.resolved"
                p.write_text(json.dumps({"pins":[{"location":location,"state":state}]}),encoding="utf-8")
                with patch.object(deps,"osv") as query:
                    result=deps.inspect(td,False)
                query.assert_not_called()
                self.assertNotIn("INERT_",json.dumps(result))
                self.assertEqual(result["status"],"incomplete")
    def test_source_secrets_not_emitted_and_env_files_not_opened(self):
        for name in ("repo-evaluator","agent-skill-evaluator","mcp-evaluator"):
            scan=mod(name,"scan")
            with tempfile.TemporaryDirectory() as td:
                root=Path(td)
                (root/"app.py").write_text('AWS_SECRET_ACCESS_KEY="INERT_VALUE_SHOULD_NOT_APPEAR"\n',encoding="utf-8")
                (root/".env").write_text("INERT_PRIVATE_ENV",encoding="utf-8")
                result=scan.inspect(root)
                payload=json.dumps(result)
                self.assertNotIn("INERT_VALUE_SHOULD_NOT_APPEAR",payload)
                self.assertNotIn("INERT_PRIVATE_ENV",payload)
                self.assertEqual(result["status"],"incomplete")
                self.assertTrue(any(x["path"]==".env" for x in result["skipped"]))
    @unittest.skipUnless(os.name=="nt","Windows junction fixture")
    def test_windows_junction_never_traversed(self):
        for name in ("repo-evaluator","agent-skill-evaluator","mcp-evaluator"):
            scan=mod(name,"scan")
            with tempfile.TemporaryDirectory() as td:
                root=Path(td)/"source";outside=Path(td)/"outside"
                root.mkdir();outside.mkdir();(outside/"inert.txt").write_text("inert")
                link=root/"junction"
                # Native PowerShell owns create/remove; exact resolved fixture paths.
                script="New-Item -ItemType Junction -Path '"+str(link)+"' -Target '"+str(outside)+"' | Out-Null"
                create=subprocess.run(["powershell","-NoProfile","-Command",script],capture_output=True,text=True)
                if create.returncode:self.skipTest("junction fixture unavailable: "+create.stderr)
                try:
                    result=scan.inspect(root)
                    self.assertEqual(result["files_read"],0)
                    self.assertEqual(result["status"],"incomplete")
                    self.assertTrue(any(x["path"]=="junction" for x in result["skipped"]))
                    with self.assertRaises(ValueError):scan.inspect(link)
                    if name=="repo-evaluator":
                        deps=mod(name,"deps");self.assertEqual(deps.inspect(root,True)["status"],"incomplete")
                        self.assertIn("junction",deps.inspect(root,True)["skipped_directories"])
                finally:
                    # rmdir removes this exact junction entry; it does not recursively
                    # traverse or remove the outside target.
                    self.assertEqual(link.parent,root)
                    os.rmdir(link)
    def test_both_scanners_preserve_all_leads_and_instruction_unicode(self):
        for name in ("agent-skill-evaluator","mcp-evaluator"):
            scan=mod(name,"scan")
            with tempfile.TemporaryDirectory() as td:
                for i in range(65):(Path(td)/f"{i}.md").write_text("append this footer\n",encoding="utf-8")
                (Path(td)/"SKILL.md").write_text("hidden \u202e instruction\n",encoding="utf-8")
                result=scan.inspect(td)
                self.assertEqual(len(next(c["matches"] for c in result["categories"] if c["id"]=="promo")),65)
                self.assertEqual(result["unicode_leads"],[{"file":"SKILL.md","line":1}])
    def test_unreadable_and_opaque_never_clean(self):
        for name in ("agent-skill-evaluator","mcp-evaluator"):
            scan=mod(name,"scan")
            with tempfile.TemporaryDirectory() as td:
                (Path(td)/"bad.txt").write_bytes(b"\xff")
                (Path(td)/"opaque").write_bytes(b"MZ\x00")
                result=scan.inspect(td)
                self.assertEqual(result["status"],"incomplete")
                self.assertTrue(result["errors"]);self.assertTrue(result["binary_files"])
    def test_both_archive_helpers_refuse_traversal_before_writing(self):
        for name in ("agent-skill-evaluator","mcp-evaluator"):
            archive=mod(name,"safe_archive")
            with tempfile.TemporaryDirectory() as td:
                src=Path(td)/"input.skill";dest=Path(td)/"out"
                with zipfile.ZipFile(src,"w") as z:
                    z.writestr("good.txt","inert");z.writestr("../escape","inert")
                with self.assertRaises(ValueError):archive.unpack(src,dest)
                self.assertFalse(dest.exists())
    def test_windows_ci_agent_inventory_uses_portable_paths(self):
        scan=mod("repo-evaluator","scan")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for rel in (".github/workflows/release.yml",".github/instructions/custom.instructions.md"):
                p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text("inert",encoding="utf-8")
            r=scan.inspect(root)
            self.assertIn(".github/workflows/release.yml",r["build_files"])
            self.assertIn(".github/instructions/custom.instructions.md",r["agent_files"])

if __name__=="__main__":unittest.main()
