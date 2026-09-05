"""Headless full-page screenshots of every built page into _shots/ (fresh Edge profile per run).
Run: python tools/shoot.py [page ...]   e.g. python tools/shoot.py index products"""
import os, sys, subprocess, tempfile, shutil, pathlib
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / '_shots'; OUT.mkdir(exist_ok=True)
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
BASE = os.environ.get('SHOT_BASE', 'http://localhost:5199')
pages = sys.argv[1:] or [p.stem for p in sorted((ROOT / 'src' / 'pages').glob('*.html'))]
W, H = 1280, 3400
for name in pages:
    prof = tempfile.mkdtemp(prefix='edge-')
    url = f"{BASE}/{'' if name == 'index' else name}?noanim"
    png = OUT / f"{name}.png"
    if png.exists(): png.unlink()
    subprocess.run([EDGE, '--headless=new', '--disable-gpu', '--hide-scrollbars', f'--user-data-dir={prof}',
                    f'--window-size={W},{H}', f'--screenshot={png}', '--virtual-time-budget=6000', url],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    import time
    for _ in range(60):
        if png.exists() and png.stat().st_size > 0: break
        time.sleep(1)
    time.sleep(1); shutil.rmtree(prof, ignore_errors=True)
    if not png.exists():
        print('FAILED', name); continue
    im = Image.open(png).convert('RGB')
    # trim trailing rows that are the plain page background
    px = im.load(); w, h = im.size; last = h - 1
    bg = px[w // 2, h - 1]
    while last > 200 and all(abs(px[x, last][i] - bg[i]) < 6 for x in range(0, w - 260, 40) for i in range(3)):
        last -= 1
    im = im.crop((0, 0, w, min(h, last + 40))); im.save(png)
    print(name, im.size)
