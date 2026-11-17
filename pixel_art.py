"""Raster illustrations for the Drain Town game, drawn with Pillow."""
from io import BytesIO
import random
from PIL import Image, ImageDraw

W, H = 640, 360


def start_scene():
    """Centered front-facing sewer outfall and quiet riverbank."""
    im = Image.new("RGB", (W, H), (45, 70, 139))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 639, 169), fill=(76, 94, 169))
    d.rectangle((0, 0, 639, 58), fill=(60, 76, 153))
    rng = random.Random(37)
    for _ in range(190):
        x, y = rng.randrange(W), rng.randrange(8, 160)
        d.point((x, y), fill=rng.choice([(191, 194, 226), (240, 218, 153), (104, 202, 207), (202, 145, 201)]))
    d.rectangle((0, 164, 639, 208), fill=(28, 43, 107))
    for x in range(0, W, 34):
        d.line((x, 169, x, 205), fill=(18, 33, 91), width=2)
        d.line((x + 9, 183, x + 24, 183), fill=(101, 125, 190), width=2)
    d.rectangle((0, 209, 639, 359), fill=(45, 64, 137))
    d.line((0, 212, 639, 212), fill=(221, 222, 235), width=4)
    d.line((0, 338, 639, 338), fill=(219, 225, 238), width=4)
    for _ in range(100):
        x, y = rng.randrange(W), rng.randrange(219, 333)
        d.line((x, y, min(639, x + rng.randrange(2, 9)), y), fill=rng.choice([(79, 99, 171), (35, 54, 128), (106, 125, 187)]))
    # Symmetric masonry frame and front-facing round sewer mouth.
    d.rectangle((194, 104, 229, 278), fill=(17, 29, 82), outline=(11, 21, 67), width=3)
    d.rectangle((411, 104, 446, 278), fill=(17, 29, 82), outline=(11, 21, 67), width=3)
    d.ellipse((220, 106, 420, 306), fill=(16, 27, 77), outline=(9, 18, 63), width=4)
    d.ellipse((231, 117, 409, 295), fill=(225, 208, 155), outline=(20, 31, 86), width=4)
    d.ellipse((243, 128, 397, 284), fill=(101, 119, 144), outline=(38, 57, 118), width=5)
    d.ellipse((258, 143, 382, 267), fill=(13, 43, 86), outline=(14, 33, 82), width=4)
    d.arc((237, 122, 403, 289), 198, 342, fill=(246, 224, 168), width=4)
    d.rectangle((271, 194, 369, 229), fill=(38, 180, 211))
    d.rectangle((281, 188, 359, 197), fill=(166, 242, 222))
    d.rectangle((279, 225, 361, 240), fill=(29, 142, 189))
    d.line((288, 207, 352, 207), fill=(111, 226, 231), width=3)
    bands = [(239, 288, 64, (29, 151, 199)), (252, 270, 100, (43, 184, 213)),
             (268, 247, 146, (69, 204, 221)), (283, 218, 204, (124, 222, 220)),
             (301, 190, 260, (82, 205, 215)), (320, 162, 316, (175, 237, 221))]
    for y, x, width, color in bands:
        d.rectangle((x, y, x + width, y + 8), fill=color)
        d.line((x + 14, y + 2, x + width - 18, y + 2), fill=(215, 250, 231), width=2)
    for x, y, color in [(33, 120, (54, 198, 185)), (105, 139, (230, 111, 174)),
                        (164, 98, (67, 201, 188)), (466, 126, (228, 111, 173)),
                        (533, 97, (57, 196, 187)), (597, 144, (235, 131, 184))]:
        d.line((x, y + 23, x, y + 8), fill=(105, 54, 126), width=3)
        d.line((x, y + 14, x - 8, y + 7), fill=color, width=4)
        d.line((x, y + 14, x + 8, y + 3), fill=color, width=4)
    d.text((421, 57), "DRAIN TOWN", fill=(255, 238, 190), stroke_width=1, stroke_fill=(26, 34, 91))
    return im


def start_scene_gif():
    """Short looping river animation with highlights flowing from the centered drain."""
    base = start_scene()
    frames = []
    for frame_index in range(10):
        frame = base.copy()
        d = ImageDraw.Draw(frame)
        for lane, (start_x, end_x) in enumerate([(304, 206), (319, 320), (336, 430)]):
            y = 244 + ((frame_index * 8 + lane * 13) % 80)
            progress = (y - 244) / 80
            center = start_x + (end_x - start_x) * progress
            x = int(center + ((frame_index * 17 + lane * 11) % 39) - 19)
            d.rectangle((x, y, x + 15, y + 2), fill=(213, 255, 234))
            d.point((x + 19, y + 1), fill=(246, 230, 155))
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE))
    result = BytesIO()
    frames[0].save(result, format="GIF", save_all=True, append_images=frames[1:], duration=120, loop=0, disposal=2)
    return result.getvalue()


