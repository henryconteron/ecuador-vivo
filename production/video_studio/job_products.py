"""Resolve completed worker products from validated receipt metadata.

Older receipts keep their explicit legacy/Studio filename contracts. Never
guess by scanning the folder or expose a path outside the completed job.
"""
from pathlib import Path
import re
from jobs import read_json


def video_artifact(name, digest):
    if (not isinstance(name, str) or not name or len(name) > 180
            or any(c in name for c in '/\\:\x00') or not name.endswith('.mp4')
            or name.endswith('.partial.mp4') or name == 'video-incompleto.mp4'):
        raise ValueError('Nombre de artefacto MP4 inválido.')
    if not isinstance(digest, str) or not re.fullmatch(r'[a-f0-9]{64}', digest):
        raise ValueError('Hash de artefacto MP4 inválido.')
    return {'name': name, 'mime': 'video/mp4', 'sha256': digest}


def published_movie(job):
    job = Path(job)
    status = read_json(job / 'status.json', {})
    if not isinstance(status, dict):
        raise ValueError('Estado del trabajo inválido.')
    if status.get('state') != 'complete':
        return None
    receipt = read_json(job / 'receipt.json', {})
    if not isinstance(receipt, dict):
        raise ValueError('Comprobante del trabajo inválido.')
    if 'artifacts' in receipt:
        artifacts = receipt['artifacts']
        if not isinstance(artifacts, dict) or not isinstance(artifacts.get('video'), dict):
            raise ValueError('Falta metadata del producto de video.')
        declared = artifacts['video']
        record = video_artifact(declared.get('name'), declared.get('sha256'))
        if declared.get('mime') != record['mime']:
            raise ValueError('MIME del producto de video inválido.')
        if receipt.get('video_sha256', record['sha256']) != record['sha256']:
            raise ValueError('El hash del producto difiere del comprobante.')
    else:
        if receipt.get('renderer') == 'studio_scene_v1':
            name = 'video.mp4'
        elif receipt.get('complete') is True:
            name = 'ecuador-vivo.mp4'
        else:
            raise ValueError('No hay un contrato de producto publicado reconocible.')
        record = video_artifact(name, receipt.get('video_sha256'))
    movie = job / record['name']
    if not movie.resolve().is_relative_to(job.resolve()) or not movie.is_file() or movie.stat().st_size == 0:
        raise ValueError('El MP4 publicado falta o está fuera del trabajo.')
    return movie
