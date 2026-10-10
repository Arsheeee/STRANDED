import os
import math
import uuid
from PIL import Image

CLIFFS_DIR = r'd:\Unity\Projects\STRANDED\Assets\Art\Terrain\Cliffs'
GRASS_DIR  = r'd:\Unity\Projects\STRANDED\Assets\Art\Terrain\Grass'
DIRT_DIR   = r'd:\Unity\Projects\STRANDED\Assets\Art\Terrain\Dirt'
BRAIN_DIR  = r'C:\Users\PAVILION\.gemini\antigravity-ide\brain\84db0e2d-58d2-466d-be05-dbff8f133035'

# Palette
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

# Mud Colors
D_DIRT      = (179, 119, 41, 255)  # Mud base (#b37729)
D_DARK      = (145, 78, 12, 255)   # Mud shadow / groove (#914e0c)
D_DEEP      = (110, 55, 10, 255)   # Deep mud crevice (#6e370a)
D_LIGHT     = (205, 145, 55, 255)  # Sunlit mud crest (#cd9137)

# Micro Pebbles
P_SLATE     = (125, 140, 128, 255) # Slate pebble (#7d8c80)
P_SLATE_D   = (78, 92, 82, 255)
P_DIRT      = (160, 120, 50, 255)  # Earth pebble
P_DIRT_D    = (100, 70, 25, 255)

mud_tile   = Image.open(os.path.join(DIRT_DIR, 'mud_base_01.png')).convert('RGBA')
grass_tile = Image.open(os.path.join(GRASS_DIR, 'grass_base_01.png')).convert('RGBA')

# -------------------------------------------------------------
# 1. PERFECT SEAMLESS WEST-FACING CLIFF WALL (32px high)
# -------------------------------------------------------------
# Top tile (16x16) and Bot tile (16x16)
# Geometry specification:
# - Columns 10..15: Level 1 grass meadow!
# - Column 9: Grass overhang blades (G_DARK, G_MID, with tips on col 8)
# - Column 8: Golden rim lip (C_LIP_HI, C_LIP_MID)
# - Columns 2..7: Volumetric rock boulder face!
# - Columns 0..1: Lowland terrain / base shadow.
def build_seamless_west_cliff():
    w32 = Image.new('RGBA', (16, 32), (0, 0, 0, 0))

    # Grass meadow on columns 10..15
    for y in range(32):
        for x in range(10, 16):
            w32.putpixel((x, y), grass_tile.getpixel((x, y % 16)))

    # Golden rim on col 8, grass edge on col 9
    for y in range(32):
        w32.putpixel((8, y), C_LIP_HI if y % 2 == 0 else C_LIP_MID)
        w32.putpixel((9, y), G_DARK if y % 3 != 0 else G_MID)
        # Jagged blade tips poking to x=7
        if y % 4 == 1:
            w32.putpixel((7, y), G_HI)
        elif y % 4 == 3:
            w32.putpixel((7, y), G_LUSH)

    # Rock boulder fill on columns 2..7 (with base shadow)
    for y in range(32):
        for x in range(2, 8):
            w32.putpixel((x, y), C_SHADOW)

    # Draw rounded chunky boulders along x=4.8
    # Boulder 1: cy=6.0
    # Boulder 2 (straddler): cy=16.0 (perfectly bridges row 15 of top and row 0 of bot!)
    # Boulder 3: cy=25.5
    def draw_boulder(cy, ry):
        for y in range(max(0, int(cy - ry - 2)), min(32, int(cy + ry + 3))):
            for x in range(2, 9):
                dx = (x - 4.8) / 3.2
                dy = (y - cy) / float(ry)
                d = dx*dx + dy*dy
                if d <= 1.0:
                    light = -0.75 * dx - 0.55 * dy
                    if light > 0.35:    col = C_ROCK_HI
                    elif light > 0.05:  col = C_ROCK_MID
                    elif light > -0.35: col = C_ROCK_DARK
                    elif light > -0.65: col = C_SHADOW
                    else:               col = C_CREVICE
                    w32.putpixel((x, y), col)
                elif d <= 1.3:
                    if w32.getpixel((x, y)) in [C_SHADOW, C_ROCK_DARK]:
                        w32.putpixel((x, y), C_CREVICE)

    draw_boulder(6.0, 4.5)
    draw_boulder(16.0, 5.0)
    draw_boulder(25.5, 4.5)

    # Base shelf and grounding shadow on bottom rows (y=28..31, x=0..2)
    for y in range(28, 32):
        w32.putpixel((0, y), (20, 13, 6, 70))
        w32.putpixel((1, y), (20, 13, 6, 140))
        w32.putpixel((2, y), C_DARKEST)

    # Micro pebbles at base
    w32.putpixel((0, 30), P_SLATE); w32.putpixel((0, 31), P_SLATE_D)
    w32.putpixel((2, 31), P_DIRT)

    top = w32.crop((0, 0, 16, 16))
    bot = w32.crop((0, 16, 16, 32))
    return top, bot


