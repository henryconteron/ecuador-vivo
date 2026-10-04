"""Question-led river story with explanatory motion, not animated slide cards."""
import argparse
from hashlib import sha256
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from reel_river_story import load_evidence as previous_evidence
from reel_napo_methods import Design as EvidenceDesign
from reel_napo_ndwi import export, fit_map
from reel_design import CREDIT_NAME
from reel_territory import INK, MUTED, GOLD, LIME, PAPER, LINE, text, paragraph

FOLDER = Path("artifacts/rios_historia_v6")
BLUE = "#36aeca"
CORAL = "#ed8d74"
BOX = (60, 285, 1020, 1245)
SCRIPT = {
    "hook": "Mira estas dos imágenes. Es el mismo río. ¿Se está secando? Antes de responder, sigue la curva. Lo que parece una historia evidente puede esconder tres cosas muy distintas.",
    "predict": "Puede haber menos agua. Puede haberse movido el cauce. O puede haber cambiado nuestra forma de detectarla. ¿Cuál elegirías? Vamos a separar esas pistas, una por una.",
    "level": "Primero, bajemos el nivel en este ejemplo. Aparece un banco de grava. Desde arriba, el agua ocupa menos espacio, aunque el lecho no se haya movido. Una fotografía muestra superficie; no te dice cuánta agua pasa por segundo. Para eso hace falta medir el flujo.",
    "light": "Pero distinguir agua de tierra también tiene su truco. El satélite no reconoce ríos: registra luz. Mira el agua y la vegetación. En el infrarrojo responden de forma diferente. Nuestros ojos no ven esa luz; Sentinel dos sí. Ahí aparece una herramienta para buscar agua.",
    "index": "Comparamos el verde con el infrarrojo de onda corta. Restamos las dos señales y dividimos por su suma. Ese contraste se llama índice de agua modificado: M N D W I. No necesitas memorizar la fórmula. Quédate con esto: destaca una señal que debemos comprobar, no cuenta litros.",
    "threshold": "Ahora sí: misma imagen, mismo día. Muevo esta regla y desaparece parte del azul. ¿Se fue el agua? No. Cambió qué valores aceptamos como candidatos. Cero y cero coma dos son reglas de demostración, no umbrales calibrados para este río. El mapa cambió; el paisaje no.",
    "pixel": "Y hay otra trampa. En esta comparación, cada celda representa veinte metros de lado. Una sola puede mezclar agua, grava y vegetación. ¿Dónde termina exactamente el río dentro de ella? El color no lo resuelve. Acercar la pantalla agranda la celda, no crea una fotografía más detallada.",
    "comparefirst": "Volvamos a las imágenes reales: Ecuador, Jatunyacu. Once de julio de dos mil diecinueve. Guardamos el encuadre y el ajuste de color. Esta es una observación, no un antes intacto.",
    "comparemiddle": "Ocho de agosto de dos mil veinticuatro. Mira los bancos claros y los brazos de agua. Movemos la cortina para comparar las dos fechas sin cambiar la escala. Hay diferencias visibles. Todavía no sabemos cuánto viene del nivel y cuánto de cambios en el cauce.",
    "comparerecent": "Veintinueve de julio de dos mil veintiséis. Una tercera imagen ayuda, pero no rellena los años que faltan. Entre estas fechas hubo muchos días que no estamos mostrando. No vamos a inventar una película para unirlas.",
    "dry": "Entonces, ¿cómo investigar si se seca? Sigue muchas observaciones y busca si el agua conserva conexión. Puede haber pozas sin flujo continuo. Y si una nube tapa el río, la respuesta es no sabemos, no está seco. Después contrasta con niveles, lluvia y mediciones de campo.",
    "cause": "¿Y la minería? Puede aumentar los sedimentos en ríos tropicales; hay estudios que lo documentan. Pero una crecida también los mueve. Para investigar una causa local necesitamos intervenciones verificables, fechas, comparaciones aguas arriba y abajo, y muestras. Un índice no mide mercurio ni señala al responsable.",
    "end": "Vuelve a la primera pregunta. ¿Se está secando este río? Con estas tres imágenes no podemos afirmarlo. Ahora sí podemos distinguir lo que vimos, lo que calculamos y lo que falta medir. El satélite encuentra pistas. La investigación decide qué significan.",
}
TITLES = {
    "hook": "¿Se está secando?", "predict": "Elige una explicación.",
    "level": "Menos superficie, ¿menos caudal?", "light": "El satélite no ve un río.",
    "index": "Dos señales. Una pista.", "threshold": "Muevo una regla. Cambia el azul.",
    "pixel": "¿Dónde está la orilla?", "comparefirst": "Volvamos al paisaje.",
    "comparemiddle": "Aquí vale la pena detenerse.", "comparerecent": "Otra fecha. No toda la historia.",
    "dry": "Agua no siempre significa flujo.", "cause": "¿Qué lo causó?",
    "end": "Una imagen no es un diagnóstico.",
}


