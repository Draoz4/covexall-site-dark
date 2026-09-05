"""Cut the generated bottle renders (white background) into transparent WebPs and
convert the generated hero scene. Run: python tools/cut_generated.py"""
import os, numpy as np
from PIL import Image
ns = {'__file__': os.path.abspath(os.path.join('tools', 'crop_mockups.py'))}
src = open(os.path.join('tools', 'crop_mockups.py'), encoding='utf-8').read().split('only = sys.argv')[0]
exec(src, ns)
for n in ['pocket', 'daily', 'family', 'bundle']:
    raw = f'assets/gen/bottle-{n}-raw.png'
    if not os.path.exists(raw):
        continue
    rgb = np.array(Image.open(raw).convert('RGB'))
    out = Image.fromarray(ns['cut'](rgb, tol=14), 'RGBA')
    bbox = out.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
    out = out.crop(bbox)
    if out.height > 900:
        out = out.resize((round(out.width * 900 / out.height), 900), Image.LANCZOS)
    out.save(f'assets/bottle-{n}.webp', quality=90, method=6)
    print(n, out.size)
raw = 'assets/hero-scene-raw.png'
if os.path.exists(raw):
    h = Image.open(raw).convert('RGB')
    h.save('assets/hero-scene.webp', quality=84, method=6)
    os.remove(raw)
    print('hero', h.size)
