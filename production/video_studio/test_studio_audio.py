"""Real decoded audio, frame scheduling and transactional publication."""
import copy
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import imageio_ffmpeg
sys.path.insert(0,str(Path(__file__).parent))
from studio_model import Scene, Element
from studio_editing import new_workspace
from studio_media import import_asset, AssetFrames
from studio_timeline import export_movie, PreparedTimeline
from studio_audio import audio_settings, video_sources, mix_pcm, SAMPLE_RATE, SAMPLES_PER_FRAME


class StudioAudioTests(unittest.TestCase):
    def command(self,args):
        r=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-nostdin',*args],
            capture_output=True,timeout=30,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        self.assertEqual(r.returncode,0,r.stderr.decode(errors='replace'));return r.stdout

    def clip(self,root,name,frequency=440,amplitude=.2,offset=0):
        path=root/(name+'.mp4')
        self.command(['-f','lavfi','-i','color=c=red:s=160x160:r=30:d=1',
            '-itsoffset',str(offset),'-f','lavfi','-i',f'aevalsrc={amplitude}*sin(2*PI*{frequency}*t):s=48000:d={1-offset}',
            '-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k',str(path)])
        return import_asset(path.read_bytes(),name+'.mp4')

    def project(self,records,styles,durations=(1,)):
        p=new_workspace({'endcard_enabled':False});p['studio']['media']=records
        p['studio']['output_profile']={'id':'custom','width':160,'height':160}
        p['studio']['scenes']=[Scene(id=f's{index}',duration=seconds,elements=[
            Element(id=f'v{index}.{j}',type='video',transform={'x':0,'y':0,'width':160,'height':160},
                style={'asset_id':aid,**style}).to_dict() for j,(aid,style) in enumerate(styles[index])]).to_dict()
            for index,seconds in enumerate(durations)]
        p['studio']['timeline']=[s['id'] for s in p['studio']['scenes']];return p

    def decode(self,path):
        return np.frombuffer(self.command(['-i',str(path),'-map','0:a:0','-ac','2','-ar','48000',
            '-f','f32le','pipe:1']),dtype='<f4').reshape(-1,2)

    def test_strict_settings_preserve_legacy_silence(self):
        self.assertEqual(audio_settings({}),(True,1.))
        self.assertEqual(audio_settings({'mute':False,'volume':.25}),(False,.25))
        for style in ({'mute':1},{'volume':True},{'volume':float('nan')},{'volume':-1},{'volume':2.01}):
            with self.assertRaises(ValueError): audio_settings(style)

    def test_mix_overlap_individual_levels_and_source_schedule(self):
        import storyboard
        with tempfile.TemporaryDirectory() as directory,patch.object(storyboard,'MEDIA_ROOT',Path(directory)):
            root=Path(directory);record=self.clip(root,'tone')
            p=self.project({'a':record},[[('a',{'mute':False,'volume':.25}),('a',{'mute':False,'volume':.75})]])
            before=copy.deepcopy(p);prepared=PreparedTimeline(p)
            with AssetFrames(p['studio']['media']) as assets:
                sources=video_sources(prepared.project,prepared.rows,assets)
                self.assertEqual(len(sources),2);self.assertEqual(sources[0].start_frame,0)
                raw=mix_pcm(sources,prepared.total_frames,root/'pcm')
                mixed=np.fromfile(raw,dtype='<f4').reshape(-1,2)
            original=self.decode(Path(record['path']))[:SAMPLE_RATE]
            self.assertEqual(mixed.shape,(SAMPLE_RATE,2))
            self.assertLess(float(np.max(np.abs(mixed[3000:40000]-original[3000:40000]))),.0001)
            self.assertEqual(p,before)

    def test_mute_zero_hidden_deleted_and_no_audio_are_silent(self):
        import storyboard
        with tempfile.TemporaryDirectory() as directory,patch.object(storyboard,'MEDIA_ROOT',Path(directory)):
            root=Path(directory);record=self.clip(root,'tone')
            quiet=root/'quiet.mp4'
            self.command(['-f','lavfi','-i','color=black:s=160x160:r=30:d=1','-c:v','libx264','-pix_fmt','yuv420p',str(quiet)])
            p=self.project({'a':record,'quiet':import_asset(quiet.read_bytes(),'quiet.mp4')},
                [[('a',{}),('a',{'mute':False,'volume':0}),('a',{'mute':False}),('a',{'mute':False}),('quiet',{'mute':False})]])
            p['studio']['scenes'][0]['elements'][2]['visible']=False
            p['studio']['scenes'][0]['elements'][3]['editor_deleted']=True
            with AssetFrames(p['studio']['media']) as assets:
                self.assertEqual(video_sources(p,PreparedTimeline(p).rows,assets),[])
            receipt=export_movie(p,root/'out'/'video.mp4');self.assertEqual(receipt['audio'],'silent')
            self.assertEqual(hashlib.sha256((root/'out'/'video.mp4').read_bytes()).hexdigest(),receipt['video_sha256'])

    def test_trim_loop_nonloop_silence_and_scene_boundary_sync(self):
        import storyboard
        with tempfile.TemporaryDirectory() as directory,patch.object(storyboard,'MEDIA_ROOT',Path(directory)):
            root=Path(directory);record=self.clip(root,'tone')
            styles=[[('a',{'mute':False,'trim_in':.2,'trim_out':.4})],
                    [('a',{'mute':False,'trim_in':.2,'trim_out':.4,'loop':True})]]
            p=self.project({'a':record},styles,durations=(.4,.4));prepared=PreparedTimeline(p)
            with AssetFrames(p['studio']['media']) as assets:
                sources=video_sources(p,prepared.rows,assets)
                self.assertEqual(sources[0].trim_frame,6);self.assertEqual(sources[1].start_frame,12)
                raw=mix_pcm(sources,24,root/'pcm');mixed=np.fromfile(raw,dtype='<f4').reshape(-1,2)
            self.assertEqual(len(mixed),24*SAMPLES_PER_FRAME)
            self.assertEqual(float(np.max(np.abs(mixed[6*SAMPLES_PER_FRAME:12*SAMPLES_PER_FRAME]))),0)
            self.assertTrue(np.array_equal(mixed[12*SAMPLES_PER_FRAME:18*SAMPLES_PER_FRAME],mixed[18*SAMPLES_PER_FRAME:]))
            target=root/'out'/'video.mp4';export_movie(p,target);encoded=self.decode(target)[:len(mixed)]
            self.assertLess(float(np.max(np.abs(encoded[7*SAMPLES_PER_FRAME:11*SAMPLES_PER_FRAME]))),.001)
            self.assertLess(float(np.mean(np.abs(encoded[12*SAMPLES_PER_FRAME+500:]-mixed[12*SAMPLES_PER_FRAME+500:]))),.003)

    def test_source_pts_gap_is_preserved(self):
        import storyboard
        with tempfile.TemporaryDirectory() as directory,patch.object(storyboard,'MEDIA_ROOT',Path(directory)):
            root=Path(directory);record=self.clip(root,'late',offset=.2)
            p=self.project({'a':record},[[('a',{'mute':False})]])
            with AssetFrames(p['studio']['media']) as assets:
                raw=mix_pcm(video_sources(p,PreparedTimeline(p).rows,assets),30,root/'pcm')
                mixed=np.fromfile(raw,dtype='<f4').reshape(-1,2)
            self.assertLess(float(np.max(np.abs(mixed[:7000]))),.001)
            self.assertGreater(float(np.max(np.abs(mixed[11000:20000]))),.05)

    def test_sub_100ms_pts_gap_does_not_advance_audio(self):
        from studio_audio import AudioSource
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);pcm=root/'step.f32';source=root/'gap.mp4'
            samples=np.zeros((48000,2),dtype='<f4');samples[28800:]=.5;pcm.write_bytes(samples.tobytes())
            self.command(['-f','lavfi','-i','color=black:s=64x64:r=30:d=1','-f','f32le','-ar','48000','-ac','2',
                '-i',str(pcm),'-af',r'aselect=not(between(t\,0.5\,0.55))','-c:v','libx264','-c:a','aac','-b:a','320k',str(source)])
            clip=AudioSource('x','a',source,hashlib.sha256(source.read_bytes()).hexdigest(),0,30,0,30,1.,False)
            mixed=np.fromfile(mix_pcm([clip],30,root/'mix'),dtype='<f4').reshape(-1,2)
            self.assertEqual(int(np.flatnonzero(mixed[:,0]>.25)[0]),28800)

    def test_export_limiter_measured_peak_and_video_preview_equality(self):
        import storyboard
        with tempfile.TemporaryDirectory() as directory,patch.object(storyboard,'MEDIA_ROOT',Path(directory)):
            root=Path(directory);record=self.clip(root,'loud',amplitude=.8)
            p=self.project({'a':record},[[('a',{'mute':False,'volume':2}),('a',{'mute':False,'volume':2})]])
            prepared=PreparedTimeline(p);target=root/'export'/'video.mp4';receipt=export_movie(p,target)
            audio=self.decode(target);self.assertLessEqual(float(np.max(np.abs(audio))),.981)
            self.assertGreater(float(np.max(np.abs(audio))),.7)
            self.assertEqual(receipt['audio']['sample_rate'],48000);self.assertEqual(len(receipt['audio']['sources']),2)
            self.assertAlmostEqual(receipt['audio']['decoded_peak'],float(np.max(np.abs(audio))),places=5)
            self.assertGreaterEqual(len(audio),48000);self.assertLess(len(audio)-48000,1024)
            reader=imageio_ffmpeg.read_frames(str(target),pix_fmt='rgb24');next(reader)
            try: frames=list(reader)
            finally: reader.close()
            self.assertEqual(len(frames),30)
            self.assertLess(np.max(np.abs(np.frombuffer(frames[10],dtype=np.uint8).astype(int)-
                np.frombuffer(prepared.frame_at(10).convert('RGB').tobytes(),dtype=np.uint8).astype(int))),5)
            self.assertFalse(list(target.parent.glob('.studio-audio-*')))

    def test_audio_failure_and_cancel_do_not_publish_or_leak_temporaries(self):
        import storyboard
        with tempfile.TemporaryDirectory() as directory,patch.object(storyboard,'MEDIA_ROOT',Path(directory)):
            root=Path(directory);record=self.clip(root,'tone');p=self.project({'a':record},[[('a',{'mute':False})]])
            for label,fixture in [('failed',patch('studio_audio._run',side_effect=ValueError('decode failed'))),
                                  ('cancelled',patch('studio_audio._check_cancel',side_effect=InterruptedError('cancelled')))]:
                target=root/label/'video.mp4'
                with fixture,self.assertRaises((ValueError,InterruptedError)): export_movie(p,target)
                self.assertFalse(target.exists());self.assertFalse((target.parent/'receipt.json').exists())
                self.assertFalse(list(target.parent.glob('.studio-audio-*')))

    def test_ui_audio_properties_undo_and_real_audiovisual_preview(self):
        import storyboard,studio_ui,studio_jobs
        from streamlit.testing.v1 import AppTest
        from test_studio_jobs import tracked_workers,wait_terminal
        storyboard.MEDIA_ROOT.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=storyboard.MEDIA_ROOT) as directory,patch.object(storyboard,'MEDIA_ROOT',Path(directory)), \
             patch.object(studio_ui,'STORE',Path(directory)),patch.object(studio_jobs,'STORE',Path(directory)),tracked_workers(), \
             patch('data.load_values',side_effect=AssertionError('No science during audio')):
            root=Path(directory);record=self.clip(root,'tone')
            p=self.project({'a':record},[[('a',{'mute':True})]])
            script='import sys\nsys.path.insert(0,{!r})\nfrom studio_ui import show_studio\nshow_studio({!r},key="audio")'.format(str(Path(__file__).parent),p)
            app=AppTest.from_string(script,default_timeout=30).run()
            self.assertFalse(app.exception);self.assertFalse(app.error)
            before=copy.deepcopy(app.session_state['audio_document'])
            next(c for c in app.checkbox if c.label=='Silenciar audio del clip').uncheck()
            next(s for s in app.slider if s.label=='Volumen del clip').set_value(.5)
            next(b for b in app.button if b.label=='Aplicar propiedades').click().run()
            doc=copy.deepcopy(app.session_state['audio_document'])
            self.assertFalse(app.error);self.assertEqual(doc['studio']['scenes'][0]['elements'][0]['style']['volume'],.5)
            self.assertFalse(doc['studio']['scenes'][0]['elements'][0]['style']['mute'])
            next(b for b in app.button if b.label=='Deshacer').click().run()
            self.assertEqual(app.session_state['audio_document'],before)
            next(b for b in app.button if b.label=='Rehacer').click().run()
            next(b for b in app.button if b.label=='Preparar preview audiovisual').click().run()
            job=Path(app.session_state['audio_job']);self.assertEqual(wait_terminal(job)['state'],'complete')
            app.run();self.assertFalse(app.exception);self.assertFalse(app.error)
            from jobs import read_json
            self.assertEqual(read_json(job/'project.json'),doc)
            self.assertLess(float(np.max(np.abs(self.decode(job/'video.mp4')))),.11)
            self.assertTrue(any('exactamente el mismo MP4' in c.value for c in app.caption))
            next(s for s in app.slider if s.label=='Volumen del clip').set_value(1.)
            next(b for b in app.button if b.label=='Aplicar propiedades').click().run()
            self.assertTrue(any('versión anterior' in w.value for w in app.warning))

    def test_budget_hash_and_block_cancellation_guards(self):
        import storyboard,studio_audio
        with tempfile.TemporaryDirectory() as directory,patch.object(storyboard,'MEDIA_ROOT',Path(directory)):
            root=Path(directory);record=self.clip(root,'tone');p=self.project({'a':record},[[('a',{'mute':False})]])
            with AssetFrames(p['studio']['media']) as assets:
                sources=video_sources(p,PreparedTimeline(p).rows,assets)
            with patch.object(studio_audio,'PCM_BUDGET',1),self.assertRaises(ValueError): mix_pcm(sources,30,root/'budget')
            def cancel_during_mix():
                return (root/'cancel'/'source-0.f32').is_file() and (root/'cancel'/'mix.f32').is_file()
            with self.assertRaises(InterruptedError): mix_pcm(sources,30,root/'cancel',cancelled=cancel_during_mix)
            Path(record['path']).write_bytes(b'changed')
            with self.assertRaises(ValueError): mix_pcm(sources,30,root/'changed')


if __name__=='__main__': unittest.main()
