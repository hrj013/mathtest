"""Fine-grid pixel art for Drain Town (drawn on a 320x180 pixel canvas)."""

W, H = 320, 180


def box(x, y, w, h, color):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"/>'


def start_scene():
    """Front view of the round outfall mouth with water spilling into the river."""
    s = ['<svg viewBox="0 0 320 180" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated;shape-rendering:crispEdges">']
    s += [box(0,0,320,76,'#4e83ca'), box(0,0,320,54,'#77a8dc'), box(0,54,320,25,'#253f87')]
    # distant masonry / river-town tiles
    for x in range(0,320,20):
        s += [box(x,55,2,22,'#1b3478'), box(x+8,61,6,2,'#9cb9de')]
    # clustered pixel vegetation and coral
    for x,y,c in [(14,34,'#39c9c4'),(39,44,'#ec77ad'),(85,30,'#51d4bd'),(122,46,'#f17cab'),(237,35,'#40c8c0'),(286,45,'#f185b4')]:
        s += [box(x,y,10,5,c),box(x+3,y-4,6,4,c),box(x+4,y+5,3,7,'#713e83'),box(x-3,y+3,4,4,c)]
    s += [box(0,79,320,101,'#354e9a'),box(0,84,320,3,'#d7e2f1'),box(0,155,320,4,'#e1e6f4')]
    for x in range(0,320,32): s.append(box(x,119,15,2,'#516eae'))
    # round pipe opening, built from nested pixel blocks and rings (not a side-on tube)
    cx,cy=84,87
    rings=[(42,'#101d59'),(37,'#e7d59b'),(32,'#687d95'),(27,'#213e75'),(21,'#12335f')]
    for r,col in rings:
        for yy in range(cy-r,cy+r+1):
            for xx in range(cx-r,cx+r+1):
                if max(abs(xx-cx),abs(yy-cy))==r: s.append(box(xx,yy,1,1,col))
    # intrados shine and water flowing out through the round mouth
    s += [box(62,76,44,3,'#94aac0'),box(57,80,3,22,'#7f92a4'),box(108,80,3,22,'#7f92a4')]
    s += [box(61,88,46,12,'#35c7df'),box(66,84,36,4,'#a5f2e7'),box(65,100,38,5,'#24b1d5')]
    for y,x,w,c in [(106,69,30,'#27add2'),(112,60,48,'#45c7dc'),(119,52,64,'#8de7df'),(127,40,88,'#c7f1dc'),(135,30,108,'#6bd9dc'),(145,18,132,'#b1efe1')]: s.append(box(x,y,w,4,c))
    for x,y,c in [(9,131,'#f5db72'),(19,140,'#a2f1e4'),(154,132,'#f07baa'),(175,144,'#9beee0'),(200,125,'#ef7aaa'),(261,139,'#f0d668')]: s.append(box(x,y,5,2,c))
    # bold frame rails, bolts, and labels
    s += [box(39,42,4,72,'#101d59'),box(125,42,4,72,'#101d59'),box(43,43,3,69,'#e8d69c'),box(122,43,3,69,'#e8d69c')]
    s += [box(0,78,320,2,'#162a6a'),box(0,157,320,2,'#d9e3f2')]
    s.append('<text x="169" y="29" font-family="monospace" font-size="10" fill="#fff1c2">DRAIN TOWN WATERWAY</text>')
    s.append('</svg>')
    return ''.join(s)


def calendar_wall(x, y):
    s=[box(x,y,27,37,'#101c59'),box(x+2,y+2,23,33,'#f4e7bf'),box(x+2,y+2,23,8,'#e879a8')]
    s += [box(x+7,y-2,3,7,'#101c59'),box(x+19,y-2,3,7,'#101c59')]
    for yy in (13,20,27):
        for xx in (x+5,x+12,x+19): s.append(box(xx,yy,4,3,'#3559a3'))
    s += [box(x+12,y+27,2,5,'#049577'),box(x+12,y+30,6,2,'#049577')]
    return ''.join(s)


