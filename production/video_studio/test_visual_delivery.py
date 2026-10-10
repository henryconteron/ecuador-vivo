"""Presentation delivery keeps capability expiry and scientific integrity."""
import asyncio
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from PIL import Image
from starlette.requests import Request
import studio_delivery as delivery


class RasterDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.source={'id':'source.fixture','date':'2024-01-01','sha256':'a'*64,'units':'mm/día'}

    def response(self,url):
        request=Request({'type':'http','method':'GET','path':url,'headers':[], 'path_params':{'token':url.rsplit('/',1)[1]}})
        return asyncio.run(delivery.raster_response(request))

    def test_verified_rgba_and_observed_date(self):
        url=delivery.register_raster_display(self.source,{'stops':[0,10]})
        with patch('studio_sig_raster.representation',return_value=(Image.new('RGBA',(2,2),(0,0,0,0)),[0,0,1,1])) as render:
            response=self.response(url)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.headers['x-ecuador-observation-date'],'2024-01-01')
        self.assertEqual(response.headers['x-ecuador-source-sha256'],'a'*64)
        self.assertEqual(response.headers['cache-control'],'private, no-store')
        render.assert_called_once_with(self.source,{'stops':[0,10]})

    def test_warm_capability_still_verifies_source(self):
        url=delivery.register_raster_display(self.source,None)
        self.assertEqual(url,delivery.register_raster_display(self.source,None))
        with patch('studio_sig_raster.representation',side_effect=ValueError('hash changed')) as render:
            self.assertEqual(self.response(url).status_code,409)
            self.assertEqual(self.response(url).status_code,409)
        self.assertEqual(render.call_count,2)

    def test_unknown_or_expired_capability_rejected(self):
        self.assertEqual(self.response('/sig-display/unknown').status_code,404)
        url=delivery.register_raster_display(self.source,None)
        with patch('studio_delivery.time.monotonic',return_value=10**12):
            self.assertEqual(self.response(url).status_code,404)

    def test_registration_snapshot_is_not_mutated_by_caller(self):
        source=dict(self.source);url=delivery.register_raster_display(source,None);source['date']='2024-02-01'
        with patch('studio_sig_raster.representation',return_value=(Image.new('RGBA',(1,1)),[0,0,1,1])):
            self.assertEqual(self.response(url).headers['x-ecuador-observation-date'],'2024-01-01')


class JobProgressTests(unittest.IsolatedAsyncioTestCase):
    async def test_capability_checks_path_and_does_not_publish_partial_movie(self):
        from starlette.testclient import TestClient
        from starlette.applications import Starlette
        from starlette.routing import Route
        with tempfile.TemporaryDirectory() as folder,patch.object(delivery,'STORE',Path(folder)):
            job=Path(folder)/'jobs'/'studio-progress';job.mkdir(parents=True)
            (job/'request.json').write_text('{}',encoding='utf-8')
            (job/'status.json').write_text('{"state":"running","progress":0.5}',encoding='utf-8')
            url=delivery.register_job_status(job)
            client=TestClient(Starlette(routes=[Route('/studio-status/{token}',delivery.job_response)]))
            result=client.get(url);self.assertEqual(result.status_code,200)
            self.assertEqual(result.json(),{'job':{'state':'running','progress':0.5}})
            (job/'status.json').write_text('{"state":"complete"}',encoding='utf-8')
            self.assertEqual(client.get(url).status_code,409)
            self.assertEqual(client.get('/studio-status/unknown').status_code,404)
            with self.assertRaises(ValueError):delivery.register_job_status(Path(folder)/'outside')

    async def test_server_dispatch_uses_current_delivery_module(self):
        import importlib,sys,types
        from unittest.mock import AsyncMock
        with patch('streamlit.App'):
            server=importlib.import_module('studio_server')
        replacement=types.SimpleNamespace(movie_response=AsyncMock(return_value='movie'),
            raster_response=AsyncMock(return_value='raster'),job_response=AsyncMock(return_value='job'))
        with patch.dict(sys.modules,{'studio_delivery':replacement}):
            self.assertEqual(await server.movie_route('request'),'movie')
            self.assertEqual(await server.raster_route('request'),'raster')
            self.assertEqual(await server.job_route('request'),'job')


class CompletedRenderTests(unittest.TestCase):
    def test_identical_complete_verified_product_is_reused_after_preflight(self):
        import studio_jobs,hashlib,json
        project={'name':'fixture','studio':{'media':{}}}
        with tempfile.TemporaryDirectory() as folder,patch.object(studio_jobs,'STORE',Path(folder)):
            job=Path(folder)/'jobs'/'studio-fixture';job.mkdir(parents=True)
            studio_jobs.write_json(job/'request.json',project)
            studio_jobs.write_json(job/'status.json',{'state':'complete'})
            (job/'video.mp4').write_bytes(b'verified-fixture')
            identity=hashlib.sha256(json.dumps(project,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()
            studio_jobs.write_json(job/'receipt.json',{'project_sha256':identity,'video_sha256':hashlib.sha256(b'verified-fixture').hexdigest()})
            with patch.object(studio_jobs,'validate_export') as preflight,patch.object(studio_jobs.subprocess,'Popen') as worker:
                self.assertEqual(studio_jobs.start_studio_job(project),job)
                preflight.assert_called_once_with(project);worker.assert_not_called()
                changed_identity={**project,'project_meta':{'id':'copy','revision':2}}
                reused=studio_jobs.start_studio_job(changed_identity)
                self.assertNotEqual(reused,job)
                self.assertEqual(studio_jobs.read_json(reused/'status.json')['state'],'complete')
                receipt=studio_jobs.read_json(reused/'receipt.json')
                self.assertEqual(receipt['project_sha256'],studio_jobs._document_hash(changed_identity))
                self.assertEqual(receipt['render_cache']['source_job'],job.name)
                worker.assert_not_called()
                with patch('studio_media.AssetFrames',side_effect=ValueError('source changed')):
                    with self.assertRaisesRegex(ValueError,'source changed'):studio_jobs.start_studio_job(changed_identity)
                (job/'video.mp4').write_bytes(b'corrupt')
                (reused/'video.mp4').write_bytes(b'also corrupt')
                self.assertNotEqual(studio_jobs.start_studio_job(project),job)
                self.assertEqual(worker.call_count,1)
                changed_output={**project,'name':'different displayed project'}
                self.assertNotEqual(studio_jobs.start_studio_job(changed_output),job)
                self.assertEqual(worker.call_count,2)
