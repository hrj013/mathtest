"""Raster pixel-art illustrations for the Drain Town game.

Each scene is painted directly on a 640x360 RGB canvas with Pillow. The canvas is
not a collection of enlarged vector rectangles: details, texture, contours and
lighting are authored as pixel clusters. Streamlit displays it with nearest-neighbour
scaling for crisp pixels.
"""
from PIL import Image, ImageDraw
import random

W, H = 640, 360

C = {
    "night": (34, 30, 95), "deep": (18, 27, 83), "blue": (40, 62, 142),
    "wall": (101, 96, 151), "wall_light": (150, 139, 179),
    "cream": (241, 220, 170), "water": (56, 194, 218), "foam": (176, 242, 222),
    "pink": (231, 112, 174), "teal": (60, 195, 183),
    "wood": (132, 91, 67), "wood_light": (177, 127, 88), "shadow": (44, 37, 66),
}


def _image(color):
    return Image.new("RGB", (W, H), color)


def _rect(d, xy, fill, outline=None, width=1):
    d.rectangle(xy, fill=fill, outline=outline, width=width)


def _pixel_scatter(d, bounds, count, colors, seed, size=(1, 2)):
    rng = random.Random(seed)
    x0, y0, x1, y1 = bounds
    for _ in range(count):
        x, y = rng.randrange(x0, x1), rng.randrange(y0, y1)
        w, h = rng.choice(size), rng.choice(size)
        d.rectangle((x, y, x + w, y + h), fill=rng.choice(colors))


def _coral(d, x, y, color, scale=1):
    dark = (112, 56, 130)
    d.line([(x, y+21*scale), (x, y+10*scale), (x-5*scale, y+4*scale)], fill=dark, width=2*scale)
    d.line([(x, y+13*scale), (x+6*scale, y+7*scale), (x+8*scale, y+1*scale)], fill=color, width=3*scale)
    d.line([(x-2*scale, y+17*scale), (x-9*scale, y+11*scale)], fill=color, width=3*scale)
    d.rectangle((x-3*scale, y+6*scale, x+1*scale, y+10*scale), fill=color)
    d.rectangle((x+5*scale, y+3*scale, x+9*scale, y+7*scale), fill=(247, 171, 210))


