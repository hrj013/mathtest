"""Raster illustrations for the Drain Town game, drawn with Pillow."""
from io import BytesIO
import random
from PIL import Image, ImageDraw

W, H = 640, 360


def start_scene():
    """Centered front-facing sewer outfall; returns a Pillow image for previews."""
    im = Image.new("RGB", (W, H), (55, 81, 151))
    d = ImageDraw.Draw(im)
    # River-town night sky and distant bank.
    d.rectangle((0, 0, 639, 169), fill=(91, 112, 184))
    d.rectangle((0, 0, 639, 60), fill=(74, 91, 167))
    rng = random.Random(37)
    for _ in range(220):
        x, y = rng.randrange(W), rng.randrange(8, 160)
        d.point((x, y), fill=rng.choice([(191, 194, 226), (240, 218, 153), (104, 202, 207), (202, 145, 201)]))
    d.rectangle((0, 164, 639, 208), fill=(31, 48, 113))
    for x in range(0, W, 34):
        d.line((x, 169, x, 205), fill=(20, 38, 101), width=2)
        d.line((x + 9, 183, x + 24, 183), fill=(101, 125, 190), width=2)
    # Single blue stone channel / ground plane.
    d.rectangle((0, 209, 639, 359), fill=(47, 66, 143))
    d.line((0, 212, 639, 212), fill=(221, 222, 235), width=4)
    d.line((0, 338, 639, 338), fill=(219, 225, 238), width=4)
    for _ in range(110):
        x, y = rng.randrange(W), rng.randrange(219, 333)
        d.line((x, y, min(639, x + rng.randrange(2, 9)), y), fill=rng.choice([(79, 99, 171), (35, 54, 128), (106, 125, 187)]))
    # The circular mouth is centered at x=320, not offset to one side.
    cx, cy = 320, 205
    # Concrete mount and stepped blue/stone rim around a true circular opening.
    d.rectangle((194, 104, 229, 278), fill=(17, 29, 82), outline=(11, 21, 67), width=3)
    d.rectangle((411, 104, 446, 278), fill=(17, 29, 82), outline=(11, 21, 67), width=3)
    d.rectangle((222, 117, 239, 265), fill=(224, 207, 151), outline=(18, 30, 82), width=3)
    d.rectangle((401, 117, 418, 265), fill=(224, 207, 151), outline=(18, 30, 82), width=3)
    d.ellipse((220, 106, 420, 306), fill=(16, 27, 77), outline=(9, 18, 63), width=4)
    d.ellipse((231, 117, 409, 295), fill=(225, 208, 155), outline=(20, 31, 86), width=4)
    d.ellipse((243, 128, 397, 284), fill=(101, 119, 144), outline=(38, 57, 118), width=5)
    d.ellipse((258, 143, 382, 267), fill=(13, 43, 86), outline=(14, 33, 82), width=4)
    # Inner water level and spill flowing out of the round opening.
    d.arc((237, 122, 403, 289), 198, 342, fill=(246, 224, 168), width=4)
    d.rectangle((271, 194, 369, 229), fill=(38, 180, 211))
    d.rectangle((281, 188, 359, 197), fill=(166, 242, 222))
    d.rectangle((279, 225, 361, 240), fill=(29, 142, 189))
    d.line((288, 207, 352, 207), fill=(111, 226, 231), width=3)
    # The outflow widens into one channel. Small bright streaks are animated below.
    bands = [(239, 288, 64, (29, 151, 199)), (252, 270, 100, (43, 184, 213)),
             (268, 247, 146, (69, 204, 221)), (283, 218, 204, (124, 222, 220)),
             (301, 190, 260, (82, 205, 215)), (320, 162, 316, (175, 237, 221))]
    for y, x, width, color in bands:
        d.rectangle((x, y, x + width, y + 8), fill=color)
        d.line((x + 14, y + 2, x + width - 18, y + 2), fill=(215, 250, 231), width=2)
    # little river plants and glints, balanced on both sides of the centered drain
    for x, y, color in [(33, 120, (54, 198, 185)), (105, 139, (230, 111, 174)),
                        (164, 98, (67, 201, 188)), (466, 126, (228, 111, 173)),
                        (533, 97, (57, 196, 187)), (597, 144, (235, 131, 184))]:
        d.line((x, y + 23, x, y + 8), fill=(105, 54, 126), width=3)
        d.line((x, y + 14, x - 8, y + 7), fill=color, width=4)
        d.line((x, y + 14, x + 8, y + 3), fill=color, width=4)
        d.rectangle((x - 3, y + 5, x + 2, y + 10), fill=(244, 145, 191))
    for x, y in [(43, 296), (82, 313), (451, 294), (571, 313), (602, 281)]:
        d.rectangle((x, y, x + 8, y + 2), fill=(246, 218, 121))
        d.rectangle((x + 5, y - 3, x + 12, y - 1), fill=(218, 250, 228))
    d.text((421, 57), "DRAIN TOWN WATERWAY", fill=(255, 238, 190), stroke_width=1, stroke_fill=(26, 34, 91))
    return im


