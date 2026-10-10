import os
import math
import uuid
from PIL import Image, ImageDraw

CLIFFS_DIR = r'd:\Unity\Projects\STRANDED\Assets\Art\Terrain\Cliffs'
BRAIN_DIR  = r'C:\Users\PAVILION\.gemini\antigravity-ide\brain\84db0e2d-58d2-466d-be05-dbff8f133035'
os.makedirs(CLIFFS_DIR, exist_ok=True)

# Master Palette
C_DARKEST   = (38, 25, 11, 255)    # Deep fissure cracks and crevice outlines (#26190b)
C_CREVICE   = (58, 40, 16, 255)    # Crevice shade & boulder undersides (#3a2810)
C_SHADOW    = (84, 59, 23, 255)    # Volumetric boulder shadow (#543b17)
C_ROCK_DARK = (108, 78, 30, 255)   # Base earthen rock mid-shadow (#6c4e1e)
C_ROCK_MID  = (135, 99, 38, 255)   # Main earthen boulder body (#876326)
C_ROCK_HI   = (164, 122, 48, 255)  # Sunlit stone crest highlight (#a47a30)
C_LIP_MID   = (188, 142, 56, 255)  # Golden earthen cliff rim (#bc8e38)
C_LIP_HI    = (210, 162, 68, 255)  # Sunlit upper rim shelf (#d2a244)

# Grass Colors
G_DARK      = (34, 75, 48, 255)    # Grass under-shadow (#224b30)
G_LUSH      = (48, 122, 42, 255)   # Lush dark grass (#307a2a)
G_MID       = (68, 163, 24, 255)   # Standard grass midtone (#44a318)
G_HI        = (114, 224, 65, 255)  # Grass sun highlight (#72e041)

# Natural Mud / Dirt Colors (Stardew authentic mud palette)
D_DIRT      = (179, 119, 41, 255)  # Mud base (#b37729)
D_DARK      = (145, 78, 12, 255)   # Mud shadow / groove (#914e0c)
D_DEEP      = (110, 55, 10, 255)   # Deep mud crevice (#6e370a)
D_LIGHT     = (205, 145, 55, 255)  # Sunlit mud crest (#cd9137)
D_HI        = (222, 168, 72, 255)  # Bright dry mud ridge (#dea848)

# Micro Pebbles
P_SLATE     = (125, 140, 128, 255) # Slate pebble (#7d8c80)
P_SLATE_D   = (78, 92, 82, 255)    # Slate shadow
P_DIRT      = (160, 120, 50, 255)  # Earth pebble
P_DIRT_D    = (100, 70, 25, 255)

def new_tile():
    return Image.new('RGBA', (16, 16), (0, 0, 0, 0))

print("1. Crafting authentic, volumetric West-facing cliff side (32px)...")
# West-facing cliff wall runs North-South.
# Upper plateau is on the RIGHT (x=10..15).
# The sheer rock face drops to the WEST (left, x=3..9).
# Lowland is on the LEFT (x=0..2).
# Canvas is 16 wide x 32 high, sliced into top and bot!