def start_scene():
    """Front-on round outfall mouth with water visibly flowing into the river."""
    im = _image((72, 111, 187))
    d = ImageDraw.Draw(im)
    # Night sky and underwater river-town palette, with subtle pixel grain.
    _rect(d, (0, 0, W, 176), (95, 119, 195))
    _rect(d, (0, 0, W, 64), (89, 107, 185))
    _pixel_scatter(d, (0, 5, W, 165), 190, [(186, 195, 232), (246, 221, 153), (137, 222, 222), (205, 157, 213)], 41, (1, 1))
    # Far bank, dark blue masonry and small colored plants.
    _rect(d, (0, 158, 639, 204), (42, 63, 135))
    _rect(d, (0, 159, 639, 5), (24, 39, 105))
    for x in range(-4, 645, 34):
        d.line((x, 165, x, 193), fill=(31, 47, 112), width=2)
        d.line((x+8, 177, x+23, 177), fill=(119, 143, 203), width=2)
        d.line((x-4, 188, x+7, 188), fill=(92, 116, 182), width=1)
    for x,y,col in [(24,104,C['teal']),(112,132,C['pink']),(168,91,(81,206,190)),(472,119,C['pink']),(553,92,C['teal']),(605,136,(236,133,185))]:
        _coral(d,x,y,col,1)
    # Lower channel surface, paving lines, reflections.
    _rect(d, (0, 205, 639, 359), (48, 69, 145))
    d.line((0, 211, 639, 211), fill=(223, 225, 237), width=4)
    d.line((0, 337, 639, 337), fill=(216, 223, 239), width=4)
    _pixel_scatter(d, (0, 220, 639, 329), 100, [(83, 106, 175), (37, 55, 126), (107, 128, 187)], 12, (2,1))
    # Heavy concrete mounting blocks around an actual circular pipe opening.
    d.rectangle((72, 98, 111, 279), fill=(25, 39, 103), outline=(14, 25, 79), width=3)
    d.rectangle((109, 112, 126, 263), fill=(233, 214, 159), outline=(17, 29, 86), width=3)
    d.rectangle((284, 98, 323, 279), fill=(25, 39, 103), outline=(14, 25, 79), width=3)
    d.rectangle((269, 112, 286, 263), fill=(233, 214, 159), outline=(17, 29, 86), width=3)
    # concentric ring bands, shaded upper lip, dark tunnel interior
    cx, cy = 204, 207
    d.ellipse((111, 108, 297, 294), fill=(19, 30, 82), outline=(12, 22, 70), width=4)
    d.ellipse((121, 117, 287, 285), fill=(225, 207, 151), outline=(17, 29, 86), width=4)
    d.ellipse((132, 128, 276, 274), fill=(103, 120, 144), outline=(39, 58, 120), width=5)
    d.ellipse((146, 141, 263, 258), fill=(17, 47, 91), outline=(17, 38, 91), width=4)
    # Tunnel highlights and waterline: water exits through the bottom of the circular mouth.
    d.arc((126, 120, 282, 278), 198, 342, fill=(246, 225, 171), width=4)
    d.rectangle((151, 196, 256, 228), fill=(42, 182, 211))
    d.rectangle((160, 190, 245, 198), fill=(166, 242, 222))
    d.rectangle((158, 224, 248, 239), fill=(31, 145, 193))
    d.line((165, 205, 236, 205), fill=(110, 228, 230), width=3)
    # Flow spills out and fans into the foreground channel in rippling pixel bands.
    bands = [(239, 167, 42, (31, 151, 198)), (249, 149, 78, (47, 188, 216)),
             (264, 128, 119, (75, 208, 221)), (280, 103, 170, (136, 226, 218)),
             (298, 77, 222, (92, 211, 214)), (316, 48, 281, (178, 237, 220))]
    for y, x, w, col in bands:
        d.rectangle((x, y, x+w, y+7), fill=col)
        d.line((x+12, y+2, x+w-16, y+2), fill=(213, 250, 230), width=2)
        for xx in range(x+4, x+w, 37):
            d.rectangle((xx, y+5, xx+6, y+7), fill=(69, 193, 214))
    _pixel_scatter(d, (18, 242, 620, 354), 115, [(102, 125, 185), (29, 48, 121), (180, 236, 221), (240, 216, 123)], 77, (2,1))
    # Pixel grasses and tiny flowers along the water edge.
    for x,y in [(17,320),(49,326),(392,321),(566,325),(610,313)]: _coral(d,x,y,(222,104,171),1)
    d.text((364, 59), "DRAIN TOWN WATERWAY", fill=(255, 237, 187), stroke_width=1, stroke_fill=(25, 34, 91))
    return im


def _draw_calendar(d, x, y, scale=1):
    w,h=47*scale,64*scale
    d.rectangle((x+3*scale,y+4*scale,x+w+3*scale,y+h+4*scale),fill=(59,43,82))
    d.rectangle((x,y,x+w,y+h),fill=(242,225,182),outline=(17,29,86),width=3*scale)
    d.rectangle((x,y,x+w,y+15*scale),fill=(220,103,157),outline=(17,29,86),width=2*scale)
    for xx in (x+11*scale,x+34*scale):
        d.rectangle((xx,y-5*scale,xx+5*scale,y+7*scale),fill=(18,29,83))
    for yy in (22,33,44,55):
        for xx in (8,21,34):
            d.rectangle((x+xx*scale,y+yy*scale,x+(xx+7)*scale,y+(yy+4)*scale),fill=(49,79,157))
    d.line((x+20*scale,y+49*scale,x+26*scale,y+56*scale),fill=(28,155,119),width=3*scale)
    d.line((x+26*scale,y+56*scale,x+39*scale,y+42*scale),fill=(28,155,119),width=3*scale)


