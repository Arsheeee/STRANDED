import os
import math
from PIL import Image, ImageDraw

CLIFFS_DIR = r'd:\Unity\Projects\STRANDED\Assets\Art\Terrain\Cliffs'
BRAIN_DIR = r'C:\Users\PAVILION\.gemini\antigravity-ide\brain\84db0e2d-58d2-466d-be05-dbff8f133035'
os.makedirs(CLIFFS_DIR, exist_ok=True)

# Master Palette (Warm volumetric earthen stone inspired by Stardew Valley)
C_VOID      = (20, 13, 6, 255)     # Deepest cave void (#140d06)
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

# Dirt Colors
D_DIRT      = (179, 119, 41, 255)  # Mud base (#b37729)
D_DARK      = (145, 78, 12, 255)   # Mud shadow (#914e0c)

# Pebbles
P_SLATE     = (125, 140, 128, 255) # Slate pebble (#7d8c80)
P_SLATE_D   = (78, 92, 82, 255)    # Slate pebble shadow
P_DIRT      = (160, 120, 50, 255)  # Earth pebble
P_DIRT_D    = (100, 70, 25, 255)   # Earth pebble shadow

def new_tile():
    return Image.new('RGBA', (16, 16), (0, 0, 0, 0))

print("Crafting Seamless 32px Volumetric Cliff Wall...")

# We render the continuous 16x32 cliff wall first, then slice into top (16x16) and bot (16x16)!
# This guarantees 100% seamless continuity with zero horizontal seam artifact!

