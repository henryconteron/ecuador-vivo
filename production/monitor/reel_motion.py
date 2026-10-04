"""Narration-driven editorial reveals, with unchanged seismic coordinates/scales.

Motion is explanatory only. No point pulsation, invented shaking, simulated
physical waves, or movement of epicenters/depths is added to catalog plots.
"""
from PIL import Image, ImageDraw

from export_video import font, depth_color
from historical import magnitude_size
from reel_design import (BG, PANEL, LINE, TEXT, MUTED, GOLD, TEAL, MAP,
                         canvas, write, panel, project, profile_point, depth_counts,
                         base_map, render_map)
from reel_captions import Captions


def ease(second,start,duration=.38):
    phase=max(0,min(1,(second-start)/duration))
    return phase*phase*(3-2*phase)


def shell(chapter,title,subtitle="",size=54):
    image=canvas(chapter)
    draw=ImageDraw.Draw(image)
    draw.rectangle((70,70,955,345),fill=BG)
    write(draw,(90,82),"ANDES PULSO",26,fill=GOLD)
    write(draw,(90,124),chapter,24,fill=MUTED)
    write(draw,(90,177),title,size,serif=True)
    write(draw,(90,250),subtitle,27,fill=MUTED)
    return image


def reveal(target,source,box,amount):
    if amount<=0:
        return
    target.paste(Image.blend(target.crop(box),source.crop(box),min(1,amount)),box[:2])


def compact_depth(draw,box=(90,1205,930,1330)):
    x0,y0,x1,y1=box
    panel(draw,box,TEAL)
    write(draw,(x0+24,y0+12),"COLOR → PROFUNDIDAD (km)",24,fill=TEAL)
    cx,cy=x1-167,y0+27
    draw.polygon([(cx,cy-6),(cx+6,cy),(cx,cy+6),(cx-6,cy)],fill=depth_color(float("nan")))
    write(draw,(cx+15,y0+13),"sin dato",22,fill=MUTED)
    start,end=x0+40,x1-70
    for x in range(start,end+1):
        draw.line((x,y0+48,x,y0+68),fill=depth_color((x-start)/(end-start)*300))
    for depth,label in [(0,"0"),(70,"70"),(150,"150"),(300,"≥300")]:
        x=start+depth/300*(end-start)
        draw.line((x,y0+70,x,y0+77),fill=MUTED,width=2)
        draw.text((x-font(23).getlength(label)/2,y0+81),label,font=font(23),fill=TEXT)


def compact_magnitude(draw):
    panel(draw,(90,1340,930,1410),GOLD)
    write(draw,(114,1360),"TAMAÑO → MAGNITUD",23,fill=GOLD)
    for mag,x in [(4,520),(6,665),(8,810)]:
        r=magnitude_size(mag)*1.4/2
        draw.ellipse((x-r,1375-r,x+r,1375+r),fill=depth_color(30),outline=TEXT,width=1)
        write(draw,(x+29,1359),f"M{mag}",25)


