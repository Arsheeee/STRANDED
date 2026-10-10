import os
import math
import uuid
from PIL import Image, ImageDraw

CLIFFS_DIR = r'd:\Unity\Projects\STRANDED\Assets\Art\Terrain\Cliffs'
BRAIN_DIR = r'C:\Users\PAVILION\.gemini\antigravity-ide\brain\84db0e2d-58d2-466d-be05-dbff8f133035'

# Palette Definitions
# Stone Stairs (Slate & River Rock tones)
ST_HI     = (200, 212, 205, 255) # Sunlit top edge of stone step (#c8d4cd)
ST_MID    = (148, 162, 153, 255) # Main stone tread surface (#94a299)
ST_DARK   = (102, 115, 108, 255) # Shaded stone body (#66736c)
ST_RISER  = (65, 75, 70, 255)    # Step riser drop shadow (#414b46)
ST_DEEP   = (38, 45, 42, 255)    # Deep crevice between steps (#262d2a)

# Wood Stairs (Survivor Timber / Driftwood tones)
WD_HI     = (225, 172, 78, 255)  # Sunlit wooden plank edge (#e1ac4e)
WD_MID    = (185, 130, 48, 255)  # Golden timber tread body (#b98230)
WD_DARK   = (138, 90, 28, 255)   # Shaded wood grain (#8a5a1c)
WD_RISER  = (92, 56, 16, 255)    # Timber riser drop shadow (#5c3810)
WD_DEEP   = (48, 28, 8, 255)     # Deep shadow underneath planks (#301c08)

# Post / Balustrade
POST_HI   = (165, 115, 42, 255)
POST_MID  = (125, 80, 24, 255)
POST_DARK = (75, 45, 12, 255)

# Cliff Rock & Grass colors for trims
C_ROCK_HI   = (164, 122, 48, 255)
C_ROCK_MID  = (135, 99, 38, 255)
C_ROCK_DARK = (108, 78, 30, 255)
C_SHADOW    = (84, 59, 23, 255)
C_CREVICE   = (58, 40, 16, 255)
C_DARKEST   = (38, 25, 11, 255)
G_MID       = (68, 163, 24, 255)
G_LUSH      = (48, 122, 42, 255)
G_HI        = (114, 224, 65, 255)

def new_tile():
    return Image.new('RGBA', (16, 16), (0, 0, 0, 0))

print("Crafting High-Ground Access Stairways & Incline Ramps...")

# ====================================================================
# 1. CARVED STONE STAIRCASE (2 Tiles Wide x 2 Tiles High = 32x32 px)
# ====================================================================
# A 32-pixel high grand stone staircase built into the cliff face!
# In 32 pixels, there are 8 distinct steps (4 steps per tile, 4px height each).
# Each step has:
#   - Row 0: Highlight edge (ST_HI)
#   - Row 1-2: Step tread surface (ST_MID)
#   - Row 3: Step riser & deep shadow (ST_RISER & ST_DEEP)
# Flanked on the left and right by stone balustrade / retaining rock trim!

def render_stone_stairs_32():
    w32 = Image.new('RGBA', (32, 32), (0, 0, 0, 0))

    # Total 8 steps across y=0..31 (y=0..3, y=4..7, y=8..11, y=12..15, y=16..19, y=20..23, y=24..27, y=28..31)
    for step_idx in range(8):
        sy = step_idx * 4
        # Left stone rail (x=0..3)
        for dy in range(4):
            y = sy + dy
            w32.putpixel((0, y), C_CREVICE)
            w32.putpixel((1, y), C_ROCK_MID if dy == 0 else C_ROCK_DARK)
            w32.putpixel((2, y), C_ROCK_HI if dy == 0 else C_ROCK_MID)
            w32.putpixel((3, y), C_CREVICE)

        # Right stone rail (x=28..31)
        for dy in range(4):
            y = sy + dy
            w32.putpixel((28, y), C_CREVICE)
            w32.putpixel((29, y), C_ROCK_HI if dy == 0 else C_ROCK_MID)
            w32.putpixel((30, y), C_ROCK_MID if dy == 0 else C_ROCK_DARK)
            w32.putpixel((31, y), C_CREVICE)

        # Center Stone Steps (x=4..27)
        # Row 0 of step: Sunlit edge highlight
        for x in range(4, 28):
            w32.putpixel((x, sy), ST_HI if (x + step_idx) % 3 != 0 else ST_MID)

        # Row 1: Main stone tread
        for x in range(4, 28):
            w32.putpixel((x, sy + 1), ST_MID if (x * 7 + step_idx) % 4 != 0 else ST_DARK)

        # Row 2: Shaded stone tread
        for x in range(4, 28):
            w32.putpixel((x, sy + 2), ST_DARK)

        # Row 3: Riser drop shadow
        for x in range(4, 28):
            w32.putpixel((x, sy + 3), ST_RISER if x % 2 == 0 else ST_DEEP)

    # Top step connects to upper plateau: grass overlap on row 0 at rails
    w32.putpixel((1, 0), G_MID); w32.putpixel((2, 0), G_HI)
    w32.putpixel((29, 0), G_HI); w32.putpixel((30, 0), G_MID)

    # Bottom ground contact shadow on row 31
    for x in range(32):
        w32.putpixel((x, 31), ST_DEEP)

    # Slice into 4 tiles (16x16 each): TL, TR, BL, BR
    tl = w32.crop((0, 0, 16, 16))
    tr = w32.crop((16, 0, 32, 16))
    bl = w32.crop((0, 16, 16, 32))
    br = w32.crop((16, 16, 32, 32))
    return tl, tr, bl, br, w32

