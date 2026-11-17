"""Illustrated sewer scenes drawn in code with Pillow."""
from io import BytesIO
import math
import random
from PIL import Image, ImageDraw, ImageFilter

W, H = 1200, 720


def _lerp(a, b, t):
    return tuple(round(a[i] * (1-t) + b[i] * t) for i in range(3))


def start_scene():
    """Stone sewer outfall, centered water stream and rippling pool."""
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        c = _lerp((24, 55, 59), (7, 29, 42), y / H)
        for x in range(W):
            shade = int(5 * math.sin(x / 67) + 3 * math.sin((x+y) / 41))
            px[x, y] = tuple(max(0, min(255, v + shade)) for v in c)
    d = ImageDraw.Draw(im)
    rng = random.Random(38)
    # Irregular rows of large, chipped stone blocks.
    for row, y in enumerate(range(-30, 430, 93)):
        start = -80 if row % 2 else -20
        for x in range(start, W + 100, 158):
            x0, y0 = x + rng.randint(-8, 8), y + rng.randint(-7, 7)
            x1, y1 = x0 + rng.randint(140, 160), y0 + rng.randint(74, 88)
            fill = rng.choice([(44, 87, 87), (49, 99, 96), (38, 78, 82), (57, 103, 96)])
            d.rounded_rectangle((x0, y0, x1, y1), radius=13, fill=fill, outline=(14, 43, 51), width=8)
            d.line((x0+14, y0+9, x1-17, y0+8), fill=(113, 154, 134), width=4)
            d.line((x0+18, y0+16, x0+61, y0+15), fill=(81, 132, 121), width=3)
            for _ in range(4):
                xx, yy = rng.randint(x0+18, x1-18), rng.randint(y0+25, y1-12)
                d.line((xx, yy, xx+rng.randint(10, 35), yy-rng.randint(0, 8)), fill=(28, 62, 66), width=3)
    # Dark water and an uneven stone waterline.
    d.rectangle((0, 425, W, H), fill=(10, 43, 55))
    d.line((0, 427, W, 427), fill=(112, 169, 150), width=7)
    for _ in range(300):
        x, y = rng.randrange(W), rng.randrange(434, H)
        d.line((x, y, min(W-1, x+rng.randrange(5, 58)), y+rng.choice([-1, 0, 1])),
               fill=rng.choice([(20, 72, 81), (27, 96, 101), (37, 117, 113), (14, 58, 72)]), width=2)
    # Broad, centered ring and dark round opening.
    cx, cy = 600, 218
    d.ellipse((cx-165, cy-165, cx+165, cy+165), fill=(18, 45, 50), outline=(9, 29, 37), width=15)
    d.ellipse((cx-146, cy-146, cx+146, cy+146), fill=(72, 127, 117), outline=(129, 177, 152), width=10)
    d.arc((cx-143, cy-143, cx+143, cy+143), 195, 343, fill=(171, 210, 174), width=8)
    d.ellipse((cx-120, cy-120, cx+120, cy+120), fill=(25, 68, 69), outline=(52, 99, 94), width=10)
    d.ellipse((cx-96, cy-96, cx+96, cy+96), fill=(4, 25, 33), outline=(19, 57, 62), width=8)
    # Waterfall body, layered cyan paint strokes and soft mist.
    mist = Image.new("RGBA", im.size, (0,0,0,0))
    md = ImageDraw.Draw(mist)
    md.ellipse((464, 390, 736, 514), fill=(116, 218, 198, 75))
    mist = mist.filter(ImageFilter.GaussianBlur(24))
    im = Image.alpha_composite(im.convert("RGBA"), mist).convert("RGB")
    stream = Image.new("RGBA", im.size, (0,0,0,0))
    sd = ImageDraw.Draw(stream)
    sd.polygon([(534, 214), (666, 214), (697, 425), (730, 492), (470, 492), (503, 425)], fill=(77, 195, 187, 225))
    sd.polygon([(568, 222), (632, 222), (660, 426), (681, 478), (520, 478), (540, 426)], fill=(131, 224, 204, 220))
    sd.polygon([(590, 225), (609, 225), (628, 427), (642, 472), (560, 472), (571, 427)], fill=(198, 242, 211, 210))
    im = Image.alpha_composite(im.convert("RGBA"), stream).convert("RGB")
    d = ImageDraw.Draw(im)
    rng = random.Random(51)
    for _ in range(100):
        x, y = rng.randint(510, 690), rng.randint(240, 473)
        d.line((x, y, x+rng.randint(-6, 6), y+rng.randint(14, 48)), fill=rng.choice([(207,247,216),(139,221,202),(74,181,178)]), width=rng.choice([2,3,4,5]))
    # Foamy impact and concentric, slightly irregular ripples.
    d.ellipse((457, 459, 743, 531), fill=(83, 188, 175), outline=(169, 223, 195), width=6)
    for i in range(9):
        rx, ry = 150+i*42, 24+i*12
        d.arc((600-rx, 487-ry, 600+rx, 487+ry), 8, 172, fill=(66+i*7, 142+i*9, 139+i*6), width=4)
    for _ in range(110):
        x, y, r = rng.randint(440,760), rng.randint(445,525), rng.choice([2,3,4,7])
        d.ellipse((x-r,y-r,x+r,y+r), fill=rng.choice([(150,220,195),(102,199,185),(204,239,208)]))
    return im


