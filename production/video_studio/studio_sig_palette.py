"""Presentation-only palettes. Numeric knots and scientific sources are unchanged."""
PALETTES={
 'andes':{'label':'Ecuador Vivo · multicolor','colors':['#073047','#086b9e','#28b6cd','#65d5c0','#c7e6a0','#ffdb63','#ff7845','#ce2060']},
 'viridis':{'label':'Viridis · secuencial','colors':['#440154','#46327e','#365c8d','#277f8e','#1fa187','#4ac16d','#a0da39','#fde725']},
 'thermal':{'label':'Temperatura · azul a rojo','colors':['#244b9b','#3786bc','#70b9d3','#bddfe8','#f5e9b6','#f4bc6d','#e47742','#bd2634']},
 'ocean':{'label':'Océano · secuencial azul','colors':['#eaf7fb','#cae9f2','#9bd5e6','#64b8d6','#3596be','#1773a2','#0e517e','#073047']},
}

def validate_palette(value):
    if not isinstance(value,str) or value not in PALETTES:raise ValueError('Paleta temporal desconocida.')
    return value

def change_palette(project,value):
    from studio_sig_layers import workspace_for,layer_command
    time=workspace_for(project).get('raster_time')
    if not time:raise ValueError('Prepara primero una serie temporal.')
    return layer_command(project,{'action':'raster_time','value':{**time,'palette':validate_palette(value)}})
