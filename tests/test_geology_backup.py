import importlib.util
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

spec = importlib.util.spec_from_file_location('backup', Path(__file__).resolve().parents[1] / 'scripts/package_geology_backup.py')
backup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup)


class BackupTests(unittest.TestCase):
    def test_roundtrip_and_unlisted_entry(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'pilot.zip'
            info = backup.build(output=path)
            self.assertEqual(len(backup.verify(path)['files']), len(backup.FILES))
            self.assertEqual(info['sha256'], backup.digest(path.read_bytes()))
            with self.assertRaises(FileExistsError):
                backup.build(output=path)
            with ZipFile(path, 'a') as archive:
                archive.writestr('../unexpected.txt', 'invalid')
            with self.assertRaises(ValueError):
                backup.verify(path)
