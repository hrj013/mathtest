"""Hand-built, fine-resolution pixel-art scenes for Drain Town.

The art is drawn on a 640x360 canvas (not enlarged 8px tiles), with a restrained
palette, clustered highlights, texture pixels, and crisp edges at display size.
"""
import random

W, H = 640, 360


def rect(x, y, w, h, color, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" {extra}/>'


def path(d, color, extra=""):
    return f'<path d="{d}" fill="{color}" {extra}/>'


def _svg_start():
    return ['<svg viewBox="0 0 640 360" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated;shape-rendering:crispEdges">']


def start_scene():
    """Nighttime pixel-art outfall viewed straight into the circular pipe mouth."""
    rng = random.Random(814)
    s = _svg_start()
    s += [rect(0,0,640,360,'#38217f'), rect(0,0,640,190,'#5364b8'), rect(0,190,640,170,'#283f91')]
    # Dreamy starry dusk, tiny individual pixels rather than oversized decoration.
    for i in range(90):
        x=rng.randrange(4,636); y=rng.randrange(5,178)
        color=rng.choice(['#c4b8f1','#f5d992','#8bdde6','#e8a7d2'])
        s.append(rect(x,y,rng.choice([1,2,3]),rng.choice([1,2]),color))
    # Distant tiled river wall and shoreline.
    s += [rect(0,170,640,29,'#3b438f'),rect(0,170,640,4,'#202e78'),rect(0,195,640,3,'#e1d3d9')]
    for x in range(0,640,32):
        s += [rect(x,174,2,20,'#253477'),rect(x+13,180,11,2,'#8194ce'),rect(x+4,188,7,2,'#697dbd')]
    # Bioluminescent town plants and coral, in small, irregular pixel clusters.
    for x,y,c in [(30,91,'#41c7c6'),(95,124,'#ef79b5'),(160,77,'#56d8bd'),(484,104,'#ec78ac'),(552,73,'#47c7c2'),(604,132,'#f28ab5')]:
        s += [rect(x,y+5,23,9,c),rect(x+5,y,17,8,c),rect(x+11,y-4,9,6,'#80e2d0'),rect(x+8,y+13,5,14,'#713c8b'),rect(x-5,y+9,8,7,c),rect(x+24,y+8,8,7,c)]
        s += [rect(x+3,y+7,4,3,'#f8cfe1'),rect(x+17,y+2,3,3,'#e9ffff')]
    for x,y in [(47,157),(124,148),(190,165),(457,154),(524,162),(583,145)]:
        s += [rect(x,y,5,3,'#f7d980'),rect(x+3,y-3,4,3,'#fff0bd'),rect(x+5,y+3,2,6,'#46bcad')]
    # Stone walkway and outfall basin.
    s += [rect(0,203,640,157,'#374d9a'),rect(0,208,640,5,'#e4dbe3'),rect(0,332,640,5,'#e4dbe3')]
    for x in range(0,640,48):
        s += [rect(x,214,21,2,'#657bb6'),rect(x+25,218,11,2,'#5069aa'),rect(x+7,316,26,2,'#596fac')]
    # Front-facing circular pipe mouth. Rings are rendered with 1px stepped pixels.
    cx,cy=186,210
    rings=[(89,'#101c59'),(82,'#e6d39a'),(75,'#667794'),(68,'#283f82'),(57,'#122e62')]
    for r,col in rings:
        for yy in range(cy-r,cy+r+1):
            dx=int((r*r-(yy-cy)*(yy-cy))**0.5)
            s += [rect(cx-dx,yy,2,2,col),rect(cx+dx-1,yy,2,2,col)]
    # Masonry around the circular entry, bolts and inspection rails.
    s += [rect(78,93,15,168,'#111d59'),rect(94,99,9,153,'#e2d09b'),rect(281,93,15,168,'#111d59'),rect(271,99,9,153,'#e2d09b')]
    for yy in range(105,250,20):
        s += [rect(84,yy,4,4,'#f7e9be'),rect(286,yy,4,4,'#f7e9be')]
    # Dark tunnel interior and turquoise waterline.
    s += [rect(144,177,84,66,'#102b5b'),rect(139,188,94,15,'#174276'),rect(145,203,82,24,'#2fbada'),rect(153,198,66,5,'#a4f3e7'),rect(150,229,72,8,'#228ec4')]
    s += [rect(156,208,58,4,'#54d4e4'),rect(164,218,41,3,'#b3f1e4')]
    # Water flows out of the round opening and fans across the foreground in several pixel bands.
    bands=[(240,164,45,'#27a9d2'),(251,148,77,'#34c4df'),(264,126,121,'#79e0df'),(279,101,171,'#b3eee0'),(296,76,220,'#70d9dc'),(314,49,274,'#c7f1dc')]
    for y,x,w,c in bands:
        s.append(rect(x,y,w,8,c))
        s.append(rect(x+12,y+2,max(8,w-35),2,'#d7fff0'))
    for x,y,c in [(44,284,'#f4db79'),(62,301,'#9deee0'),(332,275,'#f17cac'),(369,291,'#a1f2e4'),(428,268,'#f1d467'),(538,300,'#ed79ae'),(231,322,'#a1f0e2')]:
        s += [rect(x,y,9,3,c),rect(x+3,y-3,7,2,'#fff0bc')]
    # Foreground grasses, stones, tiny foam pixels.
    for x,y in [(12,325),(32,323),(590,323),(617,319),(402,333),(118,338)]:
        s += [rect(x,y,3,12,'#713e83'),rect(x-4,y+2,5,4,'#ef79ad'),rect(x+3,y-2,6,5,'#46c9bd')]
    for i in range(60):
        x=rng.randrange(4,636); y=rng.randrange(215,355)
        if 90 < x < 280 and 120 < y < 300: continue
        s.append(rect(x,y,rng.choice([1,2,3]),1,rng.choice(['#6880bd','#1d367e','#9aadd1'])))
    s.append('<text x="355" y="61" font-family="monospace" font-size="18" fill="#fff0c1">DRAIN TOWN WATERWAY</text>')
    s.append('</svg>')
    return ''.join(s)


def _calendar(x,y):
    s=[rect(x,y,48,61,'#101c59'),rect(x+3,y+3,42,55,'#f1e4be'),rect(x+3,y+3,42,12,'#e778aa')]
    s += [rect(x+11,y-4,5,13,'#101c59'),rect(x+32,y-4,5,13,'#101c59')]
    for yy in (21,31,41,51):
        for xx in (x+8,x+20,x+32): s.append(rect(xx,yy,7,5,'#3559a3'))
    s += [rect(x+20,y+44,3,8,'#0b997d'),rect(x+20,y+49,11,3,'#0b997d')]
    return ''.join(s)


def _pipe_feed(x,y,w,h,idx,route):
    """Fine pixel CCTV feed drawn into the same large wall screen."""
    s=[rect(x,y,w,h,'#4264a5'),rect(x,y,w,5,'#263d82'),rect(x,y+h-5,w,5,'#263d82')]
    # Subtle tunnel bricks
    for xx in range(x+4,x+w,14): s.append(rect(xx,y+8,1,h-16,'#5478ad'))
    # Concentric pipe mouth from a straight-on CCTV view.
    cx=x+w//2; cy=y+h//2
    rw=max(13,w//5); rh=max(8,h//4)
    s += [rect(cx-rw-4,cy-rh-3,2*rw+8,2*rh+6,'#101c59'),rect(cx-rw,cy-rh,2*rw,2*rh,'#decf9e'),rect(cx-rw+4,cy-rh+3,2*rw-8,2*rh-6,'#61748e'),rect(cx-rw+8,cy-rh+6,2*rw-16,2*rh-12,'#153362')]
    level=max(3,int((2*rh-13)*route[0]))
    s += [rect(cx-rw+9,cy+rh-7-level,2*rw-18,level,'#35bfdc'),rect(cx-rw+12,cy+rh-9-level,2*rw-24,3,'#b8f5e8')]
    for j in range(int(route[2]*8)):
        s.append(rect(cx-rw+12+j*5,cy+rh-11,3,3,'#ef78a8' if j%2 else '#f1d76c'))
    for j in range(int(route[3]*6)):
        s.append(rect(x+8+j*9,y+8+(j%2)*4,4,3,'#e77992'))
    for j in range(int(route[1]*8)):
        s.append(rect(x+8+j*15,y+9+(j%3)*7,2,2,'#baf4e9'))
    s += [rect(x+5,y+5,32,12,'#101c59')]
    s.append(f'<text x="{x+9}" y="{y+14}" font-family="monospace" font-size="9" fill="#fff0c2">CAM 0{idx+1}</text>')
    return ''.join(s)


def room_scene(routes):
    """Perspective office with wall calendars, wall-sized quad screen, desk-bound PC."""
    rng=random.Random(741)
    s=_svg_start()
    # Room shell and clear perspective: ceiling, back wall, side walls, and plank floor.
    s += [rect(0,0,640,360,'#77658d'),path('M0 0H640L572 51H68Z','#c6c6c4'),path('M0 0L68 51V255L0 297Z','#e2e1df'),path('M640 0L572 51V255L640 297Z','#b8b8bd'),rect(68,51,504,204,'#dedddc')]
    # Fine wall grain, pale lavender reflected light and blue architectural outlines.
    s += [rect(68,51,504,4,'#f4f0e9'),rect(68,251,504,5,'#8e7699'),rect(0,294,640,6,'#162b73')]
    for x in range(75,570,32): s.append(rect(x,61,1,179,'#d3d0d4'))
    for i in range(160):
        x=rng.randrange(70,570); y=rng.randrange(59,248)
        s.append(rect(x,y,1,1,rng.choice(['#d9d4db','#e6e2df','#cfcbd3'])))
    # Dark lower wall paneling with narrow repeated trim, not oversized tile blocks.
    s += [rect(0,258,640,36,'#53629e'),rect(68,256,504,4,'#ede2e8')]
    for x in range(0,640,16): s.append(rect(x,259,1,34,'#6875aa'))
    for x in range(8,640,32): s.append(rect(x,267,9,1,'#7782b5'))
    # Perspective wood plank floor with many thin boards and grain marks.
    s += [path('M0 300H640L640 360H0Z','#795a49')]
    for x in range(0,641,16): s.append(f'<path d="M320 300L{x} 360" stroke="#a77d5d" stroke-width="2"/>')
    for y in (307,315,325,337,349,358):
        left=max(0,int(320-(y-300)*5.2)); right=min(640,int(320+(y-300)*5.2))
        s.append(f'<path d="M{left} {y}H{right}" stroke="#4c3b48" stroke-width="1"/>')
    for i in range(55):
        x=rng.randrange(0,640); y=rng.randrange(303,359)
        s.append(rect(x,y,rng.randrange(2,7),1,rng.choice(['#a98161','#6a4e49','#916d55'])))
    # One cinema-sized monitor mounted on the back wall. The four feeds are inside this bezel.
    s += [rect(176,65,288,161,'#101c59'),rect(182,71,276,149,'#252b61'),rect(187,76,266,139,'#0b102b')]
    s += [rect(190,79,260,3,'#bcc2d0'),rect(190,210,260,3,'#bcc2d0'),rect(190,79,3,134,'#bcc2d0'),rect(447,79,3,134,'#bcc2d0'),rect(319,79,3,134,'#aeb9d1'),rect(190,145,260,3,'#aeb9d1')]
    for i,route in enumerate(routes):
        x=196+(i%2)*130; y=85+(i//2)*67
        s.append(_pipe_feed(x,y,123,57,i,route))
    # Wall mounted right calendar: hooked to the wall with shadow, paper grid, and pins.
    s += [rect(552,119,51,70,'#70618d'),rect(548,115,51,70,'#101c59'),_calendar(550,119),rect(557,120,4,3,'#fff1c1')]
    # Small pinned notices and conduit line on the right wall.
    s += [rect(515,80,25,32,'#172b70'),rect(518,83,19,25,'#f2e7c2'),rect(520,88,15,2,'#e879a8'),rect(520,94,12,1,'#5368a0'),rect(520,99,14,1,'#5368a0')]
    s += [rect(608,64,3,185,'#101c59'),rect(604,62,11,3,'#e5d19b'),rect(605,246,9,3,'#e5d19b')]
    # Desk is pushed against the LEFT wall, with a clear side-wall perspective and front edge.
    # Desk shadow first, then desktop slab, front apron, legs and drawer details.
    s += [path('M30 202L180 202L208 276L15 276Z','#48374b'),path('M24 195L176 195L198 214L12 214Z','#a87550'),path('M12 214L198 214L190 226L18 226Z','#654846')]
    s += [path('M23 226L36 226L35 278L24 278Z','#45384a'),path('M174 226L187 226L193 276L181 276Z','#45384a')]
    s += [rect(45,232,49,29,'#84583f'),rect(99,232,58,29,'#79523f'),rect(51,243,7,3,'#e6cf8f'),rect(143,243,7,3,'#e6cf8f'),rect(38,222,127,3,'#d19b66')]
    # Desktop CRT placed visibly on the desk surface; keyboard and mouse sit in front.
    s += [rect(62,145,66,47,'#101c59'),rect(67,150,56,35,'#3185bd'),rect(70,153,50,27,'#59ced9'),rect(75,158,29,3,'#e5f4ce'),rect(75,165,36,3,'#f3d87a'),rect(109,170,7,3,'#ed79aa')]
    s += [rect(88,192,15,7,'#182a63'),rect(75,198,42,5,'#101c59'),path('M47 203L137 203L143 211L42 211Z','#ddd9ce'),rect(51,205,83,2,'#5168a2'),rect(146,205,8,6,'#101c59'),rect(148,207,4,2,'#e7dcb8')]
    # Desk lamp, papers, mug and tiny pixel potted plant add lived-in visual detail.
    s += [rect(38,174,3,24,'#101c59'),rect(29,172,20,3,'#101c59'),rect(31,167,16,6,'#f3d878'),rect(36,173,7,2,'#fff1bb')]
    s += [rect(131,194,16,2,'#f2ebd8'),rect(127,197,18,2,'#cbd7dc'),rect(162,194,10,12,'#101c59'),rect(163,196,8,8,'#f2e3bf')]
    s += [rect(157,188,8,6,'#8a4c73'),rect(155,183,5,6,'#38c8b9'),rect(160,179,5,8,'#4bd2be'),rect(165,184,5,6,'#30b8ae')]
    # Chair foreground, pushed up to the desk, with pixel highlights and caster feet.
    s += [rect(253,226,123,8,'#101c59'),rect(262,213,105,19,'#233c83'),rect(270,211,89,6,'#3657a0'),rect(278,214,73,3,'#5673b5')]
    s += [rect(286,234,61,12,'#17275f'),rect(306,247,20,20,'#101c59'),rect(313,264,7,31,'#101c59'),rect(287,294,61,5,'#101c59'),rect(277,297,12,3,'#101c59'),rect(347,297,12,3,'#101c59')]
    s += [rect(300,238,5,2,'#6b84bd'),rect(338,238,5,2,'#6b84bd')]
    # Soft pixel lighting pools and wall/floor contact shadows.
    s += [rect(186,226,262,2,'#292f70'),rect(42,280,166,3,'#523d50'),rect(534,189,72,2,'#584256')]
    s.append('<text x="206" y="73" font-family="monospace" font-size="8" fill="#fff1bd">DRAIN TOWN CCTV NETWORK</text>')
    s.append('</svg>')
    return ''.join(s)
