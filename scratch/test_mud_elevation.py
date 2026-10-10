import os
from PIL import Image

CLIFFS_DIR = r'd:\Unity\Projects\STRANDED\Assets\Art\Terrain\Cliffs'
GRASS_DIR  = r'd:\Unity\Projects\STRANDED\Assets\Art\Terrain\Grass'
DIRT_DIR   = r'd:\Unity\Projects\STRANDED\Assets\Art\Terrain\Dirt'
PLAYER_PATH= r'd:\Unity\Projects\STRANDED\Assets\player\player_base.png'
BRAIN_DIR  = r'C:\Users\PAVILION\.gemini\antigravity-ide\brain\84db0e2d-58d2-466d-be05-dbff8f133035'

def load(name):
    p = os.path.join(CLIFFS_DIR, name)
    if os.path.exists(p):
        return Image.open(p).convert('RGBA')
    return None

grass_im = Image.open(os.path.join(GRASS_DIR, 'grass_base_01.png')).convert('RGBA')
dirt_im  = Image.open(os.path.join(DIRT_DIR, 'mud_base_01.png')).convert('RGBA')
player_im = Image.open(PLAYER_PATH).convert('RGBA').crop((0, 0, 32, 32))

# Let's build a map: 26 cols x 16 rows (416 x 256 px)
# Showcase:
# A central elevated plateau (Level 1) with:
# - West cliff side on x=3 (running y=2..6)
# - South cliff face on y=6..7 (running x=4..21), interrupted by a natural mud ramp at x=11..13!
# - East cliff side on x=22 (running y=2..6)
# - Lowland (Level 0) all around to the West, South, and East!
# - A continuous natural mud path coming from lowland (y=8..15), ramping up through x=11..13 (y=6..7), and spreading onto the high plateau (y=2..5)!

SW, SH = 26, 16
canvas = Image.new('RGBA', (SW * 16, SH * 16))

# Fill lowlands with grass, and mud path in the center
for y in range(SH):
    for x in range(SW):
        # Mud path coming up to the ramp at x=11..13
        if 11 <= x <= 13:
            canvas.paste(dirt_im, (x * 16, y * 16))
        else:
            canvas.paste(grass_im, (x * 16, y * 16))

# Load cliff assets
top1 = load('cliff_face_top_01.png')
top2 = load('cliff_face_top_02.png')
bot1 = load('cliff_face_bot_01.png')
bot2 = load('cliff_face_bot_02.png')

side_w_t = load('cliff_side_w_top.png')
side_w_b = load('cliff_side_w_bot.png')
side_e_t = load('cliff_side_e_top.png')
side_e_b = load('cliff_side_e_bot.png')

c_sw_t = load('cliff_corner_sw_top.png')
c_sw_b = load('cliff_corner_sw_bot.png')
c_se_t = load('cliff_corner_se_top.png')
c_se_b = load('cliff_corner_se_bot.png')

rmp_l_t = load('cliff_ramp_left_top.png')
rmp_l_b = load('cliff_ramp_left_bot.png')
rmp_r_t = load('cliff_ramp_right_top.png')
rmp_r_b = load('cliff_ramp_right_bot.png')

# 1. West cliff wall running vertically at x=3
# Tiles at y=2, y=3 (top and bot pair)
canvas.paste(side_w_t, (3 * 16, 2 * 16), side_w_t)
canvas.paste(side_w_b, (3 * 16, 3 * 16), side_w_b)
# Tiles at y=4, y=5 (second vertical pair)
canvas.paste(side_w_t, (3 * 16, 4 * 16), side_w_t)
canvas.paste(side_w_b, (3 * 16, 5 * 16), side_w_b)

# 2. Southwest Outer Corner at x=3, y=6..7
canvas.paste(c_sw_t, (3 * 16, 6 * 16), c_sw_t)
canvas.paste(c_sw_b, (3 * 16, 7 * 16), c_sw_b)

# 3. South cliff face (left section: x=4..10, rows 6 & 7)
for x in range(4, 11):
    t = top1 if x % 2 == 0 else top2
    b = bot1 if x % 2 == 0 else bot2
    canvas.paste(t, (x * 16, 6 * 16), t)
    canvas.paste(b, (x * 16, 7 * 16), b)

# 4. Natural Mud Ramp (x=11..13, rows 6 & 7) - NO STEPS, JUS MUD!
# Left shoulder at x=11
canvas.paste(rmp_l_t, (11 * 16, 6 * 16), rmp_l_t)
canvas.paste(rmp_l_b, (11 * 16, 7 * 16), rmp_l_b)
# Center mud is pure natural mud (already pasted dirt_im at x=12)
# Right shoulder at x=13
canvas.paste(rmp_r_t, (13 * 16, 6 * 16), rmp_r_t)
canvas.paste(rmp_r_b, (13 * 16, 7 * 16), rmp_r_b)

# 5. South cliff face (right section: x=14..21, rows 6 & 7)
for x in range(14, 22):
    t = top1 if x % 2 == 0 else top2
    b = bot1 if x % 2 == 0 else bot2
    canvas.paste(t, (x * 16, 6 * 16), t)
    canvas.paste(b, (x * 16, 7 * 16), b)

# 6. Southeast Outer Corner at x=22, y=6..7
canvas.paste(c_se_t, (22 * 16, 6 * 16), c_se_t)
canvas.paste(c_se_b, (22 * 16, 7 * 16), c_se_b)

# 7. East cliff wall running vertically at x=22
canvas.paste(side_e_t, (22 * 16, 4 * 16), side_e_t)
canvas.paste(side_e_b, (22 * 16, 5 * 16), side_e_b)
canvas.paste(side_e_t, (22 * 16, 2 * 16), side_e_t)
canvas.paste(side_e_b, (22 * 16, 3 * 16), side_e_b)

# Place player Aash walking up the mud ramp into the high ground!
shadow = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
from PIL import ImageDraw
sdraw = ImageDraw.Draw(shadow)
sdraw.ellipse((8, 22, 24, 28), fill=(20, 40, 50, 90))

# Player 1: Walking up the mud ramp at x=12, y=6.5
canvas.paste(shadow, (12 * 16 - 8, int(6.5 * 16) - 12), shadow)
canvas.paste(player_im, (12 * 16 - 8, int(6.5 * 16) - 20), player_im)

# Player 2: Standing on the high ground plateau at x=7, y=3
canvas.paste(shadow, (7 * 16 - 8, 3 * 16 - 12), shadow)
canvas.paste(player_im, (7 * 16 - 8, 3 * 16 - 20), player_im)

# Save test scene
test_path = os.path.join(BRAIN_DIR, 'test_mud_elevation_scene.png')
canvas.save(test_path)
canvas_4x = canvas.resize((canvas.width * 4, canvas.height * 4), Image.NEAREST)
test_path_4x = os.path.join(BRAIN_DIR, 'test_mud_elevation_scene_4x.png')
canvas_4x.save(test_path_4x)
print("Saved test scene to:", test_path_4x)
