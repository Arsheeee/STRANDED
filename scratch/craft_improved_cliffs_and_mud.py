import os
import math
import uuid
from PIL import Image, ImageDraw

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

# Natural Mud / Dirt (Matching mud_base_01.png)
D_DIRT      = (179, 119, 41, 255)  # Mud base (#b37729)
D_DARK      = (145, 78, 12, 255)   # Mud shadow / groove (#914e0c)
D_DEEP      = (110, 55, 10, 255)   # Deep mud crevice (#6e370a)
D_LIGHT     = (205, 145, 55, 255)  # Sunlit mud crest (#cd9137)

# Micro Pebbles
P_SLATE     = (125, 140, 128, 255) # Slate pebble (#7d8c80)
P_SLATE_D   = (78, 92, 82, 255)
P_DIRT      = (160, 120, 50, 255)  # Earth pebble
P_DIRT_D    = (100, 70, 25, 255)

mud_tile = Image.open(os.path.join(DIRT_DIR, 'mud_base_01.png')).convert('RGBA')

print("1. Crafting chunky, volumetric West-facing cliff wall (32px)...")
# High ground is to the EAST (x >= 9). Sheer rock face drops to the WEST (x=2..8).
def render_west_cliff_32():
    w32 = Image.new('RGBA', (16, 32), (0, 0, 0, 0))

    # Fill base shadow for rock zone x=1..9
    for y in range(32):
        for x in range(1, 10):
            w32.putpixel((x, y), C_SHADOW)

    # Draw rounded chunky boulders running vertically
    # Boulders centered along x=5.5, with radii rx=4.2, ry=4.5
    def draw_west_boulder(cx, cy, rx, ry, seed=0):
        for y in range(max(0, int(cy - ry - 2)), min(32, int(cy + ry + 3))):
            for x in range(max(1, int(cx - rx - 2)), min(11, int(cx + rx + 3))):
                dx = (x - cx) / float(rx)
                dy = (y - cy) / float(ry)
                angle = math.atan2(dy, dx)
                wobble = 1.0 + 0.12 * math.sin(angle * 3 + seed) + 0.08 * math.cos(angle * 4)
                d = (dx*dx + dy*dy) / (wobble * wobble)

                if d <= 1.0:
                    light = -0.75 * dx - 0.55 * dy
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

    # 3 Boulder tiers over 32px height
    draw_west_boulder(5.5, 5.5, 4.2, 4.8, 1)
    draw_west_boulder(5.8, 15.5, 4.4, 5.0, 2) # Perfectly straddles top/bot boundary!
    draw_west_boulder(5.5, 25.5, 4.2, 4.8, 3)

    # Upper Plateau Grass on the RIGHT (x >= 9)
    for y in range(32):
        edge_x = 9 + int((math.sin(y * 0.9) + 1.0) * 0.7)
        for x in range(edge_x, 16):
            c = G_MID if (x + y) % 2 == 0 else G_LUSH
            if (x * 3 + y * 5) % 4 == 0: c = G_HI
            w32.putpixel((x, y), c)

        # Golden earth rim
        w32.putpixel((edge_x - 1, y), C_LIP_HI if y % 2 == 0 else C_LIP_MID)
        w32.putpixel((edge_x, y), G_DARK if y % 3 != 0 else G_MID)

        # Ragged grass overhang tips
        if y % 4 == 1:
            w32.putpixel((edge_x - 2, y), G_HI)
            w32.putpixel((edge_x - 1, y), G_MID)
        elif y % 4 == 3:
            w32.putpixel((edge_x - 2, y), G_LUSH)

    # Base grounding shadow on the LEFT edge (x=0..2) on bottom rows (y=27..31)
    for y in range(27, 32):
        w32.putpixel((0, y), (20, 13, 6, 70))
        w32.putpixel((1, y), (20, 13, 6, 140))
        w32.putpixel((2, y), C_DARKEST)

    # Micro pebbles at base of west cliff (y=30..31)
    w32.putpixel((0, 30), P_SLATE); w32.putpixel((0, 31), P_SLATE_D)
    w32.putpixel((2, 31), P_DIRT)

    top = w32.crop((0, 0, 16, 16))
    bot = w32.crop((0, 16, 16, 32))
    return top, bot, w32