def _feed(d, rect, idx, route):
    x,y,w,h=rect
    d.rectangle((x,y,x+w,y+h),fill=(80,118,174))
    d.rectangle((x,y,x+w,y+5),fill=(31,48,116))
    d.rectangle((x,y+h-5,x+w,y+h),fill=(31,48,116))
    # pipe tunnel with layered ring, visible water, sediment and rust pixels
    cx=x+w//2; cy=y+h//2
    rw=int(w*.24); rh=int(h*.34)
    d.rectangle((cx-rw-4,cy-rh-3,cx+rw+4,cy+rh+3),fill=(18,29,86))
    d.rectangle((cx-rw,cy-rh,cx+rw,cy+rh),fill=(226,208,153))
    d.rectangle((cx-rw+4,cy-rh+4,cx+rw-4,cy+rh-4),fill=(98,117,143))
    d.rectangle((cx-rw+9,cy-rh+8,cx+rw-9,cy+rh-7),fill=(17,47,91))
    water=int(max(3,(rh*1.35)*route[0]))
    d.rectangle((cx-rw+10,cy+rh-8-water,cx+rw-10,cy+rh-8),fill=(43,190,216))
    d.line((cx-rw+14,cy+rh-9-water,cx+rw-14,cy+rh-9-water),fill=(182,245,226),width=2)
    for j in range(int(route[2]*7)):
        xx=cx-rw+12+j*5
        d.rectangle((xx,cy+rh-10,xx+3,cy+rh-7),fill=(241,207,100) if j%2 else (224,112,166))
    for j in range(int(route[3]*5)):
        d.rectangle((x+6+j*11,y+8+(j%2)*3,x+10+j*11,y+11+(j%2)*3),fill=(217,103,126))
    for j in range(int(route[1]*6)):
        xx=x+8+j*16; yy=y+9+(j%3)*7
        d.point((xx,yy),fill=(180,240,222)); d.point((xx+1,yy),fill=(180,240,222))
    d.rectangle((x+5,y+5,x+43,y+17),fill=(15,24,71))
    d.text((x+9,y+7),f"CAM 0{idx+1}",fill=(255,239,188))


