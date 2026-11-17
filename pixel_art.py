"""Illustrated sewer scenes drawn in code with Pillow."""
from io import BytesIO
import math
import random
from PIL import Image, ImageDraw, ImageFilter

START_W, START_H = 1000, 500
ROOM_W, ROOM_H = 1440, 960


def _lerp(a, b, t):
    return tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(3))


def start_scene():
    """Wide stone outfall reference: centered pipe, falling water, rippling pool."""
    im = Image.new("RGB", (START_W, START_H))
    px = im.load()
    for y in range(START_H):
        c = _lerp((30, 66, 68), (7, 29, 42), y / START_H)
        for x in range(START_W):
            shade = int(5 * math.sin(x / 61) + 3 * math.sin((x + y) / 39))
            px[x, y] = tuple(max(0, min(255, v + shade)) for v in c)
    d = ImageDraw.Draw(im)
    rng = random.Random(38)
    # Broad, uneven masonry blocks with dark mortar, chipped edges and mossy highlights.
    for row, y in enumerate(range(-30, 320, 70)):
        offset = -62 if row % 2 else -18
        for x in range(offset, START_W + 80, 119):
            x0, y0 = x + rng.randint(-5, 5), y + rng.randint(-5, 4)
            x1, y1 = x0 + rng.randint(109, 124), y0 + rng.randint(59, 69)
            stone = rng.choice([(45, 93, 92), (51, 104, 100), (38, 82, 87), (57, 110, 102)])
            d.rounded_rectangle((x0, y0, x1, y1), radius=9, fill=(13, 37, 43), outline=(8, 29, 37), width=4)
            d.rounded_rectangle((x0+4, y0+3, x1-4, y1-4), radius=7, fill=stone, outline=(20, 54, 57), width=2)
            d.line((x0+11, y0+7, x1-14, y0+7), fill=(110, 155, 134), width=3)
            d.line((x0+13, y0+13, x0+43, y0+13), fill=(79, 132, 124), width=2)
            for _ in range(3):
                xx, yy = rng.randint(x0+12, x1-14), rng.randint(y0+19, y1-8)
                d.line((xx, yy, xx+rng.randint(7, 22), yy-rng.randint(0, 6)), fill=(26, 63, 66), width=2)
    # Waterline and deep pool.
    d.rectangle((0, 348, START_W, START_H), fill=(8, 39, 51))
    d.line((0, 352, START_W, 352), fill=(103, 163, 147), width=5)
    for _ in range(220):
        x, y = rng.randrange(START_W), rng.randrange(360, START_H)
        d.line((x, y, min(START_W-1, x+rng.randrange(5, 45)), y+rng.choice([-1, 0, 1])),
               fill=rng.choice([(18, 68, 78), (26, 93, 100), (36, 116, 113), (13, 56, 70)]), width=2)
    # Thick round outfall lip and deep circular tunnel, precisely centered.
    cx, cy = 500, 143
    d.ellipse((cx-126, cy-126, cx+126, cy+126), fill=(15, 41, 47), outline=(8, 27, 35), width=12)
    d.ellipse((cx-112, cy-112, cx+112, cy+112), fill=(76, 134, 122), outline=(132, 183, 157), width=8)
    d.arc((cx-110, cy-110, cx+110, cy+110), 193, 344, fill=(181, 218, 179), width=6)
    d.ellipse((cx-91, cy-91, cx+91, cy+91), fill=(25, 68, 69), outline=(50, 105, 99), width=7)
    d.ellipse((cx-72, cy-72, cx+72, cy+72), fill=(3, 24, 31), outline=(21, 61, 64), width=6)
    # Waterfall with layered turquoise colors, painterly highlights and soft spray.
    spray = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(spray)
    sd.ellipse((390, 328, 610, 420), fill=(108, 218, 199, 100))
    spray = spray.filter(ImageFilter.GaussianBlur(17))
    im = Image.alpha_composite(im.convert("RGBA"), spray).convert("RGB")
    waterfall = Image.new("RGBA", im.size, (0, 0, 0, 0))
    wd = ImageDraw.Draw(waterfall)
    wd.polygon([(450, 143), (550, 143), (573, 348), (606, 405), (394, 405), (427, 348)], fill=(66, 185, 181, 236))
    wd.polygon([(475, 151), (525, 151), (548, 349), (570, 395), (430, 395), (452, 349)], fill=(129, 219, 201, 230))
    wd.polygon([(491, 155), (508, 155), (525, 351), (537, 389), (463, 389), (476, 351)], fill=(194, 240, 212, 220))
    im = Image.alpha_composite(im.convert("RGBA"), waterfall).convert("RGB")
    d = ImageDraw.Draw(im)
    rng = random.Random(51)
    for _ in range(75):
        x, y = rng.randint(425, 575), rng.randint(167, 389)
        d.line((x, y, x+rng.randint(-4, 4), y+rng.randint(11, 34)), fill=rng.choice([(213, 250, 220), (144, 224, 204), (74, 180, 177)]), width=rng.choice([2, 3, 4]))
    # Impact foam and concentric ripples spread across the lower water.
    d.ellipse((397, 377, 603, 426), fill=(80, 181, 171), outline=(171, 224, 194), width=5)
    for i in range(8):
        rx, ry = 105 + i*37, 15 + i*9
        d.arc((500-rx, 405-ry, 500+rx, 405+ry), 8, 172, fill=(62+i*7, 137+i*9, 137+i*6), width=3)
    for _ in range(90):
        x, y, r = rng.randint(380, 620), rng.randint(368, 422), rng.choice([2, 3, 4, 6])
        d.ellipse((x-r, y-r, x+r, y+r), fill=rng.choice([(149, 219, 194), (99, 195, 183), (204, 239, 209)]))
    # Tiny pale glint at lower-right, as in the supplied title illustration.
    d.polygon([(950, 454), (958, 470), (976, 478), (959, 484), (950, 500), (942, 484), (925, 477), (942, 469)], fill=(188, 213, 198))
    return im