def start_scene_gif():
    """Animated GIF with moving pixel highlights flowing away from the pipe."""
    base = start_scene()
    frames = []
    for frame_index in range(8):
        frame = base.copy()
        d = ImageDraw.Draw(frame)
        # Bright glints travel down and fan out with the current.
        for lane, (start_x, start_y, end_x) in enumerate([(304, 244, 206), (319, 250, 320), (336, 244, 430)]):
            y = 247 + ((frame_index * 9 + lane * 7) % 70)
            progress = (y - 247) / 70
            center = start_x + (end_x - start_x) * progress
            x = int(center + ((frame_index * 13 + lane * 11) % 35) - 17)
            d.rectangle((x, y, x + 13, y + 2), fill=(213, 255, 234))
            d.point((x + 17, y + 1), fill=(246, 230, 155))
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE))
    result = BytesIO()
    frames[0].save(result, format="GIF", save_all=True, append_images=frames[1:], duration=120, loop=0, disposal=2)
    return result.getvalue()


def _draw_calendar(d, x, y):
    d.rectangle((x + 4, y + 5, x + 53, y + 70), fill=(38, 31, 67))
    d.rectangle((x, y, x + 48, y + 65), fill=(241, 224, 185), outline=(12, 21, 63), width=3)
    d.rectangle((x, y, x + 48, y + 15), fill=(207, 82, 146), outline=(12, 21, 63), width=2)
    for xx in (x + 11, x + 34):
        d.rectangle((xx, y - 5, xx + 5, y + 8), fill=(13, 22, 65))
    for yy in (22, 33, 44, 55):
        for xx in (8, 21, 34):
            d.rectangle((x + xx, y + yy, x + xx + 7, y + yy + 4), fill=(48, 74, 148))
    d.line((x + 20, y + 49, x + 26, y + 56), fill=(21, 143, 110), width=3)
    d.line((x + 26, y + 56, x + 39, y + 42), fill=(21, 143, 110), width=3)


def _draw_feed(d, x, y, w, h, index, route):
    d.rectangle((x, y, x + w, y + h), fill=(71, 105, 163))
    d.rectangle((x, y, x + w, y + 4), fill=(26, 40, 100))
    cx, cy = x + w // 2, y + h // 2
    rw, rh = int(w * .24), int(h * .31)
    d.ellipse((cx-rw-4, cy-rh-3, cx+rw+4, cy+rh+3), fill=(15, 25, 74))
    d.ellipse((cx-rw, cy-rh, cx+rw, cy+rh), fill=(222, 202, 146))
    d.ellipse((cx-rw+5, cy-rh+5, cx+rw-5, cy+rh-5), fill=(94, 110, 133))
    d.ellipse((cx-rw+11, cy-rh+10, cx+rw-11, cy+rh-8), fill=(16, 43, 82))
    water_h = max(3, int(rh * route[0]))
    d.rectangle((cx-rw+12, cy+rh-9-water_h, cx+rw-12, cy+rh-9), fill=(39, 183, 212))
    d.line((cx-rw+15, cy+rh-11-water_h, cx+rw-15, cy+rh-11-water_h), fill=(182, 244, 226), width=2)
    for j in range(int(route[2] * 6)):
        xx = cx - rw + 13 + j * 5
        d.rectangle((xx, cy + rh - 10, xx + 3, cy + rh - 7), fill=(238, 204, 105) if j % 2 else (224, 112, 166))
    for j in range(int(route[3] * 4)):
        d.rectangle((x + 7 + j * 12, y + 8 + (j % 2) * 4, x + 11 + j * 12, y + 11 + (j % 2) * 4), fill=(216, 102, 126))
    d.rectangle((x + 5, y + 5, x + 42, y + 17), fill=(14, 22, 65))
    d.text((x + 9, y + 7), f"CAM 0{index + 1}", fill=(255, 239, 188))


