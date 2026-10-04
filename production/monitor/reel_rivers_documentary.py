"""Original landscape river documentary. Real photographs, audited data, explanatory motion.

Never edits previous episodes or the atlas. No frame interpolation of river imagery.
Voice is explicitly synthetic; uses cached speech and word timings, no paid API.
"""
import argparse
import asyncio
from bisect import bisect_right
from functools import lru_cache
from hashlib import sha256
import html
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import wave

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FOLDER = ROOT / "artifacts/rios_documental_v8"
EVIDENCE = ROOT / "artifacts/rios_historia_v6"
W, H, FPS = 1920, 1080, 30
VOICE = "es-EC-LuisNeural"
BG, PAPER, DIM = "#101c25", "#f5eee0", "#adc0c8"
BLUE, GOLD, GREEN, CORAL = "#48c5e4", "#e8bf75", "#80c995", "#f2957d"
SOURCES = [
    {"file": "colorado_2014-03-20.jpg", "date": "2014-03-20", "title": "Colorado River before the pulse flow", "page": "https://www.usgs.gov/media/images/colorado-river-pulse-flow", "asset": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/IMGP0444.JPG", "credit": "USGS / Communications and Publishing", "rights": "Public Domain"},
    {"file": "colorado_2014-03-29.jpg", "date": "2014-03-29", "title": "Colorado River during the pulse flow", "page": "https://www.usgs.gov/media/images/colorado-riverduring-pulse-flow", "asset": "https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/IMGP0492.JPG", "credit": "USGS / Communications and Publishing", "rights": "Public Domain"},
]

# Each beat has its own recorded duration: animation is not forced into old timings.
# Dates on real photographs are never swapped to suggest a different chronology.
BEATS = [
    ("dryphoto", "Mira este puente. Debajo no ves agua, sino un cauce seco. Cuesta creer que esto sea parte del Colorado, el río que atraviesa el Gran Cañón. Ahora guarda esa imagen un segundo.", "¿Dónde está el río?", "photo", "dry"),
    ("wetphoto", "Esta foto es del mismo lugar, nueve días después. El agua volvió. No cambiamos de río: cambiamos de fecha. Veinte de marzo de dos mil catorce; veintinueve de marzo de dos mil catorce. ¿Qué pasó entre las dos?", "Nueve días después", "photo", "wet"),
    ("reveal", "Hubo una liberación controlada de agua hacia el delta, dentro de un acuerdo entre Estados Unidos y México. No fue una recuperación permanente de todo el río. Fue un pulso. Y las fotos no explican eso solas: conocemos la intervención por su documentación.", "Una intervención documentada", "dam", "release"),
    ("invitation", "Imagínate que un amigo te manda dos fotos y te dice: mira lo que le hicieron al río. Si conoces ese sitio, pega distinto. Piensas en la gente, en el paisaje, en el agua. Pero antes de compartirlas, ¿qué tendríamos que comprobar?", "Dos fotos. ¿Toda la historia?", "pair", "message"),
    ("promise", "Vamos a mirarlas juntos. Podemos encontrar cambios reales. También voy a cambiar un mapa sin sacar una sola gota del río. Parece un truco, y lo es: uno que nos ayuda a entender cómo miramos la Tierra desde el espacio.", "¿Qué le pasó al río?", "map", "promise"),
    ("stones", "Primero olvidemos el satélite. Imagina que dejas los zapatos sobre unas piedras junto al agua. Otro día vuelves, y las piedras están cubiertas. Siguen ahí. Lo que subió fue el nivel. Desde arriba, el paisaje se ve distinto aunque el lecho no se haya movido.", "Tus piedras siguen ahí", "section", "level"),
    ("bed", "Pero el río también mueve el terreno: transporta arena y grava, erosiona aquí y deposita allá. Un brazo puede cambiar de lugar. Entonces tenemos dos historias distintas: cambió el nivel sobre el lecho, o cambió el propio lecho. A veces ocurren las dos.", "Nivel y cauce no son lo mismo", "river", "erosion"),
    ("pool", "Y cuando decimos hay menos agua, ¿qué queremos decir? Piensa en una piscina y en una manguera. En la piscina ves mucha superficie cubierta. En la manguera, poca. Pero por la manguera está pasando agua de un sitio a otro.", "Agua presente / agua que pasa", "flow", "analogy"),
    ("discharge", "No son modelos de un río. Sirven para separar dos ideas: la superficie que vemos mojada y el volumen de agua que atraviesa una sección por segundo. A lo segundo lo llamamos caudal. Para medirlo necesitamos la sección y la velocidad, no solo una foto desde arriba.", "Caudal: volumen por segundo", "flow", "section"),
    ("sensor", "Ahora sí, subamos al satélite. Tú reconoces un río por su forma y sus orillas. El sensor no lo reconoce así. Registra la luz que llega desde el terreno. No sabe que te bañabas allí: tiene mediciones, no recuerdos.", "El sensor registra luz", "light", "sensor"),
    ("bands", "Y no registra solo los colores que vemos. También ciertas bandas de infrarrojo. Una banda es una parte de esa luz que mide por separado. El verde en una; una parte del infrarrojo en otra. Nuestros ojos no ven esa segunda señal, pero el instrumento sí.", "Hay luz que no podemos ver", "light", "bands"),
    ("response", "El agua, el suelo y la vegetación no devuelven la luz de la misma manera. El agua suele responder poco en el infrarrojo de onda corta. Podemos aprovechar esa diferencia. No le enseñamos al satélite qué es un río: encontramos una pista en la luz.", "Una pista, no un reconocimiento", "light", "response"),
    ("contrast", "Para este mapa comparamos verde con infrarrojo de onda corta. Restamos sus valores. Después dividimos esa diferencia por su suma. Así obtenemos un contraste para cada celda. La fórmula parece intimidante, pero está haciendo esa comparación, una celda a la vez.", "Comparar dos señales", "formula", "build"),
    ("index", "Se llama índice de diferencia normalizada de agua modificado: M N D W I. No necesitas memorizar el nombre. Recuerda la pregunta: ¿cómo se compara el verde con ese infrarrojo? No estamos contando gotas, ni midiendo profundidad, ni calculando litros por segundo.", "MNDWI ≠ litros", "formula", "meaning"),
    ("color", "Tampoco lo calculamos con el azul que ves en la pantalla. Primero usamos los valores de las bandas. Después elegimos colores para mostrar el resultado. Ese azul tan convincente no venía pintado en el río. Lo pusimos nosotros.", "Los valores vienen antes del color", "map", "index"),
    ("rulezero", "Mira esta observación real del ocho de agosto de dos mil veinticuatro. Dejamos fija la fecha, la cuadrícula y los datos. Primero pintamos de azul las celdas cuyo índice supera cero. Son candidatas a agua. Ahora observa lo que pasa al mover la regla.", "Mismo día. Mismos datos.", "threshold", "zero"),
    ("rulemove", "En lugar de superar cero, pedimos que supere cero coma dos. Algunas celdas dejan de entrar. Hay menos azul, pero no sacamos agua del río. Lo que cambió fue nuestra selección. Acabamos de modificar el mapa sin modificar la observación.", "Menos azul. No agua extraída.", "threshold", "move"),
    ("validate", "Estos valores demuestran el efecto; no son umbrales calibrados para este lugar. ¿Cuál sería mejor? Tendríamos que contrastarlo con referencias independientes del terreno. Elegir el azul más bonito no es comprobar que acertamos.", "Bonito no significa validado", "threshold", "validate"),
    ("three", "Ya separamos tres cosas que podían parecer una sola: el nivel, las formas del cauce y la regla que produce el mapa. Esto no vuelve inútil al satélite. Al contrario: ahora sabemos qué preguntarle y qué comprobar por otro camino.", "Tres cambios distintos", "three", "summary"),
    ("pixel", "Todavía queda una frustración: acercas la orilla y aparecen cuadrados. En nuestra comparación, cada celda representa veinte metros de lado. Dentro puede haber un pedazo de agua, piedras y vegetación. Una sola medición puede mezclar sus respuestas.", "Una celda. Varias superficies.", "pixel", "mix"),
    ("zoom", "Después la mostramos con un color. Pero ese color no nos dice exactamente dónde termina el agua dentro del cuadrado. Si acercas más, el cuadrado ocupa más pantalla. La observación sigue siendo la misma. El zoom agranda lo que tenemos; no fabrica lo que faltó medir.", "El zoom no crea una observación", "pixel", "zoom"),
    ("first", "Volvamos al paisaje. Este es un tramo del Jatunyacu, en Ecuador, el once de julio de dos mil diecinueve. No es un río intacto ni el promedio de un año: es una observación de ese día. Guardemos el encuadre, la escala y el ajuste de color.", "11 JUL 2019 / Jatunyacu", "map", "first"),
    ("middle", "Ocho de agosto de dos mil veinticuatro. Detente en los bancos claros y los brazos de agua. Movemos la cortina para comparar con dos mil diecinueve sin cambiar la geometría. Hay diferencias visibles que merecen investigarse.", "2019 / 2024: mira las formas", "map", "wipe"),
    ("comparelimits", "Lo que todavía no medimos es cuánto corresponde al nivel del agua y cuánto a cambios del cauce. Una franja clara no trae una explicación escrita encima. Podemos localizar la diferencia. Para interpretarla, hacen falta más pruebas.", "Encontrar el cambio es el inicio", "map", "middle"),
    ("recent", "Veintinueve de julio de dos mil veintiséis. Otro momento del mismo lugar. Sería tentador transformar suavemente una imagen en otra, como si tuviéramos una película. Quedaría espectacular. También inventaría los estados intermedios. Son tres visitas; entre ellas faltan muchísimas.", "29 JUL 2026 / una visita más", "map", "recent"),
    ("time", "¿Y si de verdad se está secando? Entonces hay que seguirlo en el tiempo, no elegir solamente las dos fotos que más contrastan. Buscar observaciones utilizables y compararlas con lluvia, niveles y mediciones de campo. Una tendencia necesita más que una pareja de imágenes.", "Necesitamos una historia en el tiempo", "timeline", "series"),
    ("pools", "Incluso encontrar agua puede no resolverlo. Pueden quedar pozas sin conexión superficial continua entre ellas. Ver una poza no demuestra que el río siga fluyendo por todo el tramo. Presencia de agua y continuidad del flujo son preguntas distintas.", "Hay agua. ¿Pero está conectada?", "river", "pools"),
    ("cloud", "Y si una nube lo tapa, ese día no tenemos respuesta. No podemos convertir lo que no vimos en no había agua. Un hueco en nuestros datos no es un hueco en el río. A veces la información más honesta del mapa es dejar un espacio sin clasificar.", "Sin datos no significa seco", "timeline", "cloud"),
    ("mining", "Queda la pregunta incómoda: ¿y la minería? La minería aluvial puede aumentar los sedimentos en ríos tropicales; hay estudios que lo documentan. Eso hace importante investigarla. Pero no demuestra, por sí solo, la causa de las diferencias que vimos en este tramo.", "Una relación documentada / otra pregunta local", "cause", "hypothesis"),
    ("causality", "Si aparece más sedimento, una crecida también podría movilizarlo. Si hubo una intervención, necesitamos saber dónde y cuándo. Comparar antes y después, aguas arriba y abajo, revisar lluvia y niveles, y tomar muestras. ¿Qué explicación encaja con todas esas pruebas, incluso las que nos hacen cambiar de idea?", "Conectar las pruebas", "cause", "evidence"),
    ("chemistry", "Y este índice no mide mercurio. Una señal óptica no reemplaza un análisis de agua. Ser cuidadosos no es quitarle importancia a un posible daño. Si lo hay, necesitamos poder describirlo y sostenerlo con pruebas.", "MNDWI no es un análisis químico", "cause", "chemistry"),
    ("callback", "Vuelve al puente del Colorado. Ahí sí tenemos una intervención documentada y unas fechas que la acompañan. En Ecuador, estas tres imágenes todavía no permiten afirmar que el río se secó ni atribuir el cambio a una actividad concreta. Son casos distintos, no una misma conclusión.", "Lo observado / lo documentado", "pair", "callback"),
    ("answer", "Entonces, ¿qué le diría a mi amigo? No diría no pasa nada. Tampoco ya encontramos al culpable. Le diría: mira estas diferencias; veamos cuáles se repiten en otras fechas y qué estaba pasando en el terreno. La preocupación nos dio una pregunta. Ahora tenemos cómo ponerla a prueba.", "Una respuesta mejor que un veredicto", "map", "answer"),
    ("ending", "Las fotos nos dieron un lugar donde empezar. La luz nos dio una herramienta. Y mover aquella regla nos mostró algo sobre nuestros propios mapas. No se trata solo de mirar un río que cambió de color. Se trata de empezar a entender qué le está pasando.", "No solo mirar. Entender.", "photo", "ending"),
    ("credits", "Las fechas, fuentes y limitaciones acompañan este video. Fotografías del Servicio Geológico de Estados Unidos; imágenes reales de Copernicus Sentinel dos. Los esquemas son explicativos, no reconstrucciones de estos ríos. La voz de este montaje es sintética.", "Fuentes y créditos", "credits", "sources"),
]


@lru_cache(maxsize=64)
def font(size, serif=False):
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / ("georgia.ttf" if serif else "arial.ttf")), size)