def ease(t):
    t = max(0., min(1., t))
    return t*t*(3-2*t)


def stage(t, start, end):
    return ease((t-start)/(end-start))


def threshold_at(t):
    return .2*stage(t, .26, .64)


def candidates(values, common, threshold):
    return common & np.isfinite(values) & (values > threshold)


def load_evidence(folder):
    folder = Path(folder)
    m = previous_evidence(folder)
    report = json.loads((folder / "motion_evidence.json").read_text(encoding="utf-8"))
    if report["manifest_sha256"] != sha256((folder / "manifest.json").read_bytes()).hexdigest():
        raise ValueError("Motion evidence manifest changed")
    if report["array_sha256"] != sha256((folder / "threshold_values.npz").read_bytes()).hexdigest():
        raise ValueError("Motion arrays changed")
    if report["threshold_range"] != [0, .2] or report["formula"] != "(B3-B11)/(B3+B11)":
        raise ValueError("Unreviewed threshold demonstration")
    row = next(r for r in m["sources"] if r["region"] == "jatunyacu" and r["date"] == report["date"])
    if row["native_sha256"] != report["native_source_sha256"]:
        raise ValueError("Motion source mismatch")
    with np.load(folder / "threshold_values.npz", allow_pickle=False) as a:
        values, common = a["values"], a["common"]
        shape = (m["regions"]["jatunyacu_detail"]["height"], m["regions"]["jatunyacu_detail"]["width"])
        if values.shape != shape or common.shape != shape or common.dtype != bool:
            raise ValueError("Motion grid mismatch")
        if not np.isfinite(values[common]).all() or int(common.sum()) != report["support_pixels"]:
            raise ValueError("Motion support mismatch")
        if [int(candidates(values,common,v).sum()) for v in (0,.2)] != [report["candidate_pixels"][k] for k in ("low","high")]:
            raise ValueError("Motion counts mismatch")
    return m


def arrow(d, a, b, color, width=6):
    d.line((a,b), fill=color, width=width)
    angle = math.atan2(b[1]-a[1], b[0]-a[0])
    d.polygon([b, (b[0]-19*math.cos(angle-.45), b[1]-19*math.sin(angle-.45)),
               (b[0]-19*math.cos(angle+.45), b[1]-19*math.sin(angle+.45))],fill=color)


