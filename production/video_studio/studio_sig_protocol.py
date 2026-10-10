"""Presentation intents over canonical WorkspaceSession transactions.

Each envelope carries all unconfirmed intents. Overlapping envelopes can be
coalesced by Streamlit without dropping a gesture; replay never commits twice.
Only this client's uninterrupted commit chain may rebase an older envelope.
"""
import re
from studio_sig_layers import layer_command


def apply_map_intents(session, message):
    if not isinstance(message, dict):raise ValueError('Comando de mapa inválido.')
    client=message.get('client');base=message.get('version');sequence=message.get('sequence')
    commands=message.get('commands')
    if (not isinstance(client,str) or not re.fullmatch('[a-f0-9]{32}',client)
            or type(base) is not int or type(sequence) is not int or sequence<1
            or not isinstance(commands,list) or not 0<len(commands)<=64):
        raise ValueError('Secuencia de mapa inválida; actualiza la vista antes de reintentar.')
    ledger_key=session.key+'_sig_clients'
    ledger=dict(session.state.get(ledger_key,{}));previous=ledger.get(client)
    last=previous['sequence'] if previous else 0
    numbers=[entry.get('sequence') for entry in commands if isinstance(entry,dict)]
    if (len(numbers)!=len(commands) or any(type(n) is not int or n<1 for n in numbers)
            or numbers!=list(range(numbers[0],sequence+1))):
        raise ValueError('La secuencia de gestos está incompleta.')
    if previous and sequence<=last:
        # A late duplicate must not roll the viewer back after undo or navigation.
        return {**previous,'client':client,'version':session.version,'status':'saved'}
    if base!=session.version and not (previous and session.version==previous['version']
            and previous['origin_version']<=base<=previous['version']):
        raise ValueError('El proyecto cambió fuera del mapa; revisa los gestos pendientes antes de reintentar.')
    pending=[entry for entry in commands if entry['sequence']>last]
    if not pending or pending[0]['sequence']!=last+1:
        raise ValueError('Faltan gestos anteriores; no se aplicó ningún cambio.')
    candidate=session.project
    for entry in pending:
        if entry.get('action') not in ('view','select','clear_selection','raster_date'):
            raise ValueError('Este canal solo admite cámara y selección.')
        candidate=layer_command(candidate,entry)
    # All commands validated before the single existing durable transaction.
    if candidate!=session.project:session.commit(candidate)
    accepted={'sequence':sequence,'version':session.version,
              'origin_version':previous['origin_version'] if previous else base,
              'revision':session.project.get('project_meta',{}).get('revision',0)}
    ledger[client]=accepted
    while len(ledger)>4:ledger.pop(next(iter(ledger)))
    session.state[ledger_key]=ledger
    return {**accepted,'client':client,'status':'saved'}
