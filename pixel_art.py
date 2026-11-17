"""Grid-based pixel scenes for the Drain Town game.

All coordinates are integer tiles enlarged with nearest-neighbour rendering,
so scene edges stay deliberately chunky instead of looking like smooth shapes.
"""

S = 8


def rect(x, y, w, h, color):
    return f'<rect x="{x*S}" y="{y*S}" width="{w*S}" height="{h*S}" fill="{color}"/>'


def start_scene():
    out = ['<svg viewBox="0 0 960 400" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated;shape-rendering:crispEdges">']
    out.append(rect(0,0,120,50,'#3f72be'))
    out.append(rect(0,0,120,17,'#5794d2'))
    # Waterway wall and distant pixel plants
    out.append(rect(0,16,120,7,'#263f86'))
    for x in range(0,120,8): out.append(rect(x,16,1,7,'#19336f'))
    for x,y,c in [(4,9,'#35c7c1'),(14,12,'#ef75ae'),(46,8,'#51d4bd'),(57,12,'#ec77a8'),(91,9,'#46c7c3'),(106,12,'#f082b1')]:
        out.extend([rect(x,y,3,1,c),rect(x+1,y-1,2,1,c),rect(x+1,y+1,1,2,'#754683')])
    # Riverbed / town path
    out.extend([rect(0,23,120,27,'#344e9b'),rect(0,24,120,1,'#d7e1ef'),rect(0,42,120,1,'#d7e1ef')])
    for x in range(0,120,12): out.append(rect(x,31,5,1,'#536fb0'))
    # Front-facing circular sewer opening with stacked pixel rings
    cx,cy=27,23
    for radius,color in [(14,'#101d59'),(12,'#dfcf9a'),(10,'#60758d'),(8,'#143b70')]:
        for yy in range(cy-radius,cy+radius+1):
            for xx in range(cx-radius,cx+radius+1):
                if max(abs(xx-cx),abs(yy-cy))==radius: out.append(rect(xx,yy,1,1,color))
    out.extend([rect(cx-6,cy-1,12,3,'#39c5df'),rect(cx-5,cy-2,10,1,'#b3f4e9'),rect(cx-5,cy+2,10,2,'#28b4d7')])
    for y,x,w,c in [(27,22,10,'#26abd0'),(30,20,14,'#49ccdc'),(33,17,20,'#8de6df'),(35,12,30,'#c6f0dc')]: out.append(rect(x,y,w,1,c))
    # Pixel ripples / foam
    for x,y,c in [(5,36,'#f5dd78'),(9,38,'#a2f0e2'),(39,37,'#ee79ad'),(47,35,'#a1f2e3'),(53,39,'#f0d45e')]: out.append(rect(x,y,2,1,c))
    out.append('</svg>')
    return ''.join(out)


def _calendar(x, y, title='WEEK'):
    parts=[rect(x,y,11,14,'#101c59'),rect(x+1,y+1,9,12,'#f5e8bd'),rect(x+1,y+1,9,3,'#e979a8'),rect(x+3,y,1,2,'#101c59'),rect(x+8,y,1,2,'#101c59')]
    for yy in (5,8,11):
        for xx in (x+2,x+5,x+8): parts.append(rect(xx,yy,2,1,'#3459a3'))
    parts.extend([rect(x+5,y+10,1,2,'#18a77e'),rect(x+5,y+11,2,1,'#18a77e')])
    return ''.join(parts)