def _calendar(d, x, y):
    d.rectangle((x + 4, y + 5, x + 53, y + 70), fill=(15, 17, 35))
    d.rectangle((x, y, x + 48, y + 65), fill=(225, 211, 171), outline=(8, 13, 31), width=3)
    d.rectangle((x, y, x + 48, y + 15), fill=(190, 68, 139), outline=(8, 13, 31), width=2)
    for xx in (x + 11, x + 34):
        d.rectangle((xx, y - 5, xx + 5, y + 8), fill=(9, 14, 34))
    for yy in (22, 33, 44, 55):
        for xx in (8, 21, 34):
            d.rectangle((x + xx, y + yy, x + xx + 7, y + yy + 4), fill=(41, 65, 125))
    d.line((x + 20, y + 49, x + 26, y + 56), fill=(21, 143, 110), width=3)
    d.line((x + 26, y + 56, x + 39, y + 42), fill=(21, 143, 110), width=3)


def _feed(d, x, y, w, h, index, route):
    d.rectangle((x, y, x + w, y + h), fill=(61, 91, 145))
    d.rectangle((x, y, x + w, y + 5), fill=(19, 31, 79))
    cx, cy = x + w // 2, y + h // 2
    rw, rh = int(w * .24), int(h * .31)
    d.ellipse((cx-rw-4, cy-rh-3, cx+rw+4, cy+rh+3), fill=(12, 19, 58))
    d.ellipse((cx-rw, cy-rh, cx+rw, cy+rh), fill=(219, 199, 144))
    d.ellipse((cx-rw+5, cy-rh+5, cx+rw-5, cy+rh-5), fill=(89, 106, 130))
    d.ellipse((cx-rw+11, cy-rh+10, cx+rw-11, cy+rh-8), fill=(13, 37, 72))
    water_h = max(3, int(rh * route[0]))
    d.rectangle((cx-rw+12, cy+rh-9-water_h, cx+rw-12, cy+rh-9), fill=(39, 183, 212))
    d.line((cx-rw+15, cy+rh-11-water_h, cx+rw-15, cy+rh-11-water_h), fill=(182, 244, 226), width=2)
    for j in range(int(route[2] * 6)):
        xx = cx - rw + 13 + j * 5
        d.rectangle((xx, cy + rh - 10, xx + 3, cy + rh - 7), fill=(238, 204, 105) if j % 2 else (224, 112, 166))
    for j in range(int(route[3] * 4)):
        d.rectangle((x + 7 + j * 12, y + 8 + (j % 2) * 4, x + 11 + j * 12, y + 11 + (j % 2) * 4), fill=(216, 102, 126))
    d.rectangle((x + 5, y + 5, x + 42, y + 17), fill=(12, 18, 54))
    d.text((x + 9, y + 7), f"CAM 0{index + 1}", fill=(255, 239, 188))