def render_west_cliff_32(variant=1):
    w32 = Image.new('RGBA', (16, 32), (0, 0, 0, 0))

    # Base rock background on x=3..10, y=0..31
    for y in range(32):
        for x in range(3, 11):
            w32.putpixel((x, y), C_SHADOW)

    # Volumetric Boulders running vertically
    # Boulders centered along x=6.5, with y spacing every 7-8px
    def draw_west_boulder(cx, cy, rx, ry, seed=0):
        for y in range(max(0, int(cy - ry - 2)), min(32, int(cy + ry + 3))):
            for x in range(max(2, int(cx - rx - 2)), min(11, int(cx + rx + 3))):
                dx = (x - cx) / float(rx)
                dy = (y - cy) / float(ry)
                angle = math.atan2(dy, dx)
                wobble = 1.0 + 0.12 * math.sin(angle * 3 + seed) + 0.08 * math.cos(angle * 4)
                d = (dx*dx + dy*dy) / (wobble * wobble)

                if d <= 1.0:
                    # Light comes from top-left: dx < 0 and dy < 0 are sunlit!
                    light = -0.70 * dx - 0.55 * dy
                    if light > 0.35:    col = C_ROCK_HI
                    elif light > 0.05:  col = C_ROCK_MID
                    elif light > -0.35: col = C_ROCK_DARK
                    elif light > -0.65: col = C_SHADOW
                    else:               col = C_CREVICE
                    w32.putpixel((x, y), col)
                elif d <= 1.35:
                    curr = w32.getpixel((x, y))
                    if curr[3] == 0 or curr in [C_SHADOW, C_ROCK_DARK]:
                        w32.putpixel((x, y), C_CREVICE)

    # Tier 1 boulder (top)
    draw_west_boulder(6.0, 5.0, 3.8, 4.5, 1)
    # Tier 2 boulder (seam straddler: cy=16, perfectly spans row 15 of top and row 0 of bot!)
    draw_west_boulder(6.2, 15.5, 4.0, 4.8, 2)
    # Tier 3 boulder (mid-lower)
    draw_west_boulder(5.8, 24.0, 3.8, 4.5, 3)
    # Tier 4 boulder (base)
    draw_west_boulder(5.5, 29.5, 3.5, 3.0, 4)

    # Upper Plateau Grass on the RIGHT (x >= 10)
    for y in range(32):
        # Grass edge wobbles between x=9 and x=11
        edge_x = 9 + int((math.sin(y * 0.9 + variant) + 1.0) * 0.8)
        for x in range(edge_x, 16):
            c = G_MID if (x + y) % 2 == 0 else G_LUSH
            if (x * 3 + y * 5) % 4 == 0: c = G_HI
            w32.putpixel((x, y), c)

        # Golden earth rim underneath grass edge
        w32.putpixel((edge_x - 1, y), C_LIP_HI if y % 2 == 0 else C_LIP_MID)
        w32.putpixel((edge_x, y), G_DARK if y % 3 != 0 else G_MID) # jagged blades

        # Occasional grass overhang blade tip poking onto the rock
        if y % 4 == 1:
            w32.putpixel((edge_x - 2, y), G_HI)
            w32.putpixel((edge_x - 1, y), G_MID)

    # Base grounding shadow on the LEFT edge (x=1..3) on lower rows (y=28..31)
    for y in range(28, 32):
        w32.putpixel((1, y), (20, 13, 6, 80))
        w32.putpixel((2, y), (20, 13, 6, 140))
        w32.putpixel((3, y), C_DARKEST)

    # Micro pebbles at base of west cliff (y=30..31, x=1..4)
    w32.putpixel((1, 30), P_SLATE); w32.putpixel((1, 31), P_SLATE_D)
    w32.putpixel((3, 31), P_DIRT)

    top = w32.crop((0, 0, 16, 16))
    bot = w32.crop((0, 16, 16, 32))
    return top, bot, w32


print("2. Crafting authentic, volumetric East-facing cliff side (32px)...")
# East-facing cliff wall runs North-South.
# Upper plateau is on the LEFT (x=0..5).
# The rock face drops to the EAST (right, x=6..13).
# Lowland is on the RIGHT (x=14..15).
# East face faces away from top-left light, so it has richer, deeper rock shadows!

