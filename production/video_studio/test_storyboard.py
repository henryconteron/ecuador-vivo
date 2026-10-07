"""Real local FFmpeg smoke tests + pure output/timeline validations. No downloads."""
import io
import math
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import imageio_ffmpeg
import numpy as np
from PIL import Image

import storyboard as S


class StoryboardTests(unittest.TestCase):
    def config(self, **changes):
        config = {'delivery': {'format': list(S.FORMATS)[1], 'quality': '720p'},
                  'duration': .2, 'endcard_duration': .2, 'background': '#04151e'}
        config.update(changes)
        return config

    def test_all_formats_are_even_and_have_the_selected_aspect(self):
        for name, size in S.FORMATS.items():
            for quality in ('1080p', '720p'):
                result = S.dimensions({'delivery': {'format': name, 'quality': quality}})
                self.assertTrue(all(value % 2 == 0 for value in result))
                self.assertAlmostEqual(result[0]/result[1], size[0]/size[1], delta=.002)

    def test_scientific_preview_fits_completely_without_stretching(self):
        source = Image.new('RGB', (108,192), 'red')
        preview = S.format_preview(source, self.config())
        self.assertEqual(preview.size, (1280,720))
        self.assertEqual(preview.getpixel((0,0)), (4,21,30))
        self.assertEqual(preview.getpixel((640,360)), (255,0,0))

    def test_timing_is_resolved_before_the_base_render(self):
        config = self.config(storyboard={'enabled': True, 'cards': [
            {'id': 'm', 'kind': 'map', 'duration': 10},
            {'id': 'e', 'kind': 'endcard', 'duration': 4},
            {'id': 't', 'kind': 'text', 'duration': 3, 'body': 'Explicación'}]})
        timed = S.base_timing(config)
        self.assertEqual(timed['duration'],10)
        self.assertEqual(timed['endcard_duration'],4)
        self.assertEqual(sum(row['seconds'] for row in S.cards_for(timed)),17)

    def test_invalid_duration_path_and_repeated_map_are_rejected(self):
        for seconds in (float('nan'), float('inf'), -1):
            with self.assertRaises(ValueError):
                S.cards_for(self.config(duration=seconds))
        for cards in ([{'id':'x','kind':'map'},{'id':'y','kind':'map'}],
                      [{'id':'x','kind':'map'},{'id':'i','kind':'image','path':'C:/Windows/not-a-resource.png'}]):
            with self.assertRaises(ValueError):
                S.cards_for(self.config(storyboard={'enabled':True, 'cards':cards}))

    def test_uploaded_images_are_deduplicated_and_verified(self):
        image = Image.new('RGB', (30,20), 'red')
        content = io.BytesIO()
        image.save(content, format='PNG')
        with tempfile.TemporaryDirectory() as folder, patch.object(S,'MEDIA_ROOT',Path(folder)):
            first = S.store_media(content.getvalue(), 'photo.png')
            second = S.store_media(content.getvalue(), 'other.png')
            self.assertEqual(first['path'], second['path'])
            self.assertEqual(len(list(Path(folder).iterdir())),1)
            with self.assertRaises(OSError):
                S.store_media(b'not an image', 'file.png')

    def test_explanation_is_legible_and_long_headlines_fail_instead_of_overflow(self):
        preview = S.card_preview({'kind':'text','title':'Un ejemplo histórico',
            'body':'Esto es una ilustración. La fecha y fuente del clip deben verificarse.',
            'citation':'Material de prueba · no es un evento real'}, self.config())
        self.assertEqual(preview.size,(1280,720))
        with self.assertRaises(ValueError):
            S.card_preview({'kind':'text','title':'Una palabra ' * 90}, self.config())

    def test_real_montage_formats_media_preserves_audio_and_does_not_add_to_metrics(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(S,'MEDIA_ROOT',Path(folder)/'media'):
            job = Path(folder)/'job'
            job.mkdir()
            base = job/'base.mp4'
            writer = imageio_ffmpeg.write_frames(str(base),(108,192),fps=30,codec='libx264',
                macro_block_size=1, pix_fmt_out='yuv420p')
            writer.send(None)
            for color in ('red',)*6 + ('blue',)*6:
                writer.send(np.asarray(Image.new('RGB',(108,192),color)))
            writer.close()
            Image.new('RGB',(108,192),'blue').save(job/'endcard.png')
            clip = job/'example.mp4'
            subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y',
                '-f','lavfi','-i','color=c=green:s=160x90:r=30','-f','lavfi','-i','sine=frequency=400:sample_rate=48000',
                '-t','1','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',str(clip)],check=True)
            asset = S.store_media(clip.read_bytes(),'example.mp4')
            config = self.config(storyboard={'enabled':True,'cards':[
                dict(id='text',kind='text',title='Ejemplo',body='No entra en las métricas',duration=.2),
                dict(id='map',kind='map',duration=.2),
                dict(asset,id='clip',label='Clip de prueba',duration=.4,start=.1,audio=True,
                     title='Video ilustrativo',citation='Prueba local · no es un sismo',fit='contain'),
                dict(id='end',kind='endcard',duration=.2)]})
            output, receipt = S.assemble(job,base,config,map_duration=.2,endcard_duration=.2)
            self.assertTrue(output.is_file())
            self.assertAlmostEqual(receipt['duration_seconds'],1.)
            self.assertEqual([row['kind'] for row in receipt['cards']],['text','map','video','endcard'])
            self.assertTrue(receipt['cards'][2]['audio'])
            metadata = S.probe_video(output)
            self.assertEqual(metadata['size'],[1280,720])
            self.assertTrue(metadata['audio'])
            self.assertAlmostEqual(metadata['duration'],1.,delta=.12)
            self.assertNotIn('summary',receipt)
            reader = imageio_ffmpeg.read_frames(str(output))
            decoded = next(reader)
            selected = {}
            frame_count = 0
            for index, pixels in enumerate(reader):
                if index in (8, 17, 28):
                    selected[index] = np.frombuffer(pixels,dtype=np.uint8).reshape(decoded['size'][1], decoded['size'][0],3)[360,640]
                frame_count += 1
            self.assertEqual(frame_count,30)
            # Each source is still in its selected place and time, not merely
            # present somewhere in an apparently complete output.
            self.assertGreater(selected[8][0],200)  # base map: red
            self.assertGreater(selected[17][1],90)  # inserted clip: green
            self.assertGreater(selected[28][2],200) # metrics closing: blue

    def test_short_clip_rejects_time_beyond_the_original(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(S,'MEDIA_ROOT',Path(folder)):
            clip = Path(folder)/'x.mp4'
            clip.write_bytes(b'test placeholder')
            with patch.object(S,'probe_video',return_value={'duration':1., 'audio':False}):
                with self.assertRaises(ValueError):
                    S.cards_for(self.config(storyboard={'enabled':True,'cards':[
                        dict(id='map',kind='map'),dict(id='clip',kind='video',path=str(clip),start=.5,duration=1)]}))


class StoryboardUITests(unittest.TestCase):
    def test_comparison_uses_its_own_timing_and_does_not_enable_a_disabled_closing(self):
        from storyboard_ui import timeline_config
        project = {'video_type':'Comparación climática','duration':26,'endcard_duration':6,
                   'comparison_design':{'duration':18,'endcard_duration':9,'endcard_enabled':False}}
        active = timeline_config(project)
        self.assertEqual(sum(row['seconds'] for row in S.cards_for(active)),18)
        self.assertEqual([row['kind'] for row in S.cards_for(active)],['map'])

    def test_format_selection_and_text_card_use_the_same_project(self):
        from streamlit.testing.v1 import AppTest
        def script():
            import streamlit as st
            from model import default_project
            from storyboard_ui import show_storyboard
            st.session_state.setdefault('project',default_project())
            show_storyboard(st.session_state.project)
        app = AppTest.from_function(script, default_timeout=15).run()
        app.toggle(key='story_open').set_value(True).run()
        self.assertFalse(app.exception)
        app.selectbox(key='story_format').select(list(S.FORMATS)[1]).run()
        app.toggle(key='story_enabled').set_value(True).run()
        self.assertFalse(app.exception)
        app.checkbox(key='story_map_follow').set_value(False).run()
        timing = next(row for row in app.number_input if row.label == 'Duración de esta tarjeta · segundos')
        self.assertFalse(timing.disabled)
        timing.set_value(18.)
        next(row for row in app.button if row.label == 'Aplicar tarjeta').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state.project['storyboard']['cards'][0]['duration'],18.)
        app.selectbox(key='story_new_kind').select('Explicación con texto').run()
        app.button(key='story_add').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state.project['delivery']['format'],list(S.FORMATS)[1])
        self.assertEqual(app.session_state.project['storyboard']['cards'][-1]['kind'],'text')
        added_id = app.session_state.project['storyboard']['cards'][-1]['id']
        self.assertEqual(app.selectbox(key='story_selected').value,added_id)
        app.button(key='story_up').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state.project['storyboard']['cards'][1]['id'],added_id)
        self.assertEqual(app.selectbox(key='story_selected').value,added_id)


if __name__ == '__main__':
    unittest.main()
