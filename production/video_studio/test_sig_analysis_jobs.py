import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
import test_studio_geography as fixtures
from studio_sig_layers import add_geojson_layer
import studio_sig_analysis_jobs as jobs

class AnalysisJobsTests(unittest.TestCase):
    setUp=fixtures.GeographyTests.setUp
    tearDown=fixtures.GeographyTests.tearDown
    def queued(self):
        project,lid=add_geojson_layer(self.project,self.content,'regions.geojson',self.provenance)
        root=Path(self.temp.name)/'analysis'
        with patch.object(jobs,'ROOT',root),patch.object(jobs.subprocess,'Popen') as process:
            process.return_value.pid=12345
            job=jobs.start(project,{'kind':'vector','layer':lid,'tool':'boundary','parameters':{},'name':'Contornos'})
        return project,job,root
    def test_result_requires_explicit_acceptance_and_unchanged_document(self):
        project,job,root=self.queued();before=copy.deepcopy(project)
        with patch.object(jobs,'ROOT',root):
            jobs.execute(job);self.assertEqual(jobs.status(job)['state'],'complete')
            self.assertEqual(project,before)
            result,lid=jobs.accept(job,project)
            self.assertEqual(result['studio']['geography']['map_workspace']['active_layer'],lid)
            self.assertEqual(len(result['studio']['geography']['map_workspace']['layers']),2)
            self.assertEqual(result['studio']['scenes'],before['studio']['scenes'])
            changed=copy.deepcopy(project);changed['project_meta']['id']='different-project'
            with self.assertRaisesRegex(ValueError,'cambió'):jobs.accept(job,changed)
            moved=copy.deepcopy(project);moved['name']='Nombre editado';moved['studio']['geography']['map_workspace']['view']['bbox']=[-85,-6,-74,2]
            merged,_=jobs.accept(job,moved)
            self.assertEqual(merged['name'],'Nombre editado')
            self.assertEqual(merged['studio']['geography']['map_workspace']['view'],moved['studio']['geography']['map_workspace']['view'])
            result['name']='adulterado';jobs.write_json(job/'result.json',{'project':result,'layer':lid})
            with self.assertRaisesRegex(ValueError,'huella'):jobs.accept(job,project)
    def test_cancel_before_and_after_work_prevents_acceptance(self):
        project,job,root=self.queued()
        with patch.object(jobs,'ROOT',root):
            jobs.cancel(job);jobs.execute(job)
            self.assertEqual(jobs.status(job)['state'],'cancelled')
            with self.assertRaises(ValueError):jobs.accept(job,project)
        project,job,root=self.queued()
        with patch.object(jobs,'ROOT',root):
            jobs.execute(job);jobs.cancel(job)
            with self.assertRaises(ValueError):jobs.accept(job,project)
    def test_paths_unknown_requests_and_dead_worker_are_rejected(self):
        project,job,root=self.queued()
        with patch.object(jobs,'ROOT',root):
            with self.assertRaises(ValueError):jobs.status(root.parent)
            with self.assertRaises(ValueError):jobs.start(project,{'kind':'arbitrary'})
            with patch.object(jobs,'process_alive',return_value=False),patch.object(jobs.time,'time',return_value=10**12):
                self.assertEqual(jobs.status(job)['state'],'failed')

    def test_pending_job_can_be_recovered_but_handled_jobs_are_not_reopened(self):
        project,job,root=self.queued()
        with patch.object(jobs,'ROOT',root):
            self.assertEqual(jobs.find_pending(project),job)
            jobs.handled(job,'dismissed');self.assertIsNone(jobs.find_pending(project))

    def test_cancellation_during_vector_loop_never_writes_a_partial_result(self):
        from studio_sig_vector import run_operation
        project,job,root=self.queued()
        def cancelling(*args,**kwargs):
            report=kwargs['progress']
            def progress(done,total):
                if done:jobs.cancel(job)
                report(done,total)
            return run_operation(*args,**{**kwargs,'progress':progress})
        with patch.object(jobs,'ROOT',root),patch('studio_sig_vector.run_operation',side_effect=cancelling):
            jobs.execute(job);self.assertEqual(jobs.status(job)['state'],'cancelled')
            self.assertFalse((job/'result.json').exists())

    def test_raster_and_zonal_workers_use_existing_calculations(self):
        from test_sig_raster import raster_bytes
        from studio_sig_raster import add_raster
        from studio_sig_vector import layer_features
        project,vector=add_geojson_layer(self.project,self.content,'regions.geojson',self.provenance)
        project,a=add_raster(project,raster_bytes([[1,2],[3,4]]),'a.tif',self.provenance,observed_date='2024-01-01',variable='Control',units='mm')
        project,b=add_raster(project,raster_bytes([[2,3],[4,5]]),'b.tif',self.provenance,observed_date='2024-01-02',variable='Control',units='mm')
        with patch.object(jobs,'ROOT',Path(self.temp.name)/'analysis'),patch.object(jobs.subprocess,'Popen',return_value=type('Process',(),{'pid':12345})()):
            for tool,layers in [('difference',[a,b]),('zonal',[a,vector])]:
                job=jobs.start(project,{'kind':'raster','layers':layers,'tool':tool,'name':tool+'.tif'})
                jobs.execute(job);self.assertEqual(jobs.status(job)['state'],'complete')
                result,lid=jobs.accept(job,project)
                self.assertNotIn(lid,project['studio']['geography']['map_workspace']['layers'])
                self.assertEqual(result['studio']['scenes'],project['studio']['scenes'])

if __name__=='__main__':unittest.main()
