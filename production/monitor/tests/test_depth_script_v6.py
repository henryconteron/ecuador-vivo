import json
import unittest
import wave
from hashlib import sha256
import numpy as np
from prepare_depth_script_v6 import V6,SCRIPT,NAMES,parts


class NarrativeV6Tests(unittest.TestCase):
    def test_narrative_order_and_causal_connections(self):
        p=parts()
        self.assertEqual(list(p),list(NAMES))
        self.assertIn('¿Cómo puede',p['gancho'])
        self.assertIn('estimación',p['cortes'])
        self.assertIn('no es lo mismo',p['foco'])
        self.assertIn('desplazamientos permanentes',p['material'])
        self.assertIn('reflejarse',p['registro'])
        self.assertIn('comparables',p['distancia'])
        self.assertIn('regresar a Bolivia',p['bolivia'])
        self.assertIn('uno solo',p['magnitud'])
        self.assertIn('La profundidad importa',p['retorno'])

    def test_scientific_caveats_and_case_providers(self):
        p=parts()
        self.assertIn('vertical u horizontal',p['s'])
        self.assertIn('no espera',p['s'])
        self.assertIn('estructura de capas',p['love'])
        self.assertIn('representación simplificada',p['love'])
        self.assertIn('no niveles de daño',p['profundidad'])
        self.assertIn('Instituto Geofísico del Perú',p['loreto'])
        self.assertIn('informe preliminar',p['ecuador'])
        self.assertIn('Son escalas distintas',p['ecuador'])
        self.assertIn('magnitud estimada',p['pelileo'])
        self.assertIn('menor de quince',p['pelileo'])
        self.assertIn('se desprende y baja',p['reventador'])
        self.assertIn('inercia',p['edificio'])
        self.assertIn('resonancia',p['edificio'])
        self.assertNotIn('no se colocaron mirando dónde hubo daños',SCRIPT.read_text(encoding='utf-8'))

    def test_audio_only_manifest_and_complete_segments(self):
        m=json.loads((V6/'audio_review_v6.json').read_text(encoding='utf-8'))
        self.assertEqual(m['script_sha256'],sha256(SCRIPT.read_bytes()).hexdigest())
        self.assertEqual(m['status'],'audio_only_narrative_review_not_publication')
        self.assertEqual([s['name'] for s in m['segments']],list(NAMES))
        for segment in m['segments']:
            path=V6/'audio_provisional'/segment['file']
            self.assertEqual(sha256(path.read_bytes()).hexdigest(),segment['sha256'])
            self.assertLess(segment['speech_start']+segment['speech_seconds'],segment['end'])
            with wave.open(str(path)) as audio:
                self.assertEqual((audio.getnchannels(),audio.getsampwidth(),audio.getframerate()),(1,2,16000))
                samples=np.frombuffer(audio.readframes(audio.getnframes()),dtype='<i2').astype(np.int32)
            self.assertGreater(float(np.sqrt(np.mean(samples.astype(float)**2))),100)
            self.assertLess(int(np.abs(samples).max()),32767)
        for key in ('output','preview'):
            self.assertEqual(m[key]['full_decode'],'passed')
            self.assertEqual(sha256((V6/m[key]['file']).read_bytes()).hexdigest(),m[key]['sha256'])


if __name__=='__main__':unittest.main()