# -------------------------------------------------------------
# 2. PERFECT SEAMLESS EAST-FACING CLIFF WALL (32px high)
# -------------------------------------------------------------
# - Columns 0..5: Level 1 grass meadow!
# - Column 6: Grass overhang blades (G_DARK, G_MID)
# - Column 7: Golden rim lip (C_LIP_HI, C_LIP_MID)
# - Columns 8..13: Volumetric rock boulder face!
# - Columns 14..15: Lowland terrain / base shadow.
def build_seamless_east_cliff():
    w32 = Image.new('RGBA', (16, 32), (0, 0, 0, 0))

    for y in range(32):
        for x in range(0, 6):
            w32.putpixel((x, y), grass_tile.getpixel((x, y % 16)))

    for y in range(32):
        w32.putpixel((7, y), C_LIP_HI if y % 2 == 0 else C_LIP_MID)
        w32.putpixel((6, y), G_DARK if y % 3 != 0 else G_MID)
        if y % 4 == 2:
            w32.putpixel((8, y), G_HI)
        elif y % 4 == 0:
            w32.putpixel((8, y), G_LUSH)

    for y in range(32):
        for x in range(8, 14):
            w32.putpixel((x, y), C_SHADOW)

    def draw_boulder(cy, ry):
        for y in range(max(0, int(cy - ry - 2)), min(32, int(cy + ry + 3))):
            for x in range(7, 14):
                dx = (x - 10.2) / 3.2
                dy = (y - cy) / float(ry)
                d = dx*dx + dy*dy
                if d <= 1.0:
                    light = -0.55 * dx - 0.65 * dy
                    if light > 0.45:    col = C_ROCK_MID
                    elif light > 0.10:  col = C_ROCK_DARK
                    elif light > -0.30: col = C_SHADOW
                    else:               col = C_CREVICE
                    w32.putpixel((x, y), col)
                elif d <= 1.3:
                    if w32.getpixel((x, y)) in [C_SHADOW, C_ROCK_DARK]:
                        w32.putpixel((x, y), C_CREVICE)

    draw_boulder(6.0, 4.5)
    draw_boulder(16.0, 5.0)
    draw_boulder(25.5, 4.5)

    for y in range(28, 32):
        w32.putpixel((13, y), C_DARKEST)
        w32.putpixel((14, y), (20, 13, 6, 140))
        w32.putpixel((15, y), (20, 13, 6, 70))

    w32.putpixel((14, 30), P_SLATE); w32.putpixel((14, 31), P_SLATE_D)
    w32.putpixel((13, 31), P_DIRT)

    top = w32.crop((0, 0, 16, 16))
    bot = w32.crop((0, 16, 16, 32))
    return top, bot


