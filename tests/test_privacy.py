"""Regressions for publication leaks and the user-selected exceptions."""
from pathlib import Path
import importlib.util
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("publication_privacy",ROOT/"scripts/privacy.py")
privacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(privacy)
class PrivacyTests(unittest.TestCase):
    def test_collapsed_shell_path_removed(self):
        name=Path.home().name
        source="No such file: C:Users"+name+"Downloadsprojectscript.sh"
        cleaned=privacy.scrub_text(source)
        self.assertNotIn("Users"+name,cleaned)
        self.assertFalse(privacy.private_features(cleaned))
    def test_emails_and_public_repository_urls_retained(self):
        name=Path.home().name
        email=name+"@example.invalid";url="https://github.com/"+name+"/example"
        self.assertEqual(privacy.scrub_text(email+" "+url),email+" "+url)
        self.assertFalse(privacy.private_features(email+" "+url))
    def test_coarse_runtime_and_no_location(self):
        data={"timezone":"America/"+"Example_City","platform":"Windows-"+"11-10.0.12345-SP0",
              "python":"3.13.5 compiler architecture","command":[str(Path.home()/"python.exe")]}
        cleaned=privacy.clean_json(data)
        self.assertNotIn("timezone",cleaned)
        self.assertEqual(cleaned["platform"],"Windows")
        self.assertEqual(cleaned["python"],"3.13")
        self.assertEqual(cleaned["command"][0],"python")
if __name__=="__main__":unittest.main()