class Design(EvidenceDesign):
    def __init__(self,folder,manifest):
        super().__init__(folder,manifest)
        with np.load(self.folder / "threshold_values.npz", allow_pickle=False) as a:
            self.values, self.common = a["values"].copy(), a["common"].copy()
        self.surface = {key: value.resize((960,960),Image.Resampling.NEAREST)
                        for key,value in self.maps.items()}
        self.last_rule = None

    def shell(self,kind):
        image=Image.new("RGB",(1080,1920),INK)
        d=ImageDraw.Draw(image)
        text(d,(60,85),"ECUADOR VIVO / MIRAR NO ES MEDIR",24,LIME,width=960)
        paragraph(d,(60,145),TITLES[kind],49,960,PAPER,leading=1.13)
        text(d,(60,1750),CREDIT_NAME+" · borrador / voz sintética",23,MUTED,width=960)
        text(d,(60,1795),"Copernicus Sentinel modificado · 2019 / 2024 / 2026",21,MUTED,width=960)
        return image

    def label(self,d,x,y,value,color=GOLD,size=27,width=850):
        # Compact readable labels, not a permanent dashboard over the footage.
        from export_video import font
        n=d.textlength(value,font=font(size))
        if n>width:
            raise ValueError("Label exceeds safe width: "+value)
        d.rounded_rectangle((x-12,y-8,x+n+12,y+size+13),8,fill=INK)
        text(d,(x,y),value,size,color,width=width)

    def real_map(self,image,year,other=None,split=.5,mode="rgb"):
        key=("jatunyacu_detail",year,mode)
        surface=self.surface[key].copy()
        d=ImageDraw.Draw(image)
        cut=int(960*max(0,min(1,split)))
        if other:
            right=self.surface["jatunyacu_detail",other,mode]
            surface.paste(right.crop((cut,0,960,960)),(cut,0))
        image.paste(surface,BOX[:2])
        if other:
            x=60+cut
            d.line((x,BOX[1],x,BOX[3]),fill=GOLD,width=5)
            d.ellipse((x-21,741,x+21,783),fill=GOLD)
            self.label(d,80,310,str(year),size=34)
            self.label(d,867,310,str(other),size=34,width=120)
        else:
            self.label(d,80,310,{2019:"11 JUL 2019",2024:"08 AGO 2024",2026:"29 JUL 2026"}[year])
        scale=1000/20*self.ratios["jatunyacu_detail"]*(960/840)
        self.label(d,85,1149,"≈ 1 km",PAPER,24)
        d.line((85,1200,85+scale,1200),fill=PAPER,width=4)
        self.label(d,935,390,"N ↑",PAPER,24,width=60)
        text(d,(60,1270),"RGB real · cuadrícula de 20 m · mismo ajuste de color",25,LIME,width=960)
        text(d,(60,1310),"Trama: sin observación útil · Jatunyacu, Ecuador",24,MUTED,width=960)

    def diagram_note(self,d,citation):
        text(d,(60,1270),"ESQUEMA DIDÁCTICO · no reconstrucción de este río",24,GOLD,width=960)
        paragraph(d,(60,1320),citation,23,960,MUTED,leading=1.16)

    def river_level(self,image,t):
        d=ImageDraw.Draw(image)
        xs=np.linspace(100,980,180)
        bed=1090-430*((xs-540)/440)**2
        d.polygon([(100,1180),*zip(xs,bed),(980,1180)],fill="#8e7454")
        for offset in (45,100):
            d.line(list(zip(xs,np.minimum(1180,bed+offset))),fill="#b79d70",width=4)
        water=785+175*stage(t,.16,.7)
        inside=bed>=water
        wx=xs[inside]; wy=bed[inside]
        d.polygon([(wx[0],water),*zip(wx,wy),(wx[-1],water)],fill="#216b82")
        d.line((wx[0],water,wx[-1],water),fill=BLUE,width=6)
        # Surface glints are illustrative, not velocities or a flow direction.
        for i in range(6):
            px=wx[0]+((t*1.8+i/6)%1)*(wx[-1]-wx[0])
            d.line((px,water+32,px+20,water+32),fill=PAPER,width=3)
        self.label(d,105,360,"MISMO LECHO",LIME,34)
        self.label(d,105,425,"NIVEL MÁS BAJO" if t>.5 else "NIVEL MÁS ALTO",GOLD,30)
        arrow(d,(920,755),(920,water),GOLD)
        text(d,(140,1190),"Superficie visible ≠ caudal",35,PAPER,width=850)
        self.diagram_note(d,"Nivel y bancos expuestos: ejemplo conceptual. Procesos fluviales: USGS.")

    def light(self,image,t):
        d=ImageDraw.Draw(image)
        text(d,(120,365),"LA LUZ LLEGA",35,PAPER,width=800)
        for x,label,color in ((310,"AGUA",BLUE),(765,"VEGETACIÓN",LIME)):
            d.rounded_rectangle((x-165,995,x+165,1090),12,fill="#206479" if x==310 else "#648655")
            text(d,(x-100,1108),label,30,PAPER,width=350)
            if t>.17:
                p=stage(t,.17,.36)
                arrow(d,(x-55,560),(x-55,560+410*p),GOLD)
            if t>.37:
                p=stage(t,.37,.65)
                length=90 if x==310 else 350
                arrow(d,(x+45,987),(x+45,987-length*p),CORAL)
                self.label(d,x-145,740 if x==310 else 610,"POCO NIR" if x==310 else "MÁS NIR",CORAL,27,width=300)
            if t>.65:
                for i in range(3):
                    yy=490+((t*2+i/3)%1)*380
                    d.ellipse((x-60,yy-5,x-50,yy+5),fill=GOLD)
        text(d,(110,1180),"Visible + infrarrojo",37,GOLD,width=850)
        self.diagram_note(d,"Respuesta cualitativa: McFeeters (1996). Flechas sin escala; no son espectros medidos.")

    def formula(self,image,t):
        d=ImageDraw.Draw(image)
        self.label(d,110,365,"VERDE",LIME,38)
        if t>.2:
            self.label(d,110,505,"INFRARROJO DE ONDA CORTA",CORAL,34)
        if t>.38:
            text(d,(140,733),"VERDE − SWIR",61,PAPER,width=820)
        if t>.55:
            d.line((130,825,950,825),fill=LIME,width=5)
            text(d,(140,850),"VERDE + SWIR",61,PAPER,width=820)
        if t>.7:
            text(d,(140,1035),"MNDWI",77,GOLD,True,width=820)
        # Pulse links labels to the formula without inventing measurements.
        p=stage(t,.2,.5)
        d.line((110,620,110+740*p,620),fill=CORAL,width=5)
        text(d,(110,1175),"Contraste de luz. No litros.",36,PAPER,width=860)
        self.diagram_note(d,"Xu (2006) · MNDWI = (B3 − B11) / (B3 + B11). Bandas llevadas a 20 m.")

    def threshold(self,image,t):
        value=threshold_at(t)
        candidate=candidates(self.values,self.common,value)
        # Reuse the display only when every candidate is unchanged.
        key=candidate.tobytes()
        if self.last_rule is None or self.last_rule[0]!=key:
            rgba=np.zeros((*candidate.shape,4),dtype=np.uint8)
            rgba[:,:,:3]=[35,57,55]
            rgba[candidate,:3]=[54,174,202]
            rgba[:,:,3]=np.where(self.common,255,0)
            self.last_rule=(key,fit_map(Image.fromarray(rgba))[0].resize((960,960),Image.Resampling.NEAREST))
        image.paste(self.last_rule[1],BOX[:2])
        d=ImageDraw.Draw(image)
        self.label(d,80,310,"MISMA IMAGEN · 08 AGO 2024",GOLD,29)
        self.label(d,80,370,"MNDWI > "+f"{value:.3f}".replace(".",","),PAPER,33)
        d.rounded_rectangle((140,1100,950,1208),12,fill=INK)
        d.line((175,1155,895,1155),fill=MUTED,width=6)
        px=175+720*(value/.2)
        d.ellipse((px-16,1139,px+16,1171),fill=GOLD)
        text(d,(175,1180),"0",24,GOLD,width=100)
        text(d,(840,1180),"0,2",24,GOLD,width=100)
        text(d,(60,1270),"Azul: candidato · oscuro: no supera la regla",25,LIME,width=960)
        text(d,(60,1310),"Trama: sin datos · umbrales exploratorios, no calibrados",24,MUTED,width=960)

    def mixed_pixel(self,image,t):
        d=ImageDraw.Draw(image)
        x0,y0,x1,y1=220,470,860,1110
        d.rectangle((x0,y0,x1,y1),fill="#b79d70")
        for yy in range(y0,y1,20):
            bend=560+120*math.sin((yy-y0)/180)
            edge=int(80*math.sin(t*math.pi*2))
            d.rectangle((max(x0,bend-170+edge),yy,min(x1,bend+150+edge),yy+20),fill=BLUE)
        d.polygon([(220,470),(395,470),(310,780),(220,840)],fill="#648655")
        # Fixed cell boundary: water shape is hypothetical, not a geographic trace.
        d.rectangle((x0,y0,x1,y1),outline=PAPER,width=6)
        arrow(d,(x0,405),(x1,405),GOLD,4)
        text(d,(440,350),"20 m",42,GOLD,width=250)
        self.label(d,240,990,"UNA CELDA · VARIAS SUPERFICIES",PAPER,25,width=600)
        text(d,(120,1180),"Agua + grava + vegetación",34,PAPER,width=850)
        self.diagram_note(d,"Celda conceptual. Comparación a 20 m; no detalle nuevo por zoom. Sentinel-2 / Xu (2006).")

    def connection(self,image,t):
        d=ImageDraw.Draw(image)
        d.rounded_rectangle((130,470,950,1130),60,fill="#8e7454")
        xs=np.linspace(130,950,160)
        center=805+90*np.sin((xs-130)/135)
        connected=t<.42
        if connected:
            upper=list(zip(xs,center-58)); lower=list(zip(xs[::-1],(center+58)[::-1]))
            d.polygon(upper+lower,fill=BLUE)
        for x in (265,535,820):
            y=805+90*math.sin((x-130)/135)
            d.ellipse((x-65,y-63,x+65,y+63),fill=BLUE)
        if connected:
            for i in range(7):
                x=155+((t*1.8+i/7)%1)*760
                y=805+90*math.sin((x-130)/135)
                arrow(d,(x-13,y),(x+13,y),PAPER,3)
        self.label(d,160,510,"CONECTADO" if connected else "POZAS AISLADAS",PAPER,34)
        if t>.7:
            # Missing observation is an overlay, not an interpolation of drought.
            d.rounded_rectangle((120,650,955,1000),65,fill="#b4c8b5")
            text(d,(225,765),"SIN OBSERVACIÓN",44,INK,width=720)
            text(d,(250,840),"No sabemos ≠ está seco",30,INK,width=650)
        self.diagram_note(d,"Conectividad conceptual, no diagnóstico local. Cavallo et al. (2025); contrastar con campo.")

    def hypotheses(self,image,t):
        d=ImageDraw.Draw(image)
        d.line((130,855,950,855),fill=BLUE,width=110)
        for i in range(24):
            x=180+((t*1.9+i/24)%1)*700
            d.ellipse((x,847+(i%4-2)*14,x+9,856+(i%4-2)*14),fill=GOLD)
        self.label(d,110,355,"SEDIMENTOS",GOLD,38)
        p=stage(t,.15,.36)
        arrow(d,(285,560),(285,560+210*p),CORAL)
        text(d,(155,500),"Intervención",33,CORAL,width=360)
        if t>.38:
            arrow(d,(785,560),(785,770),LIME)
            text(d,(665,500),"Crecida",33,LIME,width=300)
        if t>.66:
            self.label(d,160,1005,"FECHAS + CAMPO + MUESTRAS",PAPER,31,width=820)
        self.diagram_note(d,"Fuentes posibles, no atribución local. Dethier et al. (2023) + USGS. No mide mercurio.")

    def render(self,kind,fraction,caption,progress):
        t=max(0.,min(1.,fraction))
        image=self.shell(kind)
        d=ImageDraw.Draw(image)
        if kind in ("hook","comparemiddle"):
            # Moving curtain compares actual observations; never morphs geography.
            split=.88-.76*stage(t,.16,.75)
            self.real_map(image,2019,2024,split)
        elif kind in ("comparefirst","comparerecent"):
            self.real_map(image,self.scene_year(kind))
            # A date cursor marks an observation, not intervening inferred states.
            for i,year in enumerate((2019,2024,2026)):
                x=220+320*i
                d.ellipse((x-12,1380,x+12,1404),fill=GOLD if year==self.scene_year(kind) else LINE)
        elif kind=="predict":
            for i,(heading,sub,color) in enumerate((("1 / NIVEL","Menos superficie de agua",BLUE),
                        ("2 / CAUCE","Otras formas y posiciones",GOLD),("3 / MÉTODO","Otra regla de detección",CORAL))):
                y=435+270*i
                if t>i*.19:
                    d.line((90,y,90,y+150),fill=color,width=7)
                    text(d,(130,y),heading,45,color,width=870)
                    text(d,(130,y+85),sub,32,PAPER,width=870)
            text(d,(90,1300),"Hipótesis, no resultados",26,MUTED,width=870)
        elif kind=="level": self.river_level(image,t)
        elif kind=="light": self.light(image,t)
        elif kind=="index": self.formula(image,t)
        elif kind=="threshold": self.threshold(image,t)
        elif kind=="pixel": self.mixed_pixel(image,t)
        elif kind=="dry": self.connection(image,t)
        elif kind=="cause": self.hypotheses(image,t)
        elif kind=="end":
            self.real_map(image,2024)
            entries=("VIMOS · tres observaciones", "CALCULAMOS · candidatos a agua", "FALTA · verificar el cambio y su causa")
            for i,line in enumerate(entries):
                if t>i*.22:
                    self.label(d,100,585+i*135,line,PAPER,29,width=875)
        else: raise ValueError("Unknown river scene")
        d=ImageDraw.Draw(image)
        d.rounded_rectangle((60,1425,1020,1665),20,fill="#173c35",outline=LINE,width=2)
        bottom=paragraph(d,(92,1448),caption,34,885,PAPER,leading=1.22)
        if bottom>1652: raise ValueError("Caption overflows safe area")
        d.line((60,1700,60+round(960*progress),1700),fill=LIME,width=4)
        return image


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder",type=Path,default=FOLDER)
    parser.add_argument("--storyboard-only",action="store_true")
    parser.add_argument("--silent",action="store_true")
    args=parser.parse_args()
    print(export(args.folder,args.silent,args.storyboard_only,design_type=Design,
        evidence_loader=load_evidence,script=SCRIPT,stem="rios_mirar_no_es_medir_v6",tag="movimiento",render_stride=2))
