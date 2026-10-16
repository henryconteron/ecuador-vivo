"""Bounded plain-text subtitles with one frame-based preview/export renderer."""
import copy
import sys
import unittest
from pathlib import Path

from PIL import Image, ImageChops

sys.path.insert(0, str(Path(__file__).parent))
from studio_captions import (
    DEFAULT_CAPTION_STYLE, caption_frame, export_captions, parse_captions,
    prepare_captions, render_captions, validate_captions,
    validate_caption_layout,
)


class StudioCaptionTests(unittest.TestCase):
    def test_import_srt_utf8_bom_formatting_and_frame_quantization(self):
        text = '\ufeff1\r\n00:00:00,020 --> 00:00:01,010\r\n<b>El río</b> &amp; su cauce\r\n\r\n2\r\n00:00:01,010 --> 00:00:02,000\r\nOtra idea.\r\n'
        cues = parse_captions(text.encode('utf-8'), 'narracion.srt')
        self.assertEqual(cues[0]['text'], 'El río & su cauce')
        self.assertEqual(cues[0]['start'], 1 / 30)
        self.assertEqual(cues[0]['end'], 1.0)
        self.assertEqual(cues[1]['start'], 1.0)
        self.assertNotEqual(cues[0]['id'], cues[1]['id'])

    def test_import_vtt_handles_header_notes_settings_voice_and_inline_timestamps(self):
        text = 'WEBVTT prueba\nKind: captions\nLanguage: es\n\nNOTE esto no es un subtítulo\n00:00:00.000 --> 00:00:01.000\n\nSTYLE\n::cue {color: red;}\n\nREGION\nid: one\n\nmi-cue\n00:00.000 --> 00:02.000 line:80% position:50%\n<v Henry><c.cyan>Hola</c> <00:01.000>amigo</v>\n'
        cues = parse_captions(text, 'voz.vtt')
        self.assertEqual(len(cues), 1)
        self.assertEqual(cues[0]['text'], 'Hola amigo')
        self.assertEqual((cues[0]['start'], cues[0]['end']), (0.0, 2.0))

    def test_export_srt_and_vtt_round_trip_preserves_frames_and_literal_text(self):
        cues = [{'id': 'c1', 'start': 1 / 30, 'end': 31 / 30,
                 'text': 'Agua < 2 mm & temperatura > 20 °C'}]
        for fmt in ('srt', 'vtt'):
            exported = export_captions(cues, fmt)
            self.assertIn('00:00:00', exported)
            round_trip = parse_captions(exported, 'export.' + fmt)
            for key in ('start', 'end', 'text'):
                self.assertEqual(cues[0][key], round_trip[0][key])

    def test_parse_rejects_scripts_html_unknown_types_and_non_utf8(self):
        base = '1\n00:00:00,000 --> 00:00:01,000\n{}\n'
        for text in ('<script>alert(1)</script>', '<img src=x onerror=alert(1)>', '<iframe>x</iframe>'):
            with self.assertRaises(ValueError):
                parse_captions(base.format(text), 'mal.srt')
        for content, name in ((b'\xff', 'mal.srt'), ('x', 'mal.ass'), (True, 'mal.srt')):
            with self.assertRaises(ValueError):
                parse_captions(content, name)

    def test_malformed_timestamps_overlap_empty_and_collapsed_cues_are_rejected(self):
        for text in (
            '1\n00:99:00,000 --> 00:00:01,000\nHola',
            '1\n00:00:01,000 --> 00:00:00,000\nHola',
            '1\n00:00:00,001 --> 00:00:00,002\nHola',
            '1\n00:00:00,000 --> 00:00:01,000\n',
            '1\n00:00:00,000 --> 00:00:02,000\nHola\n\n2\n00:00:01,000 --> 00:00:03,000\nMundo',
        ):
            with self.assertRaises(ValueError):
                parse_captions(text, 'mal.srt')

    def test_input_cue_text_and_encoded_payload_limits(self):
        with self.assertRaises(ValueError):
            parse_captions('a' * (2 * 1024 * 1024 + 1), 'large.srt')
        for cues in (
            [{'id': 'c', 'start': 0, 'end': 1, 'text': 'a' * 801}],
            [{'id': str(i), 'start': i, 'end': i + 1, 'text': 'a'} for i in range(5001)],
            [{'id': str(i), 'start': i, 'end': i + 1, 'text': 'é' * 800} for i in range(1500)],
        ):
            with self.assertRaises(ValueError):
                validate_captions({'captions': {'enabled': True, 'cues': cues}})

    def test_validation_is_pure_optional_and_rejects_bad_bounds_and_timing(self):
        validate_captions({})
        captions = {'enabled': True, 'cues': [{'id': 'one', 'start': 0, 'end': 1, 'text': 'Hola'}]}
        studio = {'captions': captions}
        original = copy.deepcopy(studio)
        self.assertIsNone(validate_captions(studio, total_frames=30))
        self.assertEqual(studio, original)
        invalid = [
            dict(captions, enabled=1),
            dict(captions, cues=[{'id': 'c', 'start': True, 'end': 1, 'text': 'Hola'}]),
            dict(captions, cues=[{'id': 'c', 'start': 0, 'end': float('nan'), 'text': 'Hola'}]),
            dict(captions, cues=[{'id': 'c', 'start': 0, 'end': 1, 'text': 'Hola\x00'}]),
            dict(captions, style={'x': .9, 'width': .5}),
            dict(captions, style={'font_family': '../../secret.ttf'}),
            dict(captions, style={'color': 'red; background:url(x)'}),
            dict(captions, style={'font_size': True}),
        ]
        for value in invalid:
            with self.assertRaises(ValueError):
                validate_captions({'captions': value}, total_frames=30)
        with self.assertRaises(ValueError):
            validate_captions(studio, total_frames=29)

    def test_global_frame_start_is_inclusive_end_is_exclusive(self):
        image = Image.new('RGBA', (1080, 1920), '#183040')
        captions = {'enabled': True, 'cues': [{'id': 'c', 'start': 0, 'end': 1, 'text': 'El mapa cuenta una historia.'}]}
        before = image.tobytes()
        for frame in (0, 29):
            rendered = render_captions(image, captions, frame)
            self.assertNotEqual(rendered.tobytes(), before)
        self.assertEqual(render_captions(image, captions, 30).tobytes(), before)
        self.assertEqual(image.tobytes(), before)
        self.assertEqual(render_captions(image, dict(captions, enabled=False), 0).tobytes(), before)

    def test_decimal_half_frames_are_rounded_up_and_adjacent_cues_have_no_gap(self):
        self.assertEqual(caption_frame(.05), 2)
        captions = {'enabled': True, 'cues': [
            {'id': 'a', 'start': 0, 'end': 1, 'text': 'Primera idea.'},
            {'id': 'b', 'start': 1, 'end': 2, 'text': 'Una idea diferente.'},
        ]}
        image = Image.new('RGBA', (270, 480), '#183040')
        before = render_captions(image, captions, 29)
        after = render_captions(image, captions, 30)
        self.assertNotEqual(before.tobytes(), after.tobytes())
        self.assertNotEqual(after.tobytes(), image.tobytes())

    def test_prepared_track_is_isolated_from_later_document_edits(self):
        captions = {'enabled': True, 'cues': [{'id': 'a', 'start': 0, 'end': 1, 'text': 'Texto original.'}]}
        prepared = prepare_captions(captions, total_frames=30)
        image = Image.new('RGBA', (270, 480), '#183040')
        expected = render_captions(image, captions, 0)
        captions['cues'][0]['text'] = 'Otro texto.'
        captions['style'] = {'color': '#000000'}
        self.assertEqual(render_captions(image, prepared, 0).tobytes(), expected.tobytes())

    def test_authoring_overlay_matches_composite_without_mutating_cache_or_old_info(self):
        captions = {'enabled': True, 'cues': [{'id': 'a', 'start': 0, 'end': 1, 'text': 'Texto editable.'}]}
        image = Image.new('RGBA', (270, 480), '#183040')
        image.info['caption_overlay'] = {'old': True}
        authoring = render_captions(image, captions, 0, authoring=True)
        overlay = authoring.info['caption_overlay']
        rebuilt = image.copy()
        rebuilt.alpha_composite(overlay['image'], (overlay['x'], overlay['y']))
        self.assertEqual(rebuilt.tobytes(), authoring.tobytes())
        overlay['image'].paste('red', (0, 0, *overlay['image'].size))
        self.assertEqual(render_captions(image, captions, 0).tobytes(), authoring.tobytes())
        self.assertNotIn('caption_overlay', render_captions(image, captions, 30, authoring=True).info)
        self.assertNotIn('caption_overlay', render_captions(image, captions, 0).info)
        self.assertEqual(image.info['caption_overlay'], {'old': True})

    def test_nonfinite_boolean_and_outside_frame_values_are_rejected(self):
        captions = {'enabled': True, 'cues': []}
        image = Image.new('RGBA', (270, 480))
        for frame in (-1, True, 1.0, float('inf')):
            with self.assertRaises(ValueError):
                render_captions(image, captions, frame)
        for time in (-1, True, float('inf'), float('nan'), 1e15, 10 ** 500):
            with self.assertRaises(ValueError):
                caption_frame(time)

    def test_preflight_detects_overfull_later_cue_not_just_frame_zero(self):
        captions = {'enabled': True, 'cues': [
            {'id': 'a', 'start': 0, 'end': 1, 'text': 'Un texto corto.'},
            {'id': 'b', 'start': 1, 'end': 2, 'text': 'Palabra ' * 95},
        ]}
        with self.assertRaisesRegex(ValueError, 'cabe|líneas'):
            validate_caption_layout(prepare_captions(captions), 1080, 1920)
        validate_caption_layout(dict(captions, enabled=False), 1080, 1920)

    def test_same_renderer_authoring_export_and_all_aspect_ratios_fit_normalized_box(self):
        captions = {'enabled': True, 'cues': [{'id': 'c', 'start': 0, 'end': 1, 'text': 'Mismos datos.\nOtra perspectiva.'}]}
        for size in ((1080, 1920), (1920, 1080), (1080, 1080), (270, 480)):
            image = Image.new('RGBA', size, '#183040')
            image.info['keep'] = 'metadata'
            rendered = render_captions(image, captions, 0)
            authored = render_captions(image, captions, 0, authoring=True)
            self.assertEqual(rendered.tobytes(), authored.tobytes())
            self.assertEqual(rendered.mode, 'RGBA')
            self.assertEqual(rendered.info['keep'], 'metadata')
            box = ImageChops.difference(image.convert('RGB'), rendered.convert('RGB')).getbbox()
            self.assertIsNotNone(box)
            self.assertGreaterEqual(box[0], round(size[0] * DEFAULT_CAPTION_STYLE['x']))
            self.assertGreaterEqual(box[1], round(size[1] * DEFAULT_CAPTION_STYLE['y']))
            self.assertLessEqual(box[2], round(size[0] * (DEFAULT_CAPTION_STYLE['x'] + DEFAULT_CAPTION_STYLE['width'])))
            self.assertLessEqual(box[3], round(size[1] * (DEFAULT_CAPTION_STYLE['y'] + DEFAULT_CAPTION_STYLE['height'])))

    def test_overfull_caption_fails_visibly_instead_of_cutting_words(self):
        image = Image.new('RGBA', (1080, 1920))
        captions = {'enabled': True, 'cues': [{'id': 'c', 'start': 0, 'end': 1, 'text': 'Palabra ' * 95}]}
        with self.assertRaisesRegex(ValueError, 'cabe|líneas'):
            render_captions(image, captions, 0)

    def test_real_portrait_movie_keeps_resource_caption_frames_and_independent_aac(self):
        """All generated audio/media/movie products stay in TemporaryDirectory."""
        import io
        import subprocess
        import tempfile
        import wave
        from unittest.mock import patch

        import imageio_ffmpeg
        import numpy as np
        import storyboard
        from output_profiles import profile_for
        from studio_editing import new_workspace
        from studio_media import import_asset
        from studio_resources import resource_scene
        from studio_timeline import export_movie, PreparedTimeline

        stream = io.BytesIO()
        samples = (np.sin(np.arange(19200) * 2 * np.pi * 440 / 48000) * 6000).astype('<i2')
        with wave.open(stream, 'wb') as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(48000)
            output.writeframes(samples.tobytes())
        with tempfile.TemporaryDirectory(prefix='ev-caption-export-') as directory:
            root = Path(directory)
            with patch.object(storyboard, 'MEDIA_ROOT', root / 'media'):
                record = import_asset(stream.getvalue(), 'synthetic-test-tone.wav')
                project = new_workspace({'endcard_enabled': False})
                project['studio']['output_profile'] = {'id': 'tiktok'}
                scene = resource_scene('rain_volume', profile_for({'id': 'tiktok'}), duration=.4)
                project['studio']['scenes'] = [scene]
                project['studio']['timeline'] = [scene['id']]
                project['studio']['media'] = {'voice': record}
                project['studio']['audio_tracks'] = [
                    {'id': 'voice-1', 'asset_id': 'voice', 'start': 0,
                     'duration': .4, 'mute': False, 'volume': .5, 'loop': False}]
                project['studio']['captions'] = {'enabled': True, 'style': {'y': .84}, 'cues': [
                    {'id': 'first', 'start': 0, 'end': .2, 'text': 'Un milímetro de lluvia.'}]}
                prepared = PreparedTimeline(project)
                target = root / 'export' / 'video.mp4'
                receipt = export_movie(project, target)
                self.assertEqual(receipt['dimensions'], [1080, 1920])
                self.assertEqual(receipt['fps'], 30)
                self.assertEqual(receipt['total_frames'], 12)
                self.assertEqual(receipt['captions']['cue_count'], 1)
                self.assertEqual(receipt['audio']['mode'], 'narration_mix')
                self.assertEqual(receipt['audio']['sample_rate'], 48000)
                decoded = subprocess.run(
                    [imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-nostdin', '-i', str(target),
                     '-map', '0:v:0', '-pix_fmt', 'rgb24', '-f', 'rawvideo', 'pipe:1'],
                    capture_output=True, timeout=30,
                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                details = decoded.stderr.decode(errors='replace')
                self.assertEqual(decoded.returncode, 0, details)
                self.assertIn('1080x1920', details)
                self.assertIn('30 fps', details)
                frames = np.frombuffer(decoded.stdout, dtype=np.uint8).reshape(-1, 1920, 1080, 3)
                self.assertEqual(len(frames), 12)
                for frame in (0, 5, 6, 11):
                    expected = np.asarray(prepared.frame_at(frame).convert('RGB'), dtype=np.int16)
                    self.assertLess(float(np.mean(np.abs(frames[frame].astype(np.int16) - expected))), 3)
                result = subprocess.run(
                    [imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-nostdin', '-i', str(target),
                     '-map', '0:a:0', '-ac', '2', '-ar', '48000', '-f', 'f32le', 'pipe:1'],
                    capture_output=True, timeout=30,
                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                self.assertEqual(result.returncode, 0, result.stderr.decode(errors='replace'))
                self.assertIn('Audio: aac', result.stderr.decode(errors='replace'))
                decoded_audio = np.frombuffer(result.stdout, dtype='<f4')
                self.assertTrue(np.isfinite(decoded_audio).all())
                self.assertGreater(float(np.max(np.abs(decoded_audio))), .02)


if __name__ == '__main__':
    unittest.main()
