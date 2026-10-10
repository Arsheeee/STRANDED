import os
from PIL import Image, ImageDraw, ImageFont

CLIFFS_DIR = r'd:\Unity\Projects\STRANDED\Assets\Art\Terrain\Cliffs'
GRASS_DIR  = r'd:\Unity\Projects\STRANDED\Assets\Art\Terrain\Grass'
DIRT_DIR   = r'd:\Unity\Projects\STRANDED\Assets\Art\Terrain\Dirt'
PLAYER_PATH= r'd:\Unity\Projects\STRANDED\Assets\player\player_base.png'
BRAIN_DIR  = r'C:\Users\PAVILION\.gemini\antigravity-ide\brain\84db0e2d-58d2-466d-be05-dbff8f133035'

def load(name):
    return Image.open(os.path.join(CLIFFS_DIR, name)).convert('RGBA')

grass_im = Image.open(os.path.join(GRASS_DIR, 'grass_base_01.png')).convert('RGBA')
dirt_im  = Image.open(os.path.join(DIRT_DIR, 'mud_base_01.png')).convert('RGBA')
player_im = Image.open(PLAYER_PATH).convert('RGBA').crop((0, 0, 32, 32))

# 1. Render map (26 cols x 14 rows = 416 x 224 px)
SW, SH = 26, 14
scene = Image.new('RGBA', (SW * 16, SH * 16))

# Base terrain
for y in range(SH):
    for x in range(SW):
        on_stone = (x in (4, 5))
        on_wood  = (x in (11, 12))
        on_ramp  = (x in (18, 19, 20))
        if on_stone or on_wood or on_ramp:
            scene.paste(dirt_im, (x * 16, y * 16))
        else:
            scene.paste(grass_im, (x * 16, y * 16))

# Canyon walls framing ramp (rows 0..3)
w_side = load('cliff_side_w.png')
e_side = load('cliff_side_e.png')
for y in range(4):
    scene.paste(w_side, (17 * 16, y * 16), w_side)
    scene.paste(e_side, (21 * 16, y * 16), e_side)

# Cliff Face (rows 4 & 5)
top1 = load('cliff_face_top_01.png')
top2 = load('cliff_face_top_02.png')
bot1 = load('cliff_face_bot_01.png')
bot2 = load('cliff_face_bot_02.png')

def paste_cliff(fx, tx):
    for x in range(fx, tx + 1):
        t = top1 if x % 2 == 0 else top2
        b = bot1 if x % 2 == 0 else bot2
        scene.paste(t, (x * 16, 4 * 16), t)
        scene.paste(b, (x * 16, 5 * 16), b)

# Section 1: Left (x=0..3)
paste_cliff(0, 3)

# Section 2: Stone Stairs (x=4..5)
st_tl = load('cliff_stairs_stone_tl.png')
st_tr = load('cliff_stairs_stone_tr.png')
st_bl = load('cliff_stairs_stone_bl.png')
st_br = load('cliff_stairs_stone_br.png')
scene.paste(st_tl, (4 * 16, 4 * 16), st_tl)
scene.paste(st_tr, (5 * 16, 4 * 16), st_tr)
scene.paste(st_bl, (4 * 16, 5 * 16), st_bl)
scene.paste(st_br, (5 * 16, 5 * 16), st_br)

# Section 3: Mid-left (x=6..10)
paste_cliff(6, 10)

# Section 4: Wood Stairs (x=11..12)
wd_tl = load('cliff_stairs_wood_tl.png')
wd_tr = load('cliff_stairs_wood_tr.png')
wd_bl = load('cliff_stairs_wood_bl.png')
wd_br = load('cliff_stairs_wood_br.png')
scene.paste(wd_tl, (11 * 16, 4 * 16), wd_tl)
scene.paste(wd_tr, (12 * 16, 4 * 16), wd_tr)
scene.paste(wd_bl, (11 * 16, 5 * 16), wd_bl)
scene.paste(wd_br, (12 * 16, 5 * 16), wd_br)

# Section 5: Mid-right (x=13..16)
paste_cliff(13, 16)

