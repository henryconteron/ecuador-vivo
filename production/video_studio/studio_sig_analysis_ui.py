"""One contextual job monitor; polling never reruns the map fragment."""
import streamlit as st
from studio_sig_analysis_jobs import start,status,cancel,accept,find_pending,handled

def queue(session,request):
    key=session.key+'_sig_analysis_job';previous=session.state.get(key) or find_pending(session.project)
    if previous and status(previous)['state'] in ('queued','running','cancelling','complete'):
        raise ValueError('Hay un resultado pendiente. Abre Procesos para incorporarlo o descartarlo antes de iniciar otro.')
    job=start(session.project,request);session.state[key]=str(job)
    from studio_sig_workspace import choose_tool
    choose_tool(session,'Procesos')

@st.fragment(run_every='2s')
def monitor(session):
    key=session.key+'_sig_analysis_job';job=session.state.get(key) or find_pending(session.project)
    if not job:st.caption('No hay análisis pendientes en este proyecto.');return
    session.state[key]=str(job)
    try:
        info=status(job);state=info['state']
        st.caption({'queued':'En cola','running':'Calculando','cancelling':'Cancelando','complete':'Listo para incorporar','failed':'No completado','cancelled':'Cancelado'}[state])
        st.markdown(info['message'])
        if state in ('queued','running','cancelling'):
            if info.get('total'):st.progress(min(1,info['completed']/info['total']))
            st.caption('Puedes cerrar esta ventana y navegar. Los originales no se modifican. La cancelación se comprueba entre entidades o bloques; una llamada GEOS en curso debe finalizar.')
            if st.button('Cancelar análisis',key='sig_analysis_cancel',disabled=state=='cancelling'):cancel(job);st.rerun(scope='fragment')
        if state=='complete':
            st.caption('Se añade una capa nueva sin reemplazar tu encuadre ni las ediciones del video.')
            if st.button('Incorporar resultado',type='primary',key='sig_analysis_accept'):
                candidate,_=accept(job,session.project);session.commit(candidate);handled(job,'applied')
                session.state.pop(key,None)
                from studio_sig_workspace import choose_tool,notify
                choose_tool(session,'Propiedades');notify(session,'Resultado del análisis incorporado.');st.rerun()
        if state not in ('queued','running','cancelling') and st.button('Descartar de la lista',key='sig_analysis_dismiss'):
            handled(job,'dismissed');session.state.pop(key,None);st.rerun()
    except (ValueError,TypeError,KeyError,OSError) as error:st.error(str(error))