def render_continuous_cliff(variant=1):
    # Canvas is 16 wide x 32 high
    w32 = Image.new('RGBA', (16, 32), (0, 0, 0, 0))
    
    # 1. Grass plateau on top (rows 0..3)
    for y in range(3):
        for x in range(16):
            c = G_MID if (x + y + variant) % 2 == 0 else G_LUSH
            if (x * 7 + y * 13 + variant) % 5 == 0: c = G_HI
            w32.putpixel((x, y), c)

    # 2. Fill rock shadow background for rows 7..28
    for y in range(6, 28):
        for x in range(16):
            w32.putpixel((x, y), C_SHADOW)

    # 3. Draw Organic Interlocking Boulders across the 32px height
    def draw_boulder_32(cx, cy, rx, ry, seed=0):
        for y in range(max(6, int(cy - ry - 2)), min(29, int(cy + ry + 3))):
            for x in range(max(0, int(cx - rx - 2)), min(16, int(cx + rx + 3))):
                dx = (x - cx) / float(rx)
                dy = (y - cy) / float(ry)
                angle = math.atan2(dy, dx)
                wobble = 1.0 + 0.12 * math.sin(angle * 3 + seed) + 0.08 * math.cos(angle * 5)
                d = (dx*dx + dy*dy) / (wobble * wobble)

                if d <= 1.0:
                    light = -0.55 * dx - 0.75 * dy
                    if light > 0.45:    col = C_ROCK_HI
                    elif light > 0.10:  col = C_ROCK_MID
                    elif light > -0.30: col = C_ROCK_DARK
                    elif light > -0.65: col = C_SHADOW
                    else:               col = C_CREVICE
                    w32.putpixel((x, y), col)
                elif d <= 1.35:
                    curr = w32.getpixel((x, y))
                    if curr[3] == 0 or curr in [C_SHADOW, C_ROCK_DARK]:
                        w32.putpixel((x, y), C_CREVICE)

    if variant == 1:
        # Tier 1 Boulders (upper: cy=11)
        draw_boulder_32(4.0, 11.0, 4.5, 4.2, 1)
        draw_boulder_32(12.0, 11.5, 4.5, 4.0, 2)
        draw_boulder_32(8.0, 8.5, 2.5, 2.0, 3)
        # Tier 2 Boulders (SEAM STRADDLERS: cy=17 - perfectly spans row 15 of top and row 1 of bot!)
        draw_boulder_32(7.5, 17.5, 4.8, 4.2, 4)
        draw_boulder_32(14.5, 17.0, 3.5, 3.8, 5)
        draw_boulder_32(1.0, 17.0, 3.5, 3.8, 6)
        # Tier 3 Boulders (lower: cy=23)
        draw_boulder_32(4.5, 23.5, 4.8, 4.5, 7)
        draw_boulder_32(12.0, 23.0, 4.5, 4.2, 8)
        # Tier 4 Base Boulders (cy=27)
        draw_boulder_32(3.5, 27.5, 3.8, 2.8, 9)
        draw_boulder_32(11.5, 27.5, 4.2, 2.8, 10)
    else:
        # Variant 2
        draw_boulder_32(2.5, 11.5, 3.5, 3.8, 11)
        draw_boulder_32(8.5, 11.0, 4.2, 4.0, 12)
        draw_boulder_32(14.5, 11.5, 3.5, 3.8, 13)
        # Tier 2 Seam Straddlers (cy=17)
        draw_boulder_32(4.5, 17.5, 4.8, 4.2, 14)
        draw_boulder_32(12.0, 17.0, 4.8, 4.2, 15)
        # Tier 3 Boulders (cy=23)
        draw_boulder_32(2.5, 23.0, 3.8, 4.2, 16)
        draw_boulder_32(8.5, 23.5, 4.2, 4.5, 17)
        draw_boulder_32(14.5, 23.0, 3.8, 4.2, 18)
        # Tier 4 Base (cy=27)
        draw_boulder_32(7.5, 27.5, 4.5, 2.8, 19)
        draw_boulder_32(1.5, 27.5, 2.8, 2.5, 20)
        draw_boulder_32(14.0, 27.5, 2.8, 2.5, 21)

    # 4. Golden Earthen Lip (rows 5..6)
    for x in range(16):
        lip_c = C_LIP_HI if (x + variant) % 3 != 0 else C_LIP_MID
        w32.putpixel((x, 5), lip_c)
        w32.putpixel((x, 6), C_LIP_MID if (x + variant) % 4 != 0 else C_SHADOW)

    # 5. Overhanging Grass Fringe (rows 3..5)
    fringe = [1, 2, 4, 6, 7, 9, 11, 12, 14, 15] if variant == 1 else [0, 2, 3, 5, 8, 9, 10, 13, 14]
    for x in range(16):
        w32.putpixel((x, 3), G_MID)
        if x in fringe:
            w32.putpixel((x, 4), G_HI if (x + variant) % 2 == 0 else G_MID)
            if (x * 3 + variant) % 3 == 0:
                w32.putpixel((x, 5), G_DARK)

    for x in range(16):
        if w32.getpixel((x, 5)) == G_DARK:
            if w32.getpixel((x, 6)) != G_DARK:
                w32.putpixel((x, 6), C_DARKEST)

    # 6. Bottom Rock Ledge & Base Rim (rows 27..28)
    for x in range(16):
        w32.putpixel((x, 27), C_CREVICE)
        w32.putpixel((x, 28), C_DARKEST)

    # 7. Ground Contact Shadow (rows 29..31)
    for y in range(29, 32):
        alpha = 220 if y == 29 else (130 if y == 30 else 50)
        for x in range(16):
            w32.putpixel((x, y), (35, 22, 10, alpha))

    # 8. Base loose pebbles
    if variant == 1:
        w32.putpixel((2, 29), P_SLATE);   w32.putpixel((3, 29), P_SLATE)
        w32.putpixel((2, 30), P_SLATE_D); w32.putpixel((3, 30), P_SLATE_D)
        w32.putpixel((12, 29), P_DIRT);   w32.putpixel((12, 30), P_DIRT_D)
    else:
        w32.putpixel((9, 29), P_SLATE);   w32.putpixel((10, 29), P_SLATE)
        w32.putpixel((9, 30), P_SLATE_D); w32.putpixel((10, 30), P_SLATE_D)
        w32.putpixel((4, 30), P_SLATE);   w32.putpixel((4, 31), P_SLATE_D)

    # Slice into top (0..16) and bot (16..32)
    top = w32.crop((0, 0, 16, 16))
    bot = w32.crop((0, 16, 16, 32))
    return top, bot, w32

cliff_top_01, cliff_bot_01, w32_v1 = render_continuous_cliff(1)
cliff_top_02, cliff_bot_02, w32_v2 = render_continuous_cliff(2)

cliff_top_01.save(os.path.join(CLIFFS_DIR, 'cliff_face_top_01.png'))
cliff_top_02.save(os.path.join(CLIFFS_DIR, 'cliff_face_top_02.png'))
cliff_bot_01.save(os.path.join(CLIFFS_DIR, 'cliff_face_bot_01.png'))
cliff_bot_02.save(os.path.join(CLIFFS_DIR, 'cliff_face_bot_02.png'))


# ====================================================================
# 2. CAVE / MINE ENTRANCE (2x2 Tiles)
# ====================================================================
# Carve cave directly into continuous cliff
cave_32_l = w32_v1.copy()
cave_32_r = w32_v1.transpose(Image.FLIP_LEFT_RIGHT)