def render_east_cliff_32(variant=1):
    w32 = Image.new('RGBA', (16, 32), (0, 0, 0, 0))

    # Base rock background on x=5..13
    for y in range(32):
        for x in range(5, 13):
            w32.putpixel((x, y), C_SHADOW)

    def draw_east_boulder(cx, cy, rx, ry, seed=0):
        for y in range(max(0, int(cy - ry - 2)), min(32, int(cy + ry + 3))):
            for x in range(max(5, int(cx - rx - 2)), min(14, int(cx + rx + 3))):
                dx = (x - cx) / float(rx)
                dy = (y - cy) / float(ry)
                angle = math.atan2(dy, dx)
                wobble = 1.0 + 0.12 * math.sin(angle * 3 + seed) + 0.08 * math.cos(angle * 4)
                d = (dx*dx + dy*dy) / (wobble * wobble)

                if d <= 1.0:
                    # Light from top-left: dx < 0 is light, but overall East face is in shade!
                    light = -0.55 * dx - 0.65 * dy
                    if light > 0.50:    col = C_ROCK_MID
                    elif light > 0.15:  col = C_ROCK_DARK
                    elif light > -0.25: col = C_SHADOW
                    else:               col = C_CREVICE
                    w32.putpixel((x, y), col)
                elif d <= 1.35:
                    curr = w32.getpixel((x, y))
                    if curr[3] == 0 or curr in [C_SHADOW, C_ROCK_DARK]:
                        w32.putpixel((x, y), C_CREVICE)

    draw_east_boulder(9.5, 5.0, 3.8, 4.5, 5)
    draw_east_boulder(9.8, 15.5, 4.0, 4.8, 6) # Straddles row 15/16!
    draw_east_boulder(9.5, 24.0, 3.8, 4.5, 7)
    draw_east_boulder(9.8, 29.5, 3.5, 3.0, 8)

    # Upper Plateau Grass on the LEFT (x <= 5)
    for y in range(32):
        edge_x = 5 + int((math.sin(y * 0.9 + variant) + 1.0) * 0.8)
        for x in range(0, edge_x):
            c = G_MID if (x + y) % 2 == 0 else G_LUSH
            if (x * 3 + y * 5) % 4 == 0: c = G_HI
            w32.putpixel((x, y), c)

        # Golden earth rim on east edge
        w32.putpixel((edge_x, y), C_LIP_HI if y % 2 == 0 else C_LIP_MID)
        w32.putpixel((edge_x - 1, y), G_DARK if y % 3 != 0 else G_MID)

        # Overhang blade tip
        if y % 4 == 2:
            w32.putpixel((edge_x + 1, y), G_HI)

    # Base grounding shadow on the RIGHT edge (x=13..15) on lower rows (y=28..31)
    for y in range(28, 32):
        w32.putpixel((13, y), C_DARKEST)
        w32.putpixel((14, y), (20, 13, 6, 140))
        w32.putpixel((15, y), (20, 13, 6, 80))

    # Micro pebbles on east base
    w32.putpixel((14, 30), P_SLATE); w32.putpixel((14, 31), P_SLATE_D)
    w32.putpixel((13, 31), P_DIRT)

    top = w32.crop((0, 0, 16, 16))
    bot = w32.crop((0, 16, 16, 32))
    return top, bot, w32


print("3. Crafting Outer Corners (SW, SE, NW, NE) 32px...")
# Southwest Outer Corner: South wall meets West wall!
# High ground is to the North-East!
# Low ground is to the South and West!
def render_sw_corner_32():
    w32 = Image.new('RGBA', (16, 32), (0, 0, 0, 0))
    # Rock fill
    for y in range(4, 29):
        for x in range(3, 16):
            w32.putpixel((x, y), C_SHADOW)

    # Rounded Corner Boulder
    # Top-mid corner boulder
    for y in range(3, 20):
        for x in range(2, 16):
            dx = (x - 7.5) / 5.5
            dy = (y - 12.0) / 6.0
            d = dx*dx + dy*dy
            if d <= 1.0:
                light = -0.7*dx - 0.7*dy
                col = C_ROCK_HI if light > 0.3 else (C_ROCK_MID if light > 0 else (C_ROCK_DARK if light > -0.3 else C_SHADOW))
                w32.putpixel((x, y), col)
            elif d <= 1.3:
                w32.putpixel((x, y), C_CREVICE)

    # Base corner boulder
    for y in range(16, 30):
        for x in range(2, 16):
            dx = (x - 7.0) / 5.2
            dy = (y - 24.0) / 5.0
            d = dx*dx + dy*dy
            if d <= 1.0:
                light = -0.7*dx - 0.7*dy
                col = C_ROCK_HI if light > 0.35 else (C_ROCK_MID if light > 0 else (C_ROCK_DARK if light > -0.3 else C_SHADOW))
                w32.putpixel((x, y), col)
            elif d <= 1.3:
                w32.putpixel((x, y), C_CREVICE)

    # Upper Grass Meadow curving in an arc (high ground at x >= 8, y <= 4)
    for y in range(6):
        for x in range(16):
            # Curved grass boundary
            dist_to_corner = math.sqrt((x - 16)**2 + (y - 0)**2)
            if dist_to_corner < 9.5:
                w32.putpixel((x, y), G_MID if (x + y) % 2 == 0 else G_LUSH)
            elif dist_to_corner < 11.0:
                w32.putpixel((x, y), C_LIP_HI if (x+y)%2==0 else C_LIP_MID)

    # Bottom ground contact shadow
    for x in range(16):
        w32.putpixel((x, 30), C_DARKEST)
        w32.putpixel((x, 31), (20, 13, 6, 120))
    for y in range(26, 32):
        w32.putpixel((1, y), (20, 13, 6, 80))
        w32.putpixel((2, y), (20, 13, 6, 140))

    # Micro pebbles
    w32.putpixel((2, 30), P_SLATE); w32.putpixel((2, 31), P_SLATE_D)
    w32.putpixel((4, 31), P_DIRT)

    top = w32.crop((0, 0, 16, 16))
    bot = w32.crop((0, 16, 16, 32))
    return top, bot, w32


