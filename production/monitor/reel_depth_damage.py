"""Original depth/damage lesson: real catalog, controlled diagrams, archive photos."""
from functools import lru_cache
from hashlib import sha256
import json
import math
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageOps

from prepare_depth_episode import FOLDER, HASH, load_history, CASE_IDS
from reel_design import (canvas, write, panel, land_map, project, MAP, depth_legend,
                         magnitude_legend, BG, TEXT, MUTED, GOLD, TEAL, LINE, PANEL)
from export_video import font, depth_color
from historical import magnitude_size

SCENES = [(0,18,"historia"),(18,26,"profundidad"),(26,34,"pregunta"),
          (34,56,"comparacion"),(56,74,"pedernales"),(74,92,"quito"),
          (92,111,"reventador"),(111,127,"factores"),(127,140,"cierre")]
DURATION = 140
PROFILE_SCALE = 1.7


def history_year(t):
    return min(2025, 1900+math.floor(max(0,t)/16*126))


def distance(horizontal, depth):
    """Geometric distance only, NOT an intensity model."""
    return math.hypot(horizontal, depth)


def paragraph(d, xy, text, size=31, fill=TEXT, width=760, spacing=45):
    words, line, y = text.split(), "", xy[1]
    for word in words:
        trial = (line+" "+word).strip()
        if d.textlength(trial,font=font(size)) > width and line:
            write(d,(xy[0],y),line,size,fill); y += spacing; line = word
        else:
            line = trial
    if line:
        write(d,(xy[0],y),line,size,fill)
    return y+spacing


def shell(title, subtitle):
    im = canvas("02 / PROFUNDIDAD Y DAÑOS")
    d = ImageDraw.Draw(im)
    title_size=51
    while d.textlength(title,font=font(title_size,True))>840 and title_size>32:
        title_size-=1
    write(d,(90,242),title,title_size,serif=True)
    paragraph(d,(90,315),subtitle,28,MUTED,width=840,spacing=39)
    write(d,(90,217),"MAQUETA SIN VOZ · NO PUBLICAR",17,TEAL)
    return im