class MotionDesign:
    def __init__(self,folder,df,manifest):
        self.df=df
        self.manifest=manifest
        self.captions=Captions(folder)
        self.captions.save()
        self.cache={}
        self.last_map_key=None
        self.known=df[df.depth.notna()]
        if not self.known.depth.between(0,300).all():
            raise ValueError("Extend the fixed profile axis before using this catalog.")
        self.max_row=self.known.loc[self.known.depth.idxmax()]
        self.plots=[("longitude",(-83,-74.5),(165,400,900,710),"OESTE → ESTE",[-82,-80,-78,-76]),
                    ("latitude",(-5.5,2.5),(165,835,900,1145),"SUR → NORTE",[-4,-2,0,2])]

    def map_layout(self,source,year,hold,second):
        key=("map",year,hold)
        if key not in self.cache:
            if self.last_map_key is not None:
                self.cache.pop(self.last_map_key,None)
            result=shell("01 / UN SIGLO EN MOVIMIENTO","Ecuador bajo tus pies",
                         "1900–2025 · USGS · M ≥ 4 · archivo histórico",size=56)
            result.paste(source.crop(MAP),(90,300))  # Translation only, no scale/distortion.
            draw=ImageDraw.Draw(result)
            draw.rectangle((90,300,930,1090),outline=TEAL,width=2)
            for lon in [-82,-80,-78,-76]:
                x,_=project(lon,0)
                draw.text((x-25,1098),f"{abs(lon)}° O",font=font(23),fill=MUTED)
            for lat in [-4,-2,0,2]:
                _,y=project(-83,lat)
                draw.text((32,y-72),f"{abs(lat)}°"+("S" if lat<0 else "N" if lat>0 else ""),font=font(22),fill=MUTED)
            write(draw,(90,1138),str(year),48,fill=GOLD,serif=True)
            count=int((self.df.time.dt.year<=year).sum())
            write(draw,(278,1150),f"{count} registros acumulados",29)
            compact_depth(draw)
            compact_magnitude(draw)
            self.cache[key]=result
            self.last_map_key=key
        result=self.cache[key].copy()
        draw=ImageDraw.Draw(result)
        if hold:
            draw.rectangle((90,175,930,290),fill=BG)
            title="¿Más puntos, más peligro?" if second<34.30 else "No podemos concluirlo."
            write(draw,(90,181),title,49,fill=GOLD,serif=True)
            detail="Archivo histórico incompleto" if second<38.7 else "También cambió nuestra capacidad de observar"
            write(draw,(90,254),detail,27,fill=MUTED)
        return result

    def guide(self,second):
        stage="position" if second<52.8 else "magnitude" if second<57.7 else "color"
        key=("guide",stage)
        if key not in self.cache:
            if stage=="position":
                result=shell("02 / TRES PISTAS","La posición: el epicentro.","Un ejemplo del catálogo, no un sismo actual",size=49)
                selected=self.df[self.df.id=="us20005j32"]
                if len(selected)!=1:
                    raise ValueError("Audited 2016 example missing.")
                sample=render_map(base_map(1900,2025,4),selected,2016)
                result.paste(sample.crop(MAP),(90,350))
                draw=ImageDraw.Draw(result)
                draw.rectangle((90,350,930,1140),outline=TEAL,width=2)
                write(draw,(90,1195),"16 abril 2016 · M 7,8 (mww)",35,fill=GOLD)
                write(draw,(90,1258),"Posición estimada en superficie",31)
                write(draw,(90,1320),"El punto no marca el área de daños.",29,fill=MUTED)
            elif stage=="magnitude":
                result=shell("02 / TRES PISTAS","El tamaño: la magnitud.","Mismo código que el mapa · ejemplos ampliados",size=49)
                draw=ImageDraw.Draw(result)
                panel(draw,(90,365,930,1080),GOLD)
                for mag,x in [(4,250),(6,510),(8,770)]:
                    r=magnitude_size(mag)*3.8/2
                    draw.ellipse((x-r,670-r,x+r,670+r),fill=depth_color(30),outline=TEXT,width=2)
                    write(draw,(x-41,795),f"M{mag}",49,serif=True)
                write(draw,(130,961),"Mayor círculo → mayor magnitud",35)
                panel(draw,(90,1135,930,1360),TEAL)
                write(draw,(120,1173),"No es un área de daños.",43,fill=TEAL,serif=True)
                write(draw,(120,1254),"Son símbolos, no el tamaño de la ruptura.",28,fill=MUTED)
            else:
                result=shell("02 / TRES PISTAS","El color: la profundidad.","Una escala en kilómetros, no una escala de peligro",size=47)
                draw=ImageDraw.Draw(result)
                compact_depth(draw,(90,385,930,510))
                for depth,title,detail,y in [(20,"CLARO","Más superficial",570),(200,"OSCURO","Más profundo",910)]:
                    panel(draw,(90,y,930,y+270),TEAL)
                    draw.ellipse((140,y+84,215,y+159),fill=depth_color(depth),outline=TEXT,width=2)
                    write(draw,(270,y+55),title,43,serif=True)
                    write(draw,(270,y+140),detail,37,fill=MUTED)
                write(draw,(90,1286),"No es un semáforo de peligro.",38,fill=GOLD,serif=True)
            self.cache[key]=result
        result=self.cache[key].copy()
        draw=ImageDraw.Draw(result)
        if stage=="position":
            row=self.df[self.df.id=="us20005j32"].iloc[0]
            x,y=project(row.longitude,row.latitude)
            y-=10
            # Brackets outside the actual symbol, not physical waves or new data.
            distance=43
            length=13
            for sx in [-1,1]:
                for sy in [-1,1]:
                    px,py=x+sx*distance,y+sy*distance
                    draw.line((px-sx*length,py,px,py,px,py-sy*length),fill=TEAL,width=3)
        elif stage=="magnitude":
            # Reveal the caution on the exact "no un área ..." phrase.
            if second<55.72:
                draw.rectangle((90,1135,930,1365),fill=BG)
            else:
                draw.rounded_rectangle((90,1135,930,1360),radius=22,outline=TEAL,width=3)
        else:
            if second<61.40:
                draw.rectangle((90,910,930,1185),fill=BG)
            else:
                draw.rounded_rectangle((90,910,930,1180),radius=22,outline=TEAL,width=3)
            if second<63.5:
                draw.rectangle((90,1270,930,1360),fill=BG)
        return result

    def depth(self,second):
        result=shell("03 / BAJO LA SUPERFICIE","Mira dónde empieza.","Esquema explicativo · sin escala física",size=56)
        draw=ImageDraw.Draw(result)
        panel(draw,(90,360,930,1180),TEAL)
        draw.rectangle((130,570,890,1100),fill="#263d46")
        draw.line((130,570,890,570),fill=TEAL,width=5)
        write(draw,(150,405),"SUPERFICIE",26,fill=MUTED)
        hypo=ease(second,68.9,.45)
        if hypo:
            layer=result.copy()
            d=ImageDraw.Draw(layer)
            d.ellipse((434,914,486,966),fill=GOLD,outline=TEXT,width=2)
            write(d,(225,1040),"Hipocentro",47,fill=GOLD,serif=True)
            write(d,(195,1110),"Donde comienza la ruptura",31)
            reveal(result,layer,(130,890,890,1170),hypo)
        epi=ease(second,73.1,.4)
        if epi:
            layer=result.copy()
            d=ImageDraw.Draw(layer)
            d.ellipse((447,557,473,583),fill=TEAL)
            write(d,(255,477),"Epicentro",47,fill=TEAL,serif=True)
            for y in range(594,920,26):
                d.line((460,y,460,y+12),fill=MUTED,width=3)
            reveal(result,layer,(130,470,580,925),epi)
        amount=ease(second,76.4,.75)
        draw=ImageDraw.Draw(result)
        if amount:
            end=590+(940-590)*amount
            draw.line((640,590,640,end-14),fill=GOLD,width=4)
            draw.polygon([(640,end),(630,end-18),(650,end-18)],fill=GOLD)
            if amount>.6:
                write(draw,(677,744),"Profundidad",25,fill=GOLD)
                write(draw,(677,782),"en km",25,fill=GOLD)
        panel(draw,(90,1210,930,1410))
        write(draw,(115,1225),"REFERENCIA GENERAL · USGS",23,fill=MUTED)
        for title,label,y in [("Superficial","0 a menos de 70 km",1270),
                              ("Intermedio","70 a menos de 300 km",1310),
                              ("Profundo","300 a unos 700 km",1350)]:
            write(draw,(115,y),title,27)
            write(draw,(390,y),label,27,fill=MUTED)
        return result

    def profile_base(self):
        key=("profiles",)
        if key not in self.cache:
            result=shell("04 / CAMBIA EL PUNTO DE VISTA","Ahora míralos de lado.","Toda la región · proyecciones, no cortes de una falla",size=53)
            draw=ImageDraw.Draw(result)
            for field,limits,box,title,ticks in self.plots:
                x0,y0,x1,y1=box
                write(draw,(90,y0-68),title,30,fill=TEAL)
                write(draw,(752,y0-63),"km ↓",25,fill=MUTED)
                draw.rectangle(box,fill="#243c46",outline=LINE,width=2)
                for depth in [0,70,150,300]:
                    _,y=profile_point(limits[0],depth,limits,box)
                    draw.line((x0,y,x1,y),fill=LINE,width=2)
                    write(draw,(92,y-17),str(depth),25,fill=MUTED)
                for tick in ticks:
                    x,_=profile_point(tick,0,limits,box)
                    draw.line((x,y0,x,y1),fill=LINE,width=1)
                    label=f"{abs(tick)}°"+(" O" if field=="longitude" else " S" if tick<0 else " N" if tick>0 else "")
                    draw.text((x-28,y1+10),label,font=font(25),fill=MUTED)
                layer=Image.new("RGBA",result.size,(0,0,0,0))
                points=ImageDraw.Draw(layer)
                for row in self.known.itertuples():
                    x,y=profile_point(getattr(row,field),row.depth,limits,box)
                    r=magnitude_size(row.magnitude)*1.4/2
                    points.ellipse((x-r,y-r,x+r,y+r),fill=depth_color(row.depth)+(210,),outline=(220,226,211,90))
                crop=layer.crop(box)
                result.paste(crop,box[:2],crop)
            self.cache[key]=result
        return self.cache[key]

    def profile(self,second):
        result=shell("04 / CAMBIA EL PUNTO DE VISTA","Ahora míralos de lado.","Toda la región · proyecciones, no cortes de una falla",size=53)
        source=self.profile_base()
        reveal(result,source,(90,320,930,755),ease(second,81.4,.65))
        reveal(result,source,(90,760,930,1195),ease(second,89.0,.55))
        draw=ImageDraw.Draw(result)
        if 87.35<=second<89:
            draw.rectangle(self.plots[0][2],outline=TEAL,width=3)
        if 89<=second<90.95:
            draw.rectangle(self.plots[1][2],outline=TEAL,width=3)
        counts=depth_counts(self.df)
        panel(draw,(90,1225,930,1410),GOLD)
        if second<93.05:
            write(draw,(115,1255),"Profundidad hacia abajo",35,fill=GOLD)
            write(draw,(115,1322),"No dibujamos una falla ni una placa.",29,fill=MUTED)
        else:
            write(draw,(115,1244),f"Máximo reportado: {self.max_row.depth:g} km",37,fill=GOLD)
            if second<99.55:
                write(draw,(115,1304),f"{counts['shallow']} superficiales · {counts['intermediate']} intermedios",28)
                write(draw,(115,1355),"En esta selección · no todos los sismos del país",25,fill=MUTED)
            else:
                draw.polygon([(126,1336),(140,1350),(126,1364),(112,1350)],fill=depth_color(float("nan")))
                write(draw,(163,1305),"1 sin profundidad: no se proyecta",31)
                write(draw,(163,1355),"No lo colocamos a cero.",27,fill=MUTED)
            for field,limits,box,_,_ in self.plots:
                x,y=profile_point(self.max_row[field],self.max_row.depth,limits,box)
                radius=magnitude_size(self.max_row.magnitude)*1.4/2+8
                draw.ellipse((x-radius,y-radius,x+radius,y+radius),outline=GOLD,width=3)
        return result

    def action(self,second):
        result=shell("05 / INFORMACIÓN + ACCIÓN","Conocer para prepararnos.","No para adivinar el próximo terremoto",size=49)
        draw=ImageDraw.Draw(result)
        if second<113.7:
            panel(draw,(90,465,930,1170),GOLD)
            write(draw,(145,602),"El mapa no es",57,serif=True)
            write(draw,(145,681),"una predicción.",57,fill=GOLD,serif=True)
            write(draw,(145,925),"La preparación sí está",39)
            write(draw,(145,986),"en nuestras manos.",39)
        else:
            for i,(title,detail,start) in enumerate([("CONVERSA","Acuerden qué hacer en familia.",113.7),
                                                  ("PRACTICA","Participen en simulacros.",115.18),
                                                  ("PREPARA","Tengan un kit de emergencia.",116.55)]):
                y=370+i*340
                layer=result.copy()
                d=ImageDraw.Draw(layer)
                panel(d,(90,y,930,y+280),TEAL)
                write(d,(120,y+34),f"0{i+1}",58,fill=TEAL,serif=True)
                write(d,(245,y+47),title,44,serif=True)
                write(d,(120,y+179),detail,33,fill=MUTED)
                reveal(result,layer,(90,y,930,y+281),ease(second,start,.32))
            write(ImageDraw.Draw(result),(90,1368),"Guía de preparación · IG-EPN",26,fill=MUTED)
        return result

    def closing(self,second):
        result=shell("06 / LA IDEA QUE TE LLEVAS","La tierra se mueve.","",size=57)
        draw=ImageDraw.Draw(result)
        if second>=119.55:
            write(draw,(90,267),"Prepararnos importa.",53,fill=GOLD,serif=True)
        panel(draw,(90,410,930,735),TEAL)
        write(draw,(120,449),"2661",84,serif=True)
        write(draw,(120,568),"registros USGS · M ≥ 4",35)
        write(draw,(120,650),"1900–2025 · no incluye 2026",29,fill=MUTED)
        panel(draw,(90,775,930,990),TEAL)
        write(draw,(120,801),"EL ALCANCE",25,fill=TEAL)
        write(draw,(120,859),"Continente, océano y zonas vecinas.",31)
        write(draw,(120,920),"Sin Galápagos; no sigue fronteras.",29,fill=MUTED)
        panel(draw,(90,1030,930,1275),GOLD)
        write(draw,(120,1056),"LOS LÍMITES",25,fill=GOLD)
        write(draw,(120,1116),"Archivo incompleto y revisable.",32)
        write(draw,(120,1172),"Magnitudes originales, no todas Mw.",29,fill=MUTED)
        write(draw,(120,1222),"No predice sismos ni muestra daños.",28,fill=MUTED)
        write(draw,(90,1306),"USGS · Natural Earth · preparación IG-EPN",26,fill=MUTED)
        write(draw,(90,1352),"Fuentes en descripción · voz IA: elevenlabs.io",25,fill=MUTED)
        return result

    def render(self,source,kind,year,second,scene_start,overall):
        if kind in ["year","hold"]:
            result=self.map_layout(source,year,kind=="hold",second)
        elif kind=="guide":
            result=self.guide(second)
        elif kind=="depth":
            result=self.depth(second)
        elif kind=="profile":
            result=self.profile(second)
        elif kind=="action":
            result=self.action(second)
        else:
            result=self.closing(second)
        # Brief content-only entrance; footer, captions and the catalog map stay fixed.
        if kind not in ["year","hold"]:
            entrance=ease(second,scene_start,.25)
            if entrance<1:
                clean=Image.new("RGB",(1080,1920),BG)
                reveal(clean,result,(90,300,930,1411),entrance)
                result.paste(clean.crop((90,300,930,1411)),(90,300))
        result=self.captions.draw(result,second)
        draw=ImageDraw.Draw(result)
        draw.line((90,1690,930,1690),fill=LINE,width=4)
        draw.line((90,1690,90+840*overall,1690),fill=GOLD,width=4)
        return result
