"""Serve only local scientific-editor fonts; no source, projects or user paths."""
from pathlib import Path
from starlette.responses import FileResponse,Response

FONT_ROOT=Path(__file__).parent/'ecuador-vivo-scientific-tools/ecuador_vivo_scientific_tools/frontend/build'

async def font_response(request):
    relative=request.path_params.get('path','')
    if not relative.startswith('fonts/') or '\\' in relative or '..' in relative.split('/'):
        return Response(status_code=404)
    path=(FONT_ROOT/relative).resolve()
    if not path.is_relative_to(FONT_ROOT.resolve()) or path.suffix.lower() not in ('.woff2','.woff','.ttf','.otf') or not path.is_file():
        return Response(status_code=404)
    return FileResponse(path,headers={'Cache-Control':'public, max-age=3600','X-Content-Type-Options':'nosniff'})