def room_scene(routes):
    """Perspective room: central cinema-size 2x2 screen, left desk PC, right wall calendar."""
    s=['<svg viewBox="0 0 320 190" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated;shape-rendering:crispEdges">']
    # Ceiling and room perspective based on the supplied empty-room reference.
    s += [box(0,0,320,190,'#735d8b'),'<path d="M0 0H320L287 27H33Z" fill="#c7c7c5"/>','<path d="M0 0L33 27V111L0 145Z" fill="#e2e2df"/>','<path d="M320 0L287 27V111L320 145Z" fill="#b9b9bd"/>',box(33,27,254,84,'#eeefeb')]
    # wall details: blue outlines, trim, tile seams
    s += [box(33,27,254,2,'#f9f8f2'),box(33,109,254,3,'#977c9e'),box(0,143,320,4,'#172d76')]
    for x in range(38,287,22): s.append(box(x,32,1,72,'#e4e4df'))
    # wooden pixel floor in perspective with tight plank grain
    s += [box(0,147,320,43,'#795844'),'<path d="M0 147H320L320 190H0Z" fill="#80604a"/>']
    for x in range(0,321,12): s.append(f'<path d="M160 147L{x} 190" stroke="#a77c5b" stroke-width="2"/>')
    for y in (153,160,169,179,188):
        left=max(0,int(160-(y-147)*3.7)); right=min(320,int(160+(y-147)*3.7))
        s.append(f'<path d="M{left} {y}H{right}" stroke="#4e3b45" stroke-width="1"/>')
    for x,y in [(15,166),(44,179),(78,157),(251,166),(287,182),(190,173),(116,184),(225,155),(62,169),(268,157)]: s.append(box(x,y,4,1,'#b58a64'))
    # Central cinema-like giant wall display, one broad display divided into four feeds.
    s += [box(79,35,162,79,'#101c59'),box(82,38,156,73,'#16245e'),box(85,41,150,67,'#090f26'),box(87,43,146,3,'#aebbd2'),box(87,103,146,3,'#aebbd2'),box(87,43,3,63,'#aebbd2'),box(230,43,3,63,'#aebbd2'),box(159,43,2,63,'#9fb5cf'),box(87,73,146,2,'#9fb5cf')]
    # Detailed CCTV pictures, 2 columns x 2 rows, each 70x28 pixels.
    for i,route in enumerate(routes):
        bx=90+(i%2)*71; by=47+(i//2)*29
        s += [box(bx,by,67,24,'#467cae'),box(bx,by,67,3,'#35528e'),box(bx,by+21,67,3,'#35528e')]
        # Sewage tunnel wall, pipe ring and interior channel
        s += [box(bx+13,by+5,42,15,'#dcc99a'),box(bx+16,by+6,36,13,'#687992'),box(bx+20,by+8,28,10,'#17345f'),box(bx+21,by+13,26,5,'#2cb8d4')]
        level=int(route[0]*4)
        s.append(box(bx+22,by+17-level,24,level+1,'#47cde0'))
        for j in range(int(route[2]*5)): s.append(box(bx+22+j*4,by+18,2,2,'#f2d164' if j%2 else '#ee78aa'))
        for j in range(int(route[3]*4)): s.append(box(bx+14+j*5,by+6+(j%2),3,2,'#e87991'))
        for j in range(int(route[1]*4)): s.append(box(bx+5+j*13,by+5+(j%3)*4,2,2,'#b8f1e7'))
        s.append(f'<text x="{bx+3}" y="{by+9}" font-family="monospace" font-size="6" fill="#fff0c8">0{i+1}</text>')
    # Left wall office desk with CRT PC physically sitting on the desktop.
    s += [box(5,81,62,3,'#101c59'),box(8,84,56,4,'#a16d4b'),box(12,88,4,24,'#443849'),box(56,88,4,24,'#443849'),box(12,86,48,2,'#d19a68')]
    # PC monitor, pixel screen glow, stand, base, keyboard and mouse
    s += [box(23,61,30,22,'#101c59'),box(25,63,26,16,'#3b83b9'),box(27,65,22,12,'#5ed2d7'),box(29,67,14,2,'#d8f1ce'),box(29,71,17,2,'#f2d881'),box(34,83,8,3,'#18275f'),box(29,86,18,2,'#101c59'),box(18,86,19,2,'#e9dfc6'),box(18,88,19,2,'#3c5a9c'),box(42,86,4,3,'#101c59'),box(43,87,2,1,'#e9dfc6')]
    # desk drawers and pixel handles
    s += [box(14,92,18,12,'#925f49'),box(36,92,20,12,'#855744'),box(20,96,3,2,'#dfc27c'),box(43,96,3,2,'#dfc27c')]
    # Right wall calendar visibly mounted on the wall
    s.append(calendar_wall(278,65))
    s += [box(274,59,35,2,'#172d76'),box(280,105,22,3,'#172d76')]
    # lamp and small wall notice
    s += [box(155,28,10,3,'#101c59'),box(158,31,4,5,'#f6df7c'),box(150,36,20,1,'#fff0b8'),box(69,47,7,10,'#314b91'),box(70,48,5,7,'#f3e5b6')]
    # Foreground office chair centered in front of desk/screen.
    s += [box(133,124,54,3,'#101c59'),box(138,116,44,10,'#253f86'),box(143,114,34,4,'#355aa3'),box(154,127,12,5,'#101c59'),box(158,132,5,13,'#101c59'),box(146,143,28,3,'#101c59'),box(139,145,5,2,'#101c59'),box(176,145,5,2,'#101c59')]
    # PC/calandar labels in tiny signage (not explanatory UI)
    s.append('<text x="25" y="60" font-family="monospace" font-size="5" fill="#fff1bd">WORK PC</text>')
    s.append('<text x="279" y="61" font-family="monospace" font-size="5" fill="#fff1bd">WEEK</text>')
    s.append('</svg>')
    return ''.join(s)
