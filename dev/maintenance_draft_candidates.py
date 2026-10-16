"""Identify only attributable local QA/agent drafts; never delete or move them."""
from pathlib import Path
import hashlib
import json
import re


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / '_local/video-studio/projects'
REPORT = ROOT / '_local/maintenance/cleanup-20261011-draft-candidates.json'

EXACT_QA = {
    'Studio2 assistant Chrome fixture': 'production/video_studio/workspace_checks/integration_assistant_browser.py:63',
    'Studio2 scientific Chrome fixture': 'production/video_studio/workspace_checks/integration_science_browser.py:44',
    'Studio2 free Chrome fixture': 'production/video_studio/workspace_checks/integration_browser.py:37',
    'Studio2 navigation fixture': 'tmp/studio2-document-browser.py:19',
    'Prueba 4b.3b RGBA sincronizado': 'tmp/studio2-4b3b-validation.py:20',
    'Prueba temporal · GeoTIFF sintético de dos fechas': 'tmp/studio2-temporal-browser-fixture.py:15',
    'Prueba SIG GeoJSON': 'production/video_studio/workspace_checks/integration_geojson_browser.py:52',
    'UX · verificación Chrome': 'production/video_studio/workspace_checks/ux_interactions.py:34',
    'Worker anterior conservado': 'production/video_studio/workspace_checks/ux_state.py:48',
    'Validación SIG visible CHIRPS 2024 · copia': 'tmp/studio2-sig-visible-fixture.py:8',
}
PATTERNS = [
    (r'SIG-U2 fixture [a-f0-9]{8}', 'tmp/sig-u20-browser-expanded.py:16'),
    (r'SIG-U1 fixture [a-f0-9]{8}', 'tmp/sig-u1-browser.py:12'),
    (r'SIG interfaz fixture [a-f0-9]{8}', 'tmp/sig-interface-browser.py:17'),
    (r'SIG temporal interfaz fixture [a-f0-9]{8}', 'tmp/sig-interface-temporal-browser.py:15'),
    (r'SIG G1 interfaz fixture [a-f0-9]{8}', 'tmp/sig-interface-compatible-browser.py:11'),
    (r'ENGINE-0 native latency [a-f0-9]{8}', 'tmp/sig-engine0-native-latency.py:16'),
    (r'Ecuador Vivo · revisión profesional · cuencas y territorios de prueba · proyecto de nombre largo [a-f0-9]{8}', 'tmp/sig-professional-browser.py:21 / tmp/sig-analysis-browser-expanded.py:19'),
    (r'Ecuador Vivo · estabilidad Full HD · ocho escenas(?: · 24 segundos)?(?: · contraste| · medición v1)?', 'tmp/sig-professional-browser.py:33 / tmp/visual-ready-example.py:15; isolated agent QA composition'),
]
AGENT_BASES = {
    'andes-pulso-diseno-editorial-20261011', 'andes-pulso-entrega-20261011',
    'andes-pulso-rainflow-entrada', 'andes-pulso-rainflow-transferido',
    'andes-pulso-temperatura-septiembre-2026-20261011-195644',
    'andes-pulso-temperatura-septiembre-2026-20261011-200238',
}


def main():
    verification = json.loads((ROOT / '_local/video-studio/social-pilots-20261011/FINAL-VERIFICATION.json').read_text(encoding='utf-8-sig'))
    pilots = {Path(row['project']).resolve() for row in verification['projects']}
    candidates, protected, errors = [], [], []
    for path in sorted(PROJECTS.glob('*.json')):
        raw = path.read_bytes()
        reason, evidence, name = None, None, ''
        try:
            document = json.loads(raw)
            name = document.get('name', '')
        except (ValueError, UnicodeError) as error:
            document = {}
            if raw.strip() == b'{"interrupted_test_fixture":':
                reason, evidence = 'Interrupted QA fixture, explicit content marker, no authored project JSON.', 'Exact bytes {"interrupted_test_fixture":'
            else:
                errors.append({'path': str(path.resolve()), 'error': str(error)})
        record = {'path': str(path.resolve()), 'bytes': len(raw), 'name': name,
                  'sha256': hashlib.sha256(raw).hexdigest()}
        if path.resolve() in pilots:
            protected.append({**record, 'reason': 'One of the eight explicitly retained final pilots.'})
            continue
        if name == 'Prueba Studio 4b.4a':
            protected.append({**record, 'reason': 'Historical instructions explicitly identify this as a user project; see tasks/todo.md and tmp/ecuador-vivo-sig-universal-master.md:258.'})
            continue
        stem = path.stem.removesuffix('.previous')
        if stem in AGENT_BASES:
            reason = 'Previous agent-owned editorial/transfer experiment, confirmed in this maintenance task; preserve compact recoverable backup before removal.'
            evidence = 'tmp/build_rainflow.py:19,22 for rainflow; parent-maintenance confirmation for editorial/temperature/entrega.'
        if name in EXACT_QA:
            reason, evidence = 'Exact QA project name is assigned by the browser validation harness.', EXACT_QA[name]
        for pattern, source in PATTERNS:
            if re.fullmatch(pattern, name):
                reason, evidence = 'Exact agent QA naming pattern with its generating validation harness.', source
                break
        if reason:
            candidates.append({**record, 'reason': reason, 'evidence': evidence,
                               'action': 'candidate_only; compact recoverable backup required before removal'})
        else:
            protected.append({**record, 'reason': 'Ambiguous ownership: generic name, user work, or no unequivocal generating harness. Do not delete by filename or age.'})
    output = {'scope': 'Read-only classification. No projects deleted, moved, edited, or backed up by this script.',
              'candidates': candidates, 'protected_ambiguous_and_pilots': protected,
              'unparsed_unknown': errors, 'candidate_count': len(candidates),
              'candidate_bytes': sum(row['bytes'] for row in candidates),
              'protected_count': len(protected),
              'excluded_pilots': [str(path) for path in sorted(pilots)],
              'rule': 'Never delete by borrador prefix, generic title, or date alone; preserve raw data, bundles, current source, web, and eight final pilots.'}
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'report': str(REPORT), 'candidate_count': len(candidates),
                      'candidate_bytes': output['candidate_bytes'], 'protected_count': len(protected),
                      'unparsed_unknown': len(errors)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
