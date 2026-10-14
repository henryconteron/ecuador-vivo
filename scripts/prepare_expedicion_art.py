"""Create small, project-local derivatives of approved generated illustrations.

Only mechanical resize/format conversion occurs here. No painting, background
removal, compositing, or source-image modification is performed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from PIL import Image, ImageOps


def webp(source, target, maximum, *, quality=88):
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as original:
        image = ImageOps.exif_transpose(original)
        image = image.convert('RGBA' if 'A' in image.getbands() else 'RGB')
        image.thumbnail((maximum, maximum), Image.Resampling.LANCZOS)
        image.save(target, format='WEBP', quality=quality, method=6)
        return {'path': str(target), 'size': image.size, 'mode': image.mode,
                'bytes': target.stat().st_size,
                'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}


def prepare(hero, diorama, repo):
    public = repo / 'assets/images/expedicion'
    cards = repo / 'production/video_studio/workspace_frontend/art'
    targets = [
        (hero, public / 'andes-hero.webp', 1600, 88),
        (hero, public / 'andes-hero-mobile.webp', 800, 86),
        (diorama, public / 'agua-diorama.webp', 1200, 88),
        (hero, cards / 'sig-cover.webp', 720, 84),
        (hero, cards / 'studio-cover.webp', 720, 84),
        (diorama, cards / 'resources-cover.webp', 720, 84),
    ]
    results = []
    for source, target, maximum, quality in targets:
        if source.resolve() == target.resolve():
            raise ValueError('A generated original cannot be a derivative destination.')
        results.append(webp(source, target, maximum, quality=quality))
    fonts = repo / 'assets/fonts'
    fonts.mkdir(parents=True, exist_ok=True)
    for filename in ('Lora-Variable.ttf', 'AtkinsonHyperlegible-Regular.ttf',
                     'AtkinsonHyperlegible-Bold.ttf', 'OFL-Lora.txt',
                     'OFL-AtkinsonHyperlegible.txt'):
        source = repo / 'production/video_studio/assets/fonts' / filename
        target = fonts / filename
        if target.exists() and target.read_bytes() != source.read_bytes():
            raise ValueError('Refusing to overwrite a different public font: ' + filename)
        if not target.exists():
            shutil.copy2(source, target)
        results.append({'path': str(target), 'bytes': target.stat().st_size,
                        'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hero', type=Path, required=True)
    parser.add_argument('--diorama', type=Path, required=True)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    print(json.dumps(prepare(args.hero, args.diorama, args.repo.resolve()), indent=2))