print("2. Crafting chunky, volumetric East-facing cliff wall (32px)...")
# High ground is to the WEST (x <= 6). Sheer rock face drops to the EAST (x=7..14).
def render_east_cliff_32():
    w32 = Image.new('RGBA', (16, 32), (0, 0, 0, 0))

    for y in range(32):
        for x in range(6, 15):
            w32.putpixel((x, y), C_SHADOW)

    def draw_east_boulder(cx, cy, rx, ry, seed=0):
        for y in range(max(0, int(cy - ry - 2)), min(32, int(cy + ry + 3))):
            for x in range(max(5, int(cx - rx - 2)), min(15, int(cx + rx + 3))):
                dx = (x - cx) / float(rx)
                dy = (y - cy) / float(ry)
                angle = math.atan2(dy, dx)
                wobble = 1.0 + 0.12 * math.sin(angle * 3 + seed) + 0.08 * math.cos(angle * 4)
                d = (dx*dx + dy*dy) / (wobble * wobble)

                if d <= 1.0:
                    # East face is in gentle shade
                    light = -0.55 * dx - 0.65 * dy
                    if light > 0.45:    col = C_ROCK_MID
                    elif light > 0.10:  col = C_ROCK_DARK
                    elif light > -0.30: col = C_SHADOW
                    else:               col = C_CREVICE
                    w32.putpixel((x, y), col)
                elif d <= 1.35:
                    curr = w32.getpixel((x, y))
                    if curr[3] == 0 or curr in [C_SHADOW, C_ROCK_DARK]:
                        w32.putpixel((x, y), C_CREVICE)

    draw_east_boulder(10.0, 5.5, 4.2, 4.8, 4)
    draw_east_boulder(9.8, 15.5, 4.4, 5.0, 5) # Straddles top/bot boundary!
    draw_east_boulder(10.0, 25.5, 4.2, 4.8, 6)

    # Upper Plateau Grass on the LEFT (x <= 6)
    for y in range(32):
        edge_x = 6 + int((math.sin(y * 0.9) + 1.0) * 0.7)
        for x in range(0, edge_x):
            c = G_MID if (x + y) % 2 == 0 else G_LUSH
            if (x * 3 + y * 5) % 4 == 0: c = G_HI
            w32.putpixel((x, y), c)

        # Golden earth rim
        w32.putpixel((edge_x, y), C_LIP_HI if y % 2 == 0 else C_LIP_MID)
        w32.putpixel((edge_x - 1, y), G_DARK if y % 3 != 0 else G_MID)

        # Ragged grass overhang tips
        if y % 4 == 2:
            w32.putpixel((edge_x + 1, y), G_HI)
        elif y % 4 == 0:
            w32.putpixel((edge_x + 1, y), G_MID)

    # Base grounding shadow on the RIGHT edge (x=13..15) on bottom rows (y=27..31)
    for y in range(27, 32):
        w32.putpixel((13, y), C_DARKEST)
        w32.putpixel((14, y), (20, 13, 6, 140))
        w32.putpixel((15, y), (20, 13, 6, 70))

    w32.putpixel((14, 30), P_SLATE); w32.putpixel((14, 31), P_SLATE_D)
    w32.putpixel((13, 31), P_DIRT)

    top = w32.crop((0, 0, 16, 16))
    bot = w32.crop((0, 16, 16, 32))
    return top, bot, w32