# -------------------------------------------------------------
# 3. SEAMLESS SOUTHWEST OUTER CORNER (SW_TOP & SW_BOT)
# -------------------------------------------------------------
# Turns from West-facing cliff (on north) to South-facing cliff (on east)!
# - Top edge (y=0) matches West-facing cliff bot tile (x=0..1 low, x=2..7 rock, x=8 lip, x=9 overhang, x=10..15 grass)!
# - Right edge (x=15) matches South-facing cliff top tile (y=0..3 grass, y=4 overhang, y=5 lip, y=6..15 rock)!
def build_seamless_sw_corner():
    top = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    bot = Image.new('RGBA', (16, 16), (0, 0, 0, 0))

    # --- TOP TILE ---
    # Fill base shadow for rock zone
    for y in range(16):
        for x in range(16):
            top.putpixel((x, y), C_SHADOW)

    # Large corner boulder bulging out from top-left towards bottom-right
    for y in range(16):
        for x in range(16):
            # Center of corner boulder at (5.5, 11.5)
            dx = (x - 6.0) / 5.5
            dy = (y - 10.5) / 5.5
            d = dx*dx + dy*dy
            if d <= 1.0:
                light = -0.7*dx - 0.7*dy
                col = C_ROCK_HI if light > 0.35 else (C_ROCK_MID if light > 0.05 else (C_ROCK_DARK if light > -0.35 else C_SHADOW))
                top.putpixel((x, y), col)
            elif d <= 1.3:
                top.putpixel((x, y), C_CREVICE)

    # Curved grass boundary from top edge (x=9.5, y=0) to right edge (x=15, y=4.5)
    # Circle center at (15, 0)
    for y in range(16):
        for x in range(16):
            dist = math.sqrt((x - 15.5)**2 + (y - 0.0)**2)
            if dist < 6.0:
                # Pure grass
                top.putpixel((x, y), grass_tile.getpixel((x, y)))
            elif dist < 7.2:
                # Golden lip
                top.putpixel((x, y), C_LIP_HI if (x+y)%2==0 else C_LIP_MID)
            elif dist < 8.2:
                # Overhang blades
                if (x*7 + y*13) % 3 == 0:
                    top.putpixel((x, y), G_HI)
                elif (x*7 + y*13) % 3 == 1:
                    top.putpixel((x, y), G_MID)

    # Strict boundary enforcement at y=0 (top edge):
    top.putpixel((8, 0), C_LIP_HI)
    top.putpixel((9, 0), G_DARK)
    for x in range(10, 16):
        top.putpixel((x, 0), grass_tile.getpixel((x, 0)))

    # Strict boundary enforcement at x=15 (right edge):
    for y in range(4):
        top.putpixel((15, y), grass_tile.getpixel((15, y)))
    top.putpixel((15, 4), G_DARK)
    top.putpixel((15, 5), C_LIP_HI)

    # Lowland transparent area on top-left (x <= 1, y <= 5)
    for y in range(6):
        top.putpixel((0, y), (0, 0, 0, 0))
        top.putpixel((1, y), (0, 0, 0, 0))

    # --- BOT TILE ---
    for y in range(16):
        for x in range(16):
            bot.putpixel((x, y), C_SHADOW)

    for y in range(16):
        for x in range(16):
            dx = (x - 6.5) / 5.5
            dy = (y - 6.5) / 5.5
            d = dx*dx + dy*dy
            if d <= 1.0:
                light = -0.7*dx - 0.7*dy
                col = C_ROCK_HI if light > 0.35 else (C_ROCK_MID if light > 0.05 else (C_ROCK_DARK if light > -0.35 else C_SHADOW))
                bot.putpixel((x, y), col)
            elif d <= 1.3:
                bot.putpixel((x, y), C_CREVICE)

    # Base grounding shadow on bottom (y=13..15) and left (x=0..2)
    for x in range(16):
        bot.putpixel((x, 14), C_DARKEST)
        bot.putpixel((x, 15), (20, 13, 6, 120))
    for y in range(16):
        bot.putpixel((0, y), (20, 13, 6, 70))
        bot.putpixel((1, y), (20, 13, 6, 140))
        bot.putpixel((2, y), C_DARKEST)

    # Corner micro pebbles
    bot.putpixel((1, 14), P_SLATE); bot.putpixel((1, 15), P_SLATE_D)
    bot.putpixel((4, 15), P_DIRT)

    return top, bot