def room_scene(routes):
    """Flat, legible control room: wall objects align to wall and desk legs meet floor."""
    rng = random.Random(812)
    im = Image.new("RGB", (W, H), (13, 15, 34))
    d = ImageDraw.Draw(im)
    # Flat front view: one back wall, a baseboard, then exactly one floor plane.
    d.rectangle((0, 0, 639, 256), fill=(25, 27, 49))
    d.rectangle((0, 0, 639, 38), fill=(20, 22, 41))
    d.rectangle((0, 244, 639, 258), fill=(37, 40, 67))
    d.line((0, 244, 639, 244), fill=(86, 66, 94), width=2)
    for _ in range(190):
        x, y = rng.randrange(2, 638), rng.randrange(43, 239)
        d.point((x, y), fill=rng.choice([(28, 30, 53), (34, 33, 57), (30, 34, 61)]))
    d.rectangle((0, 259, 639, 359), fill=(29, 25, 37))
    # Floorboards and grain all belong to the same floor surface.
    for x in range(0, 641, 32):
        d.line((x, 259, x, 359), fill=(39, 32, 45), width=1)
    for y in (278, 302, 330, 356):
        d.line((0, y, 639, y), fill=(22, 20, 33), width=1)
    for _ in range(95):
        x, y = rng.randrange(2, 638), rng.randrange(264, 357)
        d.line((x, y, min(639, x + rng.randrange(2, 9)), y), fill=rng.choice([(49, 37, 47), (42, 34, 45), (57, 40, 49)]))

    # Central wall-mounted cinema display and one isosceles trapezoid of reflected light.
    d.rectangle((168, 50, 472, 218), fill=(5, 8, 25), outline=(6, 9, 32), width=5)
    d.rectangle((177, 59, 463, 209), fill=(19, 26, 57), outline=(76, 82, 120), width=2)
    d.rectangle((184, 66, 456, 202), fill=(4, 8, 22))
    d.line((189, 70, 451, 70), fill=(126, 140, 171), width=2)
    d.line((189, 198, 451, 198), fill=(126, 140, 171), width=2)
    d.line((189, 70, 189, 198), fill=(126, 140, 171), width=2)
    d.line((451, 70, 451, 198), fill=(126, 140, 171), width=2)
    d.line((320, 70, 320, 198), fill=(92, 111, 151), width=2)
    d.line((189, 134, 451, 134), fill=(92, 111, 151), width=2)
    for index, route in enumerate(routes):
        _feed(d, 193 + (index % 2) * 131, 75 + (index // 2) * 62, 125, 53, index, route)

    # Low-opacity isosceles trapezoid: narrow at the screen, widening downward.
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.polygon([(190, 214), (450, 214), (610, 359), (30, 359)], fill=(77, 106, 184, 42))
    im = Image.alpha_composite(im.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(im)

    # Wall-mounted calendar, directly against the right wall with a pin/shadow.
    d.rectangle((548, 105, 610, 191), fill=(14, 13, 29))
    _calendar(d, 553, 99)
    d.rectangle((550, 95, 557, 102), fill=(173, 146, 86), outline=(8, 13, 31))

    # Left workstation is flush to wall; solid vertical legs reach the floor plane at y=259.
    d.rectangle((20, 224, 204, 240), fill=(75, 48, 47), outline=(8, 13, 31), width=3)
    d.rectangle((26, 240, 42, 259), fill=(19, 18, 31))
    d.rectangle((181, 240, 197, 259), fill=(19, 18, 31))
    # Desk legs continue down from the apron and visibly touch the floor.
    d.rectangle((31, 238, 47, 310), fill=(18, 17, 30))
    d.rectangle((176, 238, 192, 310), fill=(18, 17, 30))
    d.rectangle((51, 247, 105, 278), fill=(44, 32, 41), outline=(19, 17, 31), width=2)
    d.rectangle((112, 247, 165, 278), fill=(42, 31, 40), outline=(19, 17, 31), width=2)
    d.rectangle((59, 260, 68, 264), fill=(119, 91, 58))
    d.rectangle((149, 260, 158, 264), fill=(119, 91, 58))
    # PC monitor, stand and input devices all rest on the desktop top at y=224.
    d.rectangle((67, 151, 137, 214), fill=(6, 12, 40), outline=(5, 8, 27), width=3)
    d.rectangle((73, 157, 131, 205), fill=(23, 68, 94))
    d.rectangle((78, 162, 126, 199), fill=(41, 126, 137))
    d.line((84, 170, 114, 170), fill=(146, 204, 184), width=2)
    d.line((84, 180, 119, 180), fill=(181, 157, 99), width=2)
    d.rectangle((94, 214, 109, 220), fill=(9, 13, 35))
    d.polygon([(45, 218), (152, 218), (157, 224), (41, 224)], fill=(91, 84, 79), outline=(10, 14, 35))
    for x in range(52, 148, 7):
        d.point((x, 221), fill=(56, 61, 75))
    d.rectangle((161, 216, 174, 223), fill=(7, 11, 31))
    # Chair stands on the same floor, set in front of the screen.
    d.rectangle((275, 233, 365, 250), fill=(12, 20, 55))
    d.rectangle((286, 218, 354, 239), fill=(25, 39, 88))
    d.rectangle((305, 249, 335, 268), fill=(9, 15, 42))
    d.rectangle((315, 267, 325, 319), fill=(8, 12, 33))
    d.rectangle((286, 317, 354, 324), fill=(8, 12, 33))
    d.rectangle((274, 323, 289, 328), fill=(8, 12, 33))
    d.rectangle((351, 323, 366, 328), fill=(8, 12, 33))
    return im