# Southeast Outer Corner: South wall meets East wall!
# High ground is to the North-West!
# Low ground is to the South and East!
def render_se_corner_32():
    w32 = Image.new('RGBA', (16, 32), (0, 0, 0, 0))
    for y in range(4, 29):
        for x in range(0, 13):
            w32.putpixel((x, y), C_SHADOW)

    for y in range(3, 20):
        for x in range(0, 14):
            dx = (x - 8.0) / 5.5
            dy = (y - 12.0) / 6.0
            d = dx*dx + dy*dy
            if d <= 1.0:
                light = -0.5*dx - 0.7*dy
                col = C_ROCK_MID if light > 0.25 else (C_ROCK_DARK if light > -0.1 else C_SHADOW)
                w32.putpixel((x, y), col)
            elif d <= 1.3:
                w32.putpixel((x, y), C_CREVICE)

    for y in range(16, 30):
        for x in range(0, 14):
            dx = (x - 8.5) / 5.2
            dy = (y - 24.0) / 5.0
            d = dx*dx + dy*dy
            if d <= 1.0:
                light = -0.5*dx - 0.7*dy
                col = C_ROCK_MID if light > 0.25 else (C_ROCK_DARK if light > -0.1 else C_SHADOW)
                w32.putpixel((x, y), col)
            elif d <= 1.3:
                w32.putpixel((x, y), C_CREVICE)

    # Upper Grass Meadow curving in an arc (high ground at x <= 7, y <= 4)
    for y in range(6):
        for x in range(16):
            dist_to_corner = math.sqrt((x - 0)**2 + (y - 0)**2)
            if dist_to_corner < 8.5:
                w32.putpixel((x, y), G_MID if (x + y) % 2 == 0 else G_LUSH)
            elif dist_to_corner < 10.0:
                w32.putpixel((x, y), C_LIP_HI if (x+y)%2==0 else C_LIP_MID)

    for x in range(16):
        w32.putpixel((x, 30), C_DARKEST)
        w32.putpixel((x, 31), (20, 13, 6, 120))
    for y in range(26, 32):
        w32.putpixel((13, y), (20, 13, 6, 140))
        w32.putpixel((14, y), (20, 13, 6, 80))

    w32.putpixel((13, 30), P_SLATE); w32.putpixel((13, 31), P_SLATE_D)
    w32.putpixel((11, 31), P_DIRT)

    top = w32.crop((0, 0, 16, 16))
    bot = w32.crop((0, 16, 16, 32))
    return top, bot, w32


