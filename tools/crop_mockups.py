"""Crop reusable artwork out of the client's dark mockups in creatives/template 2/.

Each entry: (name, box, mode[, erase_rects]) where erase_rects wipe baked text; box box = (x0, y0, x1, y1) in mockup pixels and mode is
  'photo' – keep as-is (rectangular photo / baked card)
  'cut'   – flood-fill the background from the corners -> transparent (flat backgrounds)
  'dark'  – transparent on a dark background: flood-fill + luminance so glows fade out softly
Run: python tools/crop_mockups.py            (everything)
     python tools/crop_mockups.py hero- fam- (only names with these prefixes)
"""
import os, sys, numpy as np, cv2
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, '..', 'creatives', 'template 2')
OUT = os.path.join(ROOT, 'assets', 'mk')
os.makedirs(OUT, exist_ok=True)

SPEC = {
 'homepage.png': [                                   # 1055 x 1491
   ('hero-home-raw', (0,55,1055,437), 'photo'),      # full hero band (text baked) – cleaned separately
   ('hero-home-art', (330,55,1055,437), 'photo'),    # right-hand art only
   ('step-1', (100,600,208,662), 'dark'), ('step-2', (366,598,448,666), 'dark'),
   ('step-3', (598,592,698,664), 'dark'), ('step-4', (846,604,944,664), 'dark'),
   ('home-place-healthcare', (35,940,275,1056), 'photo'), ('home-place-gyms', (285,940,525,1056), 'photo'),
   ('home-place-facilities', (535,940,770,1056), 'photo'), ('home-place-education', (780,940,1020,1056), 'photo'),
   ('loved-family', (255,1195,560,1347), 'photo'),
   ('fam-h1', (718,1200,850,1268), 'photo'), ('fam-h2', (860,1200,993,1268), 'photo'),
   ('fam-h3', (718,1275,850,1345), 'photo'), ('fam-h4', (860,1275,993,1345), 'photo'),
   ('footer-note', (878,1395,1040,1487), 'dark'),
   ('hero-note', (893,70,1044,170), 'dark'),
 ],
 'all products.png': [                               # 977 x 1610
   ('hero-products', (380,55,977,235), 'photo'),
   ('card-pocket', (203,318,430,470), 'photo'), ('card-daily', (440,318,665,470), 'photo'), ('card-family', (675,318,900,470), 'photo'),
   ('cat-pocket', (45,655,255,748), 'dark', [(45,655,162,694)]), ('cat-daily', (275,655,480,748), 'dark', [(275,655,396,694)]),
   ('cat-family', (500,655,700,748), 'dark', [(500,655,606,694),(500,655,700,660)]), ('cat-bundle', (725,655,925,748), 'dark', [(725,655,800,694),(725,655,925,660)]),
   ('why-1', (100,846,170,906), 'dark'), ('why-2', (272,846,346,906), 'dark'), ('why-3', (452,846,520,906), 'dark'),
   ('why-4', (628,846,702,906), 'dark'), ('why-5', (804,846,876,906), 'dark'),
   ('fam-1', (48,1085,185,1185), 'photo'), ('fam-2', (198,1085,335,1185), 'photo'), ('fam-3', (348,1085,485,1185), 'photo'),
   ('fam-4', (498,1085,635,1185), 'photo'), ('fam-5', (648,1085,780,1185), 'photo'), ('fam-6', (795,1085,930,1185), 'photo'),
   ('nl-cove', (62,1360,222,1448), 'dark', [(62,1360,222,1366),(62,1360,68,1448)]),
 ],
 'how it works.png': [                               # 967 x 1627
   ('hero-how', (390,60,967,397), 'photo'),
   ('hstep-1', (92,462,202,562), 'dark'), ('hstep-2', (315,462,422,562), 'dark'),
   ('hstep-3', (532,462,648,548), 'dark'), ('hstep-4', (758,462,872,562), 'dark'),
   ('action-video', (62,695,608,972), 'photo'),
   ('compare-bottle', (62,1020,180,1292), 'dark'),
   ('cta-family', (58,1312,302,1432), 'dark'),
 ],
 'wheres it used.png': [                             # 953 x 1651
   ('hero-where', (290,55,953,367), 'photo'),
   ('place-healthcare', (30,388,310,602), 'photo'), ('place-gyms', (325,388,618,602), 'photo'), ('place-facilities', (633,388,920,602), 'photo'),
   ('place-education', (30,622,310,836), 'photo'), ('place-hospitality', (325,622,618,836), 'photo'), ('place-travel', (633,622,920,836), 'photo'),
   ('proof-kills', (78,1098,138,1162), 'dark'), ('proof-clock', (222,1098,284,1162), 'dark'), ('proof-water', (366,1098,420,1162), 'dark'),
   ('proof-leaf', (502,1098,562,1162), 'dark'), ('proof-feather', (648,1098,708,1162), 'dark'), ('proof-shield', (798,1098,858,1162), 'dark'),
   ('cta-cove', (18,1298,206,1456), 'dark'), ('cta-kit', (498,1300,710,1456), 'dark'),
 ],
 'proof.png': [                                      # 1024 x 1536
   ('hero-proof', (400,55,1024,392), 'photo'),
   ('pc-1', (88,398,148,458), 'dark'), ('pc-2', (252,398,314,458), 'dark'), ('pc-3', (418,398,472,458), 'dark'),
   ('pc-4', (562,398,622,458), 'dark'), ('pc-5', (702,398,764,458), 'dark'), ('pc-6', (862,398,924,458), 'dark'),
   ('eff-999', (52,562,142,656), 'dark'), ('eff-4h', (148,562,232,656), 'dark'), ('eff-water', (236,562,320,642), 'dark'),
   ('eff-leaf', (324,562,406,642), 'dark'), ('eff-feather', (410,562,492,642), 'dark'),
   ('eff-shield', (158,698,218,762), 'dark'),
   ('why-proof-1', (45,905,195,1047), 'photo'), ('why-proof-2', (350,905,532,1047), 'photo'), ('why-proof-3', (660,905,862,1047), 'photo'),
   ('nl-cove-wave', (58,1238,270,1330), 'dark', [(58,1238,270,1244)]),
 ],
 'about us.png': [                                   # 1023 x 1537
   ('hero-about', (380,55,1023,387), 'photo'),
   ('story', (45,410,340,612), 'photo'),
   ('crew-cove', (38,842,165,1012), 'dark'),
   ('fact-1', (750,418,802,464), 'dark'), ('fact-2', (750,473,802,522), 'dark'), ('fact-3', (750,524,802,572), 'dark'), ('fact-4', (750,582,802,628), 'dark'),
   ('val-1', (92,672,158,732), 'dark'), ('val-2', (282,672,344,732), 'dark'), ('val-3', (466,672,534,732), 'dark'),
   ('val-4', (668,672,728,732), 'dark'), ('val-5', (852,672,918,732), 'dark'),
   ('mission-family', (30,1045,325,1227), 'photo'), ('mission-splash', (758,1048,992,1222), 'photo'),
   ('strip-1', (30,1275,175,1367), 'photo'), ('strip-2', (188,1275,330,1367), 'photo'), ('strip-3', (345,1275,488,1367), 'photo'),
   ('strip-4', (500,1275,672,1367), 'photo'), ('strip-5', (685,1275,828,1367), 'photo'), ('strip-6', (842,1275,988,1367), 'photo'),
 ],
 'contact us.png': [                                 # 1484 x 1060
   ('hero-contact', (380,55,1062,397), 'photo'),
   ('contact-family', (1088,614,1424,826), 'dark', [(1088,614,1424,634)]),
   ('trust-shield', (70,702,142,778), 'dark'), ('trust-drop', (332,702,398,778), 'dark'), ('trust-badge', (582,702,652,778), 'dark'),
   ('trust-flag', (793,702,852,772), 'dark'), ('trust-heart', (876,702,948,778), 'dark'),
   ('footer-splash', (1288,842,1438,978), 'dark'),
 ],
 'faq.png': [                                        # 864 x 1821
   ('hero-faq', (150,55,864,612), 'photo', [(150,55,300,215),(150,215,262,258),(150,258,212,322),(636,86,842,292),(150,536,242,596)]),
   ('germ-1', (52,1212,122,1284), 'dark'), ('germ-2', (142,1212,212,1284), 'dark'), ('germ-3', (236,1212,308,1284), 'dark'),
   ('germ-4', (332,1212,402,1284), 'dark'), ('germ-5', (432,1218,498,1278), 'dark'),
   ('faq-cove', (552,1082,834,1388), 'dark'),
   ('faq-bottles', (692,1412,834,1548), 'dark'),
   ('ft-1', (52,1436,108,1502), 'dark'), ('ft-2', (280,1436,338,1502), 'dark'), ('ft-3', (512,1436,564,1502), 'dark'),
 ],
 'pocket sanitizer.png': [                           # 1023 x 1537
   ('pocket-main', (115,105,625,500), 'photo'),
   ('pocket-t1', (40,110,100,195), 'photo'), ('pocket-t2', (40,210,100,295), 'photo'), ('pocket-t3', (40,305,100,392), 'photo'), ('pocket-t4', (40,400,100,485), 'photo'),
   ('cove-bottle', (116,452,302,668), 'dark', [(116,452,302,500,'lum')]),
   ('little-viro', (592,528,662,602), 'dark'), ('little-4h', (722,522,798,608), 'dark'), ('little-bac', (886,522,958,602), 'dark'),
   ('ps-1', (48,712,132,778), 'dark'), ('ps-2', (168,712,252,778), 'dark'), ('ps-3', (288,712,372,778), 'dark'), ('ps-4', (408,712,492,778), 'dark'),
   ('pw-1', (528,712,588,778), 'dark'), ('pw-2', (628,712,692,778), 'dark'), ('pw-3', (722,712,788,778), 'dark'), ('pw-4', (822,712,882,778), 'dark'), ('pw-5', (912,712,978,778), 'dark'),
   ('moment-1', (140,908,326,1052), 'photo'), ('moment-2', (428,908,662,1052), 'photo'), ('moment-3', (768,908,986,1052), 'photo'),
   ('qa-1', (128,1160,182,1212), 'photo'), ('qa-2', (290,1160,342,1212), 'photo'), ('qa-3', (450,1160,502,1212), 'photo'),
   ('qa-4', (603,1160,655,1212), 'photo'), ('qa-5', (753,1160,807,1212), 'photo'), ('qa-6', (903,1160,957,1212), 'photo'),
   ('also-1', (408,1250,482,1332), 'dark'), ('also-2', (612,1250,688,1332), 'dark'), ('also-3', (812,1250,912,1332), 'dark'),
   ('pocket-nl-cove', (140,1362,256,1452), 'dark', [(140,1362,256,1368)]),
 ],
 'daily defense.png': [                              # 1055 x 1491
   ('daily-main', (135,100,595,610), 'photo'),
   ('daily-t1', (45,115,120,195), 'photo'), ('daily-t2', (45,205,120,285), 'photo'), ('daily-t3', (45,295,120,375), 'photo'), ('daily-t4', (45,385,120,465), 'photo'),
   ('badge-1', (630,280,688,338), 'dark'), ('badge-2', (712,280,770,338), 'dark'), ('badge-3', (796,280,856,338), 'dark'),
   ('badge-4', (878,280,938,338), 'dark'), ('badge-5', (960,280,1018,338), 'dark'),
   ('cove-thumbs', (808,648,1032,882), 'dark'),
   ('daily-villains', (45,1028,372,1196), 'dark'),
   ('cust-1', (404,934,510,1042), 'photo'), ('cust-2', (404,1058,510,1166), 'photo'),
   ('teddy', (858,1048,1002,1192), 'dark'),
   ('cta-cove-2', (58,1212,238,1328), 'dark'), ('cta-kit-2', (468,1212,692,1328), 'dark'),
 ],
 'family size.png': [                                # 1024 x 1535
   ('family-main', (135,95,630,552), 'photo'),
   ('family-t1', (42,100,125,185), 'photo'), ('family-t2', (42,195,125,280), 'photo'), ('family-t3', (42,290,125,375), 'photo'),
   ('family-t4', (42,385,125,470), 'photo'), ('family-t5', (42,480,125,540), 'photo'),
   ('big-1', (248,568,318,638), 'dark'), ('big-2', (348,568,418,638), 'dark'), ('big-3', (448,568,518,638), 'dark'), ('big-4', (548,568,618,638), 'dark'),
   ('family-photo', (640,560,985,707), 'photo'),
   ('video-thumb', (365,745,625,887), 'photo'),
   ('hiw-1', (698,742,758,792), 'dark'), ('hiw-2', (698,793,758,843), 'dark'), ('hiw-3', (698,840,758,892), 'dark'), ('hiw-4', (698,893,758,943), 'dark'),
   ('seal-1', (58,886,100,917), 'dark'), ('seal-2', (132,886,172,917), 'dark'), ('seal-3', (206,886,248,917), 'dark'), ('seal-4', (270,886,312,917), 'dark'),
   ('mission-photo', (38,1090,302,1247), 'photo'), ('mission-crew', (648,1098,832,1237), 'dark'),
   ('family-nl-cove', (128,1368,238,1442), 'dark'),
 ],
}

