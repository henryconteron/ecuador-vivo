"""Bounded read-only ZIP range inspection of published ReforesTree reference."""
import io
import json
from urllib.request import Request,urlopen
import zipfile
import csv
import math
import hashlib
from tools.parcelas.process_api import ROOT

URL='https://zenodo.org/records/6813783/files/reforesTree.zip?download=1'
SIZE=7514326095


class RangeReader(io.RawIOBase):
    def __init__(self):
        self.position=0; self.downloaded=0

    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.position

    def seek(self,offset,whence=0):
        target=offset if whence==0 else self.position+offset if whence==1 else SIZE+offset
        if not 0<=target<=SIZE: raise ValueError('Invalid archive offset')
        self.position=target; return target

    def read(self,size=-1):
        if size<0: size=SIZE-self.position
        size=min(size,SIZE-self.position)
        if not size: return b''
        if size>2_000_000 or self.downloaded+size>8_000_000: raise ValueError('Range budget exceeded')
        start=self.position; end=start+size-1
        request=Request(URL,headers={'Range':f'bytes={start}-{end}','User-Agent':'EcuadorVivo-reference-audit/0.1'})
        with urlopen(request,timeout=45) as response:
            if response.status!=206 or response.headers.get('Content-Range')!=f'bytes {start}-{end}/{SIZE}':
                raise ValueError('Server did not honor exact range; full ZIP download refused')
            raw=response.read(size+1)
        if len(raw)!=size: raise ValueError('Incomplete archive range')
        self.position+=size; self.downloaded+=size; return raw


def main():
    folder=ROOT/'_local/parcelas/referencias/reforestree-6813783'
    folder.mkdir(parents=True,exist_ok=True)
    reader=RangeReader()
    with zipfile.ZipFile(reader) as archive:
        entries=[{'name':i.filename,'size':i.file_size,'compressed_size':i.compress_size,'crc32':f'{i.CRC:08x}'}
                 for i in archive.infolist() if not i.is_dir()]
        candidates=[e for e in entries if e['name'].lower().endswith(('.csv','.geojson','.kml','.shp','.prj','.gpkg'))]
        (folder/'indice.json').write_text(json.dumps({'source':URL,'archive_bytes':SIZE,'entry_count':len(entries),
            'reference_files':candidates,'license':'CC BY 4.0','downloaded_bytes':reader.downloaded},indent=2),encoding='utf-8')
        print(json.dumps({'entries':len(entries),'reference_files':candidates,'downloaded_bytes':reader.downloaded},indent=2))
        matches=[e for e in entries if e['name'].split('/')[-1]=='field_data.csv']
        if len(matches)==1 and matches[0]['size']<=10_000_000 and matches[0]['compressed_size']<=2_000_000:
            target=folder/'field_data.csv'
            if not target.exists():
                raw=archive.read(matches[0]['name']) # zipfile also verifies CRC; no path extraction.
                target.write_bytes(raw)
            print('Field reference CSV recovered; no drone archive downloaded. Bytes read:',reader.downloaded)
        for entry in entries:
            name=entry['name']
            wanted=(name.startswith('wwf_ecuador/Merged_final_plots/') and name.endswith(('.shp','.shx','.dbf','.prj','.cpg'))) or name=='tiles/ortho_data.csv'
            if wanted:
                if entry['size']>1_000_000: raise ValueError('Reference component exceeds limit')
                target=folder/name.split('/')[-1]
                if not target.exists(): target.write_bytes(archive.read(name))
        print('Small field boundary components recovered. Total range bytes:',reader.downloaded)
    export_plots(folder)


