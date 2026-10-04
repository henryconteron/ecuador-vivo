"""Original pseudo-3D educational fault blocks with geometrically valid slip.

World z is positive upward. The right dip-slip block is the hanging wall.
Its translation remains parallel to x + (0.6/1.1)z = 0. No opening is added.
Strike-slip motion has no vertical component. Not local geology or measurements.
"""
import math

from PIL import Image, ImageDraw, ImageFilter

from reel_napo_fault import arrow, smooth
from reel_territory import INK, GOLD, PAPER, MUTED, text

DIP_RATIO = .6/1.1


def displacement(kind, phase):
    phase = smooth(phase)
    if kind == "normal":
        dx = .16*phase
        return (dx, 0., -dx/DIP_RATIO)
    if kind == "inversa":
        dx = -.16*phase
        return (dx, 0., -dx/DIP_RATIO)
    if kind == "desgarre":
        return (0., .26*phase, 0.)
    raise ValueError("Unknown fault type")


def project3(x, y, z):
    return 580+250*(.95*x-.55*y), 625+250*(.20*x+.25*y-.85*z)


def clip_z(points, value, keep_above):
    result = []
    for a, b in zip(points, points[1:]+points[:1]):
        inside_a = a[1] >= value if keep_above else a[1] <= value
        inside_b = b[1] >= value if keep_above else b[1] <= value
        if inside_a:
            result.append(a)
        if inside_a != inside_b:
            fraction = (value-a[1])/(b[1]-a[1])
            result.append((a[0]+fraction*(b[0]-a[0]), value))
    return result


def draw_block(d, polygon, shift, right=False):
    dx, dy, dz = shift
    def p(x, y, z):
        return project3(x+dx, y+dy, z+dz)
    outline = "#abc7b0"
    top_color = "#688c58" if not right else "#527f7c"
    # Exposed outer side, top and stratified front cutaway.
    edge_x = polygon[0][0] if not right else polygon[1][0]
    d.polygon([p(edge_x, 0, 0), p(edge_x, 1.1, 0), p(edge_x, 1.1, -1.1), p(edge_x, 0, -1.1)],
              fill="#284938" if not right else "#244747", outline=outline)
    x0, x1 = polygon[0][0], polygon[1][0]
    d.polygon([p(x0, 0, 0), p(x1, 0, 0), p(x1, 1.1, 0), p(x0, 1.1, 0)], fill=top_color, outline=outline)
    colors = ["#7b9470", "#bba979", "#65886b", "#aa8667", "#496d5b"] if not right else ["#6c9693", "#bba979", "#567f7f", "#aa8667", "#395e63"]
    levels = [0, -.17, -.39, -.62, -.85, -1.1]
    for i, color in enumerate(colors):
        band = clip_z(clip_z(polygon, levels[i], False), levels[i+1], True)
        if len(band) >= 3:
            d.polygon([p(x, 0, z) for x, z in band], fill=color)
    d.line([p(x, 0, z) for x, z in polygon]+[p(polygon[0][0], 0, polygon[0][1])], fill=outline, width=2)
    # Surface grid follows each block's motion; it is not a real road network.
    for fraction in (.25, .5, .75):
        x = x0+(x1-x0)*fraction
        d.line((p(x, 0, 0), p(x, 1.1, 0)), fill="#92ab86" if not right else "#85aaa8", width=2)
    for y in (.35, .70):
        d.line((p(x0, y, 0), p(x1, y, 0)), fill="#92ab86" if not right else "#85aaa8", width=2)


def render_blocks(image, kind, phase, locked=False):
    """Render actual block displacement (not a blinking arrow animation)."""
    # Keep polygon artwork and shadows separate from the surrounding text.
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.polygon([project3(x, y, -1.25) for x, y in [(-1.3, -.1), (1.5, -.1), (1.5, 1.4), (-1.3, 1.4)]], fill=(0, 0, 0, 90))
    layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))
    d = ImageDraw.Draw(layer)
    if kind == "desgarre":
        left = [(-1.2, 0), (0, 0), (0, -1.1), (-1.2, -1.1)]
        right = [(0, 0), (1.2, 0), (1.2, -1.1), (0, -1.1)]
        right_shift = displacement(kind, phase)
        left_shift = tuple(-v for v in right_shift)
        foot_x = 0
    else:
        left = [(-1.2, 0), (0, 0), (.6, -1.1), (-1.2, -1.1)]
        right = [(0, 0), (1.2, 0), (1.2, -1.1), (.6, -1.1)]
        left_shift = (0, 0, 0)
        right_shift = displacement(kind, phase)
        foot_x = .6
    draw_block(d, left, left_shift)
    draw_block(d, right, right_shift, True)
    # Fault-plane outline, not an artificial widening crack.
    fault = [project3(0, 0, 0), project3(0, 1.1, 0), project3(foot_x, 1.1, -1.1), project3(foot_x, 0, -1.1)]
    d.line(fault+[fault[0]], fill=GOLD, width=4)
    if kind == "normal":
        arrow(d, (330, 490), (190, 490), PAPER)
        arrow(d, (715, 490), (855, 490), PAPER)
        text(d, (440, 471), "EXTENSIÓN", 29, GOLD)
    elif kind == "inversa":
        arrow(d, (190, 490), (330, 490), PAPER)
        arrow(d, (855, 490), (715, 490), PAPER)
        text(d, (415, 471), "COMPRESIÓN", 29, GOLD)
    else:
        arrow(d, (290, 555), (380, 513), PAPER)
        arrow(d, (730, 510), (640, 552), PAPER)
        text(d, (409, 471), "CARGA TECTÓNICA" if locked else "MOVIMIENTO LATERAL", 27, GOLD)
    # Kinematic arrow on the moving block, parallel to the modeled slip.
    dx, dy, dz = right_shift
    if math.sqrt(dx*dx+dy*dy+dz*dz) > .02:
        a = project3(.9+dx, dy, -.5+dz)
        full = displacement(kind, 1)
        b = project3(.9+dx+full[0]*1.5, dy+full[1]*1.5, -.5+dz+full[2]*1.5)
        arrow(d, a, b, PAPER, 5)
    if kind != "desgarre":
        text(d, (140, 1020), "Bloque de muro", 29, MUTED)
        text(d, (570, 1020), "Bloque de techo", 29, "#9dd7dc")
        paragraph_value = "Techo: el bloque situado SOBRE el plano de falla."
        text(d, (140, 1070), paragraph_value, 26, PAPER)
    else:
        text(d, (140, 1020), "Este tramo no desliza." if locked else "Los bloques se desplazan lateralmente.", 32, PAPER)
        text(d, (140, 1070), "La roca puede acumular deformación." if locked else "En este ejemplo no hay ascenso ni descenso.", 27, MUTED)
    # Match the plane's gold outline without a leader crossing the explanation.
    d.line((140, 1125, 175, 1125), fill=GOLD, width=4)
    text(d, (188, 1106), "Plano de falla", 29, GOLD)
    image.paste(Image.alpha_composite(image.convert("RGBA"), layer).convert("RGB"))
    return image