# Section 6: Canyon Ramp (x=17..21)
rl_t = load('cliff_ramp_left_top.png')
rl_b = load('cliff_ramp_left_bot.png')
rr_t = load('cliff_ramp_right_top.png')
rr_b = load('cliff_ramp_right_bot.png')
scene.paste(rl_t, (17 * 16, 4 * 16), rl_t)
scene.paste(rl_b, (17 * 16, 5 * 16), rl_b)
scene.paste(rr_t, (21 * 16, 4 * 16), rr_t)
scene.paste(rr_b, (21 * 16, 5 * 16), rr_b)

# Section 7: Right (x=22..25)
paste_cliff(22, 25)

# Add Player Character standing at top of Stone Stairs entering Plateau
# Stone stairs x=4..5 (px 64..96). Top step is y=4*16=64.
# Center player at x=4.5*16 - 8 = 64, y=4*16 - 12 = 52
shadow = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
sdraw = ImageDraw.Draw(shadow)
sdraw.ellipse((8, 22, 24, 28), fill=(20, 40, 50, 90))
scene.paste(shadow, (68, 48), shadow)
scene.paste(player_im, (68, 40), player_im)

# Second player instance climbing Wood Stairs (for showcase visual comparison)
scene.paste(shadow, (180, 58), shadow)
scene.paste(player_im, (180, 50), player_im)

# Third player instance walking up Canyon Ramp
scene.paste(shadow, (296, 68), shadow)
scene.paste(player_im, (296, 60), player_im)

# Save 1x and 4x
scene.save(os.path.join(BRAIN_DIR, 'cliff_scene_preview.png'))
scene_4x = scene.resize((scene.width * 4, scene.height * 4), Image.NEAREST)
scene_4x.save(os.path.join(BRAIN_DIR, 'cliff_scene_preview_4x.png'))
print("Saved cliff_scene_preview_4x.png (", scene_4x.size, ")")

# 2. Build multi-panel showcase comparison image
# Panel size: 1000 x 720
showcase = Image.new('RGB', (1000, 720), (10, 18, 30))
sdraw = ImageDraw.Draw(showcase)

# Banner Header
sdraw.rectangle((0, 0, 1000, 60), fill=(14, 25, 41))
sdraw.line((0, 60, 1000, 60), fill=(45, 85, 125))

# Title text placeholder using draw.text
sdraw.text((24, 14), "STRANDED - HIGHER GROUND ELEVATION ACCESS SHOWCASE", fill=(240, 246, 252))
sdraw.text((24, 34), "Seamless 32px Volumetric Rock Cliffs * Carved Stone Stairs * Rustic Timber Stairs * Canyon Ramp", fill=(188, 142, 56))

# Top View: Panoramic scene (scaled 2x to fit 832 x 448)
scene_2x = scene.resize((SW * 16 * 2, SH * 16 * 2), Image.NEAREST)
showcase.paste(scene_2x, (84, 80))

# Framing around scene
sdraw.rectangle((82, 78, 84 + scene_2x.width + 1, 80 + scene_2x.height + 1), outline=(45, 85, 125), width=2)

# Bottom Zoom Highlights (3 zoomed crops at 4x scale)
# Crop 1: Stone stairs (x=60..105, y=36..100) -> 45x64 px -> 180x256 px
crop1 = scene.crop((56, 36, 104, 100)).resize((192, 256), Image.NEAREST)
# Crop 2: Wood stairs (x=168..216, y=36..100)
crop2 = scene.crop((168, 36, 216, 100)).resize((192, 256), Image.NEAREST)
# Crop 3: Canyon ramp (x=268..348, y=36..100)
crop3 = scene.crop((272, 36, 344, 100)).resize((216, 192), Image.NEAREST)

# Labels below main panorama
y_lbl = 80 + scene_2x.height + 14
sdraw.text((84, y_lbl), "[1] Carved Stone Stairs (Left)  |  [2] Timber Survivor Stairs (Center)  |  [3] Canyon Incline Ramp (Right)", fill=(25, 200, 221))
sdraw.text((84, y_lbl + 20), "Result: Zero cave assets. 100% natural, readable vertical elevation traversal between Lowlands and Highland Plateau.", fill=(139, 158, 179))

showcase.save(os.path.join(BRAIN_DIR, 'cliff_elevation_showcase.png'))
print("Saved cliff_elevation_showcase.png")
