"""Radiant threshold: a deterministic, standard-library cosmic painting."""
import math
import os
import random
import struct
import zlib
from pathlib import Path

SIZE = 800


def chunk(kind, data):
    return (struct.pack('>I', len(data)) + kind + data
            + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff))


def main():
    rng = random.Random(31827)
    rays = [(rng.random()*math.tau, rng.uniform(100, 540), rng.uniform(.5, 2))
            for _ in range(160)]
    stars = {(rng.randrange(SIZE), rng.randrange(SIZE)): rng.randrange(90, 256)
             for _ in range(2400)}
    rows = []
    for y in range(SIZE):
        row = bytearray([0])
        for x in range(SIZE):
            dx, dy = x-400, y-345
            r = math.hypot(dx, dy)
            t = math.atan2(dy, dx)
            swirl = t + r*.008
            turbulence = (math.sin(x*.023+math.sin(y*.017)*2)
                          + math.sin(y*.031+x*.009))*.14
            cloud = max(0, .7+turbulence+math.sin(swirl*3)*.3)
            envelope = math.exp(-(r/390)**2)
            blue = .5+.5*math.sin(swirl*2+1)
            red = .5+.5*math.cos(swirl*3-1)
            c = [18+envelope*cloud*(100*red+30),
                 25+envelope*cloud*(95*blue+35),
                 55+envelope*cloud*(160*blue+50)]
            shell = math.exp(-((r-(155+19*math.sin(t*5+r*.006)))/22)**2)
            for k, v in enumerate((90, 100, 180)):
                c[k] += shell*v
            for radius, color, power in [(130,(255,65,8),2),
                                          (68,(255,180,30),3),
                                          (32,(255,255,220),6)]:
                a = math.exp(-(r/radius)**2)*power
                for k in range(3):
                    c[k] += color[k]*a
            # Narrow, curved plasma spokes, resolved analytically per pixel.
            spoke = max(0, math.cos(t*53+math.sin(r*.012)*.8))**70
            a = spoke*math.exp(-r/235)*min(1,r/75)*1.6
            for k,v in enumerate((120,170,220)):
                c[k] += a*v
            # The observer floats directly in front of the brilliant event.
            sx, sy = x-400, y-485
            head = (sx/20)**2+((sy+40)/23)**2 < 1
            torso = abs(sx)<23 and -21<sy<53
            pack = abs(sx)<30 and -12<sy<35
            legs = (abs(sx+15+max(0,sy-50)*.12)<10 or
                    abs(sx-15-max(0,sy-50)*.17)<10) and 45<sy<120
            arms = abs(sy-(-8+abs(sx)*.65))<9 and 20<abs(sx)<52
            if head or torso or pack or legs or arms:
                c = [3,6,13]
            if r > 390 and ((x*17+y*31)%5): c = [v*.22 for v in c]
            star = stars.get((x,y),0)
            for k in range(3):
                value = 255*(1-math.exp(-c[k]/155))
                row.append(min(255,round(value+star)))
        rows.append(row)
    # Tiny fast fragments travel away from the core.
    for angle, length, width in rays:
        start = length-rng.uniform(3,17)
        for j in range(int((length-start)*2)+1):
            d = start+j*.5
            x=round(400+math.cos(angle)*d)
            y=round(345+math.sin(angle)*d)
            if 0<=x<SIZE and 0<=y<SIZE:
                i=1+x*3
                rows[y][i:i+3]=bytes((200,235,255))
    raw=b''.join(rows)
    png=(b'\x89PNG\r\n\x1a\n'
         +chunk(b'IHDR',struct.pack('>IIBBBBB',SIZE,SIZE,8,2,0,0,0))
         +chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b''))
    output=Path(os.environ.get('MAKEFUN_OUTPUT_DIR','/output'))
    output.mkdir(parents=True,exist_ok=True)
    (output/'entry.png').write_bytes(png)


if __name__ == '__main__':
    main()