print("3. Crafting massive volumetric Southwest and Southeast outer corners (32px)...")
# Southwest Outer Corner: High ground is North-East. Cliff drops South & West.
def render_sw_corner_32():
    w32 = Image.new('RGBA', (16, 32), (0, 0, 0, 0))

    # Base rock fill
    for y in range(3, 30):
        for x in range(1, 16):
            w32.putpixel((x, y), C_SHADOW)

    # Massive 3D corner boulder curving around the outside
    def draw_corner_boulder(cx, cy, rx, ry):
        for y in range(max(0, int(cy - ry - 2)), min(32, int(cy + ry + 3))):
            for x in range(max(1, int(cx - rx - 2)), min(16, int(cx + rx + 3))):
                dx = (x - cx) / float(rx)
                dy = (y - cy) / float(ry)
                d = dx*dx + dy*dy
                if d <= 1.0:
                    light = -0.7*dx - 0.7*dy
                    if light > 0.35:    col = C_ROCK_HI
                    elif light > 0.05:  col = C_ROCK_MID
                    elif light > -0.35: col = C_ROCK_DARK
                    elif light > -0.65: col = C_SHADOW
                    else:               col = C_CREVICE
                    w32.putpixel((x, y), col)
                elif d <= 1.3:
                    curr = w32.getpixel((x, y))
                    if curr[3] == 0 or curr == C_SHADOW:
                        w32.putpixel((x, y), C_CREVICE)

    # Top corner boulder
    draw_corner_boulder(8.5, 9.0, 7.0, 6.5)
    # Straddler corner boulder (cy=16)
    draw_corner_boulder(8.0, 16.5, 7.2, 6.0)
    # Base corner boulder
    draw_corner_boulder(7.5, 24.5, 6.8, 5.5)

    # Upper grass meadow curving in an arc in the top-right corner
    # Arc centered at (16, 0) with radius 11px
    for y in range(12):
        for x in range(16):
            dist = math.sqrt((x - 16)**2 + (y - 0)**2)
            if dist < 8.5:
                w32.putpixel((x, y), G_MID if (x + y) % 2 == 0 else G_LUSH)
            elif dist < 10.2:
                # Golden rim
                w32.putpixel((x, y), C_LIP_HI if (x + y) % 2 == 0 else C_LIP_MID)
                # Overhang blades
                if (x * 7 + y * 13) % 4 == 0:
                    w32.putpixel((x, y), G_HI)

    # Ground contact shadow on bottom and left edges
    for x in range(16):
        w32.putpixel((x, 30), C_DARKEST)
        w32.putpixel((x, 31), (20, 13, 6, 120))
    for y in range(25, 32):
        w32.putpixel((0, y), (20, 13, 6, 70))
        w32.putpixel((1, y), (20, 13, 6, 140))

    # Corner micro pebbles
    w32.putpixel((1, 30), P_SLATE); w32.putpixel((1, 31), P_SLATE_D)
    w32.putpixel((4, 31), P_DIRT)

    top = w32.crop((0, 0, 16, 16))
    bot = w32.crop((0, 16, 16, 32))
    return top, bot, w32


# Southeast Outer Corner: High ground is North-West. Cliff drops South & East.
def render_se_corner_32():
    w32 = Image.new('RGBA', (16, 32), (0, 0, 0, 0))

    for y in range(3, 30):
        for x in range(0, 15):
            w32.putpixel((x, y), C_SHADOW)

    def draw_corner_boulder(cx, cy, rx, ry):
        for y in range(max(0, int(cy - ry - 2)), min(32, int(cy + ry + 3))):
            for x in range(max(0, int(cx - rx - 2)), min(15, int(cx + rx + 3))):
                dx = (x - cx) / float(rx)
                dy = (y - cy) / float(ry)
                d = dx*dx + dy*dy
                if d <= 1.0:
                    light = -0.5*dx - 0.7*dy
                    if light > 0.35:    col = C_ROCK_MID
                    elif light > 0.05:  col = C_ROCK_DARK
                    elif light > -0.35: col = C_SHADOW
                    else:               col = C_CREVICE
                    w32.putpixel((x, y), col)
                elif d <= 1.3:
                    curr = w32.getpixel((x, y))
                    if curr[3] == 0 or curr == C_SHADOW:
                        w32.putpixel((x, y), C_CREVICE)

    draw_corner_boulder(7.5, 9.0, 7.0, 6.5)
    draw_corner_boulder(7.8, 16.5, 7.2, 6.0)
    draw_corner_boulder(8.0, 24.5, 6.8, 5.5)

    # Upper grass meadow curving in an arc in top-left corner (0, 0)
    for y in range(12):
        for x in range(16):
            dist = math.sqrt((x - 0)**2 + (y - 0)**2)
            if dist < 8.5:
                w32.putpixel((x, y), G_MID if (x + y) % 2 == 0 else G_LUSH)
            elif dist < 10.2:
                w32.putpixel((x, y), C_LIP_HI if (x + y) % 2 == 0 else C_LIP_MID)
                if (x * 7 + y * 13) % 4 == 0:
                    w32.putpixel((x, y), G_HI)

    for x in range(16):
        w32.putpixel((x, 30), C_DARKEST)
        w32.putpixel((x, 31), (20, 13, 6, 120))
    for y in range(25, 32):
        w32.putpixel((14, y), (20, 13, 6, 140))
        w32.putpixel((15, y), (20, 13, 6, 70))

    w32.putpixel((14, 30), P_SLATE); w32.putpixel((14, 31), P_SLATE_D)
    w32.putpixel((11, 31), P_DIRT)

    top = w32.crop((0, 0, 16, 16))
    bot = w32.crop((0, 16, 16, 32))
    return top, bot, w32


