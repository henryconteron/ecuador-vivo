"""Real local app/Chrome flow; installed Tornado + Chrome, no added dependencies.

Run the app: python -m streamlit run studio_server.py --server.port 8512
From repository root: python production/video_studio/verify_workspace_browser.py
Captures/logged results: tmp/ux-redesign/. Science uses one already cached CHIRPS day.
"""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
CHECKS=Path(__file__).with_name('workspace_checks')
STEPS={'shell':['ux_after.py'],'interactions':['ux_interactions.py'],
       'media':['ux_media_fixture.py','ux_media_flow.py','ux_download_verify.py'],
       'science':['ux_science_fixture.py','ux_science_flow.py'],
       'accessibility':['ux_accessibility.py'], 'state':['ux_state.py']}

def run():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--steps',nargs='+',choices=list(STEPS),default=list(STEPS))
    options=parser.parse_args()
    for step in options.steps:
        for script in STEPS[step]:
            print('Chrome workspace:',step,script,flush=True)
            subprocess.run([sys.executable,str(CHECKS/script)],cwd=ROOT,check=True,timeout=300)
    print('Workspace Chrome flow OK',flush=True)

if __name__=='__main__':run()