st_tl, st_tr, st_bl, st_br, st_w32 = render_stone_stairs_32()
st_tl.save(os.path.join(CLIFFS_DIR, 'cliff_stairs_stone_tl.png'))
st_tr.save(os.path.join(CLIFFS_DIR, 'cliff_stairs_stone_tr.png'))
st_bl.save(os.path.join(CLIFFS_DIR, 'cliff_stairs_stone_bl.png'))
st_br.save(os.path.join(CLIFFS_DIR, 'cliff_stairs_stone_br.png'))


# ====================================================================
# 2. RUSTIC WOODEN SURVIVOR STAIRS (2 Tiles Wide x 2 Tiles High = 32x32 px)
# ====================================================================
# Built from island timbers / logs, perfect for the "STRANDED" theme!
# Heavy split-log treads with wooden support stakes on left and right.

def render_wood_stairs_32():
    w32 = Image.new('RGBA', (32, 32), (0, 0, 0, 0))

    # 8 wooden plank steps across y=0..31
    for step_idx in range(8):
        sy = step_idx * 4

        # Left wooden timber post (x=0..3)
        for dy in range(4):
            y = sy + dy
            w32.putpixel((0, y), WD_DEEP)
            w32.putpixel((1, y), POST_MID if dy == 0 else POST_DARK)
            w32.putpixel((2, y), POST_HI if dy == 0 else POST_MID)
            w32.putpixel((3, y), WD_RISER)

        # Right wooden timber post (x=28..31)
        for dy in range(4):
            y = sy + dy
            w32.putpixel((28, y), WD_RISER)
            w32.putpixel((29, y), POST_HI if dy == 0 else POST_MID)
            w32.putpixel((30, y), POST_MID if dy == 0 else POST_DARK)
            w32.putpixel((31, y), WD_DEEP)

        # Center Wooden Planks (x=4..27)
        # Row 0: Highlighted timber top edge
        for x in range(4, 28):
            w32.putpixel((x, sy), WD_HI if (x + step_idx) % 3 != 0 else WD_MID)

        # Row 1: Warm wood grain surface
        for x in range(4, 28):
            w32.putpixel((x, sy + 1), WD_MID if (x * 5 + step_idx) % 4 != 0 else WD_DARK)

        # Row 2: Shaded timber grain
        for x in range(4, 28):
            w32.putpixel((x, sy + 2), WD_DARK)

        # Row 3: Deep shadow under plank
        for x in range(4, 28):
            w32.putpixel((x, sy + 3), WD_RISER if x % 2 == 0 else WD_DEEP)

        # Peg / nail details at x=6 and x=25
        w32.putpixel((6, sy + 1), WD_DEEP)
        w32.putpixel((25, sy + 1), WD_DEEP)

    # Slice into 4 tiles
    tl = w32.crop((0, 0, 16, 16))
    tr = w32.crop((16, 0, 32, 16))
    bl = w32.crop((0, 16, 16, 32))
    br = w32.crop((16, 16, 32, 32))
    return tl, tr, bl, br, w32

wd_tl, wd_tr, wd_bl, wd_br, wd_w32 = render_wood_stairs_32()
wd_tl.save(os.path.join(CLIFFS_DIR, 'cliff_stairs_wood_tl.png'))
wd_tr.save(os.path.join(CLIFFS_DIR, 'cliff_stairs_wood_tr.png'))
wd_bl.save(os.path.join(CLIFFS_DIR, 'cliff_stairs_wood_bl.png'))
wd_br.save(os.path.join(CLIFFS_DIR, 'cliff_stairs_wood_br.png'))


