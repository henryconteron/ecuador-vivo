"""Lossless, position-based edits of existing HTML; no whole-page reserialization."""
from dataclasses import dataclass, field
from html import escape, unescape
from html.parser import HTMLParser
import re

from site_editor import _replace_attribute, _safe_href

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
PROTECTED = {'html', 'head', 'body', 'main', 'script', 'style', 'link', 'base'}


@dataclass
class Node:
    key: str
    tag: str
    start: int
    open_end: int
    end_start: int
    end: int
    attrs: dict
    parent: str | None
    children: list = field(default_factory=list)
    text: str = ''

    @property
    def label(self):
        return f'{self.tag} #{self.attrs.get("id", "")} · {self.text.strip()[:85] or self.attrs.get("alt") or self.attrs.get("src") or self.attrs.get("class", "")[:85]}'


def nodes(source):
    class Tree(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.items, self.stack = [], []
            self.offsets = [0] + [m.end() for m in re.finditer('\n', source)]

        def pos(self):
            line, column = self.getpos()
            return self.offsets[line - 1] + column

        def handle_starttag(self, tag, attrs):
            start = self.pos()
            stop = start + len(self.get_starttag_text())
            parent = self.stack[-1] if self.stack else None
            node = Node(str(start), tag, start, stop, stop, stop, dict(attrs), parent.key if parent else None)
            self.items.append(node)
            if parent:
                parent.children.append(node.key)
            if tag not in VOID:
                self.stack.append(node)

        def handle_startendtag(self, tag, attrs):
            self.handle_starttag(tag, attrs)
            if self.stack and self.stack[-1].tag == tag:
                self.stack.pop()

        def handle_endtag(self, tag):
            idx = next((i for i in range(len(self.stack) - 1, -1, -1) if self.stack[i].tag == tag), None)
            if idx is not None:
                for node in self.stack[idx:]:
                    node.end_start = self.pos()
                    node.end = source.find('>', self.pos()) + 1
                del self.stack[idx:]

        def handle_data(self, data):
            if self.stack:
                self.stack[-1].text += data

        def handle_entityref(self, name):
            self.handle_data(unescape('&' + name + ';'))

        def handle_charref(self, name):
            self.handle_data(unescape('&#' + name + ';'))

    parser = Tree()
    parser.feed(source)
    return parser.items


def editable_nodes(source):
    return [node for node in nodes(source) if node.tag not in PROTECTED and node.end >= node.open_end]


def find_node(source, key):
    node = next((row for row in nodes(source) if row.key == str(key)), None)
    if node is None or node.tag in PROTECTED:
        raise ValueError('Elemento no editable; vuelve a seleccionar la página.')
    return node


def edit_node(source, key, *, text=None, attributes=None, style=None, visible=None):
    node = find_node(source, key)
    raw = source[node.start:node.open_end]
    for name, value in (attributes or {}).items():
        if not re.fullmatch(r'[a-z][\w:-]*', name) or name.startswith('on') or name in {'srcdoc', 'style'}:
            raise ValueError('Atributo ejecutable o inválido; usa los controles de diseño.')
        if name in {'href', 'src', 'poster', 'action'}:
            value = _safe_href(value)
        raw = _replace_attribute(raw, name, str(value))
    if style:
        current = dict(part.split(':', 1) for part in (node.attrs.get('style') or '').split(';') if ':' in part)
        current = {key.strip(): value.strip() for key, value in current.items()}
        for name, value in style.items():
            if name not in {'color', 'background-color', 'font-size', 'text-align', 'padding', 'border-radius', 'max-width', 'font-weight'}:
                raise ValueError('Propiedad de diseño no admitida.')
            if re.search(r'url\s*\(|expression|[<>{};]', str(value), re.I):
                raise ValueError('Valor de diseño inválido.')
            if value:
                current[name] = str(value)
            else:
                current.pop(name, None)
        raw = _replace_attribute(raw, 'style', ';'.join(f'{k}:{v}' for k, v in current.items()))
    if visible is not None:
        raw = re.sub(r'\s+hidden(?:\s*=\s*(?:"[^"]*"|\x27[^\x27]*\x27|[^\s>]+))?(?=\s|/?>)', '', raw)
        raw = re.sub(r'\s+data-site-admin-hidden=("[^"]*"|\x27[^\x27]*\x27)', '', raw)
        if not visible:
            raw = raw[:-1] + ' hidden data-site-admin-hidden="true">'
    inner = source[node.open_end:node.end_start]
    if text is not None:
        if node.children or node.tag in VOID:
            raise ValueError('Este elemento contiene otros elementos. Selecciona su texto hijo para conservarlos.')
        inner = escape(str(text))
        if 'data-es' in node.attrs:
            raw = _replace_attribute(raw, 'data-es', str(text))
    return source[:node.start] + raw + inner + source[node.end_start:]


def remove_node(source, key):
    node = find_node(source, key)
    if node.end <= node.start:
        raise ValueError('El elemento no tiene un cierre válido.')
    return source[:node.start] + source[node.end:]


def duplicate_node(source, key):
    node = find_node(source, key)
    block = source[node.start:node.end]
    # Duplicated IDs would break navigation, labels and script selectors.
    block = re.sub(r'\s+(?:id|data-site-admin-id|data-site-admin-block)=("[^"]*"|\x27[^\x27]*\x27)', '', block)
    return source[:node.end] + '\n' + block + source[node.end:]


def move_node(source, key, direction):
    node = find_node(source, key)
    siblings = [row for row in nodes(source) if row.parent == node.parent]
    idx = next(i for i, row in enumerate(siblings) if row.key == node.key)
    neighbor_idx = idx + (-1 if direction == 'up' else 1)
    if neighbor_idx < 0 or neighbor_idx >= len(siblings):
        raise ValueError('Ya está en el extremo de su contenedor.')
    neighbor = siblings[neighbor_idx]
    if neighbor.tag in PROTECTED:
        raise ValueError('No se mueve contenido a través de scripts o estilos.')
    first, second = sorted((node, neighbor), key=lambda row: row.start)
    return (source[:first.start] + source[second.start:second.end]
            + source[first.end:second.start] + source[first.start:first.end] + source[second.end:])