def export_plots(folder):
    import fiona
    from shapely.geometry import shape,Point,mapping
    from shapely.ops import transform
    from shapely import make_valid
    from shapely.validation import explain_validity
    from pyproj import Geod
    output=folder/'parcelas-estudio.geojson'
    if output.exists(): print('Existing plot export retained'); return
    rows=list(csv.DictReader((folder/'field_data.csv').read_text(encoding='utf-8-sig').splitlines()))
    features=[]; records=[]
    with fiona.open(folder/'Merged_final_plots.shp') as source:
        if source.crs.to_epsg()!=4326 or len(source)!=6:
            raise ValueError('Unexpected field boundary CRS or number of plots')
        for index,feature in enumerate(source,1):
            original=shape(feature['geometry'])
            geom=transform(lambda x,y,z=None:(x,y),original)
            validity=explain_validity(geom)
            repaired=not geom.is_valid
            if repaired:
                geom=make_valid(geom)
            if geom.is_empty or not geom.is_valid or geom.geom_type not in ('Polygon','MultiPolygon'):
                raise ValueError('Source cannot be converted to valid polygon without additional interpretation')
            counts={}
            for row in rows:
                try: point=Point(float(row['lon']),float(row['lat']))
                except (ValueError,KeyError): continue
                if geom.covers(point): counts[row['site']]=counts.get(row['site'],0)+1
            site=max(counts,key=counts.get) if counts else None
            matched=[r for r in rows if r['site']==site] if site else []
            years=[]
            for row in matched:
                try: year=float(row['year'])
                except (ValueError,KeyError): continue
                if math.isfinite(year) and 1900<=year<=2020: years.append(int(year))
            area=abs(Geod(ellps='WGS84').geometry_area_perimeter(geom)[0])/10000
            properties={'plot_id':f'RF{index:02d}','source_name':feature['properties']['Name'],
                'matched_inventory_site':site,'inventory_records_inside_by_site':counts,
                'area_geodesic_ha':area,'planting_years_in_inventory':sorted(set(years)),
                'crop_reference':'cacao and mixed agroforestry reported by ReforesTree paper',
                'boundary_type':'published field study polygon, NOT cadastral ownership boundary',
                'original_geometry_validity':validity,'topological_repair_applied':repaired,
                'geometry_review':'required_before_analysis' if repaired else 'original_2D_geometry_valid',
                'change_history':'unknown; planting years do not establish prior forest or clearing',
                'drone_reference_year':2020,'drone_pixel_spacing_reported_m':0.02,
                'drone_imagery_downloaded':False,'source_doi':'10.5281/zenodo.6813783','license':'CC BY 4.0',
                'geometry_change':'Z removed; Shapely make_valid applied where declared, review required; original SHP/PRJ preserved',
                'geolocation_warning':'Paper v2 documents drone-field alignment correction; inspect corrected data before subpixel co-registration'}
            features.append({'type':'Feature','geometry':mapping(geom),'properties':properties})
            records.append(properties)
    output.write_text(json.dumps({'type':'FeatureCollection','features':features},indent=2),encoding='utf-8')
    manifest={'source':URL,'archive_size':SIZE,'archive_not_downloaded':True,'license':'CC BY 4.0',
        'source_files_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir()
                              if p.suffix in ('.shp','.shx','.prj','.dbf','.cpg','.csv')},
        'plot_count':len(features),'valid_original_plots':sum(not p['topological_repair_applied'] for p in records),
        'plots':records,'status':'real_field_plots_recovered_not_deforestation_history_validation'}
    (folder/'procedencia-parcelas.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    lines=['# Ecuador Vivo · parcelas ecuatorianas documentadas','',
        '**Se recuperaron seis polígonos de parcelas de estudio ReforesTree. No son linderos catastrales.**','',
        'Fuente pública CC BY 4.0: https://zenodo.org/records/6813783 . Archivo original de 7.514.326.095 bytes NO descargado completo.',
        'Se leyeron rangos HTTP acotados, índice ZIP, inventario de campo y componentes de polígonos. CRC de cada miembro validado por zipfile.',
        'Publicación: https://arxiv.org/html/2201.11192v2 . Declara captura con dron en 2020 y píxel de 2 cm, inventario de especies/GPS y plantaciones de 2016–2019.',
        'La revisión v2 documenta correcciones de alineación entre imágenes y campo: no confundir píxel de 2 cm con exactitud geográfica de 2 cm.', '',
        'Control topológico: cuatro geometrías originales tienen autointersecciones y dos son válidas.',
        'En el GeoJSON derivado se aplicó make_valid a las cuatro, marcadas para revisión; SHP original conservado. No aceptarlas automáticamente como límites verificados.', '',
        '| ID | Parcela fuente | Área calculada ha | Años de plantación en inventario asociado |', '|---|---|---:|---|']
    for p in records:
        lines.append(f'| {p["plot_id"]} | {p["source_name"]} | {p["area_geodesic_ha"]:.4f} | {", ".join(map(str,p["planting_years_in_inventory"])) or "no recuperados"} |')
    lines+=['', '## Qué permite aplicar', '',
        '- Usar geometrías publicadas reales para recortes, soporte espacial y contraste con inventario agroforestal de 2020.',
        '- Importar `parcelas-estudio.geojson` al SIG; no se modificaron proyectos ni se publicaron datos.',
        '- Seleccionar series ópticas y radar por parcela manteniendo máscaras y sin inventar límites.', '',
        '## Qué no prueba', '',
        '- No verifica propiedad, uso del resto de la finca ni fecha de conversión de bosque.',
        '- Los años del inventario son plantación de individuos, no prueba de tala o cobertura previa.',
        '- Son parcelas ~0,4–0,53 ha: pocos píxeles Sentinel-1/2 y mezcla en bordes; el dron sirve como evidencia complementaria.',
        '- Las imágenes de dron no se descargaron ni revisaron todavía. La fecha anual 2020 no da por sí sola un día exacto.', '',
        '## Segunda referencia con historia de establecimiento', '',
        'El estudio El Deseo/Yaguachi documenta 15 sistemas agroforestales, 12 establecidos en 2016 y 3 en 2017, total 11,8873 ha.',
        'https://centrosuragraria.com/index.php/revista/article/download/209/423?inline=1',
        'Aporta historia publicada, pero no se han recuperado sus polígonos digitales. No trasladar esa historia a los seis sitios ReforesTree.', '',
        'Siguiente validación: recuperar recortes de dron corregidos con fecha documentada y series antes/después; identificar cambios independientes, incluyendo controles estables.']
    (folder/'FINCAS-DOCUMENTADAS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'plots':len(features),'areas_ha':[round(p['area_geodesic_ha'],4) for p in records],
                      'inventory_sites':[p['matched_inventory_site'] for p in records]}))


if __name__=='__main__': main()
