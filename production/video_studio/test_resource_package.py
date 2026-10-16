"""Package registration and file boundaries; no browser or WebGL claim."""
import tempfile
from pathlib import Path
from unittest.mock import patch
import unittest
from streamlit.testing.v1 import AppTest

class ResourcePackageTests(unittest.TestCase):
    def test_official_template_package_mounts_in_streamlit_runtime(self):
        app=AppTest.from_string('from ecuador_vivo_scientific_tools import scientific_tool\nscientific_tool("vector",key="smoke")',default_timeout=30).run()
        self.assertFalse(app.exception,[e.value for e in app.exception])
    def test_svg_rejects_active_content_and_external_references(self):
        from resource_engines.vendor_bioicons import safe_svg
        safe_svg(b'<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0L1 1"/></svg>')
        for markup in [b'<svg><script>bad()</script></svg>',b'<svg><path fill="url(#ok) url(https://bad.test/a)"/></svg>',b'<svg><image href="file:///private"/></svg>']:
            with self.assertRaises(ValueError):safe_svg(markup)

class FontRouteTests(unittest.IsolatedAsyncioTestCase):
    async def test_route_only_serves_font_assets(self):
        from studio_resource_static import font_response
        with tempfile.TemporaryDirectory() as folder,patch('studio_resource_static.FONT_ROOT',Path(folder)):
            (Path(folder)/'fonts').mkdir();(Path(folder)/'fonts/test.woff2').write_bytes(b'font')
            for path,status in [('fonts/test.woff2',200),('fonts/../../private.json',404),('src/main.py',404),('fonts/test.js',404)]:
                response=await font_response(type('Request',(),{'path_params':{'path':path}})())
                self.assertEqual(response.status_code,status)
