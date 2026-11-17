"""Painterly pixel illustrations for the Drain Town night-shift game.

The scenes are composed in code so the app has no external image-file dependency.
"""
from io import BytesIO
import math
import random

from PIL import Image, ImageDraw, ImageFilter

W, H = 1000, 600


def _lerp(a, b, t):
    return tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(3))


def start_scene():
    """A centered stone outfall and falling water, in a cool illustrated style."""
    im = Image.new("RGB", (W, H))
    p = im.load()
    top, bottom = (25, 58, 65), (8, 36, 48)
    for y in range(H):
        c = _lerp(top, bottom, y / (H - 1))
        for x in range(W):
            shade = int(8 * math.sin(x / 113) + 5 * math.sin((x + y) / 61))
            p[x, y] = tuple(max(0, min(255, v + shade)) for v in c)
    d = ImageDraw.Draw(im, "RGB")
    rng = random.Random(30)
    # Staggered hand-shaded masonry blocks fill the background.
    for row, y in enumerate(range(-22, 355, 82)):
        offset = -70 if row % 2 else -12
        for x in range(offset, W + 90, 144):
            x0 = x + rng.randint(-7, 5)
            y0 = y + rng.randint(-5, 5)
            x1, y1 = x0 + rng.randint(125, 145), y0 + rng.randint(66, 75)
            base = rng.choice([(44, 91, 94), (48, 101, 100), (39, 82, 88), (57, 105, 99)])
            d.rounded_rectangle((x0, y0, x1, y1), radius=10, fill=base, outline=(17, 47, 55), width=7)
            d.line((x0 + 10, y0 + 8, x1 - 12, y0 + 7), fill=(112, 157, 138), width=3)
            d.line((x0 + 12, y0 + 13, x0 + 45, y0 + 13), fill=(82, 132, 124), width=2)
            for _ in range(3):
                xx, yy = rng.randint(x0 + 12, x1 - 15), rng.randint(y0 + 20, y1 - 8)
                d.line((xx, yy, xx + rng.randint(8, 25), yy - rng.randint(1, 7)), fill=(30, 66, 69), width=2)
    # Waterline and dark pool occupy the lower third.
    d.rectangle((0, 355, W, H), fill=(11, 48, 60))
    d.line((0, 358, W, 358), fill=(107, 173, 157), width=5)
    for _ in range(180):
        x, y = rng.randrange(W), rng.randrange(363, H)
        d.line((x, y, min(W - 1, x + rng.randrange(5, 45)), y + rng.choice([-1, 0, 1])),
               fill=rng.choice([(23, 86, 93), (30, 107, 111), (48, 131, 127), (17, 67, 82)]), width=2)
    # Concentric stone rings around a centered circular sewer opening.
    cx, cy = 500, 177
    d.ellipse((cx - 135, cy - 135, cx + 135, cy + 135), fill=(20, 54, 60), outline=(11, 35, 44), width=12)
    d.ellipse((cx - 119, cy - 119, cx + 119, cy + 119), fill=(79, 137, 126), outline=(135, 186, 163), width=8)
    d.ellipse((cx - 99, cy - 99, cx + 99, cy + 99), fill=(23, 69, 73), outline=(53, 105, 100), width=8)
    d.ellipse((cx - 78, cy - 78, cx + 78, cy + 78), fill=(5, 29, 38), outline=(20, 66, 71), width=7)
    d.arc((cx - 115, cy - 115, cx + 115, cy + 115), 190, 342, fill=(179, 220, 184), width=6)
    # Falling, translucent turquoise water with hand-painted vertical light ribbons.
    stream = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stream)
    sd.polygon([(450, 176), (550, 176), (572, 350), (594, 406), (405, 406), (428, 350)], fill=(77, 201, 191, 220))
    sd.polygon([(478, 180), (520, 180), (543, 349), (557, 397), (447, 397), (462, 349)], fill=(140, 235, 213, 190))
    sd.polygon([(493, 184), (505, 184), (522, 351), (527, 393), (482, 393), (486, 351)], fill=(205, 250, 220, 170))
    im = Image.alpha_composite(im.convert("RGBA"), stream).convert("RGB")
    d = ImageDraw.Draw(im)
    rng = random.Random(13)
    for _ in range(48):
        x = rng.randint(440, 560)
        y = rng.randint(194, 388)
        d.line((x, y, x + rng.randint(-5, 5), y + rng.randint(10, 38)),
               fill=rng.choice([(211, 251, 221), (149, 230, 209), (77, 193, 184)]), width=rng.choice([2, 3, 4]))
    # Splash and soft concentric ripples.
    d.ellipse((407, 383, 593, 430), fill=(90, 204, 190), outline=(178, 235, 208), width=4)
    for i in range(7):
        rx = 105 + i * 36
        ry = 17 + i * 9
        d.arc((500 - rx, 397 - ry, 500 + rx, 397 + ry), 8, 172,
              fill=(79 + i * 8, 167 + i * 8, 157 + i * 6), width=3)
    for _ in range(55):
        x, y = rng.randint(392, 608), rng.randint(370, 419)
        r = rng.choice([2, 3, 5, 7])
        d.ellipse((x-r, y-r, x+r, y+r), fill=rng.choice([(157, 233, 204), (104, 209, 195), (211, 245, 214)]))
    # Edge highlights, restrained so the center drain stays the focus.
    d.rectangle((0, 348, W, 355), fill=(22, 84, 83))
    return im