def room_scene(routes):
    """Cozy pixel office: one floor, back wall, side walls, left desk PC, right calendar."""
    rng=random.Random(812)
    im=Image.new("RGB",(W,H),(76,66,119)); d=ImageDraw.Draw(im)
    # Room shell: ceiling, one back wall, two perspective side walls and a single floor plane.
    d.polygon([(0,0),(640,0),(568,45),(72,45)],fill=(192,190,197))
    d.polygon([(0,0),(72,45),(72,244),(0,285)],fill=(226,222,222))
    d.polygon([(640,0),(568,45),(568,244),(640,285)],fill=(177,176,189))
    d.rectangle((72,45,568,244),fill=(218,211,213))
    # Gentle wall light, subtle pixel plaster grain and blue-edged wainscot.
    for _ in range(330):
        x=rng.randrange(74,567); y=rng.randrange(48,241)
        col=rng.choice([(222,216,215),(211,204,213),(232,224,216),(202,199,210)])
        d.point((x,y),fill=col)
    d.line((72,241,568,241),fill=(150,119,155),width=3)
    d.polygon([(0,247),(72,244),(568,244),(640,247),(640,285),(0,285)],fill=(70,82,145))
    d.line((0,285,640,285),fill=(18,37,105),width=5)
    for x in range(8,640,18): d.line((x,251,x,281),fill=(81,96,157),width=1)
    # The only floor is one continuous wood plane, with perspective plank seams.
    d.polygon([(0,290),(640,290),(640,360),(0,360)],fill=(112,79,65))
    for x in range(0,641,24): d.line((320,291,x,359),fill=(165,119,85),width=1)
    for y in (298,307,319,333,348,358):
        left=max(0,int(320-(y-290)*4.5)); right=min(639,int(320+(y-290)*4.5))
        d.line((left,y,right,y),fill=(68,51,59),width=1)
    for _ in range(145):
        x=rng.randrange(3,637); y=rng.randrange(294,359)
        col=rng.choice([(155,111,80),(134,91,72),(184,137,96),(92,67,62)])
        d.line((x,y,x+rng.randrange(2,8),y),fill=col,width=1)
    # Main cinema-sized monitor mounted on the back wall; four feeds share one screen.
    d.rectangle((161,56,477,225),fill=(14,24,79),outline=(8,17,62),width=4)
    d.rectangle((169,64,469,217),fill=(38,46,99),outline=(115,124,165),width=2)
    d.rectangle((176,71,462,210),fill=(9,14,39))
    d.line((181,75,457,75),fill=(207,207,203),width=2)
    d.line((181,206,457,206),fill=(207,207,203),width=2)
    d.line((181,75,181,206),fill=(207,207,203),width=2)
    d.line((457,75,457,206),fill=(207,207,203),width=2)
    d.line((319,75,319,206),fill=(151,166,193),width=2)
    d.line((181,140,457,140),fill=(151,166,193),width=2)
    for i,route in enumerate(routes):
        x=185+(i%2)*138; y=80+(i//2)*65
        _feed(d,(x,y,132,56),i,route)
    # Wall calendar fixed on the RIGHT side wall, with a mount, paper shadow and pins.
    d.line((589,71,589,207),fill=(20,34,91),width=4)
    d.rectangle((581,77,628,143),fill=(65,49,89))
    _draw_calendar(d,577,72,1)
    d.rectangle((574,68,580,74),fill=(246,225,162),outline=(18,29,83))
    # Small wall notice, utility pipe and wall sockets.
    d.rectangle((516,83,548,119),fill=(31,47,112),outline=(16,28,83),width=2)
    d.rectangle((520,87,544,115),fill=(240,225,187))
    for yy in (92,99,106): d.line((524,yy,540,yy),fill=(86,101,154),width=1)
    d.line((608,44,608,238),fill=(24,39,99),width=3)
    d.rectangle((604,43,612,48),fill=(231,210,151))
    # LEFT workstation: desk is against the left wall, extends into room in perspective.
    # Dark contact shadow beneath desk, desktop top, front fascia, two legs and drawers.
    d.polygon([(20,202),(170,202),(211,279),(10,279)],fill=(48,39,68))
    d.polygon([(18,190),(166,190),(199,213),(9,213)],fill=(162,108,75),outline=(17,29,86))
    d.polygon([(9,213),(199,213),(192,228),(17,228)],fill=(91,59,61),outline=(17,29,86))
    d.polygon([(19,228),(34,228),(33,277),(21,277)],fill=(54,43,62))
    d.polygon([(173,228),(188,228),(194,276),(180,276)],fill=(54,43,62))
    d.rectangle((43,233,96,261),fill=(126,79,65),outline=(51,40,67))
    d.rectangle((99,233,156,261),fill=(117,74,63),outline=(51,40,67))
    d.rectangle((50,244,57,247),fill=(229,201,133)); d.rectangle((143,244,150,247),fill=(229,201,133))
    # CRT PC sits ON the desktop; keyboard, mouse, lamp, papers and mug share desktop plane.
    d.rectangle((58,139,128,190),fill=(15,25,79),outline=(8,17,61),width=3)
    d.rectangle((64,145,122,181),fill=(46,121,174))
    d.rectangle((68,149,118,176),fill=(77,202,210))
    d.line((73,155,103,155),fill=(210,242,208),width=2)
    d.line((73,163,111,163),fill=(244,215,119),width=2)
    d.rectangle((107,169,114,172),fill=(235,117,168))
    d.rectangle((88,190,101,197),fill=(23,36,89)); d.rectangle((74,197,117,202),fill=(14,24,76))
    d.polygon([(42,201),(135,201),(142,210),(37,210)],fill=(224,218,204),outline=(24,40,103))
    for x in range(48,134,6): d.point((x,205),fill=(83,103,155))
    d.rectangle((146,202,157,209),fill=(17,27,79)); d.rectangle((148,203,153,206),fill=(232,220,186))
    # Desk lamp and a small shade pool on the wall; mug and stacked work papers.
    d.line((36,197,36,170),fill=(16,26,78),width=3); d.line((36,173,51,169),fill=(16,26,78),width=3)
    d.polygon([(45,164),(58,164),(55,171),(47,171)],fill=(243,211,113),outline=(16,26,78))
    d.rectangle((132,193,148,196),fill=(242,233,213)); d.rectangle((128,197,145,199),fill=(184,205,207))
    d.rectangle((163,194,174,207),fill=(18,29,82),outline=(239,222,177)); d.rectangle((165,196,171,202),fill=(234,222,185))
    # Foreground office chair, aligned in front of desk facing the giant display.
    d.polygon([(255,219),(370,219),(379,239),(247,239)],fill=(17,29,84),outline=(10,20,66))
    d.polygon([(264,211),(360,211),(369,232),(256,232)],fill=(43,62,133))
    d.rectangle((278,233,350,249),fill=(24,39,103))
    d.rectangle((302,248,326,265),fill=(17,28,83)); d.rectangle((311,264,318,291),fill=(17,28,83))
    d.rectangle((283,290,346,295),fill=(17,28,83)); d.rectangle((273,294,286,297),fill=(17,28,83)); d.rectangle((344,294,357,297),fill=(17,28,83))
    d.line((276,216,348,216),fill=(86,111,180),width=2)
    # A single floor plane remains visible; chair and desk cast pixel shadows onto it.
    d.polygon([(6,279),(207,279),(220,286),(4,286)],fill=(70,48,59))
    d.polygon([(245,297),(383,297),(397,302),(232,302)],fill=(68,49,61))
    d.text((184, 67), "DRAIN TOWN CCTV", fill=(255, 238, 187), stroke_width=1, stroke_fill=(15,25,77))
    return im