def start_scene_gif():
    base = start_scene()
    frames=[]
    for f in range(8):
        im=base.copy(); d=ImageDraw.Draw(im)
        for lane in range(19):
            x=520+lane*9+(f*(lane%3+2)*4)%25
            y=237+(lane*23+f*29)%226
            d.line((x,y,x+(lane%3)-1,y+18), fill=(220,255,225) if lane%2 else (138,229,207), width=4)
        for j in range(9):
            x=459+(j*47+f*19)%282
            d.ellipse((x,466+(j*11)%47,x+8,475+(j*11)%47),fill=(217,250,220))
        frames.append(im.convert("P",palette=Image.Palette.ADAPTIVE))
    out=BytesIO(); frames[0].save(out,format="GIF",save_all=True,append_images=frames[1:],duration=130,loop=0,disposal=2)
    return out.getvalue()


def _tunnel(d, box, cam, route):
    x0,y0,x1,y1=box
    d.rectangle(box,fill=(107,126,133),outline=(17,24,39),width=5)
    d.rectangle((x0+5,y0+5,x1-5,y0+32),fill=(27,38,57))
    d.text((x0+15,y0+7),f"CAM{cam}",fill=(241,238,226),stroke_width=1,stroke_fill=(25,29,39))
    # Concrete-lined perspective pipe tunnel, matching the reference's CCTV feeds.
    d.polygon([(x0+7,y0+34),(x1-7,y0+34),((x0+x1)//2+56,(y0+y1)//2+32),((x0+x1)//2-56,(y0+y1)//2+32)],fill=(144,151,143))
    d.polygon([(x0+7,y1-7),(x1-7,y1-7),((x0+x1)//2+56,(y0+y1)//2+27),((x0+x1)//2-56,(y0+y1)//2+27)],fill=(86,101,107))
    d.line((x0+9,y0+39,(x0+x1)//2-55,(y0+y1)//2+25),fill=(190,194,174),width=5)
    d.line((x1-9,y0+39,(x0+x1)//2+55,(y0+y1)//2+25),fill=(190,194,174),width=5)
    d.line((x0+12,y1-10,(x0+x1)//2-55,(y0+y1)//2+31),fill=(65,81,91),width=5)
    d.line((x1-12,y1-10,(x0+x1)//2+55,(y0+y1)//2+31),fill=(65,81,91),width=5)
    cx,cy=(x0+x1)//2,(y0+y1)//2+20
    d.ellipse((cx-53,cy-43,cx+53,cy+45),fill=(17,31,43),outline=(205,201,177),width=8)
    d.ellipse((cx-39,cy-31,cx+39,cy+33),fill=(5,19,28),outline=(79,128,125),width=5)
    wh=int(12+28*route[0]); d.polygon([(cx-34,cy+25-wh),(cx+34,cy+25-wh),(cx+34,cy+28),(cx-34,cy+28)],fill=(66,183,187))
    d.line((cx-30,cy+25-wh,cx+30,cy+25-wh),fill=(183,230,207),width=3)
    d.line((x0+15,y1-14,x1-15,y1-14),fill=(56,144,148),width=2)


def room_scene(routes):
    """Recreate the provided control-room composition: ceiling, CCTV, desk, chair, calendar."""
    w,h=1440,960
    im=Image.new("RGB",(w,h),(48,48,64)); d=ImageDraw.Draw(im)
    # Ceiling: inset perspective panels and cool recessed lights.
    d.rectangle((0,0,w,110),fill=(55,57,72))
    d.polygon([(0,0),(1440,0),(1270,94),(170,94)],fill=(64,65,79),outline=(31,34,48),width=6)
    for x in (100,360,720,1080,1340): d.line((720,0,x,91),fill=(39,42,57),width=4)
    for x in (115,430,1010,1325):
        d.ellipse((x-33,14,x+33,51),fill=(25,34,47),outline=(25,35,46),width=5)
        d.ellipse((x-20,21,x+20,43),fill=(145,207,187),outline=(196,224,202),width=3)
        d.ellipse((x-9,26,x+9,38),fill=(216,234,211))
    d.line((0,105,1440,105),fill=(140,206,186),width=5)
    # Back and angled side walls.
    d.rectangle((0,110,1440,642),fill=(79,75,91))
    d.polygon([(0,110),(170,95),(170,642),(0,690)],fill=(91,85,101))
    d.polygon([(1440,110),(1270,95),(1270,642),(1440,690)],fill=(75,70,88))
    # Subtle plaster grain and fine seam lines.
    rng=random.Random(88)
    for x in range(24,1440,88): d.line((x,115,x,637),fill=(83,78,94),width=2)
    for _ in range(2500):
        x,y=rng.randrange(1440),rng.randrange(115,635)
        d.point((x,y),fill=rng.choice([(82,79,96),(86,81,98),(77,77,93),(94,86,101)]))
    # Papers pinned to the far left wall.
    for box in [(48,205,158,330),(188,254,265,341)]:
        x0,y0,x1,y1=box
        d.rectangle((x0+7,y0+8,x1+7,y1+8),fill=(42,40,52))
        d.rectangle(box,fill=(196,188,171),outline=(44,43,51),width=5)
        d.text((x0+12,y0+13),"Inspection",fill=(49,47,50))
        for yy in range(y0+33,y1-12,13): d.line((x0+12,yy,x1-12,yy),fill=(111,106,103),width=2)
    # Large central wall display with four sewer camera views.
    d.rounded_rectangle((338,128,1100,555),radius=8,fill=(11,17,31),outline=(28,38,51),width=12)
    d.rectangle((357,147,1081,535),fill=(28,40,57),outline=(153,193,174),width=5)
    d.rectangle((372,162,1066,519),fill=(15,24,36))
    for i,route in enumerate(routes):
        x=382+(i%2)*339; y=172+(i//2)*171
        _tunnel(d,(x,y,x+330,y+163),i+1,route)
    d.line((720,165,720,520),fill=(175,190,173),width=6)
    d.line((376,343,1065,343),fill=(175,190,173),width=6)
    # Monitor's teal spill and wall-mounted frame glow.
    glow=Image.new("RGBA",(w,h),(0,0,0,0)); gd=ImageDraw.Draw(glow)
    gd.polygon([(375,548),(1060,548),(1370,956),(110,956)],fill=(105,177,163,32))
    gd.rectangle((345,135,1095,548),outline=(106,194,169,55),width=15)
    im=Image.alpha_composite(im.convert("RGBA"),glow).convert("RGB"); d=ImageDraw.Draw(im)
    # Wall baseboard and tiled concrete floor.
    d.rectangle((0,640,w,674),fill=(49,45,57)); d.line((0,640,w,640),fill=(116,91,99),width=5)
    d.rectangle((0,675,w,h),fill=(91,88,92))
    for x in range(-500,1900,150): d.line((720,675,x,959),fill=(112,106,108),width=2)
    for y in (710,758,818,890,950): d.line((0,y,w,y),fill=(74,74,82),width=2)
    for _ in range(400):
        x,y=rng.randrange(w),rng.randrange(680,h)
        d.line((x,y,min(w-1,x+rng.randrange(2,12)),y),fill=(102,97,101),width=1)
    # Left-side utility desk: desktop, drawers and two supports that terminate on the floor.
    d.polygon([(18,480),(456,480),(424,548),(0,548)],fill=(73,57,60),outline=(35,35,48),width=5)
    d.polygon([(28,462),(442,462),(456,488),(10,488)],fill=(133,106,96),outline=(39,37,48),width=4)
    d.rectangle((57,488,82,709),fill=(41,38,52)); d.rectangle((383,488,410,709),fill=(41,38,52))
    d.rectangle((100,505,235,591),fill=(65,49,55),outline=(39,37,48),width=4)
    d.rectangle((244,505,374,591),fill=(61,47,53),outline=(39,37,48),width=4)
    d.rectangle((118,542,138,550),fill=(153,123,80)); d.rectangle((344,542,364,550),fill=(153,123,80))
    # Desktop computer and keyboard.
    d.rectangle((127,320,326,452),fill=(13,22,39),outline=(23,31,43),width=8)
    d.rectangle((139,332,314,437),fill=(46,121,128))
    d.line((157,357,279,357),fill=(175,218,191),width=5)
    d.line((157,380,292,380),fill=(192,191,150),width=4)
    d.line((157,402,266,402),fill=(175,218,191),width=3)
    d.rectangle((210,452,246,462),fill=(28,32,44))
    d.polygon([(94,463),(344,463),(359,480),(78,480)],fill=(130,128,117),outline=(38,40,49),width=3)
    for x in range(101,346,15): d.line((x,470,x+8,470),fill=(58,66,72),width=2)
    # Green inspection board above the left workstation.
    d.rectangle((86,274,392,421),fill=(44,70,71),outline=(27,39,47),width=5)
    for yy in (303,331,359,387):
        d.line((107,yy,365,yy),fill=(174,207,180),width=3)
    # Right wall calendar, large and clearly mounted.
    d.rectangle((1183,202,1386,495),fill=(39,39,53),outline=(37,38,51),width=8)
    d.rectangle((1195,214,1374,482),fill=(211,205,187),outline=(63,59,61),width=4)
    d.rectangle((1195,214,1374,266),fill=(168,164,154))
    d.text((1241,225),"CALENDAR",fill=(40,41,46),stroke_width=1)
    for x in (1216,1252,1288,1324,1360): d.line((x,271,x,470),fill=(131,127,119),width=2)
    for y in (272,310,348,386,424,462): d.line((1200,y,1368,y),fill=(131,127,119),width=2)
    for row in range(5):
        for col in range(5): d.text((1206+col*33,277+row*38),str(row*5+col+1),fill=(61,61,60))
    d.line((1289,420,1307,440,1345,393),fill=(43,139,112),width=9)
    # Foreground worktable as in the reference; paper is the clickable gradient-descent note.
    d.polygon([(341,850),(1120,850),(1203,959),(246,959)],fill=(81,64,61),outline=(42,36,43),width=5)
    d.polygon([(619,838),(790,838),(832,920),(574,920)],fill=(211,202,180),outline=(66,59,56),width=4)
    for y in (856,872,888,904): d.line((631,y,779,y),fill=(150,143,128),width=2)
    d.rectangle((918,838,980,902),fill=(52,44,43),outline=(35,34,40),width=4)
    d.ellipse((928,830,971,844),fill=(126,126,111))
    # Shelf on right, secondary detail.
    d.polygon([(1168,530),(1417,530),(1417,547),(1150,547)],fill=(99,77,69))
    for i in range(4):
        x=1190+i*52
        d.rectangle((x,474-i*5,x+43,529),fill=(85,70,68),outline=(38,38,47),width=3)
        d.rectangle((x+6,482-i*5,x+36,489-i*5),fill=(160,145,120))
    return im


def zoomed_object(routes, obj):
    scene=room_scene(routes)
    if obj=="pc": return scene.crop((0,245,470,725)).resize((705,720),Image.Resampling.LANCZOS)
    if obj=="calendar": return scene.crop((1150,175,1420,515)).resize((570,720),Image.Resampling.LANCZOS)
    return scene
