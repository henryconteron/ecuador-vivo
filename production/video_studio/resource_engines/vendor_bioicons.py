"""Curate a tiny CC0 pack; never clone the icon collection or execute SVG code."""
import hashlib,json,re,urllib.request,urllib.parse,xml.etree.ElementTree as ET
from pathlib import Path

DEST=Path(__file__).parent/'artwork'
API='https://api.github.com/repos/duerrsimon/bioicons/git/trees/main?recursive=1'
def fetch(url):
    request=urllib.request.Request(url,headers={'User-Agent':'EcuadorVivo-scientific-resources'})
    with urllib.request.urlopen(request,timeout=30) as response:return response.read(4_000_000)

def safe_svg(content):
    if len(content)>400_000 or b'<!ENTITY' in content.upper():raise ValueError('SVG demasiado grande o con entidades.')
    tree=ET.fromstring(content)
    forbidden={'script','foreignObject','iframe','image','audio','video','use','style','animate','set'}
    for element in tree.iter():
        if element.tag.split('}')[-1] in forbidden:raise ValueError('SVG con contenido no permitido.')
        for key,value in element.attrib.items():
            low=value.lower().replace(' ','')
            refs=re.findall(r'url\((.*?)\)',low)
            if key.split('}')[-1].lower().startswith('on') or key.split('}')[-1] in ('href','src') or 'javascript:' in low or '@import' in low or '\\' in low or any(not re.fullmatch(r"['\"]?#[\w.-]+['\"]?",ref) for ref in refs):
                raise ValueError('Referencia SVG no permitida.')
    return content

def main():
    tree=json.loads(fetch(API));commit=tree['sha'];entries=[]
    wanted=[('Animals','Alpaca.svg','Alpaca'),('Animals','avocet.svg','Avoceta'),('Animals','Mouse.svg','Ratón'),
            ('Plants_Algae',None,'Planta'),('Cell_types',None,'Célula'),('Chemistry',None,'Química')]
    for category,suffix,label in wanted:
        choices=[i for i in tree['tree'] if i['path'].startswith('static/icons/cc-0/'+category+'/') and i['path'].endswith(suffix or '.svg') and 1000<i.get('size',0)<120_000]
        for item in choices:
            path=item['path'];url='https://raw.githubusercontent.com/duerrsimon/bioicons/'+commit+'/'+urllib.parse.quote(path)
            try:content=safe_svg(fetch(url))
            except ValueError:continue
            identifier='bioicons.'+hashlib.sha256(path.encode()).hexdigest()[:12]
            DEST.mkdir(exist_ok=True);(DEST/(identifier+'.svg')).write_bytes(content)
            entries.append({'id':identifier,'name':label if suffix else Path(path).stem.replace('_',' '),
                'category':'Biología' if category!='Chemistry' else 'Química','type':'asset','author':path.split('/')[-2],
                'license':'CC0','source':'https://github.com/duerrsimon/bioicons/blob/'+commit+'/'+path,
                'original':identifier+'.svg','image':identifier+'.png','sha256':hashlib.sha256(content).hexdigest(),
                'summary':'Ilustración conceptual de Bioicons · no prueba presencia de una especie en Ecuador.'})
            break
    (DEST/'catalog.json').write_text(json.dumps({'version':1,'commit':commit,'items':entries},ensure_ascii=False,indent=2),encoding='utf8')
    (DEST/'CC0.txt').write_bytes(fetch('https://raw.githubusercontent.com/duerrsimon/bioicons/'+commit+'/static/icons/cc-0/LICENSE'))
    print('Ilustraciones CC0 seleccionadas:',len(entries))

if __name__=='__main__':main()
