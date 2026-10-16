"""Exercise retained document adapters without resurrecting retired Home buttons."""
def open_document_adapter(app):
    from model import default_project
    if app.session_state['project'] is None:
        app.session_state['project'] = default_project()
    app.session_state['section'] = 'Editor'
    app.session_state['studio_phase'] = 'Datos'
    return app.run()


def open_sig_tool(app, document, tool):
    from studio_project import workspace_key
    key = workspace_key(document)
    preferences = dict(app.session_state[key + '_sig_ui']) if key + '_sig_ui' in app.session_state else {'left': True, 'right': True, 'dock': False}
    preferences.update(tool=tool)
    app.session_state[key + '_sig_ui'] = preferences
    app.session_state[key + '_sig_dialog'] = 'tools'
    return app.run()
