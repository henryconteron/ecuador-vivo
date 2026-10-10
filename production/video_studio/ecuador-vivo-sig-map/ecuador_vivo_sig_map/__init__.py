"""Pinned CCv2 OpenLayers consumer; official template packaging."""
import streamlit as st

HTML='''
<div id="sig-map">
 <div class="sig-toolbar">
  <button id="sig-zoom-in" title="Acercar" aria-label="Acercar">+</button><button id="sig-zoom-out" title="Alejar" aria-label="Alejar">−</button>
  <button id="sig-fit-all" title="Ajustar todas las capas visibles" aria-label="Ajustar todo">⛶</button><button id="sig-fit-layer" title="Ajustar capa seleccionada" aria-label="Ajustar capa">▣</button>
  <button id="sig-clear" title="Limpiar selección" aria-label="Limpiar selección">×</button>
  <button id="sig-retry" hidden>Reintentar guardado</button><button id="sig-discard" hidden>Descartar gestos pendientes</button>
 </div>
 <div class="sig-viewport">
  <div id="sig-geographic-map" tabindex="0" role="application" aria-label="Mapa SIG interactivo"></div>
  <div id="sig-empty" role="status" hidden><svg viewBox="0 0 48 48" aria-hidden="true"><path d="m8 15 16-8 16 8-16 8-16-8Zm0 9 16 8 16-8M8 33l16 8 16-8"/></svg><h2>Tu mapa empieza con tus datos</h2><p>Importa un GeoJSON para explorar sus capas, seleccionar entidades y consultar atributos.</p><button id="sig-empty-import">Importar datos</button><small>Fuentes, condiciones de uso y geometrías originales vinculadas al proyecto.</small></div>
  <aside id="sig-legend" tabindex="0" aria-label="Leyenda de las capas visibles; desplázate para consultar todas"></aside>
  <div id="sig-output-frame" hidden aria-label="Encuadre geográfico de salida"><span></span><div id="sig-safe-guides"></div></div>
  <output id="sig-raster-query" aria-live="polite"></output>
  <div id="sig-basemap-credit" hidden>© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap contributors</a> · ODbL · mapa base excluido de Studio</div>
  <figure id="sig-temporal-preview" hidden><img alt="Observación cartográfica prerenderizada con su fecha científica"><figcaption></figcaption></figure>
 </div>
 <section id="sig-raster-controls" hidden aria-label="Serie temporal geográfica"><button id="sig-raster-play">Reproducir fechas</button><output id="sig-raster-calendar"></output><input id="sig-raster-date" type="range" min="0" step="1" aria-label="Fecha geográfica"><label><input id="sig-raster-compare" type="checkbox">Comparar</label><label>Comparación <input id="sig-raster-swipe" type="range" min="5" max="95" value="50" aria-label="Separación de las fechas"></label><span id="sig-raster-summary"></span><button id="sig-raster-configure">Periodo y duración</button><button id="sig-raster-send">Enviar a Studio</button></section>
 <div class="sig-status"><span id="sig-coordinate"></span><span id="sig-map-status" role="status"></span></div>
 <div id="sig-engine"></div><div id="sig-notice" role="status"></div>
</div>
'''

def register():
    return st.components.v2.component('ecuador-vivo-sig-map.ecuador_vivo_sig_map',
        js='index-u20.js',css='*.css',html=HTML)

out=register()

def ecuador_vivo_sig_map(*,data,key,on_command_change):
    return out(data=data,key=key,on_command_change=on_command_change,width='stretch',height='content')
