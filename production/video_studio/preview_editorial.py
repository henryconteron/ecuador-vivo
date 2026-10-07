"""Reproduce the social comparison preview using cached originals, no downloads.

Run from the repository: python production/video_studio/preview_editorial.py
Add --video to export a short local MP4 with the same maps and closing card.
"""
import argparse
import calendar
import datetime as dt
import json
from pathlib import Path

import pandas as pd

from model import STORE, PALETTES
from climate_comparison import cached_power_download, summarize_raster_months
from comparison_video import render_preview, render_comparison_endcard, create_comparison_job


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video', action='store_true', help='Exporta una prueba local de 6 s + 3 s de cierre, sin publicar.')
    parser.add_argument('--layout-demo', action='store_true', help='Comprueba geometría personalizada e iconos con los mismos datos originales.')
    parser.add_argument('--story-demo', action='store_true', help='Prueba horizontal con explicación, imagen y clip local; sin nuevos datos ni publicación.')
    options = parser.parse_args()
    receipts, tables = [], []
    for year in (2016, 2024, 2026):
        start, end = dt.date(year, 1, 1), dt.date(year, 2, calendar.monthrange(year, 2)[1])
        found = False
        for path in (STORE/'downloads').glob('nasa-power-*/metadata.json'):
            manifest = json.loads(path.read_text(encoding='utf-8'))
            if manifest.get('parameter') == 'T2M' and manifest.get('requested_period') == {'start': start.isoformat(), 'end': end.isoformat()}:
                found = True
                break
        if not found:
            raise SystemExit(f'Falta la copia original local T2M de {year}, enero–febrero. No se descargará ni se inventará.')
        receipt = cached_power_download(start, end, 'T2M')
        receipts.append(receipt)
        tables.append(summarize_raster_months(receipt['tiff_path'], 'T2M', year, 1, 2))
    output = dict(parameter='T2M', mode='nacional', area='Ecuador', years=[2016, 2024, 2026],
                  first_month=1, last_month=2, source='NASA POWER', receipts=receipts)
    config = dict(title='¿Cómo cambió la temperatura media del aire a 2 m?',
                  subtitle='Misma escala · 3 años · Ecuador.', variable='Temperatura media del aire a 2 m',
                  parameter='T2M', units='°C', palette_colors=PALETTES['Termal editorial'], map_layout='Dos mapas',
                  citation='NASA POWER · NASA / MERRA-2 · ~50–60 km',
                  method='Mapas mensuales. Sin datos: sin color. Suavizar no añade resolución. Islas reubicadas.',
                  tiktok='@elgeocientifico', instagram='@henry_conteron')
    table = pd.concat(tables, ignore_index=True)
    folder = STORE/'previews'
    folder.mkdir(parents=True, exist_ok=True)
    prefix = 'editor-layout' if options.layout_demo else 'comparacion-editorial'
    if options.layout_demo:
        captured = render_preview(table, output, {**config, '_layout_capture': True}, progress=1)
        main = next(row for row in captured.info['visual_scene'].items if row['id'] == 'map.0.main')
        closing, _ = render_comparison_endcard(table, output, {**config, '_layout_capture': True})
        icon = next(row for row in closing.info['visual_scene'].items if row['kind'] == 'icon')
        config['visual_layout'] = {'version': 1, 'full_canvas': True,
            'map': {main['id']: {'x': main['x'] + 12, 'y': main['y'] + 8, 'w': round(main['w'] * .94)}},
            'endcard': {icon['id']: {'icon': 'temperature'}}}
    render_preview(table, output, config, progress=1).save(folder/(prefix+'-mapas.png'))
    image, summary = render_comparison_endcard(table, output, config)
    image.save(folder/(prefix+'-metricas.png'))
    print(json.dumps({'values': summary['period_values'], 'findings': summary['findings'], 'folder': str(folder)}, ensure_ascii=False))
    if options.video:
        config.update(duration=6, endcard_duration=3, name='Prueba editorial · temperatura · enero–febrero')
        if options.story_demo:
            from storyboard import store_media, FORMATS, card_preview
            original = STORE/'jobs'/'comparacion-20261007-120633-78af4988'/'ecuador-vivo.mp4'
            if not original.is_file():
                raise SystemExit('Falta el clip editorial previo. No se descargará otro.')
            asset = store_media(original.read_bytes(), 'comparacion-temperatura.mp4')
            photo = store_media((folder/(prefix+'-mapas.png')).read_bytes(), 'mapas-temperatura.png')
            config['delivery'] = {'format': list(FORMATS)[1], 'quality': '720p'}
            config['storyboard'] = {'enabled': True, 'cards': [
                dict(id='intro',kind='text',duration=2,title='¿Un mapa puede contar una historia?',
                     body='Comparamos la temperatura con los mismos meses y la misma escala. Los ejemplos son ilustrativos: no entran en los cálculos.', citation='NASA POWER · enero–febrero · 2016 / 2024 / 2026'),
                dict(id='map',kind='map',duration=6,label='Mapa animado'),
                dict(photo,id='image',duration=2,label='Imagen del mapa', title='También puedes insertar imágenes', citation='Mismos datos · vista previa original'),
                dict(asset,id='clip',duration=2,start=1,audio=False,label='Ejemplo de clip',title='Un clip dentro de la historia',citation='Prueba local · comparación de temperatura · no es un sismo'),
                dict(id='end',kind='endcard',duration=3,label='Métricas calculadas')]}
            card_preview(config['storyboard']['cards'][0],config).save(folder/'montaje-horizontal-intro.png')
        job = create_comparison_job(table, output, config)
        print(json.dumps({'video': str(job/'ecuador-vivo.mp4'), 'receipt': str(job/'receipt.json')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
