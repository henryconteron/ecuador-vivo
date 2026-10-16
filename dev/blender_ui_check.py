"""Exercise the completed local Blender product through native Streamlit controls."""
import argparse
import copy
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'production/video_studio'))
from streamlit.testing.v1 import AppTest
from studio_blender import verified_product

SCRIPT='''
import streamlit as st
from studio_blender_ui import show_blender_ui
show_blender_ui(st.session_state.get('test_project'),
    lambda doc:st.session_state.update(accepted=doc),key='verified_blender_ui')
'''


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('identifier');args=parser.parse_args()
    folder,recipe,receipt=verified_product(args.identifier)
    app=AppTest.from_string(SCRIPT,default_timeout=45)
    app.session_state['verified_blender_ui_job']=args.identifier
    app.run()
    if app.exception:raise RuntimeError(str(app.exception))
    if app.error:raise RuntimeError(str(app.error))
    app.button(key='verified_blender_ui_edit').click().run()
    if app.exception or app.error:raise RuntimeError(str(app.exception)+str(app.error))
    document=app.session_state['accepted']
    assert document['source']=='local' and document['studio']['calculations']=={}
    assert document['studio']['scenes'][0]['resource']['blender']['recipe']==recipe
    original=copy.deepcopy(document)
    app.session_state['test_project']=document
    app.run()
    app.button(key='verified_blender_ui_replace').click().run()
    if app.exception or app.error:raise RuntimeError(str(app.exception)+str(app.error))
    assert document==original, 'Replacing mutated the original project.'
    updated=app.session_state['accepted']
    assert updated['studio']['scenes'][0]['elements']==document['studio']['scenes'][0]['elements']
    verified_product(args.identifier)
    report=dict(completed_product_display=True,open_in_editable_canvas=True,
        replace_preserves_elements=True,original_unchanged=True,recipe_preserved=True,
        no_scientific_calculations=True,source_hashes_verified=True,
        browser_layout_acceptance=False)
    output=ROOT/'_local/resource-development-20261012/blender-proof-final/ui-verification.json'
    output.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))


if __name__=='__main__':main()
