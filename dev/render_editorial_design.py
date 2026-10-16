"""Review a presentation-only copy using the already sealed real-data project."""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'production' / 'video_studio'))
from studio_templates import rainfall_scenes
from studio_map_bundles import read_bundle
from studio_timeline import PreparedTimeline
from studio_recovery import save_snapshot


def prepare():
    source = ROOT / '_local/video-studio/projects/andes-pulso-entrega-20261011.json'
    original = json.loads(source.read_text(encoding='utf-8'))
    project = copy.deepcopy(original)
    transfer = project['studio']['sig_transfer']
    record = project['studio']['media'][transfer['asset_id']]
    snapshot = project['studio']['datasets'][transfer['science_dataset']]
    scenes = rainfall_scenes(project, record, read_bundle(record), snapshot)
    for scene in scenes:
        previous = next(s for s in project['studio']['scenes'] if s.get('rainfall_template') == scene['rainfall_template'])
        scene['id'] = previous['id']
        scene['duration'] = previous['duration']
        project['studio']['scenes'][project['studio']['scenes'].index(previous)] = scene
    project['name'] = 'Andes Pulso · diseño editorial · 1–7 enero 2024'
    for key in ('calculations', 'datasets', 'media', 'geography', 'sig_transfer'):
        assert project['studio'][key] == original['studio'][key], key
    assert project['studio']['timeline'] == original['studio']['timeline']
    path = ROOT / '_local/video-studio/projects/andes-pulso-diseno-editorial-20261011.json'
    save_snapshot(path, project)
    return project, path


if __name__ == '__main__':
    project, path = prepare()
    output = ROOT / 'tmp/editorial-design-20261011'
    output.mkdir(exist_ok=True, parents=True)
    for maximum in (None, 640):
        timeline = PreparedTimeline(project, preview_max_side=maximum)
        for frame, label in ((18, 'mapa'), (126, 'metricas')):
            image = timeline.frame_at(frame)
            image.save(output / f'{label}-{maximum or 1920}.png')
            image.close()
    print(path)
    print(output)
    if '--video' in sys.argv:
        from studio_jobs import start_studio_job
        print(start_studio_job(project))