# -------------------------------------------------------------
# 4. SEAMLESS SOUTHEAST OUTER CORNER (SE_TOP & SE_BOT)
# -------------------------------------------------------------
# Turns from South-facing cliff (on west) to East-facing cliff (on north)!
# - Left edge (x=0) matches South cliff top tile (y=0..3 grass, y=4 overhang, y=5 lip, y=6..15 rock)!
# - Top edge (y=0) matches East cliff bot tile (x=0..5 grass, x=6 overhang, x=7 lip, x=8..13 rock, x=14..15 low)!
def build_seamless_se_corner():
    top = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    bot = Image.new('RGBA', (16, 16), (0, 0, 0, 0))

    # --- TOP TILE ---
    for y in range(16):
        for x in range(16):
            top.putpixel((x, y), C_SHADOW)

    for y in range(16):
        for x in range(16):
            dx = (x - 9.5) / 5.5
            dy = (y - 10.5) / 5.5
            d = dx*dx + dy*dy
            if d <= 1.0:
                light = -0.55*dx - 0.7*dy
                col = C_ROCK_MID if light > 0.25 else (C_ROCK_DARK if light > -0.1 else C_SHADOW)
                top.putpixel((x, y), col)
            elif d <= 1.3:
                top.putpixel((x, y), C_CREVICE)

    # Grass arc centered at (0, 0)
    for y in range(16):
        for x in range(16):
            dist = math.sqrt((x - 0.0)**2 + (y - 0.0)**2)
            if dist < 6.0:
                top.putpixel((x, y), grass_tile.getpixel((x, y)))
            elif dist < 7.2:
                top.putpixel((x, y), C_LIP_HI if (x+y)%2==0 else C_LIP_MID)
            elif dist < 8.2:
                if (x*7 + y*13) % 3 == 0:
                    top.putpixel((x, y), G_HI)
                elif (x*7 + y*13) % 3 == 1:
                    top.putpixel((x, y), G_MID)

    # Strict top boundary enforcement (y=0):
    for x in range(0, 6):
        top.putpixel((x, 0), grass_tile.getpixel((x, 0)))
    top.putpixel((6, 0), G_DARK)
    top.putpixel((7, 0), C_LIP_HI)

    # Strict left boundary enforcement (x=0):
    for y in range(4):
        top.putpixel((0, y), grass_tile.getpixel((0, y)))
    top.putpixel((0, 4), G_DARK)
    top.putpixel((0, 5), C_LIP_HI)

    # Transparent on top-right (x >= 14, y <= 5)
    for y in range(6):
        top.putpixel((14, y), (0, 0, 0, 0))
        top.putpixel((15, y), (0, 0, 0, 0))

    # --- BOT TILE ---
    for y in range(16):
        for x in range(16):
            bot.putpixel((x, y), C_SHADOW)

    for y in range(16):
        for x in range(16):
            dx = (x - 9.0) / 5.5
            dy = (y - 6.5) / 5.5
            d = dx*dx + dy*dy
            if d <= 1.0:
                light = -0.55*dx - 0.7*dy
                col = C_ROCK_MID if light > 0.25 else (C_ROCK_DARK if light > -0.1 else C_SHADOW)
                bot.putpixel((x, y), col)
            elif d <= 1.3:
                bot.putpixel((x, y), C_CREVICE)

    for x in range(16):
        bot.putpixel((x, 14), C_DARKEST)
        bot.putpixel((x, 15), (20, 13, 6, 120))
    for y in range(16):
        bot.putpixel((13, y), C_DARKEST)
        bot.putpixel((14, y), (20, 13, 6, 140))
        bot.putpixel((15, y), (20, 13, 6, 70))

    bot.putpixel((14, 14), P_SLATE); bot.putpixel((14, 15), P_SLATE_D)
    bot.putpixel((11, 15), P_DIRT)

    return top, bot


# -------------------------------------------------------------
# 5. NATURAL MUD RAMP SHOULDERS (NO STEPS, JUS MUD!)
# -------------------------------------------------------------
def build_seamless_mud_ramp_shoulders():
    # Left Ramp Shoulder (16x32)
    # Left side (x=0..9): South-facing rock cliff with rounded end-cap boulder.
    # Right side (x=10..15): 100% natural mud from mud_base_01.png!
    l32 = Image.new('RGBA', (16, 32), (0, 0, 0, 0))
    # Fill entire right side with genuine mud_base_01.png pixels!
    for y in range(32):
        for x in range(16):
            l32.putpixel((x, y), mud_tile.getpixel((x, y % 16)))

    for y in range(3, 29):
        for x in range(0, 9):
            l32.putpixel((x, y), C_SHADOW)

    # End-cap boulder on the left
    def draw_l_end(cy, ry):
        for y in range(max(0, int(cy - ry - 2)), min(32, int(cy + ry + 3))):
            for x in range(0, 10):
                dx = (x - 3.8) / 4.8
                dy = (y - cy) / float(ry)
                if dx*dx + dy*dy <= 1.0:
                    light = -0.7*dx - 0.7*dy
                    col = C_ROCK_HI if light > 0.35 else (C_ROCK_MID if light > 0.05 else (C_ROCK_DARK if light > -0.35 else C_SHADOW))
                    l32.putpixel((x, y), col)
                elif dx*dx + dy*dy <= 1.3:
                    l32.putpixel((x, y), C_CREVICE)

    draw_l_end(10.0, 5.5)
    draw_l_end(17.0, 5.5) # Straddles top/bot boundary!
    draw_l_end(24.5, 5.5)

    # Upper grass on top-left (y <= 3) curving back into mud
    for y in range(4):
        for x in range(8 - y):
            l32.putpixel((x, y), grass_tile.getpixel((x, y)))
        l32.putpixel((8 - y, y), G_DARK)
        l32.putpixel((9 - y, y), C_LIP_HI)

    # Ragged contact line between rock and mud on x=8..9
    for y in range(4, 30):
        cx = 8 + int(math.sin(y * 0.7) * 0.7)
        l32.putpixel((cx, y), C_DARKEST)
        l32.putpixel((cx + 1, y), D_DARK)
        if y % 6 == 3:
            l32.putpixel((cx + 2, y), P_SLATE) # tiny natural pebble on the mud

    # Base contact shadow at bottom
    for x in range(9):
        l32.putpixel((x, 30), C_DARKEST)
        l32.putpixel((x, 31), (20, 13, 6, 120))

    l_top = l32.crop((0, 0, 16, 16))
    l_bot = l32.crop((0, 16, 16, 32))

    # Right Ramp Shoulder (16x32)
    # Left side (x=0..5): 100% natural mud from mud_base_01.png!
    # Right side (x=6..15): South-facing rock cliff with rounded end-cap boulder.
    r32 = Image.new('RGBA', (16, 32), (0, 0, 0, 0))
    for y in range(32):
        for x in range(16):
            r32.putpixel((x, y), mud_tile.getpixel((x, y % 16)))

    for y in range(3, 29):
        for x in range(7, 16):
            r32.putpixel((x, y), C_SHADOW)

    def draw_r_end(cy, ry):
        for y in range(max(0, int(cy - ry - 2)), min(32, int(cy + ry + 3))):
            for x in range(6, 16):
                dx = (x - 12.2) / 4.8
                dy = (y - cy) / float(ry)
                if dx*dx + dy*dy <= 1.0:
                    light = -0.55*dx - 0.7*dy
                    col = C_ROCK_MID if light > 0.25 else (C_ROCK_DARK if light > -0.1 else C_SHADOW)
                    r32.putpixel((x, y), col)
                elif dx*dx + dy*dy <= 1.3:
                    r32.putpixel((x, y), C_CREVICE)

    draw_r_end(10.0, 5.5)
    draw_r_end(17.0, 5.5)
    draw_r_end(24.5, 5.5)

    for y in range(4):
        for x in range(8 + y, 16):
            r32.putpixel((x, y), grass_tile.getpixel((x, y)))
        r32.putpixel((7 + y, y), G_DARK)
        r32.putpixel((6 + y, y), C_LIP_HI)

    for y in range(4, 30):
        cx = 7 - int(math.sin(y * 0.7) * 0.7)
        r32.putpixel((cx, y), C_DARKEST)
        r32.putpixel((cx - 1, y), D_DARK)
        if y % 6 == 4 and cx - 2 >= 0:
            r32.putpixel((cx - 2, y), P_DIRT)

    for x in range(7, 16):
        r32.putpixel((x, 30), C_DARKEST)
        r32.putpixel((x, 31), (20, 13, 6, 120))

    r_top = r32.crop((0, 0, 16, 16))
    r_bot = r32.crop((0, 16, 16, 32))

    return l_top, l_bot, r_top, r_bot