def start_scene_gif():
    base = start_scene()
    frames = []
    for frame_index in range(8):
        frame = base.copy()
        d = ImageDraw.Draw(frame)
        for lane in range(15):
            x = 432 + lane*9 + (frame_index*(lane % 3 + 2)*3) % 19
            y = 163 + (lane*19 + frame_index*25) % 221
            d.line((x, y, x+(lane % 3)-1, y+14), fill=(222, 255, 227) if lane % 2 else (139, 230, 209), width=3)
        for j in range(8):
            x = 401 + (j*39 + frame_index*17) % 197
            d.ellipse((x, 382+(j*9) % 35, x+7, 389+(j*9) % 35), fill=(213, 250, 221))
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE))
    out = BytesIO()
    frames[0].save(out, format="GIF", save_all=True, append_images=frames[1:], duration=130, loop=0, disposal=2)
    return out.getvalue()


def _tunnel(d, box, cam, route):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(103, 124, 132), outline=(17, 24, 39), width=5)
    d.rectangle((x0+5, y0+5, x1-5, y0+32), fill=(27, 38, 57))
    d.text((x0+15, y0+7), f"CAM{cam}", fill=(241, 238, 226), stroke_width=1, stroke_fill=(25, 29, 39))
    # Concrete corridor perspective with pipes, seams, damp staining and a distant drain.
    cx, cy = (x0+x1)//2, (y0+y1)//2
    d.polygon([(x0+7,y0+34),(x1-7,y0+34),(cx+56,cy+32),(cx-56,cy+32)], fill=(137,148,143))
    d.polygon([(x0+7,y1-7),(x1-7,y1-7),(cx+56,cy+27),(cx-56,cy+27)], fill=(79,96,105))
    for k in range(4):
        yy = y0 + 43 + k*22
        d.line((x0+15, yy, cx-57, cy+27-k*3), fill=(178-k*13,184-k*12,166-k*10), width=2)
        d.line((x1-15, yy, cx+57, cy+27-k*3), fill=(178-k*13,184-k*12,166-k*10), width=2)
    d.line((x0+9,y0+39,cx-55,cy+24),fill=(191,198,177),width=5)
    d.line((x1-9,y0+39,cx+55,cy+24),fill=(191,198,177),width=5)
    d.line((x0+12,y1-10,cx-55,cy+30),fill=(61,79,91),width=5)
    d.line((x1-12,y1-10,cx+55,cy+30),fill=(61,79,91),width=5)
    d.ellipse((cx-53,cy-43,cx+53,cy+45),fill=(17,31,43),outline=(205,201,177),width=8)
    d.ellipse((cx-39,cy-31,cx+39,cy+33),fill=(5,19,28),outline=(79,128,125),width=5)
    water_h = int(12 + 28*route[0])
    d.polygon([(cx-34,cy+25-water_h),(cx+34,cy+25-water_h),(cx+34,cy+28),(cx-34,cy+28)],fill=(66,183,187))
    d.line((cx-30,cy+25-water_h,cx+30,cy+25-water_h),fill=(183,230,207),width=3)
    # A few pink/rust/cream sensor specks along water.
    for j in range(int(route[2]*5)):
        xx = cx - 22 + j*10
        d.rectangle((xx, cy+18, xx+5, cy+22), fill=(203,162,108) if j%2 else (207,130,148))
    d.line((x0+15,y1-14,x1-15,y1-14),fill=(56,144,148),width=2)