def start_scene_gif():
    """Small looping animation that moves highlights down the water stream."""
    base = start_scene()
    frames = []
    for frame_index in range(8):
        frame = base.copy()
        d = ImageDraw.Draw(frame)
        for lane in range(13):
            x = 444 + lane * 9 + (frame_index * (lane % 3 + 2) * 3) % 18
            y = 201 + (lane * 19 + frame_index * 23) % 183
            d.line((x, y, x + (lane % 3) - 1, y + 13),
                   fill=(225, 255, 227) if lane % 2 else (138, 231, 211), width=3)
        for lane in range(6):
            x = 423 + (lane * 37 + frame_index * 17) % 154
            d.ellipse((x, 382 + (lane * 9) % 26, x + 7, 390 + (lane * 9) % 26), fill=(210, 250, 220))
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE))
    out = BytesIO()
    frames[0].save(out, format="GIF", save_all=True, append_images=frames[1:], duration=130, loop=0, disposal=2)
    return out.getvalue()


def _feed(d, rect, index, route):
    x0, y0, x1, y1 = rect
    d.rectangle(rect, fill=(67, 90, 111), outline=(12, 21, 36), width=5)
    d.rectangle((x0 + 4, y0 + 4, x1 - 4, y0 + 25), fill=(23, 37, 61))
    d.text((x0 + 12, y0 + 6), f"CAM{index + 1}", fill=(229, 233, 222), stroke_width=1, stroke_fill=(19, 28, 42))
    # Perspective tunnel walls and dark opening.
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 + 6
    d.polygon([(x0+8,y0+27),(x1-8,y0+27),(cx+31,cy+21),(cx-31,cy+21)], fill=(104, 127, 137))
    d.polygon([(x0+8,y1-7),(x1-8,y1-7),(cx+31,cy+17),(cx-31,cy+17)], fill=(75, 96, 111))
    d.ellipse((cx-38,cy-26,cx+38,cy+34), fill=(13, 31, 45), outline=(177, 185, 164), width=6)
    d.ellipse((cx-27,cy-17,cx+27,cy+25), fill=(6, 20, 32), outline=(82, 123, 123), width=4)
    water_h = int(10 + 22 * route[0])
    d.rectangle((cx-24,cy+12-water_h,cx+24,cy+14), fill=(69, 188, 190))
    d.line((cx-20,cy+12-water_h,cx+20,cy+12-water_h), fill=(178, 232, 210), width=2)
    for j in range(int(route[2] * 5)):
        d.ellipse((cx-18+j*8,cy+15,cx-14+j*8,cy+19), fill=(205, 162, 108))


