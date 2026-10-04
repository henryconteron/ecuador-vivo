"""Portrait satellite river story: retains v6 identity, corrects v8 opening.

USGS Landsat pair is an editorial comparison, not newly registered geospatial data.
Original qualitative animations are explicitly distinguished from measured imagery.
Previous renders and the atlas remain untouched.
"""
import argparse
import asyncio
from bisect import bisect_right
from contextlib import contextmanager
from hashlib import sha256
import json
import math
from pathlib import Path
import shutil

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw

import reel_river_motion as motion
import reel_rivers_documentary as previous
from reel_territory import INK, PAPER, MUTED, GOLD, LIME, LINE, text, paragraph

ROOT = Path(__file__).resolve().parent
FOLDER = ROOT / 'artifacts/rios_doce_v9'
EVIDENCE = ROOT / 'artifacts/rios_historia_v6'
W, H, FPS = 1080, 1920, 30
VOICE = previous.VOICE
OUTPUT = FOLDER / 'rio_doce_desde_el_espacio_v9.mp4'
PAGE = 'https://eros.usgs.gov/media-gallery/image-of-the-week/brazilian-mining-disaster-doce-river'
PAPER_URL = 'https://doi.org/10.1016/j.isprsjprs.2018.02.013'
# Exact pixel crops of the two photographic panels, no fabricated coastline/detail.
# Coordinates were inspected on the original 5288 x 3000 USGS publication.
CROPS = {'before': (148,374,2548,1724), 'after': (2738,374,5138,1724)}
DATES = {'before': '11 SEP 2015', 'after': '30 NOV 2015'}

def old(sid, kind=None):
    row = next(b for b in previous.BEATS if b[0] == sid)
    return (row[0], row[1], row[2], kind or row[3], row[4])

BEATS = [
    ('docepair', 'Este es el río Doce, en Brasil, donde desemboca en el Atlántico. Mira las dos imágenes: septiembre de dos mil quince, arriba; noviembre, abajo. Las tomó Landsat ocho desde el espacio. Fíjate en esa mancha junto a la costa. ¿Qué le pasó al agua?', 'El mismo río. ¿Qué cambió?', 'doce', 'pair'),
    ('doceevent', 'El cinco de noviembre se rompió Fundão, una presa que contenía residuos de una mina de hierro. El material llegó a la cuenca y después a la desembocadura. Es un impacto humano documentado. Pero estas dos imágenes, por sí solas, no nos cuentan todo lo que ocurrió.', 'Una presa se rompió aguas arriba.', 'doce', 'event'),
    ('docestudy', 'Rudorff y sus colegas estudiaron los cambios de turbidez con imágenes de Landsat y MODIS. O sea, investigaron desde el espacio cuánto había cambiado la claridad del agua. Pero, espera: ¿cómo puede un instrumento allá arriba notar eso? ¿Qué está viendo que nosotros no vemos?', '¿Cómo lo investigaron desde el espacio?', 'doce', 'study'),
    old('sensor', 'sensor'),
    old('bands', 'sensor'),
    ('sedimentlight', 'Las partículas suspendidas cambian la luz que sale del agua y llega al sensor. En el estudio del Doce, el método usaba rojo e infrarrojo cercano para estimar turbidez. No era simplemente mirar una mancha marrón. Y combinaron esa señal con mediciones de caudal y turbidez en el río.', 'La pista está en la luz.', 'sediment', 'rednir'),
    ('twoquestions', 'Ahora viene una diferencia que parece pequeña, pero cambia todo. Una pregunta es: ¿dónde hay agua? Otra es: ¿qué está transportando? Para seguir sedimentos necesitamos un método para esa señal. Para explorar las orillas y la superficie cubierta por agua, podemos empezar con un índice de agua. No son la misma herramienta.', 'Dos preguntas. Dos herramientas.', 'questions', 'separate'),
    old('response', 'swir'),
    old('contrast', 'formula'),
    old('index', 'formula'),
    old('color', 'indexmap'),
    old('rulezero', 'thresholdzero'),
    old('rulemove', 'threshold'),
    old('validate', 'threshold'),
    old('pixel', 'pixel'),
    old('zoom', 'pixel'),
    ('levelv9', 'Y antes de culpar a alguien por un mapa con menos azul, mira este ejemplo. Bajamos el nivel y aparece un banco de grava. El lecho sigue ahí. Desde arriba vemos menos superficie cubierta, pero eso no nos da directamente el caudal: cuánto volumen pasa por segundo. Necesitamos la sección del río y la velocidad.', 'Menos superficie, ¿menos caudal?', 'level', 'lower'),
    old('first', 'first'),
    old('middle', 'middle'),
    old('comparelimits', 'middlefixed'),
    old('recent', 'recent'),
    old('time', 'timeline'),
    old('pools', 'pools'),
    old('cloud', 'cloud'),
    old('causality', 'cause'),
    old('chemistry', 'chemistry'),
    ('docecallback', 'Volvamos al Doce. Allí la rotura está documentada, y el estudio cruzó satélites con mediciones del río. Así separó el impacto de otras fuentes naturales de sedimento. No trasladamos esa conclusión al Jatunyacu. Compartimos las herramientas para preguntar, no un culpable elegido de antemano.', 'Del cambio visible a una explicación.', 'doce', 'callback'),
    old('answer', 'endingmap'),
    ('creditsv9', 'Las dos imágenes del Doce son de Landsat, publicadas por el Servicio Geológico de Estados Unidos. La comparación de Ecuador usa observaciones reales de Sentinel dos. Los esquemas son didácticos, no reconstrucciones de estos lugares. Las fuentes, fechas y límites acompañan el video. Esta narración es sintética.', 'Fuentes, fechas y límites.', 'credits', 'sources'),
]

