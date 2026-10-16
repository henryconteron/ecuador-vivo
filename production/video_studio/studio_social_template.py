"""Reference-led social composition over existing maps and immutable results.

Only presentation: transforms, local fonts, vector icons and scalar bindings.
No aggregation, provider access, mutation of datasets, or changes to map pixels.
"""
import datetime as dt
import uuid
from output_profiles import profile_for, contain_bounds
from studio_model import Scene, Element
from studio_typography import studio_font
from studio_editorial import INK, WHITE, MINT, BLUE, MUTED, LINE, DISPLAY, BODY


def regions(profile):
    """Authoring coordinates; landscape is recomposed, not a cropped portrait."""
    portrait=profile.height/profile.width >= 1.45
    # Tall format uses the user's composition, with breathing room for social UI.
    boxes=({
        'brand':(64,100,850,42),'brand_rule':(590,120,74,2),
        'count':(64,154,220,112),'title_first':(284,154,700,112),
        'title':(64,266,920,114),'subtitle_bg':(60,389,920,66),
        'subtitle':(80,400,870,46),'calendar':(64,478,48,55),
        'date':(142,476,492,76),'date_rule':(650,475,2,64),
        'play':(690,475,68,68),'counter_bg':(780,474,204,70),
        'counter':(790,489,184,43),'continent':(32,530,1000,950),
        'galapagos':(64,635,175,190),'gal_label':(64,820,175,34),
        'legend_static':(64,1472,920,136),'legend_note':(64,1604,920,30),
        'footer_line':(64,1660,920,2),'source_icon':(64,1688,48,66),
        'source':(132,1685,476,106),'footer_separator':(624,1687,2,102),
        'author_icon':(646,1686,57,48),'author':(720,1685,264,44),
        'qualification':(720,1730,264,33),'social':(720,1766,264,58),
        'tiktok':(683,1766,27,27),'instagram':(683,1797,27,27),
    } if portrait else {
        'brand':(70,55,1100,44),'brand_rule':(640,76,92,2),
        'count':(70,123,200,108),'title_first':(280,123,1520,108),
        'title':(70,233,1760,106),'subtitle_bg':(66,348,1760,58),
        'subtitle':(86,359,1720,39),'calendar':(1210,453,46,54),
        'date':(1276,448,550,76),'date_rule':(1208,540,618,2),
        'play':(1214,568,60,60),'counter_bg':(1298,568,340,62),
        'counter':(1310,580,316,38),'continent':(198,430,850,503),
        'galapagos':(70,488,168,174),'gal_label':(72,670,160,31),
        'legend_static':(1208,680,618,128),'legend_note':(1208,811,618,31),
        'footer_line':(70,954,1756,2),'source_icon':(70,978,42,58),
        'source':(128,971,1000,84),'footer_separator':(1176,976,2,76),
        'author_icon':(1208,979,52,40),'author':(1280,975,546,34),
        'qualification':(1280,1012,300,30),'social':(1588,1012,238,30),
        'tiktok':(1208,1021,22,25),'instagram':(1240,1021,25,25),
    })
    base_w,base_h=(1080,1920) if portrait else (1920,1080)
    sx,sy=profile.width/base_w,profile.height/base_h
    return {k:{'x':x*sx,'y':y*sy,'width':w*sx,'height':h*sy} for k,(x,y,w,h) in boxes.items()}


def _date(value,year=False):
    if not value:return 'Sin datos'
    date=dt.date.fromisoformat(value)
    month=('ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic')[date.month-1]
    return f'{date.day:02d} {month}'+(f' {date.year}' if year else '')


