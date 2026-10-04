import json
from hashlib import sha256
from pathlib import Path
import unittest
import wave
import numpy as np
from prepare_depth_script_v7 import ROOT, V7, SCRIPT, NAMES, parts


class NarrativeV7Tests(unittest.TestCase):
    def test_observation_before_technical_names(self):
        p = parts()
        self.assertEqual(list(p), list(NAMES))
        for observation, label in (('resorte', 'p'), ('cuerda', 's')):
            self.assertLess(NAMES.index(observation), NAMES.index(label))
        self.assertNotIn('estadio', SCRIPT.read_text(encoding='utf-8'))
        self.assertIn('avanza la onda', p['particula'])
        self.assertIn('no viaja desde el foco hasta la ciudad', p['particula'])
        self.assertIn('inercia', p['bus'])
        self.assertIn('columpio', p['columpio'])
        self.assertIn('resonancia', p['columpio'])
        self.assertIn('frecuencia', p['ritmo'])

    def test_continuity_and_accessible_questions(self):
        p = parts()
        self.assertIn('cortes de Ecuador', p['cortes'])
        self.assertIn('hasta llegar a una casa', p['cortes'])
        self.assertIn('¿qué llega hasta acá?', p['ruptura'])
        self.assertIn('regresemos a Bolivia', p['bolivia'])
        self.assertIn('respuesta a nuestra pregunta del inicio', p['bolivia'])
        self.assertIn('mismo terremoto', p['tena'])
        self.assertIn('cortes del principio', p['retorno'])
        self.assertNotIn('Soy Henry Conteron', SCRIPT.read_text(encoding='utf-8'))
        self.assertNotIn('En el siguiente episodio', SCRIPT.read_text(encoding='utf-8'))
        self.assertEqual(NAMES[-1], 'conciencia')
        self.assertTrue(SCRIPT.read_text(encoding='utf-8').rstrip().endswith(
            'Nos ayudan a comprender un riesgo con el que ya vivimos.'))

    def test_science_qualifiers_and_providers(self):
        p = parts()
        self.assertIn('puede extenderse', p['ruptura'])
        self.assertIn('desplazamiento permanente', p['particula'])
        self.assertIn('horizontal', p['s'])
        self.assertIn('generar ambas', p['s'])
        self.assertIn('rigidez', p['agua'])
        self.assertIn('capas del terreno', p['love'])
        self.assertIn('simplifica', p['love'])
        self.assertIn('rebota', p['registro'])
        self.assertIn('No son tres niveles de peligro', p['profundidad'])
        self.assertIn('En condiciones comparables', p['distancia'])
        self.assertIn('Instituto Geofísico del Perú', p['loreto'])
        self.assertIn('informe preliminar', p['tena'])
        self.assertIn('cada una con su escala', p['tena'])
        self.assertIn('magnitud estimada', p['pelileo'])
        self.assertIn('menor de quince', p['pelileo'])
        self.assertIn('no una reconstrucción exacta', p['piedemonte'])
        self.assertIn('por gravedad', p['contraste'])
        self.assertIn('no predice', p['columpio'])

    def test_audio_complete_and_unchanged_script(self):
        m = json.loads((V7 / 'audio_review_v7.json').read_text(encoding='utf-8'))
        self.assertEqual(m['script_file'], 'guion_elevenlabs_v7_corregido.txt')
        self.assertEqual(m['script_sha256'], sha256(SCRIPT.read_bytes()).hexdigest())
        self.assertEqual(m['word_count'], len(SCRIPT.read_text(encoding='utf-8').split()))
        self.assertEqual(m['status'], 'audio_only_narrative_review_not_publication')
        self.assertEqual([s['name'] for s in m['segments']], list(NAMES))
        previous_end = 0
        for s in m['segments']:
            self.assertAlmostEqual(s['start'], previous_end)
            self.assertLess(s['speech_start'] + s['speech_seconds'], s['end'])
            previous_end = s['end']
            path = V7 / 'audio_provisional' / s['file']
            self.assertEqual(sha256(path.read_bytes()).hexdigest(), s['sha256'])
            with wave.open(str(path)) as audio:
                self.assertEqual((audio.getnchannels(), audio.getsampwidth(), audio.getframerate()), (1, 2, 16000))
                samples = np.frombuffer(audio.readframes(audio.getnframes()), dtype='<i2').astype(np.int32)
            self.assertGreater(float(np.sqrt(np.mean(samples.astype(float)**2))), 100)
            self.assertLess(int(np.abs(samples).max()), 32767)
        self.assertAlmostEqual(previous_end, m['duration_seconds'])
        self.assertAlmostEqual(m['preview']['duration_seconds'], m['segments'][1]['end'])
        for key in ('output', 'preview'):
            self.assertEqual(m[key]['full_decode'], 'passed')
            self.assertEqual(sha256((V7 / m[key]['file']).read_bytes()).hexdigest(), m[key]['sha256'])

    def test_prior_versions_and_original_catalogue_preserved(self):
        files = {
            'artifacts/serie_memoria_sismica/00_profundidad_danos/v5/ondas_profundidad_3d_voz_provisional_v5.mp4':
                '50e04fb52e0a805c90bb247d256e43b270acd477c79f071a69568e93c7cf0ede',
            'artifacts/serie_memoria_sismica/00_profundidad_danos/v6/lectura_guion_voz_provisional_v6.mp3':
                '7e45f2f13a73400231b3b14262331ad4531c7e59347627d4efaabda12a8fe31a',
            'artifacts/reel_ecuador_1900_2025_v6/usgs_snapshot.geojson':
                '8cf19180b19b9a9998f76f1feee9bf88b69d141287a9d213e3455f20c1b2d5c8',
        }
        for filename, expected in files.items():
            self.assertEqual(sha256((ROOT / filename).read_bytes()).hexdigest(), expected)


if __name__ == '__main__':
    unittest.main()