print("Generating updated seamless assets...")
w_top, w_bot = build_seamless_west_cliff()
w_top.save(os.path.join(CLIFFS_DIR, 'cliff_side_w_top.png'))
w_bot.save(os.path.join(CLIFFS_DIR, 'cliff_side_w_bot.png'))
w_top.save(os.path.join(CLIFFS_DIR, 'cliff_side_w.png'))

e_top, e_bot = build_seamless_east_cliff()
e_top.save(os.path.join(CLIFFS_DIR, 'cliff_side_e_top.png'))
e_bot.save(os.path.join(CLIFFS_DIR, 'cliff_side_e_bot.png'))
e_top.save(os.path.join(CLIFFS_DIR, 'cliff_side_e.png'))

sw_top, sw_bot = build_seamless_sw_corner()
sw_top.save(os.path.join(CLIFFS_DIR, 'cliff_corner_sw_top.png'))
sw_bot.save(os.path.join(CLIFFS_DIR, 'cliff_corner_sw_bot.png'))
sw_top.save(os.path.join(CLIFFS_DIR, 'cliff_outer_tl_top.png'))

se_top, se_bot = build_seamless_se_corner()
se_top.save(os.path.join(CLIFFS_DIR, 'cliff_corner_se_top.png'))
se_bot.save(os.path.join(CLIFFS_DIR, 'cliff_corner_se_bot.png'))
se_top.save(os.path.join(CLIFFS_DIR, 'cliff_outer_tr_top.png'))

rl_top, rl_bot, rr_top, rr_bot = build_seamless_mud_ramp_shoulders()
rl_top.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_left_top.png'))
rl_bot.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_left_bot.png'))
rr_top.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_right_top.png'))
rr_bot.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_right_bot.png'))

# Mud passage is pure natural mud_base_01.png!
mud_tile.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_mid_top.png'))
mud_tile.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_mid_bot.png'))
mud_tile.save(os.path.join(CLIFFS_DIR, 'cliff_mud_slope_top.png'))
mud_tile.save(os.path.join(CLIFFS_DIR, 'cliff_mud_slope_bot.png'))

print("All seamless assets saved!")