print("4. Crafting 100% Natural Earthen Mud Elevation Incline Ramps (NO STEPS, JUS MUD!)...")
# Natural Mud Elevation Ramp:
# A natural earthen incline cutting through the 32px cliff wall!
# Features:
# - Left Shoulder: Rock cliff tapering into sloping mud embankment
# - Center Mud Ramp (2-tile wide): Organic trodden mud slope with subtle horizontal earthen contour terraces / ridges
# - Right Shoulder: Rock cliff tapering into sloping mud embankment

def render_mud_ramp_left_32():
    # Left cliff shoulder meeting the mud ramp
    w32 = Image.new('RGBA', (16, 32), (0, 0, 0, 0))

    # Rock boulder on the left (x=0..9), sloping mud on the right (x=10..15)
    for y in range(32):
        # Mud takes over more width as we go towards the bottom!
        edge_x = 9 + int((y / 31.0) * 4) + int(math.sin(y * 0.8) * 0.8)
        # Mud surface on right
        for x in range(edge_x, 16):
            c = D_DIRT if (x + y) % 2 == 0 else (170, 110, 36, 255)
            # Gentle earthen incline ridges
            if y in (6, 14, 22, 29): c = D_LIGHT
            elif y in (7, 15, 23, 30): c = D_DARK
            w32.putpixel((x, y), c)

        # Rock face on left
        for x in range(0, edge_x):
            w32.putpixel((x, y), C_SHADOW)

    # Boulder body on left
    for y in range(4, 29):
        for x in range(0, 11):
            dx = (x - 4.5) / 5.0
            dy = (y - 16.0) / 11.0
            if dx*dx + dy*dy <= 1.0:
                light = -0.7*dx - 0.6*dy
                col = C_ROCK_HI if light > 0.3 else (C_ROCK_MID if light > 0 else (C_ROCK_DARK if light > -0.3 else C_SHADOW))
                w32.putpixel((x, y), col)

    # Edge between rock and mud: ragged earth embankment & shadow
    for y in range(32):
        edge_x = 9 + int((y / 31.0) * 4) + int(math.sin(y * 0.8) * 0.8)
        w32.putpixel((edge_x - 1, y), C_DARKEST)
        w32.putpixel((edge_x, y), D_DARK)
        if y % 5 == 2:
            w32.putpixel((edge_x + 1, y), P_SLATE) # tiny trail pebble

    # Upper grass meadow on top-left (y <= 3, x <= 8)
    for y in range(4):
        for x in range(9 - y*2):
            w32.putpixel((x, y), G_MID if (x+y)%2==0 else G_LUSH)
        if 9 - y*2 > 0:
            w32.putpixel((9 - y*2, y), C_LIP_HI)

    top = w32.crop((0, 0, 16, 16))
    bot = w32.crop((0, 16, 16, 32))
    return top, bot, w32


def render_mud_ramp_right_32():
    # Right cliff shoulder meeting the mud ramp
    w32 = Image.new('RGBA', (16, 32), (0, 0, 0, 0))

    for y in range(32):
        # Mud on left (x=0..edge_x), rock on right (x=edge_x..15)
        edge_x = 6 - int((y / 31.0) * 4) + int(math.sin(y * 0.8) * 0.8)
        edge_x = max(0, edge_x)
        for x in range(0, edge_x):
            c = D_DIRT if (x + y) % 2 == 0 else (170, 110, 36, 255)
            if y in (6, 14, 22, 29): c = D_LIGHT
            elif y in (7, 15, 23, 30): c = D_DARK
            w32.putpixel((x, y), c)

        for x in range(edge_x, 16):
            w32.putpixel((x, y), C_SHADOW)

    for y in range(4, 29):
        for x in range(4, 16):
            dx = (x - 11.5) / 5.0
            dy = (y - 16.0) / 11.0
            if dx*dx + dy*dy <= 1.0:
                light = -0.5*dx - 0.7*dy
                col = C_ROCK_MID if light > 0.2 else (C_ROCK_DARK if light > -0.1 else C_SHADOW)
                w32.putpixel((x, y), col)

    for y in range(32):
        edge_x = 6 - int((y / 31.0) * 4) + int(math.sin(y * 0.8) * 0.8)
        edge_x = max(0, edge_x)
        w32.putpixel((edge_x, y), D_DARK)
        if edge_x + 1 < 16:
            w32.putpixel((edge_x + 1, y), C_DARKEST)
        if y % 5 == 3 and edge_x > 0:
            w32.putpixel((edge_x - 1, y), P_DIRT)

    for y in range(4):
        for x in range(7 + y*2, 16):
            w32.putpixel((x, y), G_MID if (x+y)%2==0 else G_LUSH)
        if 7 + y*2 < 16:
            w32.putpixel((7 + y*2 - 1, y), C_LIP_HI)

    top = w32.crop((0, 0, 16, 16))
    bot = w32.crop((0, 16, 16, 32))
    return top, bot, w32