def room_scene(routes):
    """Perspective office with side-wall calendars, one 2x2 wall monitor, desk PC."""
    out=['<svg viewBox="0 0 1200 680" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated;shape-rendering:crispEdges">']
    # Room shell: ceiling, back wall, side walls, and parquet floor in chunky pixel perspective.
    out += [rect(0,0,120,85,'#d1d1d0'),'<path d="M0 0H120L103 10H17Z" fill="#bdbfbe"/>', '<path d="M0 0L17 10V47L0 62Z" fill="#e4e4e1"/>','<path d="M120 0L103 10V47L120 62Z" fill="#b9babd"/>',rect(17,10,86,37,'#efefeb')]
    out.append(rect(0,47,120,38,'#765646'))
    # floorboards with perspective lines, narrow planks and alternating wood pixels
    out.append('<path d="M0 47H120L120 85H0Z" fill="#80604d"/>')
    for x in range(0,121,4): out.append(f'<path d="M60 47L{x} 85" stroke="#a77b5d" stroke-width="2"/>')
    for y in (51,56,62,69,77,84): out.append(f'<path d="M{max(0,60-(y-47)*1.6):.0f} {y}H{min(120,60+(y-47)*1.6):.0f}" stroke="#4a3c48" stroke-width="1"/>')
    for x,y in [(8,57),(22,67),(40,53),(78,59),(101,71),(57,78),(90,53),(31,77)]: out.append(rect(x,y,2,1,'#b18461'))
    # Back wall dado rail, baseboards and checker-like trim
    out += [rect(17,45,86,2,'#8b7899'),rect(17,47,86,1,'#31458d'),rect(0,61,120,2,'#293f89')]
    # The single giant central CCTV screen, with four feeds inside one bezel.
    out += [rect(38,15,44,28,'#101c59'),rect(40,17,40,24,'#172a70'),rect(41,18,38,22,'#20264f')]
    # Pixel screen frames and divider
    out += [rect(41,18,38,1,'#d6d7dc'),rect(41,39,38,1,'#d6d7dc'),rect(41,18,1,22,'#d6d7dc'),rect(78,18,1,22,'#d6d7dc'),rect(59,18,1,22,'#a8b8d2'),rect(41,29,38,1,'#a8b8d2')]
    # CCTV wells, pixel rings and sensor patterns per quadrant.
    for i,route in enumerate(routes):
        bx=42+(i%2)*19; by=19+(i//2)*11
        out.extend([rect(bx,by,17,9,'#386da5'),rect(bx+1,by+1,15,7,'#7597b5'),rect(bx+3,by+2,11,5,'#182f60'),rect(bx+4,by+5,9,max(1,int(route[0]*2)),'#36c5dc')])
        for j in range(int(route[2]*4)): out.append(rect(bx+4+j*2,by+6,1,1,'#ef78a9'))
        for j in range(int(route[3]*3)): out.append(rect(bx+2+j*3,by+2,1,1,'#e0788c'))
        out.append(f'<text x="{bx*S+5}" y="{by*S+10}" font-family="monospace" font-size="7" fill="#fff0c8">{i+1}</text>')
    # Two calendars are actually attached to opposite side walls.
    out += [_calendar(7,28),_calendar(102,28)]
    out += [rect(5,25,15,1,'#243b80'),rect(100,25,15,1,'#243b80')]
    # Wall notices / pixel fixtures
    out += [rect(22,25,7,5,'#536ba4'),rect(23,26,5,3,'#f0dfab'),rect(91,25,6,5,'#536ba4'),rect(92,26,4,3,'#e978a8')]
    # Office desk foreground, front edge, legs and surface.
    out += ['<path d="M18 49H102L111 59H9Z" fill="#a36d4f"/>',rect(9,58,102,3,'#101c59'),rect(14,61,4,14,'#42364b'),rect(102,61,4,14,'#42364b'),rect(17,58,86,1,'#d39b69')]
    for x in range(20,101,12): out.append(rect(x,51,7,1,'#c28a60'))
    # Desktop CRT computer sitting on the desk, keyboard and mug.
    out += [rect(51,39,19,12,'#101c59'),rect(53,40,15,8,'#347fbd'),rect(54,41,13,5,'#64d6d7'),rect(55,43,9,1,'#e6f4ce'),rect(58,51,5,2,'#17265d'),rect(53,53,15,2,'#101c59'),rect(43,55,18,1,'#e5e0d0'),rect(43,56,18,2,'#5168a2')]
    out += [rect(81,50,5,6,'#101c59'),rect(82,51,3,4,'#e57ca8'),rect(86,51,2,1,'#f8eab0'),rect(32,52,5,4,'#e8e2d5'),rect(32,52,5,1,'#101c59')]
    # Chair in front of desk, pixel silhouette
    out += [rect(49,62,22,2,'#101c59'),rect(51,64,18,5,'#354f9c'),rect(55,69,10,2,'#101c59'),rect(59,71,3,5,'#101c59'),rect(53,76,15,2,'#101c59')]
    out.append('</svg>')
    return ''.join(out)
