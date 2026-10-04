"""Pure, testable seismological helpers used by SeismoTrack."""

from __future__ import annotations

import math

import numpy as np


def vectorized_haversine(lat_target, lon_target, lats_arr, lons_arr):
    """Return great-circle distances in kilometres from one point."""
    radius_km = 6371.0
    p1 = math.radians(lat_target)
    p2 = np.radians(lats_arr)
    dp = np.radians(lats_arr - lat_target)
    dl = np.radians(lons_arr - lon_target)
    a = np.sin(dp / 2.0) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2.0) ** 2
    return 2.0 * radius_km * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def evaluar_consistencia_buzamiento(profundidad, distancia_km, dip_deg):
    """Exploratory geometry check; not a focal-mechanism solution."""
    if dip_deg is None or dip_deg <= 0 or dip_deg >= 90:
        return None
    distancia_esperada = profundidad / math.tan(math.radians(dip_deg))
    tolerancia = max(3.0, 0.4 * distancia_esperada)
    return bool(abs(distancia_km - distancia_esperada) <= tolerancia), distancia_esperada


def estimar_mc_maxima_curvatura(magnitudes, bin_width=0.1):
    """Estimate completeness magnitude using maximum curvature (+0.2 correction)."""
    magnitudes = np.asarray(magnitudes, dtype=float)
    magnitudes = magnitudes[np.isfinite(magnitudes)]
    if len(magnitudes) < 5:
        return None
    m_min, m_max = float(magnitudes.min()), float(magnitudes.max())
    if m_max <= m_min:
        return m_min
    bordes = np.arange(m_min, m_max + bin_width, bin_width)
    conteos, _ = np.histogram(magnitudes, bins=bordes)
    if conteos.max() == 0:
        return m_min
    idx_pico = int(np.argmax(conteos))
    return round(bordes[idx_pico] + bin_width / 2.0 + 0.2, 2)


def calcular_valor_b(magnitudes, mc, bin_width=0.1):
    """Return Aki b-value, Shi-Bolt standard error and sample size."""
    magnitudes = np.asarray(magnitudes, dtype=float)
    completas = magnitudes[np.isfinite(magnitudes) & (magnitudes >= mc)]
    if len(completas) < 5:
        return None, None, len(completas)
    denominador = completas.mean() - (mc - bin_width / 2.0)
    if denominador <= 0:
        return None, None, len(completas)
    b_value = math.log10(math.e) / denominador
    diff_sq = np.sum((completas - completas.mean()) ** 2)
    n = len(completas)
    error = 2.30 * (b_value**2) * math.sqrt(diff_sq / (n * (n - 1)))
    return b_value, error, n
