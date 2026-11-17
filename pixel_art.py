"""Small-grid pixel-art scenes for the Drain Town game.

Every scene is drawn on a fixed low-resolution grid and enlarged with nearest-neighbour
rendering. The palette and clustered tiles are intentionally limited for a crisp sprite look.
"""
from html import escape

P = 8


def _svg_open(width, height, background):
    return [f'<svg viewBox="0 0 {width*P} {height*P}" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;image-rendering:pixelated;shape-rendering:crispEdges"><rect width="100%" height="100%" fill="{background}"/>']


def _px(out, x, y, color, w=1, h=1):
    out.append(f'<rect x="{x*P}" y="{y*P}" width="{w*P}" height="{h*P}" fill="{color}"/>')


def _line(out, x1, y1, x2, y2, color, thickness=1):
    # Orthogonal, pixel-grid line segments only.
    if x1 == x2:
        _px(out, x1, min(y1,y2), color, thickness, abs(y2-y1)+thickness)
    elif y1 == y2:
        _px(out, min(x1,x2), y1, color, abs(x2-x1)+thickness, thickness)


def _tree(out, x, y, variant=0):
    trunk = ['#713e78', '#624982', '#8a477c'][variant % 3]
    leaves = ['#32c6c7', '#40bfc2', '#50cdb9'][variant % 3]
    shadow = ['#145b9d', '#155293', '#1b639a'][variant % 3]
    _px(out, x+3, y+5, shadow, 5, 4)
    _px(out, x+2, y+3, leaves, 6, 3); _px(out, x+1, y+4, leaves, 8, 2)
    _px(out, x+3, y+2, '#71e0cb', 3, 1); _px(out, x+6, y+3, '#77ded5', 2, 1)
    _px(out, x+4, y+8, trunk, 2, 4); _px(out, x+2, y+10, trunk, 2, 1); _px(out, x+6, y+9, trunk, 2, 1)
    _px(out, x+4, y+8, '#b75c9a', 1, 1)


def _flower(out, x, y, color='#f078b1'):
    _px(out, x+1, y, color); _px(out, x, y+1, color); _px(out, x+1, y+1, '#ffe47b'); _px(out, x+2, y+1, color); _px(out, x+1, y+2, color)
    _px(out, x+1, y+3, '#328978')


def start_scene():
    """Town outfall: front-facing round sewer mouth with visible water spilling out."""
    W,H=120,44; o=_svg_open(W,H,'#5489cf')
    _px(o,0,0,'#72a5dc',W,18); _px(o,0,18,'#193d8b',W,26)
    # Distant tiled riverbank and pixel clouds.
    for x,y,w in [(4,4,8),(18,7,10),(77,3,11),(101,6,9)]:
        _px(o,x,y,'#b3c9e8',w,1); _px(o,x+2,y-1,'#d7e4f2',max(2,w-5),1)
    # Distant sewer-town wall, block masonry, and bright vegetation.
    _px(o,0,14,'#465f9d',120,5); _px(o,0,15,'#7794bc',120,1)
    for x in range(2,120,8):
        _px(o,x,14,'#263f86',1,5); _px(o,x+4,16,'#5478af',2,1)
    for x,y,v in [(7,6,0),(46,5,1),(82,5,2),(108,8,1)]: _tree(o,x,y,v)
    for x,y in [(17,13),(37,10),(56,12),(74,11),(95,13),(114,12)]: _flower(o,x,y)
    # Opening silhouette: stepped pixel rings, viewed straight on, not a pipe sidewall.
    cx,cy=27,23
    for r,col in [(13,'#101d59'),(11,'#e7d59b'),(10,'#31549c'),(8,'#5e7897'),(7,'#163d6a')]:
        for yy in range(cy-r,cy+r+1):
            for xx in range(cx-r,cx+r+1):
                d=max(abs(xx-cx),abs(yy-cy))
                if r-1 <= d <= r: _px(o,xx,yy,col)
    # Inner tunnel highlights and blue-green water flowing from the circular mouth.
    _px(o,cx-5,cy-5,'#758ca4',10,1); _px(o,cx-6,cy-4,'#758ca4',1,7); _px(o,cx+5,cy-4,'#758ca4',1,7)
    _px(o,cx-6,cy+1,'#37c6e0',12,3); _px(o,cx-5,cy,'#9af0e8',10,1)
    for yy,xx,ww,col in [(29,22,10,'#31b9df'),(32,23,8,'#24a9d2'),(35,21,12,'#50d3dd'),(38,18,18,'#8de8df'),(40,14,26,'#d1f6dc')]: _px(o,xx,yy,col,ww,1)
    # Ripples, stones and foam, rendered as individual pixel clusters.
    for x,y,col in [(10,36,'#98e6df'),(47,37,'#a8eee5'),(51,39,'#50c5d7'),(39,34,'#f8e276'),(8,41,'#f079b0'),(53,42,'#e77ba9')]: _px(o,x,y,col,2,1)
    # Pixel sea grass and coral on either bank.
    for x,y,v in [(64,12,0),(71,9,1),(89,13,2),(100,11,0)]:
        _px(o,x,y+2,'#8c4c91',1,4); _px(o,x-1,y,'#ef79b1',2,2); _px(o,x+2,y+2,'#e765a9',1,2)
    for x in range(59,120,7): _px(o,x,18,'#2d4d95',1,26)
    # foreground walkway and drainage channel.
    _px(o,0,19,'#d4dcef',120,1); _px(o,0,20,'#a6bde1',120,1); _px(o,0,41,'#d7dfef',120,1)
    for x in range(0,120,6): _px(o,x,42,'#4565a9',3,1)
    o.append('<text x="520" y="54" font-family="monospace" font-size="20" fill="#fff1bd">DRAIN TOWN WATERWAY</text>')
    o.append('</svg>'); return ''.join(o)