def room_scene(routes):
    """Dark perspective control room, wall-mounted screen and fixtures, one floor."""
    rng = random.Random(812)
    im = Image.new("RGB", (W, H), (11, 14, 35))
    d = ImageDraw.Draw(im)
    # Ceiling and room perspective: back wall plus two side walls.
    d.polygon([(0, 0), (640, 0), (568, 45), (72, 45)], fill=(30, 32, 54))
    d.polygon([(0, 0), (72, 45), (72, 244), (0, 285)], fill=(36, 39, 68))
    d.polygon([(640, 0), (568, 45), (568, 244), (640, 285)], fill=(25, 28, 54))
    d.rectangle((72, 45, 568, 244), fill=(29, 30, 55))
    # Light grain is subtle; room remains dark away from the display.
    for _ in range(220):
        x, y = rng.randrange(74, 567), rng.randrange(48, 241)
        d.point((x, y), fill=rng.choice([(33, 34, 59), (38, 36, 60), (31, 34, 63)]))
    # One baseboard and one continuous wooden floor plane.
    d.line((72, 241, 568, 241), fill=(88, 65, 98), width=3)
    d.polygon([(0, 247), (72, 244), (568, 244), (640, 247), (640, 285), (0, 285)], fill=(27, 34, 70))
    d.line((0, 285, 640, 285), fill=(10, 17, 52), width=4)
    d.polygon([(0, 290), (640, 290), (640, 360), (0, 360)], fill=(38, 31, 45))
    for x in range(0, 641, 24):
        d.line((320, 291, x, 359), fill=(57, 43, 55), width=1)
    for y in (298, 307, 319, 333, 348, 358):
        left = max(0, int(320 - (y - 290) * 4.5))
        right = min(639, int(320 + (y - 290) * 4.5))
        d.line((left, y, right, y), fill=(24, 23, 39), width=1)
    for _ in range(100):
        x, y = rng.randrange(2, 638), rng.randrange(294, 359)
        d.line((x, y, min(639, x + rng.randrange(2, 8)), y), fill=rng.choice([(66, 47, 54), (51, 40, 51), (75, 53, 56)]), width=1)

    # A single symmetrical trapezoid of monitor light spills onto the wall and floor.
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.polygon([(178, 215), (462, 215), (565, 359), (75, 359)], fill=(74, 107, 191, 62))
    gd.polygon([(205, 218), (435, 218), (505, 359), (135, 359)], fill=(98, 133, 211, 38))
    im = Image.alpha_composite(im.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(im)

    # The large cinema-like display is physically mounted on the back wall.
    d.rectangle((161, 56, 477, 225), fill=(7, 11, 38), outline=(5, 9, 32), width=5)
    d.rectangle((169, 64, 469, 217), fill=(29, 36, 78), outline=(83, 91, 133), width=2)
    d.rectangle((176, 71, 462, 210), fill=(5, 9, 25))
    d.line((181, 75, 457, 75), fill=(132, 145, 179), width=2)
    d.line((181, 206, 457, 206), fill=(132, 145, 179), width=2)
    d.line((181, 75, 181, 206), fill=(132, 145, 179), width=2)
    d.line((457, 75, 457, 206), fill=(132, 145, 179), width=2)
    d.line((319, 75, 319, 206), fill=(101, 119, 159), width=2)
    d.line((181, 140, 457, 140), fill=(101, 119, 159), width=2)
    for index, route in enumerate(routes):
        x = 185 + (index % 2) * 138
        y = 80 + (index // 2) * 65
        _draw_feed(d, x, y, 132, 56, index, route)

    # Left-side workstation is pushed against the back wall; the CRT sits on the desk.
    d.polygon([(18, 190), (166, 190), (199, 213), (9, 213)], fill=(77, 52, 50), outline=(10, 17, 54))
    d.polygon([(9, 213), (199, 213), (192, 228), (17, 228)], fill=(47, 37, 48), outline=(10, 17, 54))
    d.polygon([(19, 228), (34, 228), (33, 277), (21, 277)], fill=(29, 27, 43))
    d.polygon([(173, 228), (188, 228), (194, 276), (180, 276)], fill=(29, 27, 43))
    d.rectangle((43, 233, 96, 261), fill=(57, 39, 45), outline=(29, 26, 43))
    d.rectangle((99, 233, 156, 261), fill=(52, 36, 43), outline=(29, 26, 43))
    d.rectangle((50, 244, 57, 247), fill=(131, 104, 67))
    d.rectangle((143, 244, 150, 247), fill=(131, 104, 67))
    # PC monitor, clearly resting on the desktop, with faint cyan phosphor glow.
    d.rectangle((58, 139, 128, 190), fill=(8, 15, 51), outline=(5, 10, 37), width=3)
    d.rectangle((64, 145, 122, 181), fill=(25, 66, 99))
    d.rectangle((68, 149, 118, 176), fill=(45, 128, 142))
    d.line((73, 155, 103, 155), fill=(134, 200, 187), width=2)
    d.line((73, 163, 111, 163), fill=(180, 151, 93), width=2)
    d.rectangle((88, 190, 101, 197), fill=(11, 17, 48))
    d.rectangle((74, 197, 117, 202), fill=(7, 13, 42))
    d.polygon([(42, 201), (135, 201), (142, 210), (37, 210)], fill=(105, 99, 91), outline=(10, 17, 54))
    for x in range(48, 134, 6):
        d.point((x, 205), fill=(60, 68, 86))
    d.rectangle((146, 202, 157, 209), fill=(9, 15, 45))
    # Lamp, mug, papers: objects are on the workstation, not floating on the floor.
    d.line((36, 197, 36, 170), fill=(9, 15, 49), width=3)
    d.line((36, 173, 51, 169), fill=(9, 15, 49), width=3)
    d.polygon([(45, 164), (58, 164), (55, 171), (47, 171)], fill=(186, 148, 79), outline=(9, 15, 49))
    d.rectangle((132, 193, 148, 196), fill=(157, 153, 138))
    d.rectangle((163, 194, 174, 207), fill=(9, 15, 49), outline=(137, 118, 78))

    # Calendar is pinned directly to the right wall with a visible hook/shadow.
    d.line((592, 67, 592, 160), fill=(9, 17, 53), width=4)
    d.rectangle((565, 91, 615, 161), fill=(22, 20, 43))
    _draw_calendar(d, 563, 88)
    d.rectangle((560, 84, 566, 90), fill=(184, 157, 94), outline=(9, 15, 49))
    # Chair in front of the desk, facing the wall screen.
    d.polygon([(255, 219), (370, 219), (379, 239), (247, 239)], fill=(8, 15, 51), outline=(5, 10, 36))
    d.polygon([(264, 211), (360, 211), (369, 232), (256, 232)], fill=(25, 39, 92))
    d.rectangle((278, 233, 350, 249), fill=(14, 25, 69))
    d.rectangle((302, 248, 326, 265), fill=(8, 15, 49))
    d.rectangle((311, 264, 318, 291), fill=(8, 15, 49))
    d.rectangle((283, 290, 346, 295), fill=(8, 15, 49))
    d.rectangle((273, 294, 286, 297), fill=(8, 15, 49))
    d.rectangle((344, 294, 357, 297), fill=(8, 15, 49))
    return im
