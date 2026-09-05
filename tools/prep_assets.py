import numpy as np, cv2, os
from PIL import Image
SRC='creatives/animation'; OUT='covexall-site/assets'
os.makedirs(OUT, exist_ok=True)
def load(name): return np.array(Image.open(os.path.join(SRC,name)).convert('RGB'))
def crop(a,x0,y0,x1,y1): return a[y0:y1,x0:x1]

def flood(rgb,tol):
    h,w,_=rgb.shape; img=rgb.copy(); mask=np.zeros((h+2,w+2),np.uint8)
    flags=4|(255<<8)|cv2.FLOODFILL_MASK_ONLY|cv2.FLOODFILL_FIXED_RANGE
    for s in [(0,0),(w-1,0),(0,h-1),(w-1,h-1),(w//2,0),(0,h//2),(w-1,h//2),(w//2,h-1)]:
        cv2.floodFill(img,mask,s,(0,0,0),(tol,)*3,(tol,)*3,flags)
    return mask[1:-1,1:-1]>0

def largest_component(fg):
    n,lab,stats,_=cv2.connectedComponentsWithStats(fg.astype(np.uint8),8)
    if n<=2: return fg
    idx=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]); return lab==idx

def cutout(rgb,tol=24,loose=75,feather=2,keep_largest=True):
    bg=flood(rgb,tol)
    # shadow removal: low-saturation light pixels reachable with a loose tolerance
    loose_bg=flood(rgb,loose)
    sat=rgb.max(axis=2).astype(int)-rgb.min(axis=2).astype(int)
    shadow=loose_bg & ~bg & (sat<28) & (rgb.min(axis=2)>150)
    fg=~(bg|shadow)
    fg=cv2.morphologyEx(fg.astype(np.uint8),cv2.MORPH_OPEN,np.ones((5,5),np.uint8)).astype(bool)
    if keep_largest: fg=largest_component(fg)
    a=(fg*255).astype(np.uint8)
    a=cv2.erode(a,np.ones((3,3),np.uint8)); a=cv2.GaussianBlur(a,(0,0),feather)
    return np.dstack([rgb,a])

def glow_cutout(rgb,tol=14):
    # body mask via flood fill + soft glow alpha from whiteness; keep original colours
    bg=flood(rgb,tol); fg=largest_component(~bg)
    body=cv2.GaussianBlur((fg*255).astype(np.uint8),(0,0),3).astype(np.float32)/255
    f=rgb.astype(np.float32)/255; glow=np.clip((1-f.min(axis=2))*1.6,0,1)
    # limit glow to a halo near the body so far-away white stays clear
    halo=cv2.GaussianBlur((fg*255).astype(np.uint8),(0,0),40).astype(np.float32)/255
    a=np.maximum(body,glow*np.clip(halo*2,0,1))
    return np.dstack([rgb,(a*255).astype(np.uint8)])

def save(rgba,name,maxh=1400):
    im=Image.fromarray(rgba,'RGBA')
    bbox=im.getchannel('A').point(lambda v:255 if v>8 else 0).getbbox()
    if bbox: im=im.crop(bbox)
    if im.height>maxh: im=im.resize((round(im.width*maxh/im.height),maxh),Image.LANCZOS)
    im.save(os.path.join(OUT,name+'.png'),optimize=True)
    im.save(os.path.join(OUT,name+'.webp'),quality=88,method=6)
    print(name,im.size,os.path.getsize(os.path.join(OUT,name+'.webp'))//1024,'KB')

cove=load('cove.png')
save(glow_cutout(crop(cove,0,0,1330,2880)),'cove-front')
save(glow_cutout(crop(cove,1280,0,2560,2880)),'cove-front-2')
save(glow_cutout(crop(cove,2520,0,3780,2880)),'cove-side')
save(glow_cutout(load('cove 2.png')),'cove-bust',maxh=1600)

viro=load('viro.png')
save(cutout(crop(viro,850,150,3200,2880),tol=26),'viro-main')
save(cutout(crop(viro,3400,1660,5120,2880),tol=26),'viro-action')
save(cutout(crop(viro,0,0,1350,1400),tol=26),'viro-head')
save(cutout(crop(load('viro 1.png'),1180,60,2950,3072),tol=26),'viro-front')

bac=load('bac.png')
save(cutout(crop(bac,0,0,2560,1440),tol=28),'bac-front')
save(cutout(crop(bac,2560,0,5120,1440),tol=28),'bac-front-2')
snot=load('snot.png')
save(cutout(crop(snot,0,300,1350,2600),tol=24),'snot-front')
save(cutout(crop(snot,1350,300,2650,2600),tol=24),'snot-front-2')
d=load('daughter.png')
save(cutout(crop(d,0,0,1400,3072),tol=24),'maya-front')
save(cutout(crop(d,1350,0,2750,3072),tol=24),'maya-three-quarter')
m=load('mom.png')
save(cutout(crop(m,0,0,950,2880),tol=24),'mom-full')
save(cutout(crop(m,900,0,2350,2200),tol=24),'mom-bust')
Image.open(os.path.join(SRC,'crew.png')).convert('RGB').resize((1920,1080),Image.LANCZOS).save(os.path.join(OUT,'crew-lineup.webp'),quality=85,method=6)

# photos
def photo(src,name,maxw):
    im=Image.open(src).convert('RGB')
    if im.width>maxw: im=im.resize((maxw,round(im.height*maxw/im.width)),Image.LANCZOS)
    im.save(os.path.join(OUT,name+'.webp'),quality=82,method=6); print(name,im.size)
P='landing_page/public/'
for s,n in [('person-mother-child','photo-mother-baby'),('person-baby','photo-baby'),('person-doctor','photo-doctor'),('person-mother-craft','photo-mother-craft')]:
    photo(P+s+'.png',n,800)
for s in ['gym','hospital','office','hotel','military']:
    photo(P+f'industry-{s}.png',f'place-{s}',900)
for s in ['gym','office','travel','commute']:
    photo(f'landingpage4/lifestyle-{s}.png',f'life-{s}',900)
Image.open(P+'product-4oz-bottle.png').save(os.path.join(OUT,'product-4oz.png'))
Image.open(P+'product-5gal-pail.png').save(os.path.join(OUT,'product-5gal.png'))
Image.open(P+'product-55gal-drum.png').save(os.path.join(OUT,'product-55gal.png'))
Image.open(P+'product-250gal-tote.png').save(os.path.join(OUT,'product-250gal.png'))
print('done')
