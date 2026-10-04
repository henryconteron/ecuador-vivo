"""A river can vanish from a map: original, story-first science video v5."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from PIL import Image, ImageDraw
from reel_napo_methods import Design as MethodsDesign, load_evidence as scientific_evidence
from reel_napo_ndwi import export, fit_map, WIDTH, HEIGHT
from reel_design import CREDIT_NAME, CREDIT_SPECIALTY
from reel_territory import INK, MUTED, GOLD, LIME, PAPER, text, paragraph, card

FOLDER = Path("artifacts/rios_historia_v5")
SCRIPT = {
    "hook": "Voy a hacer desaparecer parte de un río de este mapa. Sin sacar agua. Solo cambiaré una regla. Mira el azul. ¿Viste? Una imagen; dos resultados.",
    "suspect": "Si una regla puede cambiar lo que llamamos agua, imagina lo que puede pasar al comparar dos años. Una franja azul se encoge y ya tenemos un sospechoso: sequía, una mina, una obra. La historia parece escrita. El problema es que todavía no sabemos qué cambió.",
    "river": "Porque un río no es una línea azul. Es agua moviéndose entre sedimentos, islas y vegetación. Cuando cambia el nivel, aparecen bancos antes cubiertos. También puede cambiar el propio cauce: erosiona aquí, deposita allá. Dos fotografías pueden mostrar diferencias parecidas por razones distintas.",
    "invisible": "Para separar esas pistas necesitamos mirar algo invisible para nuestros ojos: el infrarrojo. Sentinel dos lo registra junto a la luz visible. El agua suele devolver poco infrarrojo cercano. La vegetación responde de otra manera. Esa diferencia nos da una pista; todavía no un veredicto.",
    "index": "Ahora sí tiene sentido la fórmula. Contrastamos luz verde con infrarrojo cercano: restamos sus reflectancias y dividimos por la suma. Eso es N D W I. No cuenta gotas ni mide profundidad: resume una diferencia entre dos bandas. Cambiar a infrarrojo de onda corta produce M N D W I.",
    "reveal": "Y aquí está el truco del inicio: usamos M N D W I, pero cambiamos el umbral. Primero aceptamos valores mayores que cero; después, mayores que cero coma dos. La misma observación. Menos píxeles pintados como candidatos a agua. No se secó el río: cambió nuestra regla.",
    "doubt": "¿Cuál regla es correcta? No lo decide el azul más bonito. Hay que comprobarlo con referencias independientes. Agua poco profunda, sombra y orilla pueden confundirse. A W E I combina más bandas para abordar algunas confusiones. Si los métodos discrepan, esa duda también merece aparecer en el mapa.",
    "comparefirst": "Probémoslo con un caso real en Ecuador. Jatunyacu, once de julio de dos mil diecinueve. Guardamos el encuadre y el ajuste de color. No es un antes intacto: es una observación de ese día.",
    "comparemiddle": "Ocho de agosto de dos mil veinticuatro. Detente aquí. Sigue los brazos de agua y los bancos claros. Hay diferencias visibles que vale la pena investigar. Pero aún debemos separar el efecto del nivel del agua de cambios en las formas del cauce.",
    "comparerecent": "Veintinueve de julio de dos mil veintiséis. Otro momento del mismo paisaje. Tenemos tres ventanas en el tiempo, no una película continua. Entre una y otra faltan crecidas, periodos de aguas bajas y muchísimas observaciones.",
    "dry": "Un río puede conservar pozas y haber perdido el flujo que las conecta. Por eso, detectar agua no basta para saber si sigue corriendo. Para estudiar desecación necesitamos muchas fechas, referencias y datos hidrológicos. Y cuando una nube tapa el río, no cuenta como un día seco.",
    "sediment": "Queda otra pregunta: ¿qué transporta esa agua? Los sedimentos pueden cambiar su respuesta a la luz. Un contraste entre rojo y verde, como N D T I, ayuda a explorar señales ópticas. Pero no es un análisis químico. Para convertir una señal en concentración hacen falta muestras y calibración local.",
    "cause": "La minería aluvial puede aumentar los sedimentos; está documentado en ríos tropicales. Una crecida también puede movilizarlos. Para distinguir causas hay que buscar intervenciones verificables, revisar antes y después, comparar aguas arriba y abajo, y contrastar lluvia y niveles. Una imagen llamativa no reemplaza esa investigación.",
    "end": "Al principio hice desaparecer parte de un río del mapa. No del paisaje. Y esa diferencia cambia todo. Los satélites nos permiten encontrar pistas extraordinarias; la ciencia empieza cuando preguntamos qué otra explicación podría producirlas. No busques solo un cambio de color. Busca qué lo explica.",
}
TITLES = {
    "hook": ("Voy a borrar parte del río.", "De este mapa. No del paisaje. · demostración real"),
    "suspect": ("Ya tenemos un sospechoso.", "Pero todavía no sabemos qué cambió"),
    "river": ("Un río no es una línea.", "Agua + sedimentos + islas + vegetación"),
    "invisible": ("La pista que no puedes ver.", "Sentinel-2 registra visible e infrarrojo"),
    "index": ("Dos bandas. Una pista.", "NDWI / MNDWI · contraste, no litros"),
    "reveal": ("El río no desapareció.", "Misma fecha · mismo índice · distinta regla"),
    "doubt": ("¿Y si el mapa se equivoca?", "El desacuerdo también es información"),
    "comparefirst": ("Primera ventana: 2019.", "Caso real · Jatunyacu · 11 JUL 2019"),
    "comparemiddle": ("Detente en 2024.", "Caso real · Jatunyacu · 08 AGO 2024"),
    "comparerecent": ("Otra ventana: 2026.", "Caso real · Jatunyacu · 29 JUL 2026"),
    "dry": ("Hay agua. ¿Pero fluye?", "Una poza no demuestra conexión ni caudal"),
    "sediment": ("Lo que viaja con el agua.", "NDTI · señal óptica, no análisis químico"),
    "cause": ("Una pista. Varias causas.", "Comparar explicaciones, no elegir un culpable"),
    "end": ("Borré el mapa. No el río.", "¿Qué otra explicación produciría lo mismo?"),
}


def load_evidence(folder):
    m=scientific_evidence(folder)
    hook=json.loads((Path(folder)/"hook_evidence.json").read_text(encoding="utf-8"))
    if hook["source_manifest_sha256"] != sha256((Path(folder)/"manifest.json").read_bytes()).hexdigest():
        raise ValueError("Hook source changed")
    if hook["method"]!="mndwi" or hook["thresholds"]!={"low":0,"high":0.2} or hook["date"]!="2024-08-08":
        raise ValueError("Unreviewed hook rule")
    for name,digest in hook["images_sha256"].items():
        if Path(name).name != name or sha256((Path(folder)/name).read_bytes()).hexdigest()!=digest:
            raise ValueError("Hook view changed")
    return m


class Design(MethodsDesign):
    def __init__(self,folder,manifest):
        super().__init__(folder,manifest)
        for key in ("low","high"):
            with Image.open(self.folder/f"threshold_{key}.png") as image:
                self.maps["jatunyacu_detail",2024,"rule"+key],_=fit_map(image.convert("RGBA"))

    def shell(self,kind):
        image=Image.new("RGB",(WIDTH,HEIGHT),INK)
        d=ImageDraw.Draw(image)
        text(d,(90,142),"ECUADOR VIVO / CIENCIA PARA MIRAR MEJOR",24,LIME)
        text(d,(90,184),"EL RÍO QUE DESAPARECE DE UN MAPA",24,MUTED)
        title,detail=TITLES[kind]
        text(d,(90,250),title,43,PAPER,True)
        text(d,(90,330),detail,24,MUTED)
        text(d,(90,1621),CREDIT_NAME,28,PAPER)
        text(d,(90,1659),CREDIT_SPECIALTY,23,MUTED)
        text(d,(90,1723),"BORRADOR · VOZ SINTÉTICA DE REFERENCIA",22,GOLD)
        text(d,(90,1765),"Contains modified Copernicus Sentinel data (2019, 2024, 2026)",20,MUTED)
        return image

    def legend(self,d,mode):
        if mode.startswith("rule"):
            text(d,(90,1320),"Azul: candidato por MNDWI · oscuro: no supera la regla",24,LIME)
            text(d,(90,1350),"08 AGO 2024 · trama: sin datos · umbrales no calibrados",24,MUTED)
        else:
            super().legend(d,mode)

    def rule_map(self,image,high):
        super().map(image,"jatunyacu_detail",2024,"rulehigh" if high else "rulelow")
        d=ImageDraw.Draw(image)
        d.rounded_rectangle((110,485,605,550),8,fill=INK)
        text(d,(130,499),"REGLA: MNDWI > 0,2" if high else "REGLA: MNDWI > 0",32,GOLD)

    def base(self,kind,year,phase):
        image=self.shell(kind)
        if kind in ("hook","reveal"):
            self.rule_map(image,phase>=.5)
        elif kind=="suspect":
            self.map(image,"jatunyacu_detail",2019,"rgb",other_year=2024)
        elif kind in ("river","invisible"):
            self.map(image,"jatunyacu_detail",2024,"rgb")
            if kind=="invisible":
                d=ImageDraw.Draw(image)
                d.rounded_rectangle((110,485,790,550),8,fill=INK)
                text(d,(130,501),"Aquí ves RGB. El infrarrojo no es visible.",27,GOLD)
        elif kind=="index":
            self.formula(image,phase>=.8)
        elif kind=="doubt":
            self.map(image,"jatunyacu_detail",2024,"agreement")
        elif kind.startswith("compare"):
            self.map(image,"jatunyacu_detail",year,"rgb")
        elif kind=="sediment":
            self.map(image,"jatunyacu_detail",2024,"ndti")
        else:
            rows,citation={
                "dry": ([("VER AGUA", "Puede haber pozas sin flujo continuo."),
                         ("SEGUIR EL TIEMPO", "Más observaciones útiles + lluvia y niveles."),
                         ("COMPROBAR EL TERRENO", "Clasificar agua, sedimento y vegetación con referencias.")],
                        "Cavallo et al. (2025): dos tramos en Italia, no validación local. Una nube es falta de observación; tres fechas no dan días secos."),
                "cause": ([("HIPÓTESIS HUMANA", "Intervenciones verificables; comparación antes/después."),
                           ("EXPLICACIONES NATURALES", "Crecidas, niveles del agua y transporte de sedimentos."),
                           ("PONERLAS A PRUEBA", "Aguas arriba/abajo + hidrología + muestreo.")],
                          "Dethier et al. (2023), minería aluvial en ríos tropicales; USGS, transporte y depósito. No atribución de estos píxeles ni medida de mercurio."),
                "end": ([("CAMBIÓ UNA REGLA", "No la imagen ni el agua que observó el satélite."),
                         ("UNA PISTA NO ES UNA CAUSA", "Comparar métodos y explicaciones independientes."),
                         ("PUEDES COMPROBARLO", "Fechas, fórmulas y referencias acompañan el video.")],
                        "McFeeters (1996), Xu (2006), Feyisa et al. (2014), Cavallo et al. (2025), Lobo et al. (2018), Dethier et al. (2023), USGS. Método: RIOS_GUION_V5.md."),
            }[kind]
            self.cards(image,rows,citation)
        return image

    def render(self,kind,fraction,caption,progress):
        # The original cache keys only vary for hook/date scenes. v5 additionally
        # switches index/rule at halfway; explicitly key every phase transition.
        year=self.scene_year(kind)
        threshold=.8 if kind=="index" else .5
        key=(kind,year,fraction>=threshold if kind in ("hook","reveal","index") else None)
        if key not in self.cache:
            self.cache[key]=self.base(kind,year,fraction)
        image=self.cache[key].copy()
        d=ImageDraw.Draw(image)
        card(d,(90,1380,930,1578),GOLD)
        bottom=paragraph(d,(138,1402),caption,31,757,PAPER,leading=1.23)
        if bottom>1568:
            raise ValueError("Caption overflows safe area")
        d.line((90,1598,90+round(840*progress),1598),fill=LIME,width=4)
        return image


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder",type=Path,default=FOLDER)
    parser.add_argument("--storyboard-only",action="store_true")
    parser.add_argument("--silent",action="store_true")
    args=parser.parse_args()
    print(export(args.folder,args.silent,args.storyboard_only,design_type=Design,
                 evidence_loader=load_evidence,script=SCRIPT,stem="el_rio_que_desaparece_v5",tag="historia"))
