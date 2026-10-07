"""Public preview must not expose the editor's private data."""
from pathlib import Path
import tempfile
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

from preview_server import start_preview


class PreviewTests(unittest.TestCase):
    def test_public_file_served_but_private_paths_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'index.html').write_text('<h1>Local preview</h1>', encoding='utf-8')
            for private in ('_local', 'production', '.git', 'node_modules'):
                (root / private).mkdir()
                (root / private / 'secret.txt').write_text('private', encoding='utf-8')
            server = start_preview(root)
            base = f'http://127.0.0.1:{server.server_port}'
            try:
                with urlopen(base) as response:
                    self.assertIn(b'Local preview', response.read())
                    self.assertEqual(response.headers['Cache-Control'], 'no-store')
                for path in ('_local/secret.txt', 'production/secret.txt', '.git/secret.txt',
                             'node_modules/secret.txt', '%2e%2e/secret.txt'):
                    with self.assertRaises(HTTPError) as error:
                        urlopen(base + '/' + path)
                    self.assertEqual(error.exception.code, 404)
            finally:
                server.shutdown()
                server.server_close()


if __name__ == '__main__':
    unittest.main()
