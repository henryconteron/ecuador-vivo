"""Read-only dependency guard for local Studio cleanup; writes only its report."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from pathlib import Path
import re
import sys


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def strings(value, key=''):
    if isinstance(value, str):
        yield key, value
    elif isinstance(value, dict):
        for name, child in value.items():
            yield from strings(child, name)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child, key)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()
    store = repo / '_local/video-studio'
    reports = store / 'social-pilots-20261011'
    report_path = (args.report or repo / '_local/maintenance/cleanup-20261011-pilot-guard/protection.json').resolve()
    permitted_reports = (repo / '_local/maintenance/cleanup-20261011-pilot-guard').resolve()
    if not report_path.is_relative_to(permitted_reports):
        raise ValueError('Report must stay inside its dedicated maintenance directory.')
    final_path = reports / 'FINAL-VERIFICATION.json'
    final = json.loads(final_path.read_text(encoding='utf-8-sig'))
    pilot_paths = {Path(row['project']).resolve() for row in final['projects']}
    all_projects = sorted((store / 'projects').glob('*.json'))
    files, directories, origins, missing, parse_errors = set(), set(), {}, {}, {}
    scanned = set()
    pending = deque()

    def add(path, origin):
        path = path.resolve()
        if path.is_dir():
            # An explicitly referenced directory is indivisible without a
            # provider-specific proof. Do not infer ownership from its name.
            directories.add(path)
        elif path.is_file():
            files.add(path)
            if path.suffix.lower() in {'.json', '.geojson'} and path not in scanned:
                pending.append(path)
            if path.name == 'manifest.json' and 'map-bundles' in path.parts:
                directories.add(path.parent)
        else:
            return False
        origins.setdefault(str(path), set()).add(str(origin))
        return True

    for path in all_projects:
        add(path, 'saved_project_protected_until_ownership_proven')
    for path in [final_path, reports / 'exports.json', reports / 'enso-review/report.json']:
        add(path, 'pilot_verification_report')
    for row in final['projects']:
        add(Path(row['video']).parent, 'final_pilot_export_job')
        for name in ('project.json', 'receipt.json', 'request.json', 'options.json', 'status.json'):
            add(Path(row['video']).parent / name, row['project'])
        add(Path(row['video']), 'final_pilot_movie')
    for name in ('LEEME-PRUEBAS.md', 'research.json', 'guide.md'):
        add(reports / name, 'pilot_usage_documentation')

    while pending:
        path = pending.popleft()
        if path in scanned:
            continue
        scanned.add(path)
        if path.stat().st_size > 24 * 1024 * 1024:
            parse_errors[str(path)] = 'Protected but not traversed: JSON larger than 24 MiB.'
            continue
        try:
            value = json.loads(path.read_text(encoding='utf-8-sig'))
        except (UnicodeError, ValueError, OSError) as error:
            parse_errors[str(path)] = str(error)
            continue
        for key, text in strings(value):
            if not text or len(text) > 4096 or text.startswith(('http:', 'https:', 'data:')):
                continue
            absolute = bool(re.match(r'^[A-Za-z]:[\\/]', text))
            path_key = 'path' in key.lower() or key.lower() in {'file', 'directory', 'video', 'preview', 'project', 'job', 'manifest', 'receipt'}
            if not absolute and not path_key and not text.startswith(('_local/', '_local\\', 'data/', 'data\\')):
                continue
            try:
                candidates = [Path(text)] if absolute else [path.parent / text, repo / text, store / text, store / 'media' / text]
                candidates = [candidate.resolve() for candidate in candidates]
                found = False
                for candidate in candidates:
                    if candidate.exists():
                        add(candidate, path)
                        found = True
                if absolute and not found:
                    missing.setdefault(str(Path(text).resolve()), set()).add(str(path))
            except (OSError, ValueError):
                continue

    sys.path.insert(0, str(repo / 'production/video_studio'))
    from studio_project import validate_document
    from studio_timeline import PreparedTimeline
    results = []
    for row in final['projects']:
        project_path = Path(row['project'])
        movie = Path(row['video'])
        result = {'name': row['name'], 'project': str(project_path.resolve()),
                  'video': str(movie.resolve()), 'movie_exists': movie.is_file()}
        if movie.is_file():
            result.update(movie_bytes=movie.stat().st_size, sha256=digest(movie))
            result['movie_matches_final_report'] = result['sha256'] == row['sha256'] and result['movie_bytes'] == row['movie_bytes']
        try:
            original_bytes = project_path.read_bytes()
            document = json.loads(original_bytes)
            opened = validate_document(document)
            prepared = PreparedTimeline(opened)
            receipt = json.loads((movie.parent / 'receipt.json').read_text(encoding='utf-8-sig'))
            receipt_project = hashlib.sha256(json.dumps(document, sort_keys=True, ensure_ascii=False, allow_nan=False).encode('utf-8')).hexdigest()
            result.update(open_validation_passed=True, total_frames=prepared.total_frames,
                          frame_count_matches=prepared.total_frames == row['frames'],
                          dimensions=[prepared.profile.width, prepared.profile.height],
                          project_file_unchanged=original_bytes == project_path.read_bytes(),
                          project_canonical_sha256=receipt_project,
                          receipt_project_sha256=receipt.get('project_sha256'),
                          project_matches_receipt=receipt_project == receipt.get('project_sha256'))
        except Exception as error:
            result.update(open_validation_passed=False, validation_error=f'{type(error).__name__}: {error}')
        results.append(result)

    protected_existing_files = set(files)
    for directory in directories:
        # Only enumerate filenames/sizes; do not decode or read binary assets.
        protected_existing_files.update(path for path in directory.rglob('*') if path.is_file())
    # A second closure lets maintenance distinguish the eight requested pilots
    # from conservative protection of other saved documents without guessing.
    pilot_reachable = {str(path) for path in pilot_paths}
    pilot_reachable.update(str(Path(row['video']).parent.resolve()) for row in final['projects'])
    for row in final['projects']:
        for name in ('project.json', 'receipt.json', 'request.json', 'options.json', 'status.json'):
            pilot_reachable.add(str((Path(row['video']).parent / name).resolve()))
    for path, reasons in origins.items():
        if reasons & {'final_pilot_movie', 'pilot_verification_report', 'pilot_usage_documentation'}:
            pilot_reachable.add(path)
    while True:
        previous_count = len(pilot_reachable)
        for path, reasons in origins.items():
            if reasons & pilot_reachable:
                pilot_reachable.add(path)
        if len(pilot_reachable) == previous_count:
            break
    missing_pilot_dependencies = {name: sorted(refs) for name, refs in missing.items()
                                  if any(Path(ref) in pilot_paths for ref in refs)}
    payload = {
        'scope': 'No deletes, moves, app edits, installs, downloads, or project rewrites.',
        'repo': str(repo), 'pilot_count': len(pilot_paths),
        'saved_project_json_count': len(all_projects),
        'unknown_project_policy': 'Preserve every other saved project and dependencies until independent evidence proves an agent-only draft.',
        'unknown_or_other_project_files': [str(path.resolve()) for path in all_projects if path.resolve() not in pilot_paths],
        'protected_files': sorted(str(path) for path in files),
        'protected_directories': sorted(str(path) for path in directories),
        'pilot_protected_files': sorted(str(path) for path in files if str(path) in pilot_reachable),
        'pilot_protected_directories': sorted(str(path) for path in directories if str(path) in pilot_reachable or str(path / 'manifest.json') in pilot_reachable),
        'protection_reasons': {path: sorted(reasons) for path, reasons in sorted(origins.items())},
        'protected_unique_file_count_including_directories': len(protected_existing_files),
        'protected_bytes_including_directories': sum(path.stat().st_size for path in protected_existing_files),
        'parsed_json_count': len(scanned), 'json_parse_or_budget_issues': parse_errors,
        'missing_absolute_references': {name: sorted(refs) for name, refs in missing.items()},
        'missing_direct_pilot_references': missing_pilot_dependencies,
        'pilots': results,
        'all_8_pilots_valid': len(results) == 8 and all(row.get('movie_matches_final_report') and row.get('open_validation_passed') and row.get('frame_count_matches') and row.get('project_file_unchanged') and row.get('project_matches_receipt') for row in results),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'report': str(report_path), 'all_8_pilots_valid': payload['all_8_pilots_valid'],
                      'saved_project_json_count': len(all_projects), 'protected_files': len(files),
                      'protected_directories': len(directories), 'protected_total_files': len(protected_existing_files),
                      'protected_bytes': payload['protected_bytes_including_directories'],
                      'missing_direct_pilot_references': len(missing_pilot_dependencies),
                      'parse_issues': len(parse_errors)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