def prepare():
    m = motion.load_evidence(EVIDENCE)
    source = FOLDER / 'sources/Brazil-Dam2.jpg'
    with Image.open(source) as im:
        if im.size != (5288,3000):
            raise ValueError('USGS source dimensions changed; review crops')
    report = dict(version=9, satellite_only=True,
        case='Doce river mouth after the November 2015 Fundao tailings-dam failure',
        images=[dict(file='sources/Brazil-Dam2.jpg', sha256=sha256(source.read_bytes()).hexdigest(),
            dimensions=[5288,3000], page=PAGE,
            asset='https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/co/media_gallery/iow/Brazil-Dam2.jpg.zip',
            credit='USGS EROS / Landsat 8; original publication also credits NASA',
            dates=['2015-09-11','2015-11-30'], crops=CROPS,
            rights='USGS-produced information: US public domain; no third-party copyright marking on this publication',
            rights_page='https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits')],
        study=dict(doi=PAPER_URL, authors='Rudorff, N.; Rudorff, C. M.; Kampel, M.; Ortiz, G. (2018)',
            consulted='Published abstract on NASA MODIS, not the full paywalled paper',
            abstract='https://modis.gsfc.nasa.gov/sci_team/pubs/abstract_new.php?id=27170',
            method='Red/NIR semi-analytical turbidity retrieval; Landsat and MODIS-Aqua plus in-situ measurements',
            limitation='This video does not reproduce the published turbidity retrieval. MNDWI demonstration answers a different question.'),
        local_manifest_sha256=sha256((EVIDENCE/'manifest.json').read_bytes()).hexdigest(),
        local_evidence_folder=str(EVIDENCE), local_region=m['regions']['jatunyacu_detail'],
        local_files={n:sha256((EVIDENCE/n).read_bytes()).hexdigest() for n in
            ['threshold_values.npz','motion_evidence.json']+[f'jatunyacu_detail_{y}_{mode}.png' for y in (2019,2024,2026) for mode in ('rgb','mndwi')]},
        processing='USGS panels cropped and downsampled equally; no registration, morphing, computed plume area, new detail or colour enhancement. Ecuador display nearest-neighbour.',
        diagrams='Original qualitative explanatory animation; no measured spectra, turbidity or discharge.',
        scientific_claims='Doce impact documented; no mining/drying attribution for Ecuador from these three dates.',
        previous_renders={str(p):sha256(p.read_bytes()).hexdigest() for p in
            [EVIDENCE/'rios_mirar_no_es_medir_v6_vista_previa.mp4', previous.FOLDER/'que_le_paso_al_rio_v8.mp4']},
        publication='Local review version only; not published')
    (FOLDER/'sources_manifest.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    (FOLDER/'narration.json').write_text(json.dumps({b[0]:b[1] for b in BEATS},indent=2,ensure_ascii=False),encoding='utf-8')
    (FOLDER/'GUION_PARA_GRABAR.md').write_text('# Un río visto desde el espacio\n\nGuion original v9.\n\n'+
        '\n\n'.join('## '+b[2]+'\n\n'+b[1] for b in BEATS),encoding='utf-8')
    # Reuse only recordings whose text and voice are identical; no new request needed.
    for sid, speech, *_ in BEATS:
        p = previous.FOLDER/f'times_{sid}.json'
        if p.exists() and json.loads(p.read_text(encoding='utf-8'))['text_sha256'] == sha256((VOICE+'-3%'+speech).encode()).hexdigest():
            for name in (f'times_{sid}.json',f'voz_{sid}.mp3',f'voz_{sid}.wav'):
                shutil.copy2(previous.FOLDER/name,FOLDER/name)

@contextmanager
def bind_audio():
    # Reuse voice/timing utilities without editing the previous renderer or artifacts.
    saved = previous.FOLDER, previous.BEATS
    previous.FOLDER, previous.BEATS = FOLDER, BEATS
    try:
        yield
    finally:
        previous.FOLDER, previous.BEATS = saved

async def voices():
    with bind_audio():
        await previous.voices()

def plan():
    with bind_audio():
        return previous.plan()

class Design(motion.Design):
    def __init__(self):
        super().__init__(EVIDENCE,motion.load_evidence(EVIDENCE))
        with Image.open(FOLDER/'sources/Brazil-Dam2.jpg') as im:
            self.dope = {k:im.crop(box).convert('RGB').resize((960,540),Image.Resampling.LANCZOS) for k,box in CROPS.items()}
        with Image.open(EVIDENCE/'jatunyacu_detail_2024_rgb.png') as im:
            self.native=im.convert('RGBA').copy()
        ys,xs=np.where(motion.candidates(self.values,self.common,.2))
        j=np.argmin((xs-self.native.width/2)**2+(ys-self.native.height/2)**2)
        self.zoom_center=(int(xs[j]),int(ys[j]))

    def shell_title(self,title):
        im = Image.new('RGB',(W,H),INK)
        d = ImageDraw.Draw(im)
        text(d,(60,80),'ECUADOR VIVO / MIRAR NO ES MEDIR',24,LIME,width=960)
        # Original portrait type hierarchy and palette, not v8 landscape layout.
        paragraph(d,(60,135),title,49,960,PAPER,leading=1.13)
        text(d,(60,1750),'Henry Conteron · narración sintética · versión de revisión',22,MUTED,width=960)
        return im

    def pair(self,im,t,variant):
        # Both actual observations stay present throughout the Doce opening.
        for tag,y in (('before',285),('after',865)):
            im.paste(self.dope[tag],(60,y))
            d=ImageDraw.Draw(im)
            self.label(d,80,y+15,DATES[tag],GOLD,28)
            self.label(d,750,y+15,'LANDSAT 8',PAPER,23,width=245)
        d=ImageDraw.Draw(im)
        text(d,(60,835),'ANTES · desembocadura del Doce, Brasil',23,MUTED,width=960)
        if variant=='event':
            self.label(d,95,1160,'05 NOV · ROTURA DE FUNDÃO',PAPER,27,width=850)
        elif variant in ('study','callback'):
            self.label(d,95,1160,'RUDORFF ET AL. (2018) · SATÉLITE + CAMPO',PAPER,24,width=860)
        else:
            # Attention guide on the actual after panel, not an invented plume boundary.
            r=40+12*math.sin(t*math.pi*2)
            d.ellipse((60+565-r,865+280-r,60+565+r,865+280+r),outline=GOLD,width=3)
        text(d,(60,1810),'USGS EROS / Landsat · recorte editorial · no medida de área',22,MUTED,width=960)

    def swir(self,im,t):
        d=ImageDraw.Draw(im)
        text(d,(100,340),'AGUA',40,motion.BLUE,width=800)
        d.rounded_rectangle((145,925,935,1100),20,fill='#216b82')
        motion.arrow(d,(365,520),(365,900),GOLD)
        length=190*motion.stage(t,.2,.6)
        motion.arrow(d,(650,925),(650,925-length),motion.CORAL)
        for i in range(8):
            y=535+((t*1.8+i/8)%1)*340
            d.ellipse((358,y,370,y+12),fill=GOLD)
        self.label(d,480,620,'POCO SWIR',motion.CORAL,36,width=460)
        text(d,(110,1190),'La onda corta ayuda a buscar agua.',34,PAPER,width=860)
        self.diagram_note(d,'Respuesta cualitativa, no espectro medido · Xu (2006). Verde / onda corta.')

    def sediment(self,im,t):
        d=ImageDraw.Draw(im)
        for x,label,col,n in ((105,'AGUA MÁS CLARA',motion.BLUE,4),(565,'CON PARTÍCULAS',GOLD,42)):
            d.rounded_rectangle((x,830,x+410,1100),15,fill='#216b82')
            for i in range(n):
                px=x+30+((i*.618+t*.55)%1)*345
                py=890+((i*.37+t*.2)%1)*175
                d.ellipse((px,py,px+7,py+7),fill=col)
            motion.arrow(d,(x+90,480),(x+90,815),PAPER)
            length=(90 if n==4 else 240)*motion.stage(t,.1,.5)
            motion.arrow(d,(x+290,820),(x+290,820-length),motion.CORAL)
            text(d,(x,1140),label,26,col,width=410)
        text(d,(115,390),'MISMA LUZ · RESPUESTA DIFERENTE',32,PAPER,width=860)
        self.label(d,110,660,'ROJO / INFRARROJO CERCANO',GOLD,29,width=855)
        self.diagram_note(d,'Esquema cualitativo · sin valores de turbidez ni espectro medido. Rudorff et al. (2018).')

    def questions(self,im,t):
        d=ImageDraw.Draw(im)
        for i,(q,tool,col) in enumerate((('¿DÓNDE HAY AGUA?','Índice de agua · MNDWI',LIME),('¿QUÉ TRANSPORTA?','Método de turbidez validado',GOLD))):
            y=430+i*450
            d.line((90,y,90,y+240),fill=col,width=6)
            text(d,(135,y),q,39,col,width=850)
            paragraph(d,(135,y+100),tool,34,840,PAPER)
            motion.arrow(d,(140,y+215),(140+660*motion.stage(t,i*.2,i*.2+.45),y+215),col,3)
        self.diagram_note(d,'Doce: rojo / NIR · demostración de Ecuador: verde / SWIR. No son el mismo método.')

    def sensor(self,im,t):
        self.light(im,t)
        # The existing diagram explicitly says NIR; this chapter discusses NIR.

    def timeline(self,im,t,cloud=False):
        d=ImageDraw.Draw(im)
        d.line((130,870,940,870),fill=LINE,width=5)
        for i in range(9):
            x=150+i*95
            d.ellipse((x-10,860,x+10,880),fill=GOLD if i not in (2,6) else MUTED)
            if i in (2,6):text(d,(x-12,750),'?',38,MUTED,width=80)
        x=130+810*motion.stage(t,.05,.95)
        d.line((x,815,x,930),fill=LIME,width=4)
        paragraph(d,(130,470),'Lluvia + niveles + observaciones útiles',44,820,PAPER)
        if cloud:
            self.label(d,140,1000,'SIN DATOS ≠ SECO',GOLD,36,width=820)
        else:
            self.label(d,140,1000,'DOS FOTOS NO SON UNA TENDENCIA',GOLD,27,width=820)
        self.diagram_note(d,'Línea de tiempo conceptual · no observaciones adicionales ni caudales medidos.')

    def zoom(self,im,t):
        # Zoom into existing 20 m samples, never interpolate or generate detail.
        side=round(110-80*motion.stage(t,.1,.8))
        cx,cy=self.zoom_center
        x=max(0,min(self.native.width-side,cx-side//2))
        y=max(0,min(self.native.height-side,cy-side//2))
        tile=self.native.crop((x,y,x+side,y+side)).resize((960,960),Image.Resampling.NEAREST)
        base=Image.new('RGB',(960,960),'#263832')
        base.paste(tile,mask=tile.getchannel('A'))
        im.paste(base,(60,285))
        d=ImageDraw.Draw(im)
        self.label(d,80,315,'08 AGO 2024 · MUESTRAS REALES',PAPER,28)
        text(d,(60,1270),'Cada celda sigue representando 20 m de lado.',28,LIME,width=960)
        text(d,(60,1320),'Ampliación sin suavizado · no aparece detalle nuevo.',25,MUTED,width=960)

    def credits(self,im):
        d=ImageDraw.Draw(im)
        for i,(label,value) in enumerate((
            ('DOCE / IMÁGENES','USGS EROS · Landsat 8 · 11 SEP / 30 NOV 2015'),
            ('DOCE / INVESTIGACIÓN','Rudorff et al. (2018) · doi:10.1016/j.isprsjprs.2018.02.013'),
            ('ECUADOR / OBSERVACIONES','Copernicus Sentinel-2 · 2019 / 2024 / 2026'),
            ('ÍNDICE DE AGUA','Xu (2006) · verde / SWIR · umbral no calibrado'),
            ('ANIMACIONES','Esquemas cualitativos · no reconstrucciones de los casos'))):
            y=340+i*200
            text(d,(90,y),label,27,GOLD,width=900)
            paragraph(d,(90,y+50),value,28,900,PAPER)
        text(d,(60,1810),'Guion y bibliografía completos acompañan el archivo.',22,MUTED,width=960)

    def render(self,beat,t,caption='',progress=0):
        sid,speech,title,kind,variant=beat
        im=self.shell_title(title)
        if kind=='doce':self.pair(im,t,variant)
        elif kind=='sediment':self.sediment(im,t)
        elif kind=='questions':self.questions(im,t)
        elif kind=='sensor':self.sensor(im,t)
        elif kind=='swir':self.swir(im,t)
        elif kind=='formula':self.formula(im,1 if sid=='index' else t)
        elif kind=='indexmap':self.real_map(im,2024,mode='mndwi')
        elif kind in ('threshold','thresholdzero'):self.threshold(im,1 if sid=='validate' else t if kind=='threshold' else 0)
        elif kind=='pixel':self.zoom(im,t) if sid=='zoom' else self.mixed_pixel(im,t)
        elif kind=='level':self.river_level(im,t)
        elif kind=='first':self.real_map(im,2019)
        elif kind=='middle':self.real_map(im,2019,2024,.88-.76*motion.stage(t,.16,.75))
        elif kind in ('middlefixed','endingmap'):self.real_map(im,2024)
        elif kind=='recent':self.real_map(im,2026)
        elif kind=='timeline':self.timeline(im,t)
        elif kind=='cloud':self.timeline(im,t,True)
        elif kind=='pools':self.connection(im,t*.65)
        elif kind=='cause':self.hypotheses(im,t)
        elif kind=='chemistry':
            self.hypotheses(im,t)
            self.label(ImageDraw.Draw(im),110,1130,'MNDWI ≠ MERCURIO',GOLD,33,width=850)
        elif kind=='credits':self.credits(im)
        else:raise ValueError(kind)
        d=ImageDraw.Draw(im)
        if kind=='indexmap':
            # Do not inherit the RGB legend from the old map renderer.
            d.rectangle((60,1260,1020,1360),fill=INK)
            text(d,(60,1270),'MNDWI real · colores de visualización, no RGB',25,LIME,width=960)
            text(d,(60,1310),'Trama: sin datos · índice calculado antes de colorear',24,MUTED,width=960)
        d.rounded_rectangle((60,1440,1020,1680),20,fill='#173c35',outline=LINE,width=2)
        bottom=paragraph(d,(92,1460),caption,34,885,PAPER,leading=1.22)
        if bottom>1666:raise ValueError('Caption overflows')
        d.line((60,1710,60+round(960*progress),1710),fill=LIME,width=4)
        if kind not in ('doce','credits'):
            text(d,(60,1810),'Imágenes reales + esquemas didácticos · fuentes en el guion',22,MUTED,width=960)
        return im

def storyboard():
    design=Design()
    sheet=Image.new('RGB',(1350,math.ceil(len(BEATS)/5)*510),INK)
    for i,beat in enumerate(BEATS):
        im=design.render(beat,.55)
        im.save(FOLDER/f'qa_{beat[0]}.jpg',quality=92)
        sheet.paste(im.resize((270,480),Image.Resampling.LANCZOS),((i%5)*270,(i//5)*510))
        ImageDraw.Draw(sheet).text(((i%5)*270+10,(i//5)*510+484),beat[0],fill=PAPER)
    sheet.save(FOLDER/'storyboard.jpg',quality=92)
    print('Storyboard ready',flush=True)

def export():
    from reel_editorial import mux_audio
    scenes=plan()
    with bind_audio():
        previous.write_subtitles(scenes)
    design=Design()
    total=sum(s['frames'] for s in scenes)
    visual=FOLDER/'visual_sin_audio.mp4'
    writer=imageio_ffmpeg.write_frames(str(visual),(W,H),fps=FPS,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',quality=7,macro_block_size=2,ffmpeg_log_level='error',output_params=['-preset','veryfast','-threads','2','-movflags','+faststart'])
    writer.send(None)
    try:
        for beat,scene in zip(BEATS,scenes):
            starts=[c['start'] for c in scene['cues']]
            for frame in range(scene['frames']):
                second=frame/FPS
                j=bisect_right(starts,second)-1
                cue=scene['cues'][j] if j>=0 else None
                cap=cue['text'] if cue and second<cue['end']+.12 else ''
                im=design.render(beat,frame/max(1,scene['frames']-1),cap,(scene['start_frame']+frame)/total)
                writer.send(im.tobytes())
            print('Rendered: '+beat[0],flush=True)
    finally:writer.close()
    mux_audio(FOLDER,visual,OUTPUT,scenes)
    metadata=dict(version=9,width=W,height=H,fps=FPS,frames=total,duration_seconds=total/FPS,
        video_sha256=sha256(OUTPUT.read_bytes()).hexdigest(),scenes=scenes,
        script_sha256=sha256((FOLDER/'narration.json').read_bytes()).hexdigest(),
        source_manifest_sha256=sha256((FOLDER/'sources_manifest.json').read_bytes()).hexdigest(),
        renderer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        audio='Synthetic es-EC-LuisNeural; no paid API, no impersonation',
        status='Local review version; verify encoded video before publication')
    (FOLDER/'video_metadata.json').write_text(json.dumps(metadata,indent=2,ensure_ascii=False),encoding='utf-8')
    print(f'Rendered {total/FPS:.2f} seconds',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare','voices','storyboard','export'])
    action=parser.parse_args().action
    if action=='prepare':prepare()
    elif action=='voices':asyncio.run(voices())
    elif action=='storyboard':storyboard()
    elif action=='export':export()