def render_mud_ramp_center_32(variant=1):
    # 100% Pure Natural Mud Elevation Slope Surface!
    # Organic island earth with natural slope terrace ridges, trodden path grooves, and trail gravel!
    w32 = Image.new('RGBA', (16, 32), (0, 0, 0, 0))

    # Base mud field
    for y in range(32):
        for x in range(16):
            # Rich organic earth variation
            n = (x * 7 + y * 13 + variant * 17) % 6
            if n == 0:   col = (185, 125, 45, 255)
            elif n == 1: col = D_DIRT
            elif n == 2: col = (168, 110, 35, 255)
            elif n == 3: col = D_DARK
            else:        col = (174, 115, 38, 255)
            w32.putpixel((x, y), col)

    # 4 Subtle Horizontal Incline Terraces / Trodden Soil Contours (cy = 6, 14, 22, 29)
    # These organic ridges give clear visual feedback of climbing upwards!
    for cy in [6, 14, 22, 29]:
        # Sunlit crest on top edge
        for x in range(16):
            wobble = int(math.sin(x * 0.7 + cy) * 0.8)
            ry = cy + wobble
            if 0 <= ry < 32:
                w32.putpixel((x, ry), D_LIGHT if (x + cy) % 2 == 0 else D_HI)
            if 0 <= ry + 1 < 32:
                w32.putpixel((x, ry + 1), D_DARK if x % 3 != 0 else D_DEEP)

    # Natural foot-trodden trail ruts / worn path depressions running slightly vertically
    for y in range(32):
        rut_x1 = 4 + int(math.sin(y * 0.3) * 1.2)
        rut_x2 = 11 + int(math.cos(y * 0.3) * 1.2)
        if 0 <= rut_x1 < 16:
            w32.putpixel((rut_x1, y), D_DARK)
        if 0 <= rut_x2 < 16:
            w32.putpixel((rut_x2, y), D_DARK)

    # A few natural embedded small pebbles along the mud slope
    pebbles = [(3, 8, P_SLATE), (12, 11, P_DIRT), (5, 18, P_DIRT), (10, 25, P_SLATE), (7, 28, P_DIRT)]
    for px, py, pcol in pebbles:
        w32.putpixel((px, py), pcol)
        if py + 1 < 32:
            w32.putpixel((px, py + 1), D_DEEP) # pebble shadow

    top = w32.crop((0, 0, 16, 16))
    bot = w32.crop((0, 16, 16, 32))
    return top, bot, w32


# Generate and save all new authentic assets
print("Saving all assets to Assets/Art/Terrain/Cliffs...")

# 1. West Cliff Sides
w_top, w_bot, w_full = render_west_cliff_32(1)
w_top.save(os.path.join(CLIFFS_DIR, 'cliff_side_w_top.png'))
w_bot.save(os.path.join(CLIFFS_DIR, 'cliff_side_w_bot.png'))
w_top.save(os.path.join(CLIFFS_DIR, 'cliff_side_w.png')) # 1-tile legacy compatibility

# 2. East Cliff Sides
e_top, e_bot, e_full = render_east_cliff_32(1)
e_top.save(os.path.join(CLIFFS_DIR, 'cliff_side_e_top.png'))
e_bot.save(os.path.join(CLIFFS_DIR, 'cliff_side_e_bot.png'))
e_top.save(os.path.join(CLIFFS_DIR, 'cliff_side_e.png'))