# ====================================================================
# 3. SINGLE-TILE COMPACT STONE STEPS (16 Wide x 32 High = 1x2 Tiles)
# ====================================================================
# Compact 1-tile wide mountain stairway!
def render_single_stone_stairs():
    w32 = Image.new('RGBA', (16, 32), (0, 0, 0, 0))
    for step_idx in range(8):
        sy = step_idx * 4
        # Rails at x=0..1 and x=14..15
        for dy in range(4):
            y = sy + dy
            w32.putpixel((0, y), C_CREVICE); w32.putpixel((1, y), C_ROCK_MID)
            w32.putpixel((14, y), C_ROCK_MID); w32.putpixel((15, y), C_CREVICE)
        # Steps at x=2..13
        for x in range(2, 14):
            w32.putpixel((x, sy), ST_HI)
            w32.putpixel((x, sy + 1), ST_MID)
            w32.putpixel((x, sy + 2), ST_DARK)
            w32.putpixel((x, sy + 3), ST_RISER)

    top = w32.crop((0, 0, 16, 16))
    bot = w32.crop((0, 16, 16, 32))
    return top, bot

st_s_top, st_s_bot = render_single_stone_stairs()
st_s_top.save(os.path.join(CLIFFS_DIR, 'cliff_stairs_single_top.png'))
st_s_bot.save(os.path.join(CLIFFS_DIR, 'cliff_stairs_single_bot.png'))

print("Stairway assets created successfully!")

# Generate .meta files for newly created stair sprites
template = '''fileFormatVersion: 2
guid: {guid}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: []
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
  ignoreMipmapLimit: 0
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
  spritePivot: {{x: 0.5, y: 0.5}}
  spritePixelsToUnits: 16
  spriteBorder: {{x: 0, y: 0, z: 0, w: 0}}
  spriteGenerateFallbackPhysicsShape: 1
  alphaIsTransparency: 1
  spriteChildren: []
  alphaTestReferenceValue: 0.5
  platformSettings: []
  spritePackingTag: 
  pVRTCHeaderVersion: 0
  colorCorrection: 0
  swizzle: 0
'''

stair_files = [
    'cliff_stairs_stone_tl.png', 'cliff_stairs_stone_tr.png', 'cliff_stairs_stone_bl.png', 'cliff_stairs_stone_br.png',
    'cliff_stairs_wood_tl.png', 'cliff_stairs_wood_tr.png', 'cliff_stairs_wood_bl.png', 'cliff_stairs_wood_br.png',
    'cliff_stairs_single_top.png', 'cliff_stairs_single_bot.png'
]

for sf in stair_files:
    mp = os.path.join(CLIFFS_DIR, sf + '.meta')
    if not os.path.exists(mp):
        with open(mp, 'w') as f:
            f.write(template.format(guid=uuid.uuid4().hex))
        print(f"Created {sf}.meta")

# ====================================================================
# 4. RENDER NEW SHOWCASE DEMO SCENE (cliff_scene_preview.png)
# ====================================================================
# Featuring:
# - Upper Plateau (High Ground)
# - Continuous 2-Tile High Cliff Wall
# - Carved Stone Staircase (Stone Stairs climbing up)
# - Rustic Wooden Survivor Staircase (Timber Stairs climbing up)
# - Natural Canyon Ramp Cut
# - Player Aash climbing onto the higher ground!

SW, SH = 26, 14
scene = Image.new('RGBA', (SW * 16, SH * 16), (68, 163, 24, 255))

grass_base = Image.open(r'd:\Unity\Projects\STRANDED\Assets\Art\Terrain\Grass\grass_base_01.png').convert('RGBA')
dirt_base  = Image.open(r'd:\Unity\Projects\STRANDED\Assets\Art\Terrain\Dirt\mud_base_01.png').convert('RGBA')
cliff_t1   = Image.open(os.path.join(CLIFFS_DIR, 'cliff_face_top_01.png')).convert('RGBA')
cliff_t2   = Image.open(os.path.join(CLIFFS_DIR, 'cliff_face_top_02.png')).convert('RGBA')
cliff_b1   = Image.open(os.path.join(CLIFFS_DIR, 'cliff_face_bot_01.png')).convert('RGBA')
cliff_b2   = Image.open(os.path.join(CLIFFS_DIR, 'cliff_face_bot_02.png')).convert('RGBA')