def flood(rgb, tol):
    h, w, _ = rgb.shape; img = rgb.copy(); mask = np.zeros((h+2, w+2), np.uint8)
    flags = 4 | (255 << 8) | cv2.FLOODFILL_MASK_ONLY | cv2.FLOODFILL_FIXED_RANGE
    for s in [(0,0),(w-1,0),(0,h-1),(w-1,h-1),(w//2,0),(0,h//2),(w-1,h//2),(w//2,h-1)]:
        cv2.floodFill(img, mask, s, (0,0,0), (tol,)*3, (tol,)*3, flags)
    return mask[1:-1, 1:-1] > 0

def cut(rgb, tol=30):
    bg = flood(rgb, tol)
    a = (~bg * 255).astype(np.uint8)
    a = cv2.morphologyEx(a, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
    a = cv2.GaussianBlur(a, (0,0), 1.0)
    return np.dstack([rgb, a])

def dark(rgb, tol=34, lo=26, hi=120):
    """Transparent background for art sitting on the dark UI. Pixels the flood fill reaches from the
    edges are background; their alpha follows luminance so glows/bubbles fade out instead of being
    clipped. Everything enclosed by the character stays opaque."""
    bg = flood(rgb, tol)
    lum = rgb.astype(np.float32).max(axis=2)
    soft = np.clip((lum - lo) / (hi - lo), 0, 1)
    interior = (~bg * 255).astype(np.uint8)
    interior = cv2.morphologyEx(interior, cv2.MORPH_OPEN, np.ones((3,3), np.uint8)).astype(np.float32) / 255
    a = np.maximum(interior, soft * (bg.astype(np.float32)))
    a = np.where(bg, soft, 1.0)
    a = np.maximum(a, interior)
    a = cv2.GaussianBlur((a * 255).astype(np.uint8), (0,0), 0.8)
    return np.dstack([rgb, a])

def upscale(im, factor=2):
    im = im.resize((im.width * factor, im.height * factor), Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))

if __name__ == '__main__':
    only = sys.argv[1:]
    for fname, items in SPEC.items():
        src = Image.open(os.path.join(SRC, fname)).convert('RGB')
        for item in items:
            name, box, mode = item[:3]; erase = item[3] if len(item) > 3 else []
            if only and not any(name.startswith(o) for o in only): continue
            crop = src.crop(box)
            if mode == 'photo':
                if erase:
                    arr = np.array(crop); H, W = arr.shape[:2]
                    for (ex0, ey0, ex1, ey1) in erase:
                        y0, y1 = max(0,ey0-box[1]), min(H,ey1-box[1]); x0, x1 = max(0,ex0-box[0]), min(W,ex1-box[0])
                        ring = np.concatenate([arr[max(0,y0-8):y0, x0:x1].reshape(-1,3), arr[y1:y1+8, x0:x1].reshape(-1,3), arr[y0:y1, max(0,x0-8):x0].reshape(-1,3), arr[y0:y1, x1:x1+8].reshape(-1,3)])
                        fill = np.median(ring, axis=0) if len(ring) else np.array([5,11,20])
                        arr[y0:y1, x0:x1] = fill
                    crop = Image.fromarray(arr)
                im = upscale(crop) if crop.width < 700 else crop
                im.save(os.path.join(OUT, name + '.webp'), quality=86, method=6)
            else:
                rgb = np.array(crop)
                rgba = cut(rgb) if mode == 'cut' else dark(rgb)
                for e in erase:   # wipe regions (mockup coords) e.g. baked labels; 5th value 'lum' = strict luminance instead
                    ex0, ey0, ex1, ey1 = e[:4]; sl = (slice(max(0,ey0-box[1]), ey1-box[1]), slice(max(0,ex0-box[0]), ex1-box[0]))
                    if len(e) > 4:
                        lum = rgb[sl].astype(np.float32).max(axis=2)
                        rgba[sl][..., 3] = np.minimum(rgba[sl][..., 3], (np.clip((lum - 150) / 70, 0, 1) * 255).astype(np.uint8))
                    else:
                        rgba[sl][..., 3] = 0
                im = Image.fromarray(rgba, 'RGBA')
                bbox = im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
                if bbox: im = im.crop(bbox)
                im = upscale(im) if im.width < 400 else im
                im.save(os.path.join(OUT, name + '.webp'), quality=90, method=6)
        print('done', fname)
