"""Output profiles and reusable adaptive geometry, with editable manual pixels.

Preset dimensions were specified by the product owner. Margins are editorial
recommendations, not claims about current platform UI overlays or upload limits.
"""
from dataclasses import dataclass
import math

PRESETS = {
    'tiktok': ('TikTok', 1080, 1920),
    'instagram_reels': ('Instagram Reels', 1080, 1920),
    'instagram_stories': ('Instagram Stories', 1080, 1920),
    'youtube_shorts': ('YouTube Shorts', 1080, 1920),
    'instagram_portrait': ('Instagram portrait', 1080, 1350),
    'instagram_square': ('Instagram square', 1080, 1080),
    'youtube': ('YouTube', 1920, 1080),
    'presentation': ('Presentación', 1920, 1080),
}


@dataclass(frozen=True)
class OutputProfile:
    id: str
    name: str
    width: int
    height: int
    margin: float
    guide_source: str = 'editorial_recommendation'
    ui_exclusion_zones: tuple = ()

    @property
    def safe_area(self):
        return {'x': self.margin, 'y': self.margin,
                'width': self.width - 2 * self.margin,
                'height': self.height - 2 * self.margin}


def profile_for(value):
    if not isinstance(value, dict):
        raise ValueError('OutputProfile debe ser un objeto.')
    profile_id = value.get('id')
    if profile_id == 'custom':
        width, height = value.get('width'), value.get('height')
        name = 'Tamaño personalizado'
    elif profile_id in PRESETS:
        name, width, height = PRESETS[profile_id]
    else:
        raise ValueError('Perfil de salida desconocido.')
    if (type(width) is not int or type(height) is not int
            or not 160 <= width <= 3840 or not 160 <= height <= 3840
            or width % 2 or height % 2 or width * height > 8_294_400):
        raise ValueError('Usa medidas pares entre 160 y 3840 px, hasta 8,3 MP para H.264.')
    margin = value.get('margin', round(min(width, height) * .04))
    if (isinstance(margin, bool) or not isinstance(margin, (int, float))
            or not math.isfinite(margin) or not 0 <= margin <= min(width, height) / 4):
        raise ValueError('Margen editorial fuera de rango.')
    return OutputProfile(profile_id, name, width, height, margin)


def adaptive_regions(profile):
    """Map/metrics starter layout: reflow by aspect, never scale a tall poster.

    This helper supplies authoring pixels for new Studio scenes. It deliberately
    does not replace existing manual visual_layout or transform legacy artwork.
    """
    area = profile.safe_area
    x, y, width, height = (area[k] for k in ('x', 'y', 'width', 'height'))
    gap = min(width, height) * .025
    # At the 160 px codec minimum, percentage-only credits were shorter than
    # one 8 px line. Reserve two lines without altering existing scenes.
    title_h, source_h = max(24,height * .09), max(24,height * .06)
    body_y = y + title_h + gap
    body_h = height - title_h - source_h - 2 * gap
    regions = {'title': dict(x=x, y=y, width=width, height=title_h),
               'source': dict(x=x, y=y + height - source_h, width=width, height=source_h),
               'body_full': dict(x=x,y=body_y,width=width,height=body_h)}
    aspect = profile.height / profile.width
    if aspect >= 1.5:
        map_h = body_h * .68
        metric_h=body_h-map_h-gap
        if metric_h<80 and body_h>80+gap: metric_h=80;map_h=body_h-metric_h-gap
        regions['map'] = dict(x=x, y=body_y, width=width, height=map_h)
        regions['metric'] = dict(x=x, y=body_y + map_h + gap,
                                 width=width, height=metric_h)
    else:
        map_fraction = .60 if aspect >= 1.15 else .56 if aspect >= .95 else .63
        map_w = width * map_fraction
        metric_w=width-map_w-gap
        if metric_w<80 and body_h>=80 and width>80+gap: metric_w=80;map_w=width-metric_w-gap
        regions['map'] = dict(x=x, y=body_y, width=map_w, height=body_h)
        regions['metric'] = dict(x=x + map_w + gap, y=body_y,
                                 width=metric_w, height=body_h)
    return regions


def contain_bounds(source_size, region):
    """One uniform fit for maps/images; geometry may be placed pixel-perfect."""
    width, height = source_size
    values = (width, height, region['width'], region['height'])
    if any(not math.isfinite(v) or v <= 0 for v in values):
        raise ValueError('Un mapa necesita dimensiones positivas finitas.')
    scale = min(region['width'] / width, region['height'] / height)
    fitted_w, fitted_h = width * scale, height * scale
    return dict(x=region['x'] + (region['width'] - fitted_w) / 2,
                y=region['y'] + (region['height'] - fitted_h) / 2,
                width=fitted_w, height=fitted_h)
