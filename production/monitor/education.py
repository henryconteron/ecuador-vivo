"""Small, independently tested helpers for seismic literacy. No live requests."""
from datetime import timedelta, timezone
from html import escape
import math
import re

MAINLAND_TIME = timezone(timedelta(hours=-5))


def energy_ratio(magnitude_a, magnitude_b):
    """Approximate seismic-energy ratio, NOT shaking or damage at a location."""
    a, b = float(magnitude_a), float(magnitude_b)
    if not all(math.isfinite(m) and 0 <= m <= 10 for m in (a, b)):
        raise ValueError("Magnitudes must be finite and between 0 and 10.")
    return 10 ** (1.5 * (a-b))


def depth_band(depth):
    """Explicit half-open classroom bands; invalid/missing depth stays unknown."""
    try:
        value = float(depth)
    except (ValueError, TypeError):
        return "unknown"
    if not math.isfinite(value) or value < 0:
        return "unknown"
    return "shallow" if value < 70 else "intermediate" if value < 300 else "deep"


def mainland_time(timestamp):
    if timestamp.tzinfo is None:
        raise ValueError("An aware timestamp is required.")
    return timestamp.astimezone(MAINLAND_TIME)


def event_url(event_id):
    value = str(event_id)
    return f"https://earthquake.usgs.gov/earthquakes/eventpage/{value}" if re.fullmatch(r"[A-Za-z0-9_-]{1,80}", value) else None


def depth_svg(depth, english=False):
    value = float(depth)
    if not math.isfinite(value) or not 0 <= value <= 700:
        raise ValueError("Demo depth must be between 0 and 700 km.")
    y = 80 + value/700*230
    surface, origin = ("Surface", "Hypocenter: where rupture starts") if english else ("Superficie", "Hipocentro: aquí empieza la ruptura")
    caption = f"Epicenter above a hypocenter {value:g} km deep" if english else f"Epicentro sobre un hipocentro a {value:g} km de profundidad"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 350" width="100%" role="img" aria-label="{escape(caption)}">
    <rect width="760" height="350" rx="16" fill="#eee9d9"/>
    <rect x="35" y="80" width="690" height="245" fill="#d4c9ab"/>
    <path d="M35 80 H725" stroke="#53634f" stroke-width="4"/>
    <g font-family="Arial,sans-serif" font-size="18" fill="#314238">
    <text x="40" y="58">{surface}</text><text x="300" y="50">Epicentro</text>
    <text x="480" y="58">0 km</text><text x="650" y="315">700 km</text>
    <path d="M245 80 V{y:.2f}" stroke="#53634f" stroke-width="2" stroke-dasharray="5 4"/>
    <circle cx="245" cy="80" r="9" fill="#d6e3e1" stroke="#314238" stroke-width="3"/>
    <circle cx="245" cy="{y:.2f}" r="6" fill="#c95434" stroke="#502b2a" stroke-width="2"/>
    <path d="M254 {y:.2f} L330 {max(y,135):.2f}" stroke="#502b2a" stroke-width="1.5"/>
    <text x="342" y="{max(y,135):.2f}">{origin}</text>
    <text x="342" y="{max(y,135)+28:.2f}" font-weight="bold">{value:g} km</text>
    </g></svg>""".replace("Epicentro", "Epicenter" if english else "Epicentro")


def subduction_svg(english=False):
    labels = ("Pacific Ocean", "South American plate", "Nazca plate", "Contact zone", "Faults within the continent") if english else (
        "Océano Pacífico", "Placa Sudamericana", "Placa Nazca", "Zona de contacto", "Fallas dentro del continente")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 300" width="100%" role="img"
    aria-label="{'Simplified subduction diagram' if english else 'Esquema simplificado de subducción'}">
    <rect width="800" height="300" rx="16" fill="#eee9d9"/>
    <path d="M30 85 H330 V130 H30 Z" fill="#d6e3e1"/>
    <path d="M330 130 L400 85 L460 55 L490 85 L525 60 L570 90 H770 V205 L655 205 Z" fill="#ccd4b5"/>
    <path d="M30 145 H330 L655 260" fill="none" stroke="#c95434" stroke-width="15"/>
    <path d="M490 90 L540 180" stroke="#53634f" stroke-width="4"/>
    <path d="M220 190 H280 M280 190 L266 183 M280 190 L266 197" fill="none" stroke="#314238" stroke-width="3"/>
    <circle cx="430" cy="181" r="7" fill="#a84153"/><circle cx="520" cy="145" r="7" fill="#a84153"/>
    <g font-family="Arial,sans-serif" font-size="18" fill="#314238">
    <text x="45" y="65">{labels[0]}</text><text x="540" y="120">{labels[1]}</text>
    <text x="45" y="183">{labels[2]}</text><text x="320" y="230">{labels[3]}</text>
    <text x="485" y="35">{labels[4]}</text></g></svg>"""