def room_scene(routes):
    """Control room inspired by the supplied reference: large CCTV, calendar, PC, desk."""
    im = Image.new("RGB", (W, H), (34, 37, 53))
    d = ImageDraw.Draw(im)
    # Painted room shell and ceiling panels.
    d.rectangle((0, 0, W, 435), fill=(62, 62, 79))
    d.rectangle((0, 0, W, 75), fill=(40, 43, 61))
    d.polygon([(0, 0), (268, 0), (320, 79), (0, 79)], fill=(51, 56, 73))
    d.polygon([(1000, 0), (733, 0), (680, 79), (1000, 79)], fill=(49, 52, 70))
    for x in (74, 222, 778, 926):
        d.ellipse((x-19, 16, x+19, 34), fill=(115, 173, 163), outline=(32, 45, 59), width=4)
        d.ellipse((x-9, 20, x+9, 29), fill=(195, 220, 193))
    d.line((0, 82, 1000, 82), fill=(118, 195, 178), width=4)
    # Back wall with subtle panel seams and cool light spill.
    for x in range(35, 1000, 110):
        d.line((x, 90, x + 4, 420), fill=(78, 76, 91), width=2)
    for _ in range(900):
        x, y = random.Random(812 + _).randrange(0, 1000), random.Random(1412 + _).randrange(90, 425)
        d.point((x, y), fill=random.Random(2222 + _).choice([(66, 67, 84), (70, 70, 88), (74, 73, 91)]))
    # Central 2x2 CCTV wall screen.
    d.rounded_rectangle((252, 92, 750, 398), radius=7, fill=(8, 14, 29), outline=(16, 25, 42), width=9)
    d.rectangle((267, 106, 735, 384), fill=(20, 31, 53), outline=(132, 176, 162), width=4)
    d.rectangle((278, 117, 724, 373), fill=(13, 23, 39))
    for i, route in enumerate(routes):
        x = 285 + (i % 2) * 218
        y = 124 + (i // 2) * 124
        _feed(d, (x, y, x + 212, y + 119), i, route)
    d.line((500, 120, 500, 372), fill=(155, 175, 167), width=5)
    d.line((280, 248, 722, 248), fill=(155, 175, 167), width=5)
    d.rectangle((0, 422, W, 439), fill=(38, 36, 49))
    d.line((0, 422, W, 422), fill=(120, 95, 103), width=4)
    # Floor tiles and perspective seams.
    d.rectangle((0, 440, W, H), fill=(65, 62, 72))
    for x in range(0, W + 1, 125):
        d.line((500, 439, x, 599), fill=(88, 82, 91), width=2)
    for y in (470, 505, 548, 585):
        d.line((0, y, W, y), fill=(52, 52, 64), width=2)
    rng = random.Random(91)
    for _ in range(260):
        x, y = rng.randrange(W), rng.randrange(441, 599)
        d.line((x, y, x + rng.randrange(2, 10), y), fill=(82, 77, 85), width=1)
    # A muted teal beam from the monitor, spilling onto the floor.
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    bd.polygon([(330, 399), (670, 399), (850, 598), (150, 598)], fill=(111, 174, 165, 28))
    im = Image.alpha_composite(im.convert("RGBA"), beam).convert("RGB")
    d = ImageDraw.Draw(im)
    # Wall calendar on the right, with paper grid and markings.
    d.rounded_rectangle((827, 152, 970, 326), radius=4, fill=(24, 27, 38), outline=(24, 29, 43), width=8)
    d.rectangle((837, 161, 960, 316), fill=(205, 201, 184), outline=(43, 42, 48), width=3)
    d.rectangle((837, 161, 960, 193), fill=(145, 75, 101))
    d.text((867, 167), "CALENDAR", fill=(244, 230, 212))
    for x in (854, 882, 910, 938):
        d.ellipse((x, 155, x+8, 168), fill=(26, 29, 40))
    for x in range(842, 961, 23):
        d.line((x, 200, x, 309), fill=(112, 111, 105), width=1)
    for y in range(200, 310, 22):
        d.line((840, y, 957, y), fill=(112, 111, 105), width=1)
    for row in range(4):
        for col in range(5):
            d.text((844 + col*23, 202 + row*22), str((row*5+col+1)), fill=(55, 55, 54))
    d.line((898, 281, 909, 294, 939, 259), fill=(51, 139, 112), width=6)
    # Left workstation, desk surface and legs clearly reaching the floor.
    d.rectangle((30, 330, 292, 354), fill=(45, 39, 48))
    d.polygon([(23, 315), (300, 315), (277, 347), (4, 347)], fill=(105, 83, 81), outline=(30, 29, 41))
    d.rectangle((28, 346, 49, 507), fill=(35, 31, 42))
    d.rectangle((255, 346, 277, 507), fill=(35, 31, 42))
    d.rectangle((63, 354, 150, 405), fill=(49, 39, 45), outline=(35, 31, 42), width=3)
    d.rectangle((158, 354, 244, 405), fill=(47, 38, 45), outline=(35, 31, 42), width=3)
    d.rectangle((74, 375, 87, 380), fill=(147, 111, 70))
    d.rectangle((224, 375, 237, 380), fill=(147, 111, 70))
    # Desktop monitor, stand and keyboard.
    d.rectangle((85, 225, 207, 308), fill=(9, 17, 34), outline=(17, 26, 41), width=6)
    d.rectangle((94, 234, 198, 296), fill=(37, 117, 126))
    d.line((105, 251, 178, 251), fill=(168, 216, 184), width=4)
    d.line((105, 267, 186, 267), fill=(203, 197, 149), width=3)
    d.rectangle((135, 308, 157, 315), fill=(26, 28, 39))
    d.polygon([(88, 310), (202, 310), (214, 320), (78, 320)], fill=(119, 119, 111), outline=(29, 34, 45))
    for x in range(91, 205, 9):
        d.line((x, 314, x+4, 314), fill=(54, 61, 69), width=1)
    # Small notes/keyboard board on the wall over desk.
    d.rectangle((41, 186, 227, 276), fill=(48, 67, 69), outline=(21, 31, 40), width=4)
    d.line((54, 204, 187, 204), fill=(181, 207, 181), width=2)
    d.line((54, 218, 205, 218), fill=(161, 190, 169), width=2)
    d.line((54, 232, 180, 232), fill=(181, 207, 181), width=2)
    # Foreground worktable with a visible paper note; note hotspot is centered here.
    d.polygon([(293, 554), (760, 554), (829, 600), (229, 600)], fill=(74, 58, 56), outline=(34, 29, 38), width=4)
    d.polygon([(515, 548), (640, 548), (674, 589), (493, 589)], fill=(207, 198, 173), outline=(51, 47, 49), width=3)
    for y in (560, 568, 576, 584):
        d.line((520, y, 635, y), fill=(145, 138, 123), width=1)
    d.rectangle((697, 548, 735, 584), fill=(43, 37, 39), outline=(21, 22, 31), width=3)
    d.ellipse((704, 543, 730, 552), fill=(103, 112, 103))
    # Small wall-side shelf, kept secondary to the main clickable objects.
    d.polygon([(833, 358), (985, 358), (985, 371), (825, 371)], fill=(89, 72, 67))
    for i in range(3):
        x = 855 + i*37
        d.rectangle((x, 318-i*4, x+29, 356), fill=(80, 68, 66), outline=(27, 28, 38), width=2)
        d.rectangle((x+4, 324-i*4, x+24, 328-i*4), fill=(157, 143, 118))
    return im


def zoomed_object(routes, obj):
    """Return a close crop of the clicked PC or wall calendar."""
    scene = room_scene(routes)
    if obj == "pc":
        return scene.crop((0, 170, 315, 525)).resize((630, 710), Image.Resampling.LANCZOS)
    if obj == "calendar":
        return scene.crop((800, 125, 990, 350)).resize((570, 675), Image.Resampling.LANCZOS)
    return scene
