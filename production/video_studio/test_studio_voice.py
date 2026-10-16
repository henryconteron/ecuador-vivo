"""Independent narration stays bounded, content-verified and frame-exact."""
import copy
import hashlib
import io
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

import imageio_ffmpeg
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import storyboard
from studio_audio import combined_sources, mix_pcm, SAMPLES_PER_FRAME
from studio_media import AssetFrames, import_asset
from studio_voice import audio_media_path, validate_audio_tracks


def wav_content(seconds=.4):
    stream = io.BytesIO()
    values = (np.sin(np.arange(round(48000*seconds))*2*np.pi*440/48000)*6000).astype('<i2')
    with wave.open(stream, 'wb') as output:
        output.setnchannels(1); output.setsampwidth(2); output.setframerate(48000)
        output.writeframes(values.tobytes())
    return stream.getvalue()


class StudioVoiceTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.media = self.root/'media'
        self.boundary = patch.object(storyboard, 'MEDIA_ROOT', self.media)
        self.boundary.start(); self.addCleanup(self.boundary.stop)

    def fixture(self, **changes):
        record = import_asset(wav_content(), 'narracion.wav')
        track = {'id':'voz-1', 'asset_id':'audio-1', 'start':.2, 'trim_in':.1,
                 'trim_out':.3, 'volume':.5, 'mute':False, 'loop':False, **changes}
        return {'studio':{'media':{'audio-1':record}, 'scenes':[], 'audio_tracks':[track]}}

    def test_wav_import_deduplicates_and_never_creates_a_visual_frame(self):
        content = wav_content()
        record = import_asset(content, '../../mi voz.wav')
        again = import_asset(content, 'otra voz.wav')
        self.assertEqual(record['path'], again['path'])
        self.assertEqual(record['name'], 'mi voz.wav')
        self.assertEqual(record['kind'], 'audio')
        self.assertEqual(record['sha256'], hashlib.sha256(content).hexdigest())
        self.assertAlmostEqual(record['duration'], .4, places=3)
        with AssetFrames({'a':record}) as assets:
            self.assertIn('a', assets.audios)
            self.assertEqual(assets.at(0), {})
            self.assertFalse(assets.videos); self.assertFalse(assets.cursors)
        self.assertEqual(len(list(self.media.iterdir())), 1)

    def test_mp3_and_m4a_are_decoded_not_trusted_by_extension(self):
        self.root.joinpath('source.wav').write_bytes(wav_content())
        for suffix, codec in (('.mp3','libmp3lame'), ('.m4a','aac')):
            with self.subTest(suffix=suffix):
                path = self.root/('voice'+suffix)
                result = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v','error','-nostdin',
                    '-i', str(self.root/'source.wav'), '-c:a',codec,str(path)],
                    capture_output=True, timeout=20)
                self.assertEqual(result.returncode,0,result.stderr)
                record = import_asset(path.read_bytes(),path.name)
                self.assertEqual(record['kind'],'audio')
                self.assertGreater(record['duration'],.3)
                with AssetFrames({'a':record}) as assets:
                    self.assertIn('a',assets.audios)

    def test_invalid_disguised_and_oversize_uploads_leave_no_media(self):
        for content,name in ((b'not audio','a.mp3'),(wav_content(),'a.mp3'),
                             (b'RIFF'+b'\0'*4+b'WAVE' + b'bad','a.wav'),(b'','a.wav')):
            with self.subTest(name=name, size=len(content)):
                with self.assertRaises(ValueError): import_asset(content,name)
        with patch('studio_voice.MAX_AUDIO_BYTES',10), self.assertRaises(ValueError):
            import_asset(wav_content(),'a.wav')
        self.assertFalse(self.media.exists() and list(self.media.iterdir()))

    def test_safe_path_and_changed_content_are_rejected(self):
        external = self.root/'outside.wav'; external.write_bytes(wav_content())
        with self.assertRaises(ValueError): audio_media_path(external)
        record = import_asset(wav_content(),'a.wav')
        Path(record['path']).write_bytes(wav_content(.2))
        with self.assertRaises(ValueError): AssetFrames({'a':record})

    def test_audio_over_duration_budget_is_not_persisted(self):
        with patch('studio_voice.MAX_AUDIO_SECONDS',.1), self.assertRaises(ValueError):
            import_asset(wav_content(),'too-long.wav')
        self.assertFalse(self.media.exists() and list(self.media.iterdir()))

    def test_sources_combine_clip_and_narration_without_mutating_the_project(self):
        from types import SimpleNamespace
        import studio_audio
        project = self.fixture()
        project['studio']['scenes'] = [{'id':'scene', 'elements':[{'id':'clip','type':'video',
            'style':{'asset_id':'clip-a','mute':False}}]}]
        rows = [{'id':'scene','start_frame':0,'end_frame':30}]
        original = copy.deepcopy(project)
        with AssetFrames(project['studio']['media']) as assets:
            path,metadata = assets.audios['audio-1']
            fake = SimpleNamespace(audios=assets.audios,records={**assets.records,'clip-a':assets.records['audio-1']},
                videos={'clip-a':(path,metadata)})
            sources = studio_audio.combined_sources(project,rows,fake)
        self.assertEqual([source.kind for source in sources],['video','narration'])
        self.assertEqual(project,original)

    def test_mismatched_metadata_and_reference_to_non_audio_fail(self):
        project = self.fixture()
        project['studio']['media']['audio-1']['duration'] = .9
        with self.assertRaises(ValueError): AssetFrames(project['studio']['media'])
        project['studio']['media']['audio-1']['kind'] = 'image'
        with self.assertRaises(ValueError): validate_audio_tracks(project['studio'],30)

    def test_warm_assets_reuse_verified_probe_but_still_check_the_source_hash(self):
        import studio_voice
        record=import_asset(wav_content(),'voice.wav')
        studio_voice._probe_cached.cache_clear()
        original_run=subprocess.run
        with patch('studio_voice.subprocess.run',wraps=original_run) as decode:
            with AssetFrames({'voice':record}) as assets: self.assertIn('voice',assets.audios)
            with AssetFrames({'voice':record}) as assets: self.assertIn('voice',assets.audios)
            self.assertEqual(decode.call_count,1)
            Path(record['path']).write_bytes(wav_content(.2))
            with self.assertRaises(ValueError): AssetFrames({'voice':record})
            self.assertEqual(decode.call_count,1)

    def test_real_workspace_commit_reopen_and_undo_preserve_voice_and_science(self):
        from studio_workspace import WorkspaceSession
        from studio_recovery import recover_snapshot
        from test_studio_jobs import small_project
        state={}; session=WorkspaceSession(state,'voice',small_project(),store=self.root/'studio')
        before=copy.deepcopy(session.project)
        candidate=copy.deepcopy(before)
        candidate['studio']['media']['a']=import_asset(wav_content(),'voice.wav')
        candidate['studio']['audio_tracks']=[{'id':'voice','asset_id':'a','start':0.,
            'trim_in':0.,'trim_out':.1,'duration':.1,'mute':False}]
        session.commit(candidate)
        recovered,used_previous=recover_snapshot(state['voice_draft'])
        self.assertFalse(used_previous); self.assertEqual(recovered,candidate)
        reopened=WorkspaceSession({},'reopened',recovered,store=self.root/'studio')
        self.assertEqual(reopened.project['studio']['audio_tracks'],candidate['studio']['audio_tracks'])
        self.assertEqual(reopened.project['studio']['calculations'],before['studio']['calculations'])
        session.dispatch({'version':session.version,'scene':session.selected,'action':'undo'})
        self.assertEqual(session.project,before)
        session.dispatch({'version':session.version,'scene':session.selected,'action':'redo'})
        self.assertEqual(session.project,candidate)
        session.cache.clear(); reopened.cache.clear()

    def test_defaults_are_silent_and_validation_does_not_mutate(self):
        project = self.fixture()
        project['studio']['audio_tracks'] = [{'id':'v','asset_id':'audio-1'}]
        original = copy.deepcopy(project)
        tracks = validate_audio_tracks(project['studio'], 30)
        self.assertTrue(tracks[0]['mute']); self.assertFalse(tracks[0]['loop'])
        self.assertEqual(tracks[0]['start'],0)
        self.assertEqual(tracks[0]['volume'],1.)
        self.assertAlmostEqual(tracks[0]['duration'],.4,places=3)
        self.assertEqual(project,original)
        self.assertEqual(validate_audio_tracks({'media':{}},30),[])

    def test_finite_numbers_booleans_ids_and_endpoints_are_strict(self):
        project = self.fixture()
        for field,value in (('start',float('nan')),('start',True),('start',-1),
                            ('trim_in',True),('trim_out',float('inf')),('trim_out',.5),
                            ('duration',0),('duration',7201),('volume',True),('volume',2.1),
                            ('mute',1),('loop',0),('id','../escape'),('asset_id','missing')):
            with self.subTest(field=field,value=value):
                changed = copy.deepcopy(project['studio'])
                changed['audio_tracks'][0][field] = value
                with self.assertRaises(ValueError): validate_audio_tracks(changed,30)
        with self.assertRaises(ValueError): validate_audio_tracks(self.fixture(start=.9)['studio'],30)
        with self.assertRaises(ValueError): validate_audio_tracks(project['studio'],True)
        changed = copy.deepcopy(project['studio'])
        changed['audio_tracks'] *= 2
        with self.assertRaises(ValueError): validate_audio_tracks(changed,30)
        changed['audio_tracks'] = [{'id':f'v{i}','asset_id':'audio-1'} for i in range(17)]
        with self.assertRaises(ValueError): validate_audio_tracks(changed,30)

    def test_narration_starts_on_global_grid_trim_and_gain(self):
        project = self.fixture()
        with AssetFrames(project['studio']['media']) as assets:
            sources = combined_sources(project,[],assets)
            self.assertEqual(len(sources),1)
            source = sources[0]
            self.assertEqual((source.start_frame,source.trim_frame,source.duration_frames),(6,3,6))
            self.assertEqual(source.kind,'narration')
            pcm = mix_pcm(sources,30,self.root/'pcm')
            mixed = np.fromfile(pcm,dtype='<f4').reshape(-1,2)
        self.assertEqual(len(mixed),30*SAMPLES_PER_FRAME)
        self.assertEqual(float(np.max(np.abs(mixed[:6*SAMPLES_PER_FRAME]))),0)
        self.assertEqual(float(np.max(np.abs(mixed[12*SAMPLES_PER_FRAME:]))),0)
        self.assertGreater(float(np.max(np.abs(mixed[7*SAMPLES_PER_FRAME:11*SAMPLES_PER_FRAME]))),.05)

    def test_mute_zero_volume_and_legacy_projects_stay_silent(self):
        for options in ({'mute':True},{'volume':0}):
            project = self.fixture(**options)
            with AssetFrames(project['studio']['media']) as assets:
                self.assertEqual(combined_sources(project,[],assets),[])
        legacy = {'studio':{'media':{},'scenes':[]}}
        with AssetFrames({}) as assets:
            self.assertEqual(combined_sources(legacy,[],assets),[])

    def test_narration_half_frames_match_subtitle_quantization(self):
        project=self.fixture(start=.15,trim_in=.15,trim_out=.35,duration=.15)
        normalized=validate_audio_tracks(project['studio'],30)[0]
        self.assertAlmostEqual(normalized['start'],5/30)
        self.assertAlmostEqual(normalized['duration'],5/30)
        with AssetFrames(project['studio']['media']) as assets:
            source=combined_sources(project,[],assets)[0]
        self.assertEqual((source.start_frame,source.trim_frame,source.duration_frames),(5,5,5))

    def test_loop_reuses_one_decode_and_nonloop_pads_silence(self):
        project = self.fixture(duration=.6,loop=True,start=0)
        with AssetFrames(project['studio']['media']) as assets:
            sources = combined_sources(project,[],assets)
            pcm = mix_pcm(sources,30,self.root/'loop')
        mixed = np.fromfile(pcm,dtype='<f4').reshape(-1,2)
        self.assertTrue(np.array_equal(mixed[:9600],mixed[9600:19200]))
        self.assertEqual(len(list((self.root/'loop').glob('source-*.f32'))),1)
        project['studio']['audio_tracks'][0]['loop'] = False
        with AssetFrames(project['studio']['media']) as assets:
            pcm = mix_pcm(combined_sources(project,[],assets),30,self.root/'nonloop')
        mixed = np.fromfile(pcm,dtype='<f4').reshape(-1,2)
        self.assertEqual(float(np.max(np.abs(mixed[9600:]))),0)

    def test_actual_mux_receipt_distinguishes_voice_clips_and_both(self):
        from dataclasses import replace
        from studio_audio import mux_audio
        project = self.fixture()
        with AssetFrames(project['studio']['media']) as assets:
            voice = combined_sources(project,[],assets)[0]
        for mode,sources in (('narration_mix',[voice]),
                             ('audiovisual_mix',[voice,replace(voice,id='clip',kind='video')]),
                             ('original_clip_mix',[replace(voice,id='clip',kind='video')])):
            with self.subTest(mode=mode):
                video = self.root/(mode+'.mp4')
                result = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-nostdin',
                    '-f','lavfi','-i','color=c=black:s=160x160:r=30:d=1',
                    '-c:v','libx264','-pix_fmt','yuv420p',str(video)],capture_output=True,timeout=20)
                self.assertEqual(result.returncode,0,result.stderr)
                receipt = mux_audio(video,sources,30)
                self.assertEqual(receipt['mode'],mode)
                self.assertEqual(receipt['sample_rate'],48000)
                self.assertEqual(receipt['total_samples'],48000)
                self.assertLessEqual(receipt['decoded_peak'],.98)
                self.assertTrue(video.is_file())
                self.assertFalse(list(self.root.glob('.studio-audio-*')))


if __name__ == '__main__': unittest.main()