def _pipe_view(out, x, y, w, h, idx, route=None):
    """Pixel-grid CCTV view with an outlined conduit and characteristic clusters."""
    route = route or [.3,.3,.3,.3]
    _px(out,x,y,'#315ca4',w,h); _px(out,x+1,y+1,'#6fa5d5',w-2,h-2)
    _px(out,x+1,y+1,'#59699a',w-2,2); _px(out,x+1,y+h-3,'#59699a',w-2,2)
    # conduit cross-section, with chunky multi-tone pixel ring
    px=x+w//2; py=y+h//2
    rw=max(7,w//4); rh=max(5,h//3)
    _px(out,px-rw-2,py-rh-2,'#101d59',2*rw+5,2*rh+5)
    _px(out,px-rw,py-rh,'#ead69a',2*rw+1,2*rh+1)
    _px(out,px-rw+1,py-rh+1,'#7c789f',2*rw-1,2*rh-1)
    _px(out,px-rw+3,py-rh+2,'#142d60',2*rw-5,2*rh-3)
    water=int(max(1,(2*rh-4)*route[0]))
    _px(out,px-rw+4,py+rh-2-water,2*rw-7,water,'#39bfdf')
    _px(out,px-rw+5,py+rh-3-water, max(2,2*rw-10),1,'#b1f5e8')
    # pressure bubbles, sediment, corrosion pixels
    for j in range(2+int(route[1]*5)):
        bx=x+3+(j*13+idx*7)%(w-7); by=y+4+(j*7)%(h-10)
        _px(out,bx,by,'#b5f2e7',1,1)
    for j in range(int(route[2]*7)):
        _px(out,px-rw+4+j*2,py+rh-4,'#f2d164' if j%2 else '#ee78aa',1,1)
    for j in range(int(route[3]*5)):
        _px(out,x+3+j*3,y+3+(j%2),'#e77891',2,1)
    _px(out,x+1,y+1,'#101d59',8,2)
    out.append(f'<text x="{(x+2)*P}" y="{(y+3)*P}" font-family="monospace" font-size="10" fill="#fff1bd">CAM 0{idx+1}</text>')


def room_scene(routes):
    """One coherent pixel-art room: fixtures on back wall, giant CCTV ahead, desk foreground."""
    W,H=140,66; o=_svg_open(W,H,'#7979ae')
    # wall tile pattern and wainscot
    for y in range(0,42,6):
        _px(o,0,y,'#7775a6',W,1); _px(o,0,y+1,'#8782b4',W,4)
        for x in range((y//6%2)*7,W,14): _px(o,x,y+1,'#6c6d9d',1,4)
    _px(o,0,41,'#d9c4dd',W,2); _px(o,0,43,'#505897',W,23)
    for x in range(0,W,8): _px(o,x,43,'#7180b6',1,23)
    # left wall PC: blue CRT and pixel file icons
    _px(o,4,10,'#101d59',17,12); _px(o,5,11,'#e6d49d',15,10); _px(o,6,12,'#1b3d82',13,7)
    _px(o,7,13,'#42c7e0',11,5); _px(o,8,14,'#d2f3d9',5,1); _px(o,8,16,'#e97eae',7,1)
    _px(o,11,22,'#101d59',3,3); _px(o,7,25,'#101d59',11,1)
    _px(o,6,28,'#5ce0ce',2,2); _px(o,10,28,'#f6df82',2,2); _px(o,14,28,'#f17eaf',2,2)
    # right wall calendar with marked days
    _px(o,119,10,'#101d59',16,17); _px(o,120,11,'#f5e7bc',14,15); _px(o,120,11,'#e975a8',14,3)
    for xx in (123,131): _px(o,xx,9,'#101d59',1,4)
    for yy in (16,20,24):
        for xx in (122,126,130,134): _px(o,xx,yy,'#3356a5',2,1)
    _px(o,125,23,'#4cdb9c',2,1); _px(o,126,22,'#4cdb9c',1,2)
    # central giant screen bezel, with all four cameras inside the same screen.
    sx,sy,sw,sh=29,5,82,36
    _px(o,sx-2,sy-2,'#101d59',sw+4,sh+4); _px(o,sx,sy,'#263d8c',sw,sh); _px(o,sx+1,sy+1,'#111a3d',sw-2,sh-2)
    _px(o,sx+2,sy+2,'#c7cbe0',sw-4,1); _px(o,sx+2,sy+sh-3,'#c7cbe0',sw-4,1)
    gap=2; mw=(sw-6)//2; mh=(sh-6)//2
    for i,route in enumerate(routes):
        xx=sx+2+(i%2)*(mw+gap); yy=sy+2+(i//2)*(mh+gap)
        _pipe_view(o,xx,yy,mw,mh,i,route)
    # top signal LEDs and hanging lamp
    _px(o,67,1,'#101d59',6,2); _px(o,68,1,'#ffe178',4,1); _px(o,69,3,'#fff0bb',2,2)
    for x,c in [(35,'#f07fa9'),(38,'#f4d45f'),(104,'#61ddc8')]: _px(o,x,3,c,1,1)
    # desk, keyboard, mug and little plant in foreground
    _px(o,0,49,'#6f493c',W,3); _px(o,0,52,'#46364c',W,1); _px(o,0,53,'#754a42',W,13)
    for x in range(0,W,12): _px(o,x,50,'#9b654a',7,1)
    _px(o,17,47,'#f2e7ca',17,3); _px(o,19,48,'#d9d7d1',13,1); _px(o,20,49,'#b1b8c5',11,1)
    _px(o,64,47,'#101d59',12,4); _px(o,65,48,'#58c9db',10,2); _px(o,67,51,'#101d59',6,2)
    _px(o,104,46,'#101d59',7,5); _px(o,105,47,'#f582af',2,2); _px(o,109,47,'#f582af',2,2)
    _px(o,106,51,'#fff0c8',3,1)
    # office chair silhouette, foreground center
    _px(o,57,57,'#101d59',25,2); _px(o,59,54,'#243b87',21,4); _px(o,62,53,'#3459a3',15,1)
    _px(o,68,58,'#101d59',3,4); _px(o,61,62,'#101d59',15,1)
    # floor markers and shadows
    _px(o,0,64,'#111d59',W,2); _px(o,5,59,'#9981ab',6,1); _px(o,127,59,'#9981ab',6,1)
    o.append('<text x="20" y="28" font-family="monospace" font-size="8" fill="#fff1bd">PC</text>')
    o.append('<text x="952" y="28" font-family="monospace" font-size="8" fill="#fff1bd">CAL</text>')
    o.append('</svg>'); return ''.join(o)


def result_art():
    return '<div style="font:12px monospace;color:#fff1bd">DRAIN TOWN PIXEL SPRITES</div>'