# Carve left arch
for y in range(7, 29):
    for x in range(6, 16):
        dx = x - 16
        dy = y - 17 # Arch center at (16, 17)
        r = math.sqrt(dx*dx + dy*dy) if y < 17 else abs(x - 16)
        if r < 10.0 and y < 28:
            cave_32_l.putpixel((x, y), C_VOID)
        elif r < 11.5 and y < 28:
            cave_32_l.putpixel((x, y), C_DARKEST)
        elif r < 13.0 and y < 28:
            cave_32_l.putpixel((x, y), C_CREVICE)

cave_32_r = cave_32_l.transpose(Image.FLIP_LEFT_RIGHT)

cliff_cave_tl = cave_32_l.crop((0, 0, 16, 16))
cliff_cave_bl = cave_32_l.crop((0, 16, 16, 32))
cliff_cave_tr = cave_32_r.crop((0, 0, 16, 16))
cliff_cave_br = cave_32_r.crop((0, 16, 16, 32))

cliff_cave_tl.save(os.path.join(CLIFFS_DIR, 'cliff_cave_tl.png'))
cliff_cave_bl.save(os.path.join(CLIFFS_DIR, 'cliff_cave_bl.png'))
cliff_cave_tr.save(os.path.join(CLIFFS_DIR, 'cliff_cave_tr.png'))
cliff_cave_br.save(os.path.join(CLIFFS_DIR, 'cliff_cave_br.png'))


# ====================================================================
# 3. CLIFF RAMP / CANYON PATHWAY SHOULDERS (Stardew Style)
# ====================================================================
# Left shoulder: Cliff curves smoothly North
ramp_32_l = w32_v1.copy()
for y in range(32):
    for x in range(11, 16):
        if x == 11:
            ramp_32_l.putpixel((x, y), C_ROCK_MID if y > 6 else C_LIP_MID)
        elif x == 12:
            ramp_32_l.putpixel((x, y), C_SHADOW)
        elif x == 13:
            ramp_32_l.putpixel((x, y), C_DARKEST)
        else:
            ramp_32_l.putpixel((x, y), (35, 22, 10, 150 if x == 14 else 70))

ramp_32_r = ramp_32_l.transpose(Image.FLIP_LEFT_RIGHT)

cliff_ramp_lt = ramp_32_l.crop((0, 0, 16, 16))
cliff_ramp_lb = ramp_32_l.crop((0, 16, 16, 32))
cliff_ramp_rt = ramp_32_r.crop((0, 0, 16, 16))
cliff_ramp_rb = ramp_32_r.crop((0, 16, 16, 32))

cliff_ramp_lt.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_left_top.png'))
cliff_ramp_lb.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_left_bot.png'))
cliff_ramp_rt.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_right_top.png'))
cliff_ramp_rb.save(os.path.join(CLIFFS_DIR, 'cliff_ramp_right_bot.png'))


# ====================================================================
# 4. VERTICAL CLIFF WALLS (For the sunken pathway sides!)
# ====================================================================
# cliff_side_w (Wall facing East)
side_w = new_tile()
for y in range(16):
    for x in range(16):
        if x < 4:
            side_w.putpixel((x, y), G_MID if (x + y) % 2 == 0 else G_LUSH)
        elif x in [4, 5]:
            side_w.putpixel((x, y), C_LIP_HI if (x + y) % 3 == 0 else C_LIP_MID)
        elif x in range(6, 12):
            side_w.putpixel((x, y), C_ROCK_MID if (x + y) % 2 == 0 else C_ROCK_DARK)
        elif x in [12, 13]:
            side_w.putpixel((x, y), C_CREVICE if x == 12 else C_DARKEST)
        else:
            side_w.putpixel((x, y), (35, 22, 10, 140 if x == 14 else 60))

side_w.save(os.path.join(CLIFFS_DIR, 'cliff_side_w.png'))
side_e = side_w.transpose(Image.FLIP_LEFT_RIGHT)
side_e.save(os.path.join(CLIFFS_DIR, 'cliff_side_e.png'))

print("All cliff tiles compiled!")