# 1. Base Ground (Grass everywhere, with dirt paths approaching the stairs & ramp)
for y in range(SH):
    for x in range(SW):
        # Path leading to Stone Stairs at x=5..6
        if 5 <= x <= 6 and (y >= 6 or y <= 3):
            scene.alpha_composite(dirt_base, (x * 16, y * 16))
        # Path leading to Wooden Stairs at x=13..14
        elif 13 <= x <= 14 and (y >= 6 or y <= 3):
            scene.alpha_composite(dirt_base, (x * 16, y * 16))
        # Path leading to Canyon Ramp at x=20..22
        elif 20 <= x <= 22:
            scene.alpha_composite(dirt_base, (x * 16, y * 16))
        else:
            scene.alpha_composite(grass_base, (x * 16, y * 16))

# 2. Canyon vertical walls at x=19 and x=23 (rows 0..3)
side_w = Image.open(os.path.join(CLIFFS_DIR, 'cliff_side_w.png')).convert('RGBA')
side_e = Image.open(os.path.join(CLIFFS_DIR, 'cliff_side_e.png')).convert('RGBA')
for y in range(4):
    scene.alpha_composite(side_w, (19 * 16, y * 16))
    scene.alpha_composite(side_e, (23 * 16, y * 16))

# 3. Horizontal Cliff Wall at rows 4 and 5
for x in range(SW):
    t = cliff_t1 if x % 2 == 0 else cliff_t2
    b = cliff_b1 if x % 2 == 0 else cliff_b2

    if 5 <= x <= 6:
        # Stone Stairs!
        if x == 5:
            scene.alpha_composite(st_tl, (x * 16, 4 * 16))
            scene.alpha_composite(st_bl, (x * 16, 5 * 16))
        else:
            scene.alpha_composite(st_tr, (x * 16, 4 * 16))
            scene.alpha_composite(st_br, (x * 16, 5 * 16))
    elif 13 <= x <= 14:
        # Wooden Survivor Stairs!
        if x == 13:
            scene.alpha_composite(wd_tl, (x * 16, 4 * 16))
            scene.alpha_composite(wd_bl, (x * 16, 5 * 16))
        else:
            scene.alpha_composite(wd_tr, (x * 16, 4 * 16))
            scene.alpha_composite(wd_br, (x * 16, 5 * 16))
    elif x == 19:
        # Ramp Left Shoulder
        rmp_lt = Image.open(os.path.join(CLIFFS_DIR, 'cliff_ramp_left_top.png')).convert('RGBA')
        rmp_lb = Image.open(os.path.join(CLIFFS_DIR, 'cliff_ramp_left_bot.png')).convert('RGBA')
        scene.alpha_composite(rmp_lt, (x * 16, 4 * 16))
        scene.alpha_composite(rmp_lb, (x * 16, 5 * 16))
    elif 20 <= x <= 22:
        # Ramp open dirt passage
        pass
    elif x == 23:
        # Ramp Right Shoulder
        rmp_rt = Image.open(os.path.join(CLIFFS_DIR, 'cliff_ramp_right_top.png')).convert('RGBA')
        rmp_rb = Image.open(os.path.join(CLIFFS_DIR, 'cliff_ramp_right_bot.png')).convert('RGBA')
        scene.alpha_composite(rmp_rt, (x * 16, 4 * 16))
        scene.alpha_composite(rmp_rb, (x * 16, 5 * 16))
    else:
        # Standard seamless cliff wall
        scene.alpha_composite(t, (x * 16, 4 * 16))
        scene.alpha_composite(b, (x * 16, 5 * 16))

# 4. Player Character walking up the Stone Stairs to the Higher Ground!
player_im = Image.open(r'd:\Unity\Projects\STRANDED\Assets\player\player_base.png').convert('RGBA')
player_idle = player_im.crop((0, 0, 32, 32))
shadow = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
draw = ImageDraw.Draw(shadow)
draw.ellipse([8, 26, 24, 31], fill=(20, 40, 50, 90))

# Place Player on the upper steps / top of Stone Stairs at x=5.5, y=3.2
px = int(5.5 * 16 - 8)
py = int(3.2 * 16 - 12)
scene.alpha_composite(shadow, (px, py))
scene.alpha_composite(player_idle, (px, py))

# Save 1x and 4x
out_1x = os.path.join(BRAIN_DIR, 'cliff_scene_preview.png')
scene.save(out_1x)

out_4x = os.path.join(BRAIN_DIR, 'cliff_scene_preview_4x.png')
scene.resize((scene.width * 4, scene.height * 4), Image.NEAREST).save(out_4x)

print(f"Saved: {out_1x}")
print(f"Saved: {out_4x}")