def txt(d, xy, value, size=40, fill=PAPER, serif=False, max_width=1760):
    if d.textlength(value, font=font(size, serif)) > max_width:
        raise ValueError("Text overflow: " + value)
    d.text(xy, value, font=font(size, serif), fill=fill)


def wrap(d, xy, value, size=40, width=650, fill=DIM):
    words, lines, current = value.split(), [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if current and d.textlength(trial, font=font(size)) > width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    for i, line in enumerate(lines):
        txt(d, (xy[0], xy[1]+i*round(size*1.3)), line, size, fill, max_width=width)
    return xy[1]+len(lines)*round(size*1.3)


def smooth(t):
    t = max(0., min(1., t))
    return t*t*(3-2*t)


def arrow(d, a, b, color=BLUE, width=5):
    d.line((a, b), fill=color, width=width)
    angle = math.atan2(b[1]-a[1], b[0]-a[0])
    d.polygon([b, (b[0]-20*math.cos(angle-.45), b[1]-20*math.sin(angle-.45)),
               (b[0]-20*math.cos(angle+.45), b[1]-20*math.sin(angle+.45))], fill=color)


def index_mask(values, common, threshold):
    return common & np.isfinite(values) & (values > threshold)


def prepare():
    from reel_river_motion import load_evidence
    m = load_evidence(EVIDENCE)  # Verifies the native crops, derived images, masks and arrays.
    FOLDER.mkdir(parents=True, exist_ok=True)
    rows = []
    for source in SOURCES:
        p = FOLDER/source["file"]
        if not p.exists():
            raise FileNotFoundError("Acquire the original USGS image: " + source["asset"])
        with Image.open(p) as im:
            if im.size != (4608, 2592):
                raise ValueError("USGS original image size changed")
        rows.append(dict(source, sha256=sha256(p.read_bytes()).hexdigest(), dimensions=[4608, 2592]))
    files = ["threshold_values.npz", "motion_evidence.json"] + [f"jatunyacu_detail_{y}_{mode}.png" for y in (2019, 2024, 2026) for mode in ("rgb", "mndwi")]
    for name in files:
        target = FOLDER/name
        if target.exists() and target.read_bytes() != (EVIDENCE/name).read_bytes():
            raise ValueError("Existing v8 evidence differs: " + name)
        shutil.copy2(EVIDENCE/name, target)
    report = dict(version=8, case="Colorado delta: dry to managed pulse; not whole-river permanent recovery", images=rows,
        local_evidence_folder=str(EVIDENCE), local_manifest_sha256=sha256((EVIDENCE/"manifest.json").read_bytes()).hexdigest(),
        local_files={name: sha256((FOLDER/name).read_bytes()).hexdigest() for name in files},
        local_region=m["regions"]["jatunyacu_detail"], dates=m["dates"],
        resampling="nearest for satellite display; USGS photographs downsampled/cropped only", 
        photo_comparison="same reported location, different camera framing; no image registration, morphing or spatial measurement",
        diagrams="Original qualitative teaching animations; no measured spectra, discharge, intervention geometry or site reconstruction",
        publication="not published; final voice and scientific review recommended")
    (FOLDER/"sources_manifest.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    script = {r[0]: r[1] for r in BEATS}
    (FOLDER/"narration.json").write_text(json.dumps(script, indent=2, ensure_ascii=False), encoding="utf-8")
    (FOLDER/"GUION_PARA_GRABAR.md").write_text("# ¿Qué le pasó al río?\n\nGuion original v8. Títulos no narrados.\n\n"+"\n\n".join("## "+r[2]+"\n\n"+r[1] for r in BEATS), encoding="utf-8")
    return report


async def voices():
    sys.path.insert(0, str(ROOT/"artifacts/river_voice_runtime"))
    import edge_tts
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    for sid, speech, *_ in BEATS:
        digest = sha256((VOICE+"-3%"+speech).encode()).hexdigest()
        mp3, wav, timing = FOLDER/f"voz_{sid}.mp3", FOLDER/f"voz_{sid}.wav", FOLDER/f"times_{sid}.json"
        if not (timing.exists() and mp3.exists() and wav.exists() and json.loads(timing.read_text())["text_sha256"] == digest):
            words = []
            # Stream only this original, non-sensitive narration to the no-key Edge speech service.
            with mp3.open("wb") as audio:
                talk = edge_tts.Communicate(speech, VOICE, rate="-3%", boundary="WordBoundary", receive_timeout=30)
                async for chunk in talk.stream():
                    if chunk["type"] == "audio":
                        audio.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        words.append(dict(start=chunk["offset"]/1e7, end=(chunk["offset"]+chunk["duration"])/1e7, text=html.unescape(chunk["text"])))
            subprocess.run([ff,"-v","error","-y","-i",str(mp3),"-ar","48000","-ac","1",str(wav)], check=True)
            with wave.open(str(wav)) as stream:
                seconds = stream.getnframes()/stream.getframerate()
            if not words or words[-1]["end"] > seconds+.3:
                raise ValueError("Speech timing or duration invalid: " + sid)
            timing.write_text(json.dumps(dict(voice=VOICE, rate="-3%", text_sha256=digest, seconds=seconds, words=words), indent=2, ensure_ascii=False), encoding="utf-8")
        print("Voice ready: " + sid, flush=True)


class Design:
    def __init__(self):
        self.bg = Image.new("RGB", (W,H))
        d=ImageDraw.Draw(self.bg)
        for y in range(H):
            f=y/H
            d.line((0,y,W,y),fill=(int(14+6*f),int(25+12*f),int(35+13*f)))
        self.photos={}
        for tag, source in zip(("dry","wet"),SOURCES):
            with Image.open(FOLDER/source["file"]) as im:
                self.photos[tag]=im.convert("RGB").resize((2040,1148), Image.Resampling.LANCZOS)
        self.pair_tiles={tag:photo.resize((855,481),Image.Resampling.LANCZOS) for tag,photo in self.photos.items()}
        self.maps={}
        for year in (2019,2024,2026):
            for mode in ("rgb","mndwi"):
                with Image.open(FOLDER/f"jatunyacu_detail_{year}_{mode}.png") as im:
                    base=Image.new("RGB",im.size,"#34434b")
                    mask=ImageDraw.Draw(base)
                    for y in range(0,im.height,4):
                        for x in range(0,im.width,4):
                            if (x//4+y//4)%2: mask.rectangle((x,y,x+3,y+3),fill="#46555b")
                    base.paste(im,mask=im.getchannel("A"))
                    self.maps[year,mode]=base.resize((850,850),Image.Resampling.NEAREST)
        with np.load(FOLDER/"threshold_values.npz",allow_pickle=False) as data:
            self.values,self.common=data["values"].copy(),data["common"].copy()
        self.rule_cache={}

    def photo(self, tag, t):
        # Slow camera crop on a fixed photograph; never an invented change in water.
        source=self.photos[tag]
        x=round(22+70*smooth(t)); y=round(20+34*smooth(t))
        return source.crop((x,y,x+W,y+H))

    def base(self,title,note):
        im=self.bg.copy();d=ImageDraw.Draw(im)
        txt(d,(80,48),title,58,serif=True)
        txt(d,(80,1040),note,22,DIM)
        return im

    def pair(self,t,variant):
        im=self.base("El mismo lugar. Otra fecha.","USGS · dominio público · encuadres distintos; no comparación métrica")
        for x, tag, date in [(80,"dry","20 MAR 2014"),(985,"wet","29 MAR 2014")]:
            p=self.pair_tiles[tag]
            im.paste(p,(x,220)); d=ImageDraw.Draw(im)
            txt(d,(x,745),date,40,GOLD)
            txt(d,(x,805),"Antes del pulso" if tag=="dry" else "Durante el pulso",32)
        d=ImageDraw.Draw(im)
        if variant=="message":
            txt(d,(80,140),"«Mira lo que le hicieron al río» · mensaje imaginario",30,DIM)
        else:
            txt(d,(80,140),"Intervención documentada ≠ causa deducida de dos fotografías",30,DIM)
        arrow(d,(892,480),(964,480),GOLD)
        return im

    def dam(self,t):
        im=self.base("Un pulso de agua hacia el delta", "USGS (2016) · mecanismo esquemático, no geometría real · efecto temporal")
        d=ImageDraw.Draw(im)
        d.polygon([(160,420),(780,420),(900,670),(260,670)],fill="#30546b")
        d.polygon([(720,345),(865,345),(865,765),(720,765)],fill="#93a0a2")
        d.polygon([(865,345),(920,380),(920,780),(865,765)],fill="#576d79")
        openness=smooth(t/.4)
        d.rectangle((770,610-120*openness,828,710-120*openness),fill=BG,outline=GOLD,width=3)
        end=960+760*smooth((t-.2)/.6)
        d.polygon([(830,620),(end,570),(end,710),(830,705)],fill="#267b9f")
        for i in range(26):
            x=840+((i/26+t*2)%1)*max(1,end-840)
            if x<end: d.ellipse((x,640,x+9,649),fill=BLUE)
        txt(d,(155,260),"Agua regulada aguas arriba",36,DIM)
        txt(d,(985,790),"Liberación controlada · 2014",40,GOLD)
        txt(d,(985,845),"No recuperación permanente de todo el río",27,DIM,max_width=850)
        return im

    def section(self,t):
        im=self.base("Cambiar el nivel no mueve las piedras", "Analogía conceptual · no reconstrucción de un tramo real")
        d=ImageDraw.Draw(im)
        # Fixed bowl-shaped riverbed; water surface intersects it as level rises.
        bed=[(160,340),(430,355),(655,710),(1230,710),(1490,355),(1760,340)]
        d.polygon(bed+[(1760,850),(160,850)],fill="#8a7961")
        d.line(bed,fill=GOLD,width=7)
        y=670-185*smooth(t/.65)
        left=430+(y-355)/355*225;right=1490-(y-355)/355*260
        d.polygon([(left,y),(right,y),(1230,710),(655,710)],fill="#276d8b")
        for i in range(20):
            x=left+(i/20+t*.1)%1*(right-left)
            d.line((x,y+12,x+32,y+12),fill=BLUE,width=2)
        # Shoes/stones remain fixed; the water is drawn over their submerged portion.
        d.ellipse((600,612,692,660),fill="#bbb19e")
        d.rounded_rectangle((615,585,660,618),9,fill=CORAL)
        if y<660:
            d.polygon([(left,y),(right,y),(1230,710),(655,710)],fill="#276d8b")
            d.line((left,y,right,y),fill=BLUE,width=6)
        arrow(d,(1500,690),(1500,y),BLUE)
        txt(d,(180,895),"Lecho fijo",38,GOLD)
        txt(d,(1450,280),"Nivel",38,BLUE)
        return im

    def river(self,t,variant):
        im=self.base("El cauce también puede cambiar" if variant=="erosion" else "Pozas no prueban flujo continuo", "Esquema conceptual · no desecación ni erosión observadas en Jatunyacu")
        d=ImageDraw.Draw(im)
        d.rounded_rectangle((160,210,1760,890),40,fill="#384b41")
        shift=80*smooth(t) if variant=="erosion" else 0
        pts=[(180+i*20,530+130*math.sin(i/10)+shift*math.sin(i/15)) for i in range(80)]
        d.line(pts,fill="#b3a17b",width=160,joint="curve")
        d.line(pts,fill="#267794",width=90,joint="curve")
        if variant=="pools":
            for x in [490,870,1260]:
                y=530+130*math.sin((x-180)/200)
                d.rectangle((x-48,y-105,x+48,y+105),fill="#b3a17b")
            txt(d,(220,270),"Agua presente",38,BLUE)
            txt(d,(1120,790),"Conexión interrumpida",36,GOLD)
        else:
            txt(d,(220,270),"Erosiona",38,CORAL);txt(d,(1180,770),"Deposita",38,GOLD)
            for i in range(40):
                k=(i*1.9+t*25)%77;j=int(k)
                x,y=pts[j]
                d.ellipse((x-4,y-4,x+4,y+4),fill=PAPER)
        return im

    def flow(self,t,variant):
        im=self.base("Superficie no es caudal", "Analogía / modelo cualitativo · USGS, How Streamflow is Measured")
        d=ImageDraw.Draw(im)
        if variant=="analogy":
            d.polygon([(180,340),(710,340),(790,650),(260,650)],fill="#2888a6",outline=BLUE)
            d.polygon([(260,650),(790,650),(790,725),(260,725)],fill="#425568")
            for i in range(12):
                y=365+i*21;d.line((240,y,665+25*math.sin(t*7+i),y),fill="#58b5c6",width=2)
            d.line((1110,490,1710,490),fill="#536574",width=110)
            d.line((1110,490,1710,490),fill="#227b98",width=65)
            for i in range(8):
                x=1110+((i/8+t*1.8)%1)*585;arrow(d,(x,490),(x+28,490),BLUE,3)
            txt(d,(220,795),"Piscina: agua presente",39)
            txt(d,(1110,795),"Manguera: agua que pasa",39)
        else:
            d.polygon([(250,345),(1590,345),(1740,690),(390,690)],fill="#286c86")
            d.polygon([(910,345),(1110,345),(1260,690),(1060,690)],fill="#4e9daa",outline=BLUE)
            for i in range(18):
                x=300+((i/18+t*1.2)%1)*1280;y=390+(i%4)*60
                arrow(d,(x,y),(x+50,y),PAPER,3)
            txt(d,(650,240),"Sección × velocidad",58,GOLD)
            txt(d,(555,780),"Volumen que atraviesa la sección por segundo",38)
        return im

    def light(self,t,variant):
        im=self.base("La pista está en la luz", "Respuestas cualitativas · no espectros medidos ni intensidades a escala")
        d=ImageDraw.Draw(im)
        d.polygon([(180,620),(840,620),(1030,840),(370,840)],fill="#235b73",outline=BLUE)
        d.polygon([(1080,620),(1560,620),(1750,840),(1270,840)],fill="#426b4b",outline=GREEN)
        txt(d,(490,855),"Agua",38,BLUE);txt(d,(1350,855),"Vegetación",38,GREEN)
        d.rounded_rectangle((780,245,1070,335),12,fill="#728a96")
        d.polygon([(675,275),(780,275),(780,310),(675,310)],fill="#2e7799",outline=BLUE)
        d.polygon([(1070,275),(1200,275),(1200,310),(1070,310)],fill="#2e7799",outline=BLUE)
        if variant=="sensor":
            for x in (570,1370):
                arrow(d,(x,650),(920,350),GOLD,4)
                f=(t*3+(x/1000))%1
                px=x+(920-x)*f;py=650+(350-650)*f
                d.ellipse((px-8,py-8,px+8,py+8),fill=GOLD)
            txt(d,(650,140),"Sensor: mediciones, no recuerdos",40)
        else:
            for a,b,c in [((510,640),(870,350),GREEN),((550,640),(965,350),CORAL),((1390,640),(975,350),CORAL)]:
                arrow(d,a,b,c,3)
                if variant=="response" and a[0]<1000 and c==CORAL:
                    d.line((a,b),fill="#4b5f69",width=2)
                else:
                    f=(t*2.5)%1;px=a[0]+(b[0]-a[0])*f;py=a[1]+(b[1]-a[1])*f
                    d.ellipse((px-6,py-6,px+6,py+6),fill=c)
            txt(d,(220,150),"Verde · visible",40,GREEN)
            txt(d,(1240,150),"SWIR · no visible",40,CORAL)
            if variant=="response":txt(d,(170,430),"Agua: respuesta SWIR baja",30,BLUE)
        return im

    def formula(self,t,variant):
        im=self.base("Dos señales. Un contraste.", "MNDWI · Xu (2006) · aplicado a reflectancias B3 / B11, no al RGB")
        d=ImageDraw.Draw(im)
        txt(d,(285,270),"VERDE",50,GREEN);txt(d,(1210,270),"ONDA CORTA",50,CORAL)
        arrow(d,(465,370),(650,490),GREEN);arrow(d,(1430,370),(1150,490),CORAL)
        txt(d,(645,465),"Verde − SWIR",72)
        if variant=="meaning" or t>.35:
            d.line((630,565,1290,565),fill=GOLD,width=4)
            txt(d,(645,590),"Verde + SWIR",72)
        if variant=="meaning" or t>.68:
            txt(d,(220,805),"MNDWI",63,GOLD)
            txt(d,(840,825),"Un contraste. No litros ni profundidad.",37,DIM)
        return im

    def map_image(self,t,variant,title):
        im=self.base(title,"Contains modified Copernicus Sentinel data (2019, 2024, 2026) · cuadrícula común 20 m")
        d=ImageDraw.Draw(im)
        year={"first":2019,"middle":2024,"recent":2026}.get(variant,2024)
        mode="mndwi" if variant=="index" else "rgb"
        surface=self.maps[year,mode].copy()
        if variant=="wipe":
            cut=round(850*(.10+.8*smooth(t)))
            surface=self.maps[2019,"rgb"].copy()
            surface.paste(self.maps[2024,"rgb"].crop((cut,0,850,850)),(cut,0))
            sd=ImageDraw.Draw(surface);sd.line((cut,0,cut,850),fill=GOLD,width=4)
        im.paste(surface,(80,160))
        # Scale bar in the actual UTM display grid: 50 cells = 1 km.
        scale=850/190*50
        d.rectangle((108,950,330,995),fill=BG)
        d.line((118,970,118+scale,970),fill=PAPER,width=5)
        txt(d,(120,980),"1 km",20)
        txt(d,(965,200),"Jatunyacu",56,serif=True)
        txt(d,(965,277),"Ecuador · Napo",30,DIM)
        content={
            "first":("11 JUL 2019","Una observación. No un antes intacto."),
            "wipe":("2019 / 2024","Mismo encuadre, escala y ajuste visual."),
            "middle":("08 AGO 2024","Diferencia visible ≠ causa identificada."),
            "recent":("29 JUL 2026","Tres momentos, no una película continua."),
            "promise":("¿Qué cambió?","El agua, el cauce… o nuestra manera de medir."),
            "answer":("¿Qué prueba falta?","Otras fechas, niveles, lluvia y observaciones de campo."),
            "index":("MNDWI","Valores primero. Colores después. No es agua validada."),
        }[variant]
        txt(d,(965,395),content[0],46,GOLD)
        wrap(d,(965,470),content[1],41,800)
        txt(d,(965,850),"Trama: fuera del soporte válido común",25,DIM)
        if variant=="index":
            # Exactly the five-stop palette used by the audited PNG builder.
            stops=np.array([[116,70,46],[220,199,157],[242,237,212],[47,141,184],[7,61,105]])
            for x in range(700):
                value=x/699*4
                rgb=tuple(int(np.interp(value,np.arange(5),stops[:,c])) for c in range(3))
                d.line((965+x,750,965+x,781),fill=rgb)
            txt(d,(965,795),"−1",25);txt(d,(1640,795),"+1",25)
            txt(d,(965,685),"Escala del contraste, no cantidad de agua",28,DIM)
        return im

    def threshold(self,t,variant):
        threshold=0 if variant=="zero" else (.2 if variant=="validate" else .2*smooth(t/.7))
        key=round(threshold,4)
        if key not in self.rule_cache:
            selected=index_mask(self.values,self.common,threshold)
            arr=np.array(Image.open(FOLDER/"jatunyacu_detail_2024_rgb.png").convert("RGB"))
            arr[selected]=(72,197,228)
            # Explicit support: rejected/unknown pixels are not drawn as dry ground.
            yy,xx=np.indices(self.common.shape)
            arr[~self.common]=np.where(((xx[~self.common]//4+yy[~self.common]//4)%2)[:,None],(70,85,91),(52,67,75))
            self.rule_cache[key]=(Image.fromarray(arr).resize((850,850),Image.Resampling.NEAREST),int(selected.sum()))
        surface,count=self.rule_cache[key]
        im=self.base("El mapa cambia. La observación no.", "MNDWI > umbral · demostración no calibrada · azul: candidatos; trama: sin soporte común")
        im.paste(surface,(80,160));d=ImageDraw.Draw(im)
        txt(d,(965,205),"08 AGO 2024",41,GOLD)
        txt(d,(965,290),"Regla de selección",34,DIM)
        txt(d,(965,350),"MNDWI > "+f"{threshold:.2f}".replace(".",","),64)
        d.line((1000,530,1740,530),fill="#42596b",width=12)
        pos=1000+740*threshold/.2
        d.line((1000,530,pos,530),fill=BLUE,width=12)
        d.ellipse((pos-16,514,pos+16,546),fill=GOLD)
        txt(d,(975,570),"0",30);txt(d,(1720,570),"0,2",30)
        txt(d,(965,675),str(count),74,BLUE)
        txt(d,(965,765),"celdas candidatas en este recorte",31,DIM)
        wrap(d,(965,850),"No son litros ni una medida de agua perdida.",30,800)
        return im

    def three(self,t):
        im=self.base("Se parecen en una foto. No son lo mismo.", "Mecanismos distintos · ninguna causa local establecida en este montaje")
        d=ImageDraw.Draw(im)
        for i,(word,col,small) in enumerate([("NIVEL",BLUE,"Agua sobre el lecho"),("CAUCE",GOLD,"El terreno cambia"),("REGLA",CORAL,"El mapa cambia")]):
            x=160+i*565;y=430-round(20*math.sin(t*math.pi+i))
            d.ellipse((x+100,y-145,x+285,y+40),outline=col,width=5)
            txt(d,(x+158,y-106),str(i+1),85,col)
            txt(d,(x,y+120),word,56,col)
            txt(d,(x,y+200),small,28,DIM)
        return im

    def pixel(self,t,variant):
        im=self.base("¿Dónde termina el agua dentro de esta celda?", "Celda conceptual · 20 m en nuestra comparación · no superresolución ni detalle inventado")
        d=ImageDraw.Draw(im)
        size=420+round(150*smooth(t)) if variant=="zoom" else 500
        x,y=240,260
        d.rectangle((x,y,x+size,y+size),fill="#597b4f")
        d.polygon([(x,y),(x+size*.72,y),(x+size*.50,y+size),(x,y+size)],fill="#2784a1")
        d.polygon([(x+size*.65,y),(x+size*.82,y),(x+size*.58,y+size),(x+size*.44,y+size)],fill="#b5a17e")
        for i in range(22):
            px=x+size*(.65+.15*(i%3)/2)-size*.2*(i/22);py=y+i/22*size
            d.ellipse((px,py,px+7,py+7),fill=GOLD)
        d.rectangle((x,y,x+size,y+size),outline=PAPER,width=6)
        txt(d,(x,y+size+25),"20 metros",35,GOLD)
        arrow(d,(900,510),(1130,510),GOLD)
        d.rectangle((1230,360,1520,650),fill="#5f968e",outline=PAPER,width=4)
        txt(d,(1150,730),"Una respuesta mezclada",38)
        txt(d,(1135,800),"No una orilla exacta",34,DIM)
        return im

    def timeline(self,t,variant):
        im=self.base("El tiempo también es una prueba", "Secuencia ilustrativa · no una serie hidrológica medida ni fechas adicionales del Jatunyacu")
        d=ImageDraw.Draw(im)
        d.line((180,510,1750,510),fill="#526876",width=4)
        for i in range(12):
            x=210+i*130;y=430+75*math.sin(i*1.4)
            if i in (3,7):
                d.ellipse((x-32,475,x+32,539),fill="#74838c")
                txt(d,(x-11,482),"?",36,PAPER)
            else:
                height=50+60*(1+math.sin(i*1.4))
                d.rectangle((x-22,780-height,x+22,780),fill=BLUE)
                d.ellipse((x-9,501,x+9,519),fill=GOLD)
        if variant=="cloud":
            cx=600+130*math.sin(t*math.pi)
            for dx,dy in [(-75,15),(0,-20),(80,20)]:
                d.ellipse((cx+dx-78,270+dy-65,cx+dx+78,270+dy+65),fill="#9ba9b1")
            txt(d,(1050,285),"No observado ≠ seco",42,GOLD)
        else:
            txt(d,(240,300),"Más observaciones",45)
            txt(d,(1010,300),"Lluvia + niveles + campo",40,GOLD)
        txt(d,(245,850),"Las barras son ilustrativas; no muestran caudales reales.",29,DIM)
        return im

    def cause(self,t,variant):
        im=self.base("¿Qué explicación encaja con todas las pruebas?", "Dethier et al. (2023): relación general · no atribución causal de estos píxeles de Napo")
        d=ImageDraw.Draw(im)
        if variant=="chemistry":
            d.line((310,500,860,500),fill=BLUE,width=80)
            d.rounded_rectangle((1220,400,1410,700),25,outline=PAPER,width=5)
            d.rectangle((1250,555,1380,675),fill="#438c9b")
            txt(d,(300,685),"Señal óptica",46,BLUE)
            txt(d,(1100,785),"Muestra + laboratorio",40,GOLD)
            txt(d,(875,470),"≠",100,CORAL)
        else:
            for y,word,col in [(310,"Intervención",CORAL),(560,"Crecida / nivel",BLUE)]:
                d.rounded_rectangle((130,y,670,y+115),15,outline=col,width=3)
                txt(d,(170,y+32),word,41,col)
                arrow(d,(700,y+55),(1070,490),col)
            d.ellipse((1080,360,1340,620),outline=GOLD,width=5)
            txt(d,(1130,460),"¿causa?",37,GOLD)
            if variant=="evidence":
                for i,word in enumerate(["Dónde y cuándo","Antes / después","Arriba / abajo","Muestras / niveles"]):
                    txt(d,(1420,285+i*150),word,30,max_width=450)
                    arrow(d,(1410,335+i*150),(1340,490),DIM,2)
            else:
                wrap(d,(1420,430),"Una asociación no demuestra esta causa local.",37,410)
        return im

    def credits(self):
        im=self.base("Una imagen es el comienzo de una pregunta.", "Henry Conteron / Ecuador Vivo · narración sintética es-EC-LuisNeural · sin publicación automática")
        d=ImageDraw.Draw(im)
        rows=[("FOTOGRAFÍAS","USGS · 20 y 29 MAR 2014 · dominio público"),
              ("OBSERVACIONES","Copernicus Sentinel-2 · 11 JUL 2019 / 08 AGO 2024 / 29 JUL 2026"),
              ("MÉTODO","Xu (2006) · MNDWI · verde / SWIR · umbrales exploratorios"),
              ("HIDROLOGÍA / CAUSAS","USGS · Cavallo et al. (2025) · Dethier et al. (2023)"),
              ("ANIMACIONES","Originales y cualitativas · no mediciones de campo")]
        for i,(label,value) in enumerate(rows):
            y=220+i*132
            txt(d,(80,y),label,26,GOLD)
            txt(d,(80,y+45),value,34)
        return im

    def render(self,beat,t,caption=""):
        sid,speech,title,kind,variant=beat
        if kind=="photo":
            tag="dry" if variant=="dry" else "wet"
            im=self.photo(tag,t);d=ImageDraw.Draw(im)
            d.rectangle((0,0,W,172),fill=BG)
            txt(d,(80,35),title,68,serif=True)
            txt(d,(80,122),"COLORADO · DELTA / "+("20 MAR 2014" if tag=="dry" else "29 MAR 2014"),27,GOLD)
            d.rectangle((0,1020,W,H),fill=BG)
            txt(d,(80,1039),"Fotografía USGS · dominio público · movimiento de encuadre, no filmación",22,DIM)
        elif kind=="pair":im=self.pair(t,variant)
        elif kind=="dam":im=self.dam(t)
        elif kind=="section":im=self.section(t)
        elif kind=="river":im=self.river(t,variant)
        elif kind=="flow":im=self.flow(t,variant)
        elif kind=="light":im=self.light(t,variant)
        elif kind=="formula":im=self.formula(t,variant)
        elif kind=="map":im=self.map_image(t,variant,title)
        elif kind=="threshold":im=self.threshold(t,variant)
        elif kind=="three":im=self.three(t)
        elif kind=="pixel":im=self.pixel(t,variant)
        elif kind=="timeline":im=self.timeline(t,variant)
        elif kind=="cause":im=self.cause(t,variant)
        elif kind=="credits":im=self.credits()
        else:raise ValueError(kind)
        if caption:
            d=ImageDraw.Draw(im)
            length=d.textlength(caption,font=font(34))
            if length>1730: raise ValueError("Caption overflow")
            x=(W-length)/2
            d.rounded_rectangle((x-20,960,x+length+20,1017),12,fill="#0a1218")
            txt(d,(x,970),caption,34)
        return im


def cues_for(words):
    cues=[]; group=[]
    for word in words:
        group.append(word)
        if len(group)>=8 or word["text"].endswith((".","?","!",":",";")):
            cues.append(dict(start=group[0]["start"],end=group[-1]["end"],text=" ".join(w["text"] for w in group)))
            group=[]
    if group:cues.append(dict(start=group[0]["start"],end=group[-1]["end"],text=" ".join(w["text"] for w in group)))
    return cues


def plan():
    scenes=[];cursor=0
    for beat in BEATS:
        sid=beat[0]
        timing=json.loads((FOLDER/f"times_{sid}.json").read_text(encoding="utf-8"))
        if timing["text_sha256"]!=sha256((VOICE+"-3%"+beat[1]).encode()).hexdigest():raise ValueError("Voice text changed")
        frames=math.ceil((timing["seconds"]+(.9 if sid in ("dryphoto","wetphoto","rulemove","middle","recent") else .45))*FPS)
        scenes.append(dict(kind=sid,start_frame=cursor,frames=frames,audio_seconds=timing["seconds"],cues=cues_for(timing["words"])))
        cursor+=frames
    return scenes


def srt_time(seconds):
    n=round(seconds*1000); h,n=divmod(n,3600000);m,n=divmod(n,60000);s,n=divmod(n,1000)
    return f"{h:02d}:{m:02d}:{s:02d},{n:03d}"


def write_subtitles(scenes):
    rows=[]
    for scene in scenes:
        for cue in scene["cues"]:
            start=scene["start_frame"]/FPS+cue["start"];end=scene["start_frame"]/FPS+cue["end"]
            rows.append(f"{len(rows)+1}\n{srt_time(start)} --> {srt_time(end)}\n{cue['text']}\n")
    (FOLDER/"subtitulos_es.srt").write_text("\n".join(rows),encoding="utf-8")


def storyboard():
    design=Design()
    sheet=Image.new("RGB",(1600,math.ceil(len(BEATS)/4)*250),BG)
    for i,beat in enumerate(BEATS):
        im=design.render(beat,.55)
        im.save(FOLDER/f"qa_{beat[0]}.jpg",quality=90)
        sheet.paste(im.resize((400,225),Image.Resampling.LANCZOS),((i%4)*400,(i//4)*250))
        ImageDraw.Draw(sheet).text(((i%4)*400+8,(i//4)*250+227),beat[0],font=font(17),fill=PAPER)
    sheet.save(FOLDER/"storyboard.jpg",quality=92)
    print("Storyboard ready",flush=True)


def export():
    from reel_editorial import mux_audio
    scenes=plan();write_subtitles(scenes);design=Design()
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    visual=FOLDER/"visual_sin_audio.mp4";output=FOLDER/"que_le_paso_al_rio_v8.mp4"
    writer=imageio_ffmpeg.write_frames(str(visual),(W,H),fps=FPS,codec="libx264",pix_fmt_in="rgb24",pix_fmt_out="yuv420p",quality=7,macro_block_size=2,ffmpeg_log_level="error",output_params=["-preset","veryfast","-threads","2","-movflags","+faststart"])
    writer.send(None)
    try:
        for beat,scene in zip(BEATS,scenes):
            cues=scene["cues"]; starts=[c["start"] for c in cues]
            for frame in range(scene["frames"]):
                seconds=frame/FPS;j=bisect_right(starts,seconds)-1
                caption=cues[j]["text"] if j>=0 and seconds<cues[j]["end"]+.12 else ""
                im=design.render(beat,frame/max(1,scene["frames"]-1),caption)
                writer.send(im.tobytes())
            print("Rendered: "+beat[0],flush=True)
    finally:writer.close()
    mux_audio(FOLDER,visual,output,scenes)
    metadata=dict(version=8,width=W,height=H,fps=FPS,visual_updates_fps=FPS,frames=sum(s["frames"] for s in scenes),duration_seconds=sum(s["frames"] for s in scenes)/FPS,
        video_sha256=sha256(output.read_bytes()).hexdigest(),script_sha256=sha256((FOLDER/"narration.json").read_bytes()).hexdigest(),
        source_manifest_sha256=sha256((FOLDER/"sources_manifest.json").read_bytes()).hexdigest(),renderer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        audio="Synthetic es-EC-LuisNeural / Edge speech; no impersonation",captions="Speech-service word-boundary timings; manual final QC recommended",scenes=scenes,
        codec="H264 / AAC",status="rendered; verify before publication")
    (FOLDER/"video_metadata.json").write_text(json.dumps(metadata,indent=2,ensure_ascii=False),encoding="utf-8")
    print(f"Rendered {metadata['duration_seconds']:.2f} seconds",flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=["prepare","voices","storyboard","export"])
    args=parser.parse_args()
    if args.action=="prepare":prepare()
    elif args.action=="voices":asyncio.run(voices())
    elif args.action=="storyboard":storyboard()
    elif args.action=="export":export()
