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

SW, SH = 26, 16
scene = Image.new('RGBA', (SW * 16, SH * 16))

# Base ground
for y in range(SH):
    for x in range(SW):
        if 11 <= x <= 13:
            scene.paste(dirt_im, (x * 16, y * 16))
        else:
            scene.paste(grass_im, (x * 16, y * 16))

# West cliff wall at x=3
w_t = load('cliff_side_w_top.png')
w_b = load('cliff_side_w_bot.png')
scene.paste(w_t, (3 * 16, 2 * 16), w_t)
scene.paste(w_b, (3 * 16, 3 * 16), w_b)
scene.paste(w_t, (3 * 16, 4 * 16), w_t)
scene.paste(w_b, (3 * 16, 5 * 16), w_b)

# SW Corner at x=3, rows 6 & 7
sw_t = load('cliff_corner_sw_top.png')
sw_b = load('cliff_corner_sw_bot.png')
scene.paste(sw_t, (3 * 16, 6 * 16), sw_t)
scene.paste(sw_b, (3 * 16, 7 * 16), sw_b)

# South cliff face (left: x=4..10)
top1 = load('cliff_face_top_01.png')
top2 = load('cliff_face_top_02.png')
bot1 = load('cliff_face_bot_01.png')
bot2 = load('cliff_face_bot_02.png')
for x in range(4, 11):
    t = top1 if x % 2 == 0 else top2
    b = bot1 if x % 2 == 0 else bot2
    scene.paste(t, (x * 16, 6 * 16), t)
    scene.paste(b, (x * 16, 7 * 16), b)

# Natural Mud Ramp (x=11..13, rows 6 & 7) - NO STEPS, JUS MUD!
rl_t = load('cliff_ramp_left_top.png')
rl_b = load('cliff_ramp_left_bot.png')
rr_t = load('cliff_ramp_right_top.png')
rr_b = load('cliff_ramp_right_bot.png')
scene.paste(rl_t, (11 * 16, 6 * 16), rl_t)
scene.paste(rl_b, (11 * 16, 7 * 16), rl_b)
scene.paste(rr_t, (13 * 16, 6 * 16), rr_t)
scene.paste(rr_b, (13 * 16, 7 * 16), rr_b)

# South cliff face (right: x=14..21)
for x in range(14, 22):
    t = top1 if x % 2 == 0 else top2
    b = bot1 if x % 2 == 0 else bot2
    scene.paste(t, (x * 16, 6 * 16), t)
    scene.paste(b, (x * 16, 7 * 16), b)

# SE Corner at x=22, rows 6 & 7
se_t = load('cliff_corner_se_top.png')
se_b = load('cliff_corner_se_bot.png')
scene.paste(se_t, (22 * 16, 6 * 16), se_t)
scene.paste(se_b, (22 * 16, 7 * 16), se_b)

# East cliff wall at x=22
e_t = load('cliff_side_e_top.png')
e_b = load('cliff_side_e_bot.png')
scene.paste(e_t, (22 * 16, 4 * 16), e_t)
scene.paste(e_b, (22 * 16, 5 * 16), e_b)
scene.paste(e_t, (22 * 16, 2 * 16), e_t)
scene.paste(e_b, (22 * 16, 3 * 16), e_b)

# Character Aash walking up the mud ramp into the high ground
shadow = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
sdraw = ImageDraw.Draw(shadow)
sdraw.ellipse((8, 22, 24, 28), fill=(20, 40, 50, 90))

# Player ascending the natural mud ramp
scene.paste(shadow, (12 * 16 - 8, int(6.5 * 16) - 12), shadow)
scene.paste(player_im, (12 * 16 - 8, int(6.5 * 16) - 20), player_im)

# Player exploring the highland meadow
scene.paste(shadow, (7 * 16 - 8, 3 * 16 - 12), shadow)
scene.paste(player_im, (7 * 16 - 8, 3 * 16 - 20), player_im)

# Save scene
scene.save(os.path.join(BRAIN_DIR, 'cliff_scene_preview.png'))
scene_4x = scene.resize((scene.width * 4, scene.height * 4), Image.NEAREST)
scene_4x.save(os.path.join(BRAIN_DIR, 'cliff_scene_preview_4x.png'))

# Build presentation showcase
showcase = Image.new('RGB', (1020, 780), (10, 18, 30))
sdraw = ImageDraw.Draw(showcase)

# Banner
sdraw.rectangle((0, 0, 1020, 60), fill=(14, 25, 41))
sdraw.line((0, 60, 1020, 60), fill=(45, 85, 125))
sdraw.text((24, 14), "STRANDED - NATURAL MUD ELEVATION & IMPROVED CLIFF FLANKS", fill=(240, 246, 252))
sdraw.text((24, 34), "Pure Earthen Mud Incline (No Steps/Stairs) * Chunky Volumetric West & East Flanks * Seamless 90 Outer Corners", fill=(188, 142, 56))

# Main Panorama View (scaled 2x: 832 x 512)
scene_2x = scene.resize((SW * 16 * 2, SH * 16 * 2), Image.NEAREST)
showcase.paste(scene_2x, (94, 80))
sdraw.rectangle((92, 78, 94 + scene_2x.width + 1, 80 + scene_2x.height + 1), outline=(45, 85, 125), width=2)

# Highlights footer
y_lbl = 80 + scene_2x.height + 16
sdraw.text((94, y_lbl), "[Left] Chunky West Wall (Col 3)  |  [Center] 100% Pure Mud Incline Ramp (Cols 11..13)  |  [Right] Chunky East Wall (Col 22)", fill=(25, 200, 221))
sdraw.text((94, y_lbl + 22), "Status: Zero stairs/steps. Zero cave assets. 100% authentic Stardew-inspired natural earthen elevation traversal.", fill=(139, 158, 179))

showcase_path = os.path.join(BRAIN_DIR, 'cliff_mud_elevation_showcase.png')
showcase.save(showcase_path)
print("Saved showcase to:", showcase_path)
