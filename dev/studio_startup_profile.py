"""Headless startup measurement: no browser, server, project writes or rendering jobs.

Run with the Studio interpreter and --output for a reproducible JSON report.
Each sample starts a fresh interpreter; reruns use that same AppTest session.
--isolate-home replaces artwork/catalogue rendering only, isolating app imports.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / 'production' / 'video_studio'


def worker(isolate_home=False):
    sys.path.insert(0, str(STUDIO))
    from streamlit.testing.v1 import AppTest
    from unittest.mock import patch
    from contextlib import nullcontext

    source = (STUDIO / 'app.py').read_text(encoding='utf-8-sig')
    # Test-only markers around existing boundaries; application sources stay untouched.
    prefix = "import time as _profile_time\nimport streamlit as st\n_profile_started=_profile_time.perf_counter()\nst.session_state['_startup_profile']={}\n"
    for label, marker in (
        ('before_model', 'import model as _model'),
        ('before_legacy_imports', 'import data as _data'),
        ('before_config', 'st.set_page_config('),
        ('before_routes', "if p is None and st.session_state.section in ('SIG', 'Editor', 'Comparar para video'):"),
    ):
        lines = source.splitlines()
        for index, line in enumerate(lines):
            if line.lstrip().startswith(marker):
                indent = line[:len(line) - len(line.lstrip())]
                lines.insert(index, indent + "st.session_state['_startup_profile']['" + label + "']=_profile_time.perf_counter()-_profile_started")
                source = '\n'.join(lines) + '\n'
                break
    # Headless metadata and gallery only, avoiding the expensive old video thumbnail.
    def lightweight_home(*args, **kwargs):
        import streamlit as st
        st.title('Ecuador Vivo')
    context = patch('studio_home.show_home', lightweight_home) if isolate_home else nullcontext()
    before = set(sys.modules)
    with context:
        app = AppTest.from_string(prefix + source, default_timeout=90)
        started = time.perf_counter()
        app.run()
        cold = time.perf_counter() - started
        phases = dict(app.session_state['_startup_profile'])
        reruns = []
        for _ in range(3):
            started = time.perf_counter()
            app.run()
            reruns.append(time.perf_counter() - started)
        errors = [str(item.value) for item in app.exception]
    modules = sorted(set(sys.modules) - before)
    return {
        'isolate_home': isolate_home, 'cold_seconds': cold,
        'rerun_seconds': reruns, 'phases_seconds': phases,
        'loaded_module_count': len(modules),
        'heavy_modules_loaded': [name for name in ('data', 'render', 'endcard', 'providers', 'jobs', 'social', 'rasterio', 'scipy', 'matplotlib') if name in modules],
        'exceptions': errors, 'project_open': app.session_state['project'] is not None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--isolate-home', action='store_true')
    parser.add_argument('--samples', type=int, default=3)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(worker(args.isolate_home), ensure_ascii=False))
        return
    rows = []
    for index in range(args.samples):
        command = [sys.executable, str(Path(__file__).resolve()), '--worker']
        if args.isolate_home:
            command.append('--isolate-home')
        started = time.perf_counter()
        run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=180)
        if run.returncode:
            raise RuntimeError(run.stderr[-6000:] + run.stdout[-6000:])
        result = json.loads(run.stdout.strip().splitlines()[-1])
        result['fresh_process_seconds'] = time.perf_counter() - started
        rows.append(result)
        print(f"Sample {index + 1}: cold={result['cold_seconds']:.3f}s, reruns={result['rerun_seconds']}", flush=True)
    report = {'clock': 'perf_counter', 'samples': rows, 'scope': 'AppTest server-side timing, not browser LCP/INP; actual local files read-only'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