# ====================================================================
# 5. GENERATE ACCURATE STARDEW-STYLE SHOWCASE SCENE
# ====================================================================
# Layout:
# 24 tiles wide x 14 tiles high (384x224 px)
# High Plateau: Rows 0..3 (Grass + dirt path at x=15..17)
# Cliff Face: Rows 4..5
# Path Cut: Dirt path going up through rows 0..13 at x=15..17
# On left of path (x=14): Cliff shoulder turns North up rows 0..3!
# On right of path (x=18): Cliff shoulder turns North up rows 0..3!
# Cave: at x=8..9 on the cliff face!
# Player: standing at x=8.5, y=6.5 facing the cave!

SW, SH = 24, 14
scene = Image.new('RGBA', (SW * 16, SH * 16), (68, 163, 24, 255))

grass_base = Image.open(r'd:\Unity\Projects\STRANDED\Assets\Art\Terrain\Grass\grass_base_01.png').convert('RGBA')
dirt_base  = Image.open(r'd:\Unity\Projects\STRANDED\Assets\Art\Terrain\Dirt\mud_base_01.png').convert('RGBA')

# 1. Base Ground
for y in range(SH):
    for x in range(SW):
        # Path going all the way up through x=15..17
        if 15 <= x <= 17:
            scene.alpha_composite(dirt_base, (x * 16, y * 16))
        else:
            scene.alpha_composite(grass_base, (x * 16, y * 16))

# 2. Vertical Cliff sides along the path cut (rows 0..3)
# On the left of the path (x=14), cliff face faces East towards path
for y in range(4):
    scene.alpha_composite(side_w, (14 * 16, y * 16))
# On the right of the path (x=18), cliff face faces West towards path
for y in range(4):
    scene.alpha_composite(side_e, (18 * 16, y * 16))

# 3. Horizontal Cliff Wall at rows 4 and 5
# Left section: x=0..7
for x in range(8):
    t = cliff_top_01 if x % 2 == 0 else cliff_top_02
    b = cliff_bot_01 if x % 2 == 0 else cliff_bot_02
    scene.alpha_composite(t, (x * 16, 4 * 16))
    scene.alpha_composite(b, (x * 16, 5 * 16))

# Cave entrance: x=8..9
scene.alpha_composite(cliff_cave_tl, (8 * 16, 4 * 16))
scene.alpha_composite(cliff_cave_tr, (9 * 16, 4 * 16))
scene.alpha_composite(cliff_cave_bl, (8 * 16, 5 * 16))
scene.alpha_composite(cliff_cave_br, (9 * 16, 5 * 16))

# Section between cave and path: x=10..13
for x in range(10, 14):
    t = cliff_top_02 if x % 2 == 0 else cliff_top_01
    b = cliff_bot_02 if x % 2 == 0 else cliff_bot_01
    scene.alpha_composite(t, (x * 16, 4 * 16))
    scene.alpha_composite(b, (x * 16, 5 * 16))

# Path Left Shoulder: x=14
scene.alpha_composite(cliff_ramp_lt, (14 * 16, 4 * 16))
scene.alpha_composite(cliff_ramp_lb, (14 * 16, 5 * 16))

# Path Right Shoulder: x=18
scene.alpha_composite(cliff_ramp_rt, (18 * 16, 4 * 16))
scene.alpha_composite(cliff_ramp_rb, (18 * 16, 5 * 16))

# Right section: x=19..23
for x in range(19, SW):
    t = cliff_top_01 if x % 2 == 0 else cliff_top_02
    b = cliff_bot_01 if x % 2 == 0 else cliff_bot_02
    scene.alpha_composite(t, (x * 16, 4 * 16))
    scene.alpha_composite(b, (x * 16, 5 * 16))

# 4. Player Character standing in front of the Cave
player_im = Image.open(r'd:\Unity\Projects\STRANDED\Assets\player\player_base.png').convert('RGBA')
player_idle = player_im.crop((0, 0, 32, 32))
shadow = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
draw = ImageDraw.Draw(shadow)
draw.ellipse([8, 26, 24, 31], fill=(20, 40, 50, 90))

# Place player facing cave at x=8.5, y=6.2
px = int(8.5 * 16 - 8)
py = int(6.2 * 16 - 12)
scene.alpha_composite(shadow, (px, py))
scene.alpha_composite(player_idle, (px, py))

# Save 1x and 4x
out_1x = os.path.join(BRAIN_DIR, 'cliff_scene_preview.png')
scene.save(out_1x)

out_4x = os.path.join(BRAIN_DIR, 'cliff_scene_preview_4x.png')
scene.resize((scene.width * 4, scene.height * 4), Image.NEAREST).save(out_4x)

print(f"Saved: {out_1x}")
print(f"Saved: {out_4x}")