class DepthDesign:
    def __init__(self, folder=FOLDER):
        self.folder = Path(folder)
        self.rows = load_history()
        self.cases = {key:next(r for r in self.rows if r['id']==identity)
                      for key,identity in zip(("pedernales","quito","reventador"),CASE_IDS)}
        self.audit = json.loads((self.folder/"evidence.json").read_text(encoding="utf-8"))
        if self.audit["snapshot_sha256"] != HASH:
            raise ValueError("Evidence and map snapshot differ")
        self.photos = {}
        for key, meta in self.audit["media"].items():
            path = self.folder/f"archive_{key}.jpg"
            if sha256(path.read_bytes()).hexdigest() != meta["sha256"]:
                raise ValueError("Archive photo changed")
            with Image.open(path) as image:
                fit = ImageOps.contain(image.convert('RGB'), (840,560), Image.Resampling.LANCZOS)
                full = Image.new('RGB', (840,560), PANEL)
                full.paste(fit, ((840-fit.width)//2,(560-fit.height)//2))
                self.photos[key] = full

    @lru_cache(maxsize=8)
    def historical(self, year):
        im = shell("¿Cuál sacude más cerca?", "USGS · consulta 1900–2025 · magnitud publicada ≥4")
        im.paste(land_map(),MAP[:2])
        d = ImageDraw.Draw(im)
        rows = [r for r in self.rows if r["year"] <= year]
        # Clip all symbols to the map; fixed coordinates and original magnitudes.
        layer = Image.new("RGBA", (840,790))
        dots = ImageDraw.Draw(layer)
        for row in rows:
            x,y = project(row["longitude"],row["latitude"]); x-=90; y-=360
            r = magnitude_size(row["magnitude"])*1.4/2
            color = depth_color(float("nan") if row["depth_km"] is None else row["depth_km"])
            if row["depth_km"] is None:
                dots.polygon([(x,y-r),(x+r,y),(x,y+r),(x-r,y)],fill=color,outline="#502b2a")
            else:
                dots.ellipse((x-r,y-r,x+r,y+r),fill=color,outline="#502b2a",width=1)
        im.paste(layer, MAP[:2],layer)
        d.rectangle(MAP,outline=TEAL,width=2)
        write(d,(805,380),"N ↑",26,"#243a36")
        for label,lon,lat in [("ECUADOR",-79.1,-1.1),("PERÚ",-76.1,-4.5),("COLOMBIA",-77,2)]:
            x,y=project(lon,lat)
            d.text((x,y),label,font=font(24),fill="#243a36",stroke_width=2,stroke_fill=TEXT)
        write(d,(90,1177),str(year),52,GOLD,True)
        write(d,(285,1188),f"{len(rows)} registros acumulados",30)
        write(d,(90,1248),"Región continental y vecina · sin Galápagos",27,MUTED)
        depth_legend(d)
        magnitude_legend(d)
        return im

    def depth(self, elapsed):
        im = shell("Los puntos tienen profundidad.","No son una medida del daño ni una predicción.")
        d=ImageDraw.Draw(im)
        depth_legend(d,(90,432,930,632))
        panel(d,(90,678,930,1140),TEAL)
        write(d,(125,704),"CORTE CONCEPTUAL · PROFUNDIDAD EN km",25,TEAL)
        for title,limits,color,y in [("SUPERFICIAL","0–70 km",depth_color(10),799),
                                     ("INTERMEDIO","70–300 km",depth_color(150),919),
                                     ("PROFUNDO","300–700 km",depth_color(400),1039)]:
            d.ellipse((130,y,160,y+30),fill=color,outline=TEXT,width=1)
            write(d,(185,y-6),title,29)
            write(d,(660,y-6),limits,27,MUTED)
        panel(d,(90,1180,930,1495),GOLD)
        paragraph(d,(125,1214),"Claro: más superficial. Oscuro: mayor profundidad. El gris indica un dato desconocido.",35,width=755,spacing=50)
        paragraph(d,(125,1400),"No es un semáforo de peligro.",32,GOLD)
        return im

    def question(self, elapsed):
        im=shell("Aquí viene la trampa.","Una comparación necesita mantener lo demás igual.")
        d=ImageDraw.Draw(im)
        panel(d,(90,435,930,1110),GOLD)
        write(d,(128,486),"MISMA MAGNITUD",37,GOLD)
        write(d,(128,550),"DISTINTA PROFUNDIDAD",37,GOLD)
        paragraph(d,(128,725),"¿Sentiríamos lo mismo en la misma ciudad?",63,width=730,spacing=82)
        for i,(label,value) in enumerate([("MAGNITUD","Igual"),("CIUDAD Y SUELO","Iguales"),("EDIFICIOS","Iguales")]):
            y=1170+i*115
            panel(d,(90,y,930,y+95),TEAL)
            write(d,(120,y+29),label,26,MUTED)
            write(d,(675,y+24),value,32,TEAL)
        return im

    def comparison(self, elapsed):
        im=shell("Cambiamos solo la profundidad.","Ejemplo hipotético · misma magnitud y distancia epicentral")
        d=ImageDraw.Draw(im)
        for index,depth in enumerate((10,150)):
            x0=90+index*430
            panel(d,(x0,460,x0+410,1120),TEAL if index==0 else GOLD)
            write(d,(x0+22,487),f"{depth} km",49,GOLD,True)
            write(d,(x0+22,561),"Superficial" if index==0 else "Intermedio",28,MUTED)
            # Identical horizontal AND vertical spatial scale in both diagrams.
            section=Image.new("RGB",(366,400),PANEL); s=ImageDraw.Draw(section)
            source_x, surface, city_x = 118,70,118+40*PROFILE_SCALE
            focus_y=surface+depth*PROFILE_SCALE
            s.rectangle((0,surface,366,400),fill="#293f49")
            radius=(elapsed*42)%370
            # Conceptual wavefronts, no physical time, velocity or intensity values.
            for offset in (0,80,160):
                rr=(radius+offset)%370
                s.ellipse((source_x-rr,focus_y-rr,source_x+rr,focus_y+rr),outline="#52717a",width=2)
            s.rectangle((0,0,366,surface-1),fill=PANEL)
            s.line((0,surface,366,surface),fill=TEAL,width=4)
            s.rectangle((city_x-17,surface-29,city_x+17,surface),fill=TEXT)
            s.polygon([(city_x-23,surface-29),(city_x,surface-49),(city_x+23,surface-29)],fill=GOLD)
            s.line((source_x,focus_y,city_x,surface),fill=GOLD,width=3)
            for yy in range(surface+4,int(focus_y),12):
                s.line((source_x,yy,source_x,yy+5),fill=MUTED,width=2)
            s.ellipse((source_x-8,focus_y-8,source_x+8,focus_y+8),fill=GOLD,outline=TEXT,width=2)
            s.text((city_x-47,4),"Ciudad",font=font(24),fill=TEXT)
            s.text((15,374),"Ondas ilustrativas",font=font(20),fill=MUTED)
            im.paste(section,(x0+22,610))
            write(d,(x0+22,1034),f"Trayecto ≈ {distance(40,depth):.0f} km",27,GOLD)
        write(d,(100,1154),"Ambos dibujos: misma escala espacial",28,TEAL)
        write(d,(100,1200),"Distancia epicentral: 40 km en los dos",27,MUTED)
        panel(d,(90,1265,930,1508),GOLD)
        paragraph(d,(125,1297),"Más cerca de la fuente suele implicar mayor sacudida, a condiciones comparables.",35,width=750,spacing=49)
        write(d,(125,1453),"No es un cálculo de intensidad o daños.",27,MUTED)
        return im

    def locator(self, im, row, xy=(675,1150)):
        mini=land_map().resize((210,198),Image.Resampling.LANCZOS)
        d=ImageDraw.Draw(mini); x,y=project(row['longitude'],row['latitude'])
        x=(x-90)/4; y=(y-360)*198/790
        d.ellipse((x-6,y-6,x+6,y+6),fill=GOLD,outline="#182c35",width=2)
        im.paste(mini,xy)

    def archive(self, key, elapsed):
        row=self.cases[key]
        coast=key=="pedernales"
        im=shell("Costa · Pedernales, 2016" if coast else "Sierra · Quito, 2014", "Casos reales, no una comparación controlada entre terremotos")
        d=ImageDraw.Draw(im)
        panel(d,(90,400,930,499),GOLD)
        write(d,(120,427),f"{row['magnitude']:g} {row['magnitude_type']}  ·  {row['depth_km']:.1f} km".replace('.',','),36,GOLD)
        write(d,(685,436),"USGS",28,MUTED)
        im.paste(self.photos[key],(90,530))
        write(d,(100,1109),"FOTOGRAFÍA REAL DE ARCHIVO · NO VIDEO",24,TEAL)
        author="Micaela Ayala V." if coast else "Luis Astudillo C."
        write(d,(100,1153),author+" / ANDES",26)
        write(d,(100,1194),"18 abr 2016" if coast else "12 ago 2014",26,MUTED)
        write(d,(100,1235),"CC BY-SA 2.0 · sin recorte",24,MUTED)
        self.locator(im,row)
        write(d,(675,1355),"Epicentro USGS",23,MUTED)
        panel(d,(90,1400,930,1575),GOLD)
        paragraph(d,(120,1424),"Colapsos y daños estructurales: la vulnerabilidad de las construcciones también importa." if coast else "Derrumbe en el río Monjas: la sacudida también puede desestabilizar laderas.",31,width=775,spacing=43)
        return im

    def amazon(self, elapsed):
        row=self.cases['reventador']
        im=shell("Piedemonte amazónico · 1987", "Secuencia del 5 de marzo, fecha local · entorno del Reventador")
        d=ImageDraw.Draw(im)
        panel(d,(90,420,930,518),GOLD)
        write(d,(120,444),"Caso principal USGS: 7,2 mw · 10 km",32,GOLD)
        panel(d,(90,552,930,1190),TEAL)
        write(d,(125,580),"ESQUEMA PROPIO · NO IMÁGENES DE 1987",25,TEAL)
        # Illustrate a process, not reconstructed local topography or casualties.
        d.polygon([(120,850),(390,680),(780,1040),(900,1040),(900,1140),(120,1140)],fill="#537059")
        d.line((120,850,390,680,780,1040,900,1040),fill=TEXT,width=5)
        for i in range(21):
            x=145+(i*97)%725; y=645+(i*29+elapsed*58)%160
            d.line((x,y,x-9,y+24),fill=TEAL,width=3)
        for i in range(26):
            f=((i/26+elapsed*.09)%1)
            x=425+f*340; y=715+f*325
            r=5+i%6
            d.ellipse((x-r,y-r,x+r,y+r),fill=GOLD,outline="#263e38")
        d.line((730,1100,890,1063),fill=TEAL,width=12)
        write(d,(125,1118),"Laderas + agua + sacudida",30,GOLD)
        self.locator(im,row,(690,1250))
        paragraph(d,(110,1230),"Deslizamientos y flujos documentados por IG-EPN. Las pendientes y la saturación fueron claves.",31,width=545,spacing=45)
        write(d,(690,1460),"Epicentro USGS",23,MUTED)
        paragraph(d,(110,1480),"No atribuimos todo el desastre a la profundidad.",29,GOLD,width=800)
        return im

    def factors(self, elapsed):
        im=shell("Sacudida no es lo mismo que daño.","La profundidad es una pieza del rompecabezas, no el veredicto.")
        d=ImageDraw.Draw(im)
        factors=[("01","FUENTE","Magnitud, ruptura y duración"),("02","DISTANCIA","Qué tan cerca estás de la fuente"),
                 ("03","TERRENO","Suelo, relieve y saturación"),("04","CONSTRUCCIÓN","Cómo responde la estructura")]
        for index,(number,title,detail) in enumerate(factors):
            y=440+index*247
            accent=GOLD if index==int(elapsed/4)%4 else TEAL
            panel(d,(90,y,930,y+219),accent)
            write(d,(120,y+27),number,47,accent,True)
            write(d,(225,y+41),title,29,accent)
            write(d,(120,y+134),detail,32)
        write(d,(100,1480),"Mayor profundidad no significa daño imposible.",29,GOLD)
        write(d,(100,1540),"Estos tres casos no aíslan el efecto de la profundidad.",27,MUTED)
        return im

    def closing(self, elapsed):
        im=shell("Entender para prepararnos.","El mapa explica el pasado; no anuncia el próximo terremoto.")
        d=ImageDraw.Draw(im)
        panel(d,(90,440,930,840),GOLD)
        paragraph(d,(128,481),"Más superficial suele significar mayor sacudida cercana... si lo demás es comparable.",50,width=745,spacing=68)
        panel(d,(90,890,930,1165),TEAL)
        write(d,(125,920),"SIGUIENTE EPISODIO",27,TEAL)
        write(d,(125,984),"Tena: ¿qué es una falla?",44,serif=True)
        write(d,(125,1093),"Historia → 2026 → bajo la superficie",29,MUTED)
        paragraph(d,(100,1240),"Fuentes: USGS e IG-EPN. Mapa: Natural Earth. Archivo fotográfico: ANDES / Wikimedia Commons.",28,MUTED,width=815,spacing=40)
        paragraph(d,(100,1395),"Montaje visual CC BY-SA 2.0. Fotografías conservadas completas; créditos y enlaces en la ficha.",27,MUTED,width=815,spacing=38)
        write(d,(100,1534),"Falta locución, sincronización y subtítulos.",28,GOLD)
        return im

    def render(self, second):
        a,b,name=next(scene for scene in SCENES if scene[0]<=second<scene[1])
        elapsed=second-a
        if name=='historia': im=self.historical(history_year(elapsed)).copy()
        elif name in ('pedernales','quito'): im=self.archive(name,elapsed)
        else: im=getattr(self,{'profundidad':'depth','pregunta':'question','comparacion':'comparison','reventador':'amazon','factores':'factors','cierre':'closing'}[name])(elapsed)
        d=ImageDraw.Draw(im)
        d.line((90,1690,930,1690),fill=LINE,width=4)
        d.line((90,1690,90+840*second/DURATION,1690),fill=GOLD,width=4)
        return im


def export(storyboard_only=False):
    import imageio_ffmpeg
    design=DepthDesign()
    sheet=Image.new('RGB',(810,1440*math.ceil(len(SCENES)/3)//3),BG)
    for index,(start,end,name) in enumerate(SCENES):
        t=end-.5 if name=='historia' else (start+end)/2
        image=design.render(t)
        image.save(FOLDER/f'qa_{name}.jpg',quality=95)
        sheet.paste(image.resize((270,480)),((index%3)*270,(index//3)*480))
    sheet.save(FOLDER/'storyboard.jpg',quality=95)
    design.render(0).save(FOLDER/'qa_inicio.jpg',quality=95)
    if storyboard_only: return
    output=FOLDER/'profundidad_danos_maqueta_sin_voz_v1.mp4'
    writer=imageio_ffmpeg.write_frames(str(output),(1080,1920),fps=30,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',macro_block_size=2,quality=8,ffmpeg_log_level='error',output_params=['-movflags','+faststart','-preset','veryfast','-threads','2'])
    writer.send(None)
    try:
        for frame in range(DURATION*30):
            writer.send(design.render(frame/30).tobytes())
            if frame%300==0: print(f'Depth episode: {frame/30:g}/{DURATION} s',flush=True)
    finally: writer.close()
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(output),'-f','null','-'],check=True,capture_output=True)
    metadata=dict(status='silent_draft_not_for_publication',sha256=sha256(output.read_bytes()).hexdigest(),width=1080,height=1920,fps=30,motion_sampling_fps=30,duration_seconds=DURATION,frames=DURATION*30,audio=None,full_decode='passed',scenes=SCENES,catalog_sha256=HASH,archive_media=list(design.photos),visual_license='CC BY-SA 2.0',pending='new voice, timing, subtitles, final scientific/rights/audio review')
    (FOLDER/'draft_metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    print(output.resolve(),flush=True)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--storyboard-only',action='store_true')
    export(parser.parse_args().storyboard_only)