print("4. Crafting natural Mud Elevation Ramp Shoulders (NO STEPS, JUS MUD!)...")
# Left Ramp Shoulder (32px high):
# - Left side: South-facing volumetric cliff boulder ending organically with a rounded end-cap.
# - Right side: 100% natural mud from mud_base_01.png!
# - Contact line: Ragged soil contact, soft dark shadow, and tiny trail pebbles.
# - ZERO steps! Pure mud!

def render_mud_ramp_left_32():
    w32 = Image.new('RGBA', (16, 32), (0, 0, 0, 0))

    # 1. Fill entire right side with genuine mud_base_01.png pixels!
    for y in range(32):
        for x in range(16):
            # Tile mud_base_01 seamlessly
            w32.putpixel((x, y), mud_tile.getpixel((x, y % 16)))

    # 2. Rock wall occupies x=0..9
    for y in range(3, 29):
        for x in range(0, 9):
            w32.putpixel((x, y), C_SHADOW)

    # Rounded end-cap boulder on the left
    def draw_end_boulder(cx, cy, rx, ry):
        for y in range(max(0, int(cy - ry - 2)), min(32, int(cy + ry + 3))):
            for x in range(max(0, int(cx - rx - 2)), min(10, int(cx + rx + 3))):
                dx = (x - cx) / float(rx)
                dy = (y - cy) / float(ry)
                if dx*dx + dy*dy <= 1.0:
                    light = -0.7*dx - 0.7*dy
                    if light > 0.35:    col = C_ROCK_HI
                    elif light > 0.05:  col = C_ROCK_MID
                    elif light > -0.35: col = C_ROCK_DARK
                    elif light > -0.65: col = C_SHADOW
                    else:               col = C_CREVICE
                    w32.putpixel((x, y), col)
                elif dx*dx + dy*dy <= 1.3:
                    w32.putpixel((x, y), C_CREVICE)

    draw_end_boulder(3.5, 10.0, 4.8, 5.5)
    draw_end_boulder(3.8, 17.0, 5.0, 5.5) # Straddles top/bot boundary!
    draw_end_boulder(3.5, 24.5, 4.8, 5.5)

    # Upper grass meadow on top-left (y <= 3, x <= 8)
    for y in range(4):
        for x in range(9 - y):
            w32.putpixel((x, y), G_MID if (x + y) % 2 == 0 else G_LUSH)
        w32.putpixel((9 - y, y), C_LIP_HI)
        w32.putpixel((8 - y, y), G_DARK)

    # Ragged contact line between rock and mud on x=8..10
    for y in range(4, 30):
        cx = 8 + int(math.sin(y * 0.7) * 0.8)
        w32.putpixel((cx, y), C_DARKEST)
        w32.putpixel((cx + 1, y), D_DARK)
        if y % 5 == 2:
            w32.putpixel((cx + 2, y), P_SLATE) # tiny natural pebble on the mud

    # Bottom ground contact shadow on rows 30..31
    for x in range(9):
        w32.putpixel((x, 30), C_DARKEST)
        w32.putpixel((x, 31), (20, 13, 6, 120))

    top = w32.crop((0, 0, 16, 16))
    bot = w32.crop((0, 16, 16, 32))
    return top, bot, w32