# 3. Outer Corners
sw_top, sw_bot, sw_full = render_sw_corner_32()
sw_top.save(os.path.join(CLIFFS_DIR, 'cliff_corner_sw_top.png'))
sw_bot.save(os.path.join(CLIFFS_DIR, 'cliff_corner_sw_bot.png'))
sw_top.save(os.path.join(CLIFFS_DIR, 'cliff_outer_tl_top.png')) # Map outer_tl to SW corner

se_top, se_bot, se_full = render_se_corner_32()
se_top.save(os.path.join(CLIFFS_DIR, 'cliff_corner_se_top.png'))
se_bot.save(os.path.join(CLIFFS_DIR, 'cliff_corner_se_bot.png'))
se_top.save(os.path.join(CLIFFS_DIR, 'cliff_outer_tr_top.png')) # Map outer_tr to SE corner

# 4. Natural Mud Elevation Ramps
mrl_top, mrl_bot, mrl_full = render_mud_ramp_left_32()
mrl_top.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_left_top.png'))
mrl_bot.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_left_bot.png'))

mrr_top, mrr_bot, mrr_full = render_mud_ramp_right_32()
mrr_top.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_right_top.png'))
mrr_bot.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_right_bot.png'))

mrc_top, mrc_bot, mrc_full = render_mud_ramp_center_32(1)
mrc_top.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_mid_top.png'))
mrc_bot.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_mid_bot.png'))
mrc_top.save(os.path.join(CLIFFS_DIR, 'cliff_mud_slope_top.png'))
mrc_bot.save(os.path.join(CLIFFS_DIR, 'cliff_mud_slope_bot.png'))

print("Generating Unity Metas...")
def make_meta(png_name):
    meta_path = os.path.join(CLIFFS_DIR, png_name + '.meta')
    guid = uuid.uuid4().hex
    meta_content = """fileFormatVersion: 2
guid: """ + guid + """
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {}
  serializedVersion: 13
  mipmaps:
    mipMapMode: 0
    enableMipMap: 0
    sRGBTexture: 1
    linearTexture: 0
    fadeOut: 0
    borderMipMap: 0
    mipMapsPreserveCoverage: 0
    alphaTestReferenceValue: 0.5
    mipMapFadeDistanceStart: 1
    mipMapFadeDistanceEnd: 3
  bumpmap:
    convertToNormalMap: 0
    externalNormalMap: 0
    heightScale: 0.25
    normalMapFilter: 0
    flipGreenChannel: 0
  isReadable: 0
  streamingMipmaps: 0
  streamingMipmapsPriority: 0
  vTOnly: 0
  ignoreMasterTextureLimit: 0
  doesTextureContainColorSpaceInformation: 0
  grayScaleToAlpha: 0
  generateCubemap: 6
  cubemapConvolution: 0
  seamlessCubemap: 0
  textureFormat: 1
  maxTextureSize: 2048
  textureSettings:
    serializedVersion: 2
    filterMode: 0
    aniso: 1
    mipBias: 0
    wrapU: 1
    wrapV: 1
    wrapW: 1
  nPOTScale: 0
  lightmap: 0
  compressionQuality: 50
  spriteMode: 1
  spriteExtrude: 1
  spriteMeshType: 1
  alignment: 0
  spritePivot: {x: 0.5, y: 0.5}
  spritePixelsToUnits: 16
  spriteBorder: {x: 0, y: 0, z: 0, w: 0}
  spriteGenerateFallbackPhysicsShape: 1
  alphaIsTransparency: 1
  spriteColliderType: 1
  editorTextureFormat: 0
"""
    if not os.path.exists(meta_path):
        with open(meta_path, 'w', encoding='utf-8') as f:
            f.write(meta_content)

for fname in os.listdir(CLIFFS_DIR):
    if fname.endswith('.png'):
        make_meta(fname)

print("All cliff sides and mud ramp assets crafted and metas verified!")