def scenes(project,record,manifest,snapshot=None,*,endcard_duration=5.):
    profile=profile_for(project['studio']['output_profile']);slots=regions(profile)
    portrait=profile.height/profile.width>=1.45
    base_w,base_h=(1080,1920) if portrait else (1920,1080)
    sx,sy=profile.width/base_w,profile.height/base_h;scale=min(sx,sy)
    def box(x,y,w,h):return dict(x=x*sx,y=y*sy,width=w*sx,height=h*sy)
    elements=[]; iid='rain.'+uuid.uuid4().hex
    def add(key,kind,region,style,*,channel=None,binding=None,visible=True):
        names={'brand':'Marca','brand_rule':'Separador · marca','title':'Titular · variable',
            'title_first':'Titular · periodo','title_tail':'Titular · territorio','count':'Número de fechas',
            'subtitle':'Subtítulo','subtitle_bg':'Fondo · subtítulo','date':'Fecha científica',
            'calendar':'Icono · calendario','counter':'Contador científico','counter_bg':'Marco · contador',
            'play':'Icono · reproducción','continent':'Ecuador continental','galapagos':'Galápagos',
            'gal_label':'Etiqueta · Galápagos','legend_static':'Escala compartida','legend_note':'Nota · escala',
            'source':'Fuentes y método','author':'Autoría','qualification':'Formación','social':'Redes sociales',
            'card_title':'Título · métricas','card_title_accent':'Título · finales','card_period':'Periodo resumido',
            'rank_0':'Ranking · provincias 1–12','rank_1':'Ranking · provincias 13–24'}
        e=Element(id='element.'+uuid.uuid4().hex,type=kind,name=key,
            transform={k:max(1,round(v,2)) if k in ('width','height') else round(v,2) for k,v in region.items()},style=style,
            z_index=len(elements),visible=visible,data_binding=binding,
            temporal_binding={'instance_id':iid,'channel':channel} if channel else None).to_dict()
        e.update(template_key=key,template_default_text=style.get('text'))
        e['name']=names.get(key,key.replace('_',' · '))
        elements.append(e);return e
    def text(key,content,region,size=32,color=WHITE,*,display=False,align='left',channel=None,gradient=None):
        style=dict(font_size=max(8,min(400,round(size*scale))),color=color,
                   font_family=DISPLAY if display else BODY,alignment=align,bold=display)
        if channel=='date':style['date_format']='long_es'
        if channel is None:style['text']=content
        if gradient:style['gradient']=gradient
        return add(key,'text',region,style,channel=channel)
    def shape(key,region,kind='line',color=LINE,**style):
        return add(key,'shape',region,{'shape':kind,'fill':color,**style})
    def metric(key,region,result,color=WHITE,size=64):
        return add(key,'metric',region,{'visualization':{'kind':'metric','style':{
            'presentation':'editorial_value','font_family':DISPLAY,'font_size':max(8,min(200,round(size*scale))),
            'color':color,'text':WHITE,'decimals':1,'title':''}}},
            binding={'result_id':result['id'],'field':'value'})
    generic=snapshot is None
    if generic:
        from studio_sig_timelapse import gaps
        dates=[o['date'] for o in manifest['observations']]
        cadence=manifest['geographic_binding'].get('cadence','irregular')
        summary={'days':len(dates),'observed_period':{'start':dates[0],'end':dates[-1]},
                 'period_complete':cadence=='daily' and not gaps(dates,cadence)}
        results={}
    else:summary=snapshot['summary'];results=snapshot['results']
    count=summary['days'];period=summary['observed_period']
    complete=summary.get('period_complete',False)
    year=period['start'][:4];annual=(period['start']==year+'-01-01' and period['end']==year+'-12-31' and complete)
    brand=project.get('brand') or 'ECUADOR VIVO / ANDES PULSO'
    author=project.get('author_name') or project.get('author') or 'Autoría · editable'
    qualifications=project.get('credits') or 'Ing. Geociencias'
    handles=[h for h in (project.get('tiktok'),project.get('instagram')) if h]
    social=('\n' if portrait else ' · ').join(handles) or project.get('social_handle') or project.get('social') or '@AndesPulso'
    def footer(*,card=False):
        # All lines/icons remain individually editable. No additional source claims.
        text('brand',brand.upper(),slots['brand'],34,MINT)
        shape('brand_rule',slots['brand_rule'],color='#7e9aa6')
        shape('footer_line',slots['footer_line'],color='#5d8291')
        shape('source_icon',slots['source_icon'],'icon.database',WHITE)
        credit=('24 provincias del Ecuador\nCHIRPS v2 · UCSB Climate Hazards Center\n0.05° nativos (~5.6 km) · geoBoundaries CC BY 4.0\nContinente + Galápagos; reubicado a distinta escala' if card else
                'Fuente: CHIRPS v2\nUCSB Climate Hazards Center · 0.05° (~5.6 km)\ngeoBoundaries CC BY 4.0 · continente + Galápagos\nIslas reubicadas; suavizado solo visual')
        if generic:
            from studio_territory import territory_label
            binding=manifest['geographic_binding'];options=binding['presentation']
            source=project['studio']['geography']['sources'][binding['sources'][0]['id']]
            citation=source['provenance']['citation'].split(' · original gzip SHA256 ')[0]
            resolution=source['raster']['transform']
            credit=('Fuente: '+citation.split(',')[0][:55]+'\n'+
                (f'Grilla nativa {abs(resolution[0]):.3g}° × {abs(resolution[4]):.3g}°' if '4326' in source['native_crs'] else 'Resolución nativa conservada')+'\n'+
                ('geoBoundaries CC BY 4.0 · ' if options['territory']!='view' else '')+territory_label(options)+'\n'+
                ('Suavizado solo visual' if options['resampling']=='bilinear' else 'Celdas originales'))
        text('source',credit,slots['source'],25,MUTED)
        shape('footer_separator',slots['footer_separator'],color='#5d8291')
        shape('author_icon',slots['author_icon'],'icon.mountain',WHITE)
        text('author',author,slots['author'],31,display=True)
        text('qualification',qualifications,slots['qualification'],29,MUTED)
        shape('tiktok',slots['tiktok'],'icon.tiktok',WHITE)
        shape('instagram',slots['instagram'],'icon.instagram',WHITE)
        text('social',social,slots['social'],25,MINT)
    footer()
    text('count',str(count),{**slots['count'],'y':slots['count']['y']+20*sy},144,MINT,display=True)
    heading=slots['title_first'].copy()
    # Match the ink width, so 7 / 31 / 366 all sit on the same headline baseline.
    count_pixels=min(round(144*scale),round(slots['count']['height']-4*scale))
    heading['x']=slots['count']['x']+studio_font(max(8,count_pixels),family=DISPLAY,bold=True).getlength(str(count))+24*sx
    heading['width']=slots['title']['x']+slots['title']['width']-heading['x']
    text('title_first','DÍAS DE' if complete else 'FECHAS DE',heading,130,display=True)
    title=slots['title'];title_pixels=min(round(132*scale),round(title['height']-4*scale))
    word='LLUVIA';tail='EN ECUADOR'
    if generic:
        binding=manifest['geographic_binding'];options=binding['presentation']
        source=project['studio']['geography']['sources'][binding['sources'][0]['id']]
        variable=source['variable'];lower=variable.lower()
        word=('TEMPERATURA' if source['semantics']=='temperature' else 'LLUVIA' if source['semantics']=='precipitation' else
              'VIENTO' if 'viento' in lower or 'wind' in lower else 'HUMEDAD' if 'humedad' in lower else variable.upper())
        territory=options.get('province') or ('ECUADOR' if options['territory'] in ('ecuador','continent') else 'GALÁPAGOS' if options['territory']=='galapagos' else 'LA REGIÓN')
        tail='EN '+territory.upper()
        font=studio_font(max(8,title_pixels),family=DISPLAY,bold=True)
        title_pixels=max(8,min(title_pixels,int(title_pixels*(title['width']-24*sx)/font.getlength(word+' '+tail))))
    word_width=studio_font(max(8,title_pixels),family=DISPLAY,bold=True).getlength(word)
    text('title',word,{**title,'width':word_width+4*sx},title_pixels/scale,BLUE,display=True,gradient=[BLUE,'#d4edf5'])
    text('title_tail',tail,{**title,'x':title['x']+word_width+22*sx,'width':max(1,title['width']-word_width-22*sx)},title_pixels/scale,display=True)
    shape('subtitle_bg',slots['subtitle_bg'],'rounded_rectangle','#192d39')
    subtitle=(f'Así cambió la precipitación día a día durante {year}.' if annual else
              f'Así cambió la lluvia del {_date(period["start"])} al {_date(period["end"],True)}.')
    if generic:subtitle=f'{manifest["variable"]} · {_date(period["start"])} — {_date(period["end"],True)}.'
    text('subtitle',subtitle,slots['subtitle'],39)
    shape('calendar',slots['calendar'],'calendar',WHITE)
    text('date','',slots['date'],66,display=True,channel='date')
    shape('date_rule',slots['date_rule'],color='#526f7c')
    shape('play',slots['play'],'play',WHITE)
    shape('counter_bg',slots['counter_bg'],'pill_outline',outline='#7795a1')
    text('counter','',slots['counter'],36,MINT,display=True,channel='counter')
    main=contain_bounds(record['layers']['continent']['size'],slots['continent'])
    continent=add('continent','map',main,{'fit':'contain','opacity':manifest['geographic_binding']['opacity']},channel='continent')
    continent['group_id']='group.'+uuid.uuid4().hex
    if not generic or options['territory']=='ecuador':
        add('galapagos','map',contain_bounds(record['layers']['galapagos']['size'],slots['galapagos']),{'fit':'contain'},channel='galapagos')
        text('gal_label','Galápagos',slots['gal_label'],28,MUTED)
    west,south,east,north=manifest['layers']['continent']['bbox']
    for name,lon,lat in [('Quito',-78.4678,-.1807),('Tena',-77.8129,-.9948),('Guayaquil',-79.8891,-2.1709),('Cuenca',-79.0045,-2.9001)]:
        if generic:
            if not west<=lon<=east or not south<=lat<=north:continue
            if options['territory']!='view':
                from shapely.geometry import shape as geographic_shape,Point
                from studio_territory import territory_payload
                if not any(geographic_shape(f['geometry']).covers(Point(lon,lat)) for f in territory_payload(options)['features']):continue
        x=main['x']+(lon-west)/(east-west)*main['width']; y=main['y']+(north-lat)/(north-south)*main['height']
        point=shape('Ciudad · '+name,dict(x=x-8*scale,y=y-8*scale,width=16*scale,height=16*scale),'marker',WHITE)
        label=text('Etiqueta · '+name,name,dict(x=x+13*scale,y=y-28*scale,width=174*scale,height=58*scale),36,display=True)
        for e in (point,label):e.update(cartographic_point={'longitude':lon,'latitude':lat},group_id=continent['group_id'])
    add('legend_static','legend',slots['legend_static'],{'fit':'contain'},channel='legend_static')
    text('legend_note','Escala común en todas las fechas · resolución nativa conservada' if generic else '120+ indica saturación del color · resolución nativa conservada',slots['legend_note'],24,MUTED)
    main_scene=Scene(id='scene.'+uuid.uuid4().hex,name=(manifest['variable'] if generic else 'Lluvia')+' · mapa temporal editable',duration=record['duration'],background=INK,
        elements=elements,map_instances={iid:{'asset_id':'map.'+record['manifest_sha256'],'trim_in_frame':0,'trim_out_frame':record['total_frames'],'loop':False}}).to_dict()
    main_scene.update(**({'series_template':'map'} if generic else {'rainfall_template':'map'}),editorial_style='ecuador-vivo-social-v2')
    if generic:
        main_scene['template_profile']={'width':profile.width,'height':profile.height}
        return main_scene

    elements=[]; footer(card=True)
    # Portrait follows the supplied reference: four columns, then two full-width rankings.
    text('card_title','MÉTRICAS',box(64,160,484,118) if portrait else box(70,125,650,106),116,display=True)
    text('card_title_accent','FINALES',box(536,180,448,118) if portrait else box(736,145,1090,106),116,BLUE,display=True,gradient=[BLUE,'#d4edf5'])
    shape('card_subtitle_bg',box(60,290,920,60) if portrait else box(66,242,1760,56),'rounded_rectangle','#192d39')
    text('card_period',f'Así se comportó la lluvia · {_date(period["start"])} — {_date(period["end"],True)}.',
         box(80,300,870,43) if portrait else box(86,250,1720,41),35)
    panel_boxes=[(60,372,920,342),(60,738,920,442),(60,1202,920,442)] if portrait else [(66,322,1760,245),(66,590,866,336),(956,590,870,336)]
    def section(index,title,note):
        x,y,w,h=panel_boxes[index-1]; shape('panel_'+str(index),box(x,y,w,h),'panel',outline=LINE)
        shape('badge_'+str(index),box(x+24,y+22,48,48),'rounded_rectangle',MINT)
        text('section_number_'+str(index),f'{index:02}',box(x+24,y+23,48,46),38,INK,display=True,align='center')
        shape('section_rule_'+str(index),box(x+94,y+29,1,32),color='#638594')
        tw=470 if portrait else 440
        text('section_'+str(index),title,box(x+116,y+20,tw,53),45,display=True)
        text('section_note_'+str(index),note,box(x+tw+132,y+29,w-tw-152,43),25,MUTED)
    section(1,f'{year} EN CIFRAS' if annual else f'{count} DÍAS EN CIFRAS','Resumen del periodo observado.')
    section(2,'¿DÓNDE LLOVIÓ MÁS?','Provincias · ranking 1–12')
    section(3,'PROVINCIAS 13–24','Continuación del ranking.')
    x,y,pw,ph=panel_boxes[0]; cell=(pw-40)/4
    for i,(icon,key,label) in enumerate((('cloud','peak_mean','Día con mayor\nmedia nacional'),('calendar','sum_means','Acumulado medio\ndel periodo'),('bars','mean_period','Promedio diario\nnacional'),('peak','peak_cell','Máximo diario\nde celda nativa'))):
        cx=x+20+(i+.5)*cell
        if i:shape('metric_divider_'+str(i),box(x+20+i*cell,y+96,1,ph-126),color='#315463')
        icon_y=y+87 if portrait else y+75; icon_size=78 if portrait else 60
        shape('metric_icon_'+key,box(cx-icon_size/2,icon_y,icon_size,icon_size),'icon.'+icon,WHITE)
        value_y=y+171 if portrait else y+141; value_h=62 if portrait else 53
        if key=='peak_mean':
            text('peak_day',_date(summary.get('peak_date')),box(cx-cell*.45,value_y,cell*.9,value_h),56,display=True,align='center')
            metric('metric_'+key,box(cx-cell*.46,y+280 if portrait else y+207,cell*.92,44 if portrait else 30),results[key],MINT,40)
        else:metric('metric_'+key,box(cx-cell*.46,value_y,cell*.92,value_h),results[key],WHITE,55)
        text('label_'+key,label,box(cx-cell*.45,y+232 if portrait else y+186,cell*.9,48 if portrait else 42),20,align='center')
        if key=='peak_cell':text('peak_cell_date',_date(summary.get('peak_pixel_date'),True),box(cx-cell*.46,y+302 if portrait else y+220,cell*.92,30 if portrait else 22),25 if portrait else 19,MINT,align='center')
    rank_rows=summary['province_rank']; axis_max=max([r['value'] for r in rank_rows if r['value'] is not None]+[1])*1.22
    for index in range(2):
        x,y,w,h=panel_boxes[index+1]
        add('rank_'+str(index),'ranking',box(x+24,y+88,w-48,h-104),{'visualization':{
            'kind':'ranking','offset':index*12,'top_n':12,'include_missing':True,
            'style':{'presentation':'editorial_ranking','title':f'Acumulado del periodo ({results["province_rank"]["units"]})',
                     'font_size':max(8,round((29 if portrait else 24)*scale)),'decimals':1,
                     'axis_domain':[0,axis_max],'font_family':BODY,'color':BLUE,'text':WHITE}}},
            binding={'result_id':results['province_rank']['id'],'field':'rows'})
    warnings=' · '.join(summary.get('warnings',[]))
    if warnings:
        # Method warnings survive the template; never replace absence with a zero.
        text('coverage',warnings,box(64,1808,920,78) if portrait else box(70,1054,1756,24),23 if portrait else 18,'#ffd18c')
    card=Scene(id='scene.'+uuid.uuid4().hex,name='Métricas · 24 provincias · editable',duration=endcard_duration,background=INK,elements=elements).to_dict()
    card.update(rainfall_template='endcard',editorial_style='ecuador-vivo-social-v2')
    for scene in (main_scene,card):scene['template_profile']={'width':profile.width,'height':profile.height}
    return main_scene,card