# Right Ramp Shoulder (32px high):
# - Left side: 100% natural mud from mud_base_01.png!
# - Right side: South-facing volumetric cliff boulder ending organically with a rounded end-cap.
# - ZERO steps! Pure mud!
def render_mud_ramp_right_32():
    w32 = Image.new('RGBA', (16, 32), (0, 0, 0, 0))

    # Fill left side with genuine mud_base_01.png pixels!
    for y in range(32):
        for x in range(16):
            w32.putpixel((x, y), mud_tile.getpixel((x, y % 16)))

    for y in range(3, 29):
        for x in range(7, 16):
            w32.putpixel((x, y), C_SHADOW)

    def draw_end_boulder(cx, cy, rx, ry):
        for y in range(max(0, int(cy - ry - 2)), min(32, int(cy + ry + 3))):
            for x in range(max(6, int(cx - rx - 2)), min(16, int(cx + rx + 3))):
                dx = (x - cx) / float(rx)
                dy = (y - cy) / float(ry)
                if dx*dx + dy*dy <= 1.0:
                    light = -0.5*dx - 0.7*dy
                    if light > 0.35:    col = C_ROCK_MID
                    elif light > 0.05:  col = C_ROCK_DARK
                    elif light > -0.35: col = C_SHADOW
                    else:               col = C_CREVICE
                    w32.putpixel((x, y), col)
                elif dx*dx + dy*dy <= 1.3:
                    w32.putpixel((x, y), C_CREVICE)

    draw_end_boulder(12.5, 10.0, 4.8, 5.5)
    draw_end_boulder(12.2, 17.0, 5.0, 5.5)
    draw_end_boulder(12.5, 24.5, 4.8, 5.5)

    for y in range(4):
        for x in range(7 + y, 16):
            w32.putpixel((x, y), G_MID if (x + y) % 2 == 0 else G_LUSH)
        w32.putpixel((6 + y, y), C_LIP_HI)
        w32.putpixel((7 + y, y), G_DARK)

    for y in range(4, 30):
        cx = 7 - int(math.sin(y * 0.7) * 0.8)
        w32.putpixel((cx, y), C_DARKEST)
        w32.putpixel((cx - 1, y), D_DARK)
        if y % 5 == 3 and cx - 2 >= 0:
            w32.putpixel((cx - 2, y), P_DIRT)

    for x in range(7, 16):
        w32.putpixel((x, 30), C_DARKEST)
        w32.putpixel((x, 31), (20, 13, 6, 120))

    top = w32.crop((0, 0, 16, 16))
    bot = w32.crop((0, 16, 16, 32))
    return top, bot, w32


# Center Mud Passage (100% pure authentic mud_base_01.png with a few subtle trail grains):
def render_mud_ramp_mid_32():
    top = mud_tile.copy()
    bot = mud_tile.copy()
    # Add a couple subtle trail pebbles so it feels like a natural earthen path
    top_d = top.copy()
    top_d.putpixel((4, 7), P_SLATE); top_d.putpixel((4, 8), D_DEEP)
    top_d.putpixel((11, 13), P_DIRT)
    bot_d = bot.copy()
    bot_d.putpixel((7, 5), P_SLATE); bot_d.putpixel((7, 6), D_DEEP)
    bot_d.putpixel((12, 11), P_DIRT)
    return top_d, bot_d


# Save everything
print("Saving updated authentic tiles...")
w_top, w_bot, _ = render_west_cliff_32()
w_top.save(os.path.join(CLIFFS_DIR, 'cliff_side_w_top.png'))
w_bot.save(os.path.join(CLIFFS_DIR, 'cliff_side_w_bot.png'))
w_top.save(os.path.join(CLIFFS_DIR, 'cliff_side_w.png'))

e_top, e_bot, _ = render_east_cliff_32()
e_top.save(os.path.join(CLIFFS_DIR, 'cliff_side_e_top.png'))
e_bot.save(os.path.join(CLIFFS_DIR, 'cliff_side_e_bot.png'))
e_top.save(os.path.join(CLIFFS_DIR, 'cliff_side_e.png'))

sw_top, sw_bot, _ = render_sw_corner_32()
sw_top.save(os.path.join(CLIFFS_DIR, 'cliff_corner_sw_top.png'))
sw_bot.save(os.path.join(CLIFFS_DIR, 'cliff_corner_sw_bot.png'))
sw_top.save(os.path.join(CLIFFS_DIR, 'cliff_outer_tl_top.png'))

se_top, se_bot, _ = render_se_corner_32()
se_top.save(os.path.join(CLIFFS_DIR, 'cliff_corner_se_top.png'))
se_bot.save(os.path.join(CLIFFS_DIR, 'cliff_corner_se_bot.png'))
se_top.save(os.path.join(CLIFFS_DIR, 'cliff_outer_tr_top.png'))

rl_top, rl_bot, _ = render_mud_ramp_left_32()
rl_top.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_left_top.png'))
rl_bot.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_left_bot.png'))

rr_top, rr_bot, _ = render_mud_ramp_right_32()
rr_top.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_right_top.png'))
rr_bot.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_right_bot.png'))

rm_top, rm_bot = render_mud_ramp_mid_32()
rm_top.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_mid_top.png'))
rm_bot.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_mid_bot.png'))
rm_top.save(os.path.join(CLIFFS_DIR, 'cliff_mud_slope_top.png'))
rm_bot.save(os.path.join(CLIFFS_DIR, 'cliff_mud_slope_bot.png'))

print("Completed crafting pure mud elevation ramp & chunky volumetric East/West cliff sides!")
