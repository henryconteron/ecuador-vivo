"""Headless native narration/subtitle editing, isolated from active projects."""
import copy
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest
sys.path.insert(0,str(Path(__file__).parent))
import storyboard
from studio_editing import new_workspace
from studio_media import import_asset
from studio_voice_ui import show_voice_captions
from test_studio_voice import wav_content


class StudioVoiceUITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        boundary = patch.object(storyboard,'MEDIA_ROOT',self.root/'media')
        boundary.start(); self.addCleanup(boundary.stop)

    def app(self, project=None, panel='Voz'):
        project = project or new_workspace({'endcard_enabled':False})
        script = '''import copy, sys, streamlit as st
sys.path.insert(0,{module!r})
from studio_voice_ui import show_voice_captions
from studio_model import validate_studio
class Fake:
    key='session'; state=st.session_state
    @property
    def project(self):return st.session_state['doc']
    def commit(self, candidate):
        validate_studio(candidate['studio'])
        st.session_state['doc']=copy.deepcopy(candidate)
        st.session_state['commits']=st.session_state.get('commits',0)+1
if 'doc' not in st.session_state:st.session_state['doc']={project!r}
show_voice_captions(Fake(),key='voice')
'''.format(module=str(Path(__file__).parent),project=project)
        app = AppTest.from_string(script,default_timeout=20)
        app.session_state['voice_panel']=panel
        return app

    def voice_project(self):
        project = new_workspace({'endcard_enabled':False})
        record = import_asset(wav_content(),'mi voz.wav')
        project['studio']['media']['audio']=record
        project['studio']['audio_tracks']=[{'id':'v','asset_id':'audio','mute':False}]
        return project

    def test_empty_voice_panel_and_captions_table_do_not_crash(self):
        for panel in ('Voz','Subtítulos'):
            app = self.app(panel=panel).run()
            self.assertFalse(app.exception)
            self.assertFalse(app.error)
            self.assertTrue(any(b.label=='Cerrar' for b in app.button))

    def test_import_audio_is_audible_and_original_calculations_are_untouched(self):
        upload=io.BytesIO(wav_content()); upload.name='voz.wav'
        with patch('studio_voice_ui.st.file_uploader',return_value=upload), \
             patch('studio_voice_ui.st.audio_input',return_value=None):
            app=self.app().run(); before=copy.deepcopy(app.session_state['doc'])
            next(b for b in app.button if b.label=='Añadir voz al video').click().run()
            self.assertFalse(app.exception); self.assertFalse(app.error)
            doc=app.session_state['doc']
            self.assertEqual(len(doc['studio']['audio_tracks']),1)
            self.assertFalse(doc['studio']['audio_tracks'][0]['mute'])
            self.assertEqual(doc['studio']['scenes'],before['studio']['scenes'])
            self.assertEqual(doc['studio']['calculations'],before['studio']['calculations'])

    def test_track_properties_save_and_remove_without_deleting_the_source(self):
        app=self.app(self.voice_project()).run()
        next(n for n in app.number_input if n.label=='Inicio en el video (s)').set_value(.1)
        next(s for s in app.slider if s.label=='Volumen').set_value(.5)
        next(b for b in app.button if b.label=='Guardar pista').click().run()
        self.assertFalse(app.exception); self.assertFalse(app.error)
        track=app.session_state['doc']['studio']['audio_tracks'][0]
        self.assertEqual(track['start'],.1); self.assertEqual(track['volume'],.5)
        record=app.session_state['doc']['studio']['media']['audio']
        next(b for b in app.button if b.label=='Quitar pista del video').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['doc']['studio']['audio_tracks'],[])
        self.assertTrue(Path(record['path']).is_file())

    def test_microphone_recording_uses_the_same_verified_import_path(self):
        upload=io.BytesIO(wav_content()); upload.name='grabacion.wav'
        with patch('studio_voice_ui.st.audio_input',return_value=upload):
            app=self.app(); app.session_state['voice_source']='Micrófono'; app.run()
            next(b for b in app.button if b.label=='Añadir voz al video').click().run()
            self.assertFalse(app.exception); self.assertFalse(app.error)
            self.assertFalse(app.session_state['doc']['studio']['audio_tracks'][0]['mute'])

    def test_manual_subtitles_save_and_invalid_overlap_is_not_committed(self):
        rows=[{'id':'one','start':0.,'end':1.,'text':'Mira esta franja.'}]
        with patch('studio_voice_ui.st.data_editor',return_value=pd.DataFrame(rows)):
            app=self.app(panel='Subtítulos').run()
            next(c for c in app.checkbox if c.label=='Mostrar subtítulos en el video').check()
            next(b for b in app.button if b.label=='Guardar subtítulos').click().run()
            self.assertFalse(app.exception); self.assertFalse(app.error)
            self.assertTrue(app.session_state['doc']['studio']['captions']['enabled'])
        before=copy.deepcopy(app.session_state['doc'])
        invalid=rows+[{'id':'two','start':.5,'end':2.,'text':'No debe solaparse.'}]
        with patch('studio_voice_ui.st.data_editor',return_value=pd.DataFrame(invalid)):
            app.run()
            next(b for b in app.button if b.label=='Guardar subtítulos').click().run()
            self.assertFalse(app.exception); self.assertTrue(app.error)
            self.assertEqual(app.session_state['doc'],before)

    def test_srt_import_requires_explicit_replacement(self):
        project=new_workspace({'endcard_enabled':False})
        project['studio']['captions']={'enabled':True,'cues':[{'id':'old','start':0.,'end':1.,'text':'Anterior'}]}
        upload=io.BytesIO(b'1\n00:00:00,000 --> 00:00:01,000\nNuevo\n'); upload.name='voz.srt'
        with patch('studio_voice_ui.st.file_uploader',return_value=upload):
            app=self.app(project,panel='Subtítulos').run()
            next(b for b in app.button if b.label=='Importar subtítulos').click().run()
            self.assertTrue(app.error)
            self.assertEqual(app.session_state['doc']['studio']['captions']['cues'][0]['text'],'Anterior')
            next(c for c in app.checkbox if c.label=='Reemplazar los subtítulos actuales').check()
            next(b for b in app.button if b.label=='Importar subtítulos').click().run()
            self.assertFalse(app.exception); self.assertFalse(app.error)
            self.assertEqual(app.session_state['doc']['studio']['captions']['cues'][0]['text'],'Nuevo')


if __name__=='__main__': unittest.main()
