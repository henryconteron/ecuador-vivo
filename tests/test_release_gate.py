import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location("release_gate", Path(__file__).resolve().parents[1] / "scripts/audit_git_release.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class ReleaseGateTests(unittest.TestCase):
    def test_private_unpublished_and_regenerable_files_are_rejected(self):
        for name in ("videos/film/index.html", "_local/projects/a.json", ".env", ".env.local",
                     "a/node_modules/a.js", "a/.venv/pyvenv.cfg", "a/pkg.egg-info/PKG-INFO",
                     ".hyperframes/history-id", "a/.streamlit/secrets.toml", "a/movie.mp4",
                     "a/voice.wav", "a/package.zip", "a/key.pem"):
            with self.subTest(name=name):
                self.assertTrue(gate.blocked_path(name))

    def test_current_source_and_required_built_assets_are_allowed(self):
        for name in ("index.html", "production/video_studio/app.py", "assets/images/cover.webp",
                     "component/frontend/build/index.js", "component/package-lock.json"):
            with self.subTest(name=name):
                self.assertFalse(gate.blocked_path(name))

    def test_access_key_pattern_does_not_flag_an_embedded_base64_substring(self):
        candidate = b"AKIA" + b"A" * 16
        self.assertTrue(any(p.search(b'"' + candidate + b'"') for p in gate.SIGNATURES))
        self.assertFalse(any(p.search(b"prefix" + candidate + b"suffix") for p in gate.SIGNATURES))


if __name__ == "__main__":
    unittest.main()