def room_scene(routes):
    """A detailed 3:2 control room matching the supplied composition and object positions."""
    w, h = ROOM_W, ROOM_H
    im = Image.new("RGB", (w, h), (49, 48, 65))
    d = ImageDraw.Draw(im)
    rng = random.Random(88)
    # Perspective ceiling, recessed panels and rows of cool circular lamps.
    d.rectangle((0, 0, w, 114), fill=(48, 51, 67))
    d.polygon([(0,0),(w,0),(1270,94),(170,94)], fill=(63,65,79), outline=(27,32,46), width=7)
    d.line((170,94,0,110), fill=(28,34,47), width=6)
    d.line((1270,94,1440,110), fill=(28,34,47), width=6)
    for x in (100,360,720,1080,1340):
        d.line((720,0,x,91), fill=(37,41,55), width=4)
    for x in (115,430,1010,1325):
        d.ellipse((x-35,12,x+35,53), fill=(20,30,43), outline=(24,36,49), width=5)
        d.ellipse((x-23,19,x+23,47), fill=(106,157,150), outline=(173,207,187), width=3)
        d.ellipse((x-12,24,x+12,42), fill=(205,226,202))
        d.ellipse((x-5,28,x+5,38), fill=(229,240,213))
    d.line((0,105,w,105), fill=(127,190,174), width=5)
    # Side walls angle toward the back wall; restrained lavender-gray palette.
    d.polygon([(0,110),(170,95),(170,640),(0,690)], fill=(83,78,95))
    d.rectangle((170,105,1270,642), fill=(73,73,89))
    d.polygon([(1440,110),(1270,95),(1270,642),(1440,690)], fill=(74,70,88))
    for x in range(196,1265,88):
        d.line((x,112,x,633),fill=(78,76,91),width=2)
    for y in range(137,631,77):
        d.line((172,y,1268,y),fill=(75,74,89),width=2)
    # Plaster brush grain and tiny scuffs.
    for _ in range(2100):
        x,y=rng.randrange(5,1435),rng.randrange(115,635)
        d.point((x,y),fill=rng.choice([(78,77,93),(83,80,96),(68,72,88),(91,84,99)]))
    for _ in range(90):
        x,y=rng.randrange(10,1430),rng.randrange(130,630)
        d.line((x,y,x+rng.randrange(5,28),y+rng.randrange(-4,5)),fill=(58,62,77),width=1)
    # Left wall certificates and inspection noticeboard.
    for box in [(48,205,158,330),(188,254,265,341)]:
        x0,y0,x1,y1=box
        d.rectangle((x0+8,y0+8,x1+8,y1+8),fill=(42,40,52))
        d.rectangle(box,fill=(187,179,164),outline=(37,39,49),width=5)
        d.rectangle((x0+8,y0+8,x1-8,y1-8),fill=(211,203,185))
        d.text((x0+15,y0+14),"Inspection",fill=(51,49,52))
        for yy in range(y0+35,y1-12,13): d.line((x0+14,yy,x1-13,yy),fill=(122,115,107),width=2)
    d.rectangle((39,364,299,510),fill=(25,32,43),outline=(23,31,44),width=5)
    d.rectangle((48,373,290,499),fill=(43,67,68))
    for yy in (397,419,441,463,485):
        d.line((62,yy,272-(yy%3)*7,yy),fill=(163,192,171),width=2)
    # Large central four-feed CCTV screen, built in several metal/glass borders.
    d.rounded_rectangle((338,128,1100,555),radius=6,fill=(8,14,28),outline=(23,31,45),width=12)
    d.rectangle((357,147,1081,535),fill=(23,36,52),outline=(120,169,154),width=5)
    d.rectangle((372,162,1066,519),fill=(11,20,33))
    for i,route in enumerate(routes):
        x=382+(i%2)*339
        y=172+(i//2)*171
        _tunnel(d,(x,y,x+330,y+163),i+1,route)
    d.line((720,165,720,520),fill=(163,179,164),width=6)
    d.line((376,343,1065,343),fill=(163,179,164),width=6)
    # Thin mint light around the screen, then a soft trapezoid spill across the room.
    glow=Image.new("RGBA",(w,h),(0,0,0,0)); gd=ImageDraw.Draw(glow)
    gd.rectangle((345,135,1095,548),outline=(104,195,169,75),width=14)
    gd.polygon([(375,548),(1060,548),(1370,956),(110,956)],fill=(105,177,163,34))
    glow=glow.filter(ImageFilter.GaussianBlur(5))
    im=Image.alpha_composite(im.convert("RGBA"),glow).convert("RGB")
    d=ImageDraw.Draw(im)
    # Baseboards, tiled floor, converging grout lines and floor wear.
    d.rectangle((0,640,w,675),fill=(46,43,55)); d.line((0,640,w,640),fill=(114,91,100),width=5)
    d.rectangle((0,675,w,h),fill=(82,80,86))
    for x in range(-500,1901,150): d.line((720,675,x,959),fill=(106,101,106),width=2)
    for y in (710,758,818,890,950): d.line((0,y,w,y),fill=(69,70,79),width=2)
    for _ in range(450):
        x,y=rng.randrange(w),rng.randrange(680,h)
        d.line((x,y,min(w-1,x+rng.randrange(2,13)),y),fill=rng.choice([(94,90,96),(105,99,101),(76,78,87)]),width=1)
    # Left desk, visible drawer fronts, and legs extending all the way to the floor.
    d.polygon([(18,480),(456,480),(424,548),(0,548)],fill=(69,54,58),outline=(32,32,45),width=5)
    d.polygon([(28,462),(442,462),(456,488),(10,488)],fill=(131,104,94),outline=(37,35,47),width=4)
    d.rectangle((57,488,82,709),fill=(34,33,46)); d.rectangle((383,488,410,709),fill=(34,33,46))
    d.rectangle((100,505,235,591),fill=(62,47,53),outline=(35,34,46),width=4)
    d.rectangle((244,505,374,591),fill=(59,46,53),outline=(35,34,46),width=4)
    d.rectangle((118,542,138,550),fill=(151,120,78)); d.rectangle((344,542,364,550),fill=(151,120,78))
    # CRT-like workstation display and keyboard on the desk surface.
    d.rectangle((127,320,326,452),fill=(10,18,34),outline=(20,29,42),width=8)
    d.rectangle((139,332,314,437),fill=(41,112,123))
    d.rectangle((146,339,307,430),fill=(48,124,130))
    d.line((157,357,279,357),fill=(169,211,187),width=5)
    d.line((157,380,292,380),fill=(191,186,148),width=4)
    d.line((157,402,266,402),fill=(164,209,187),width=3)
    d.rectangle((210,452,246,462),fill=(27,31,43))
    d.polygon([(94,463),(344,463),(359,480),(78,480)],fill=(126,125,115),outline=(35,39,48),width=3)
    for x in range(101,346,15): d.line((x,470,x+8,470),fill=(57,65,72),width=2)
    # Center office chair: back, seat, central post, star base and casters all visible.
    d.polygon([(474,397),(637,397),(666,579),(625,623),(493,611),(450,556)],fill=(50,58,74),outline=(24,30,43),width=8)
    d.polygon([(498,414),(615,414),(636,555),(611,587),(506,578),(478,546)],fill=(72,77,91),outline=(117,126,133),width=4)
    d.line((518,439,527,547),fill=(121,129,136),width=4)
    d.polygon([(461,563),(623,563),(681,607),(646,639),(471,625),(430,597)],fill=(52,61,75),outline=(24,30,43),width=7)
    d.polygon([(476,574),(606,574),(650,605),(627,620),(483,610),(457,592)],fill=(79,86,96))
    # Arm rests, support column and five-legged rolling base touch the floor.
    d.line((458,532,430,565,435,574,480,566),fill=(41,49,64),width=11)
    d.line((639,529,666,557,660,567,624,561),fill=(41,49,64),width=11)
    d.rectangle((535,625,559,719),fill=(28,34,48))
    d.ellipse((516,704,579,729),fill=(37,44,58),outline=(22,28,40),width=4)
    for angle in range(0,360,72):
        rad=math.radians(angle)
        x2=548+104*math.cos(rad); y2=724+34*math.sin(rad)
        d.line((548,716,x2,y2),fill=(38,45,59),width=12)
        d.ellipse((x2-14,y2-9,x2+14,y2+10),fill=(30,35,46),outline=(17,23,34),width=3)
    # Large paper calendar firmly attached to right wall.
    d.rectangle((1183,202,1386,495),fill=(39,39,53),outline=(35,36,49),width=8)
    d.rectangle((1195,214,1374,482),fill=(211,205,187),outline=(59,57,59),width=4)
    d.rectangle((1195,214,1374,267),fill=(183,178,164))
    d.text((1241,225),"CALENDAR",fill=(40,41,46),stroke_width=1)
    for x in (1216,1252,1288,1324,1360): d.line((x,271,x,470),fill=(127,124,118),width=2)
    for y in (272,310,348,386,424,462): d.line((1200,y,1368,y),fill=(127,124,118),width=2)
    for row in range(5):
        for col in range(5): d.text((1206+col*33,277+row*38),str(row*5+col+1),fill=(61,61,60))
    d.line((1289,420,1307,440,1345,393),fill=(43,139,112),width=9)
    # Foreground worktable, paper note, and mug.
    d.polygon([(341,850),(1120,850),(1203,959),(246,959)],fill=(77,61,59),outline=(38,34,42),width=5)
    d.polygon([(619,838),(790,838),(832,920),(574,920)],fill=(211,202,180),outline=(64,58,55),width=4)
    for y in (856,872,888,904): d.line((631,y,779,y),fill=(146,139,125),width=2)
    d.rectangle((918,838,980,902),fill=(52,44,43),outline=(35,34,40),width=4)
    d.ellipse((928,830,971,844),fill=(126,126,111))
    # Small shelf and upright files on the right wall.
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
