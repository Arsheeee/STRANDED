import os
import uuid
from PIL import Image

TEMPLATE_META = """fileFormatVersion: 2
guid: {GUID}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {{}}
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
  alphaUsage: 1
  alphaIsTransparency: 1
  spriteTessellationDetail: -1
  textureType: 8
  textureShape: 1
  singleChannelComponent: 0
  flipbookRows: 1
  flipbookColumns: 1
  maxTextureSizeSet: 0
  compressionQualitySet: 0
  textureFormatSet: 0
  ignorePngGamma: 0
  applyGammaDecoding: 0
  swizzle: 50462976
  cookieLightType: 0
  platformSettings:
  - serializedVersion: 4
    buildTarget: DefaultTexturePlatform
    maxTextureSize: 2048
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 0
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  - serializedVersion: 4
    buildTarget: Standalone
    maxTextureSize: 2048
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 0
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  - serializedVersion: 4
    buildTarget: WebGL
    maxTextureSize: 2048
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 0
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  spriteSheet:
    serializedVersion: 2
    sprites: []
    outline: []
    customData: 
    physicsShape: []
    bones: []
    spriteID: 5e97eb03825dee720800000000000000
    internalID: 0
    vertices: []
    indices: 
    edges: []
    weights: []
    secondaryTextures: []
    spriteCustomMetadata:
      entries: []
    nameFileIdTable: {{}}
  mipmapLimitGroupName: 
  pSDRemoveMatte: 0
  userData: 
  assetBundleName: 
  assetBundleVariant: 
"""

def save_sprite(filepath, img):
    img.save(filepath, "PNG")
    meta_path = filepath + ".meta"
    if not os.path.exists(meta_path):
        guid = uuid.uuid4().hex
        with open(meta_path, "w") as f:
            f.write(TEMPLATE_META.replace("{GUID}", guid))
    print(f"Saved: {filepath}")

# 1. item_shaped_wood.png (Curved carved wooden boat plank / rib)
def gen_shaped_wood():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    p = im.load()
    # Curved boat rib timber with beveled edges
    # Wood palette: Dark (60, 36, 15), Mid (120, 75, 32), Light (175, 115, 55), Highlight (210, 150, 85)
    pixels = [
        # (x, y, color)
        (2, 13, (60, 36, 15, 255)), (3, 13, (120, 75, 32, 255)), (4, 13, (120, 75, 32, 255)), (5, 13, (60, 36, 15, 255)),
        (2, 12, (60, 36, 15, 255)), (3, 12, (175, 115, 55, 255)), (4, 12, (175, 115, 55, 255)), (5, 12, (60, 36, 15, 255)),
        (3, 11, (60, 36, 15, 255)), (4, 11, (175, 115, 55, 255)), (5, 11, (210, 150, 85, 255)), (6, 11, (60, 36, 15, 255)),
        (3, 10, (60, 36, 15, 255)), (4, 10, (175, 115, 55, 255)), (5, 10, (210, 150, 85, 255)), (6, 10, (60, 36, 15, 255)),
        (4, 9, (60, 36, 15, 255)), (5, 9, (175, 115, 55, 255)), (6, 9, (210, 150, 85, 255)), (7, 9, (60, 36, 15, 255)),
        (5, 8, (60, 36, 15, 255)), (6, 8, (175, 115, 55, 255)), (7, 8, (210, 150, 85, 255)), (8, 8, (60, 36, 15, 255)),
        (6, 7, (60, 36, 15, 255)), (7, 7, (175, 115, 55, 255)), (8, 7, (210, 150, 85, 255)), (9, 7, (60, 36, 15, 255)),
        (7, 6, (60, 36, 15, 255)), (8, 6, (175, 115, 55, 255)), (9, 6, (210, 150, 85, 255)), (10, 6, (60, 36, 15, 255)),
        (8, 5, (60, 36, 15, 255)), (9, 5, (175, 115, 55, 255)), (10, 5, (210, 150, 85, 255)), (11, 5, (60, 36, 15, 255)),
        (9, 4, (60, 36, 15, 255)), (10, 4, (175, 115, 55, 255)), (11, 4, (210, 150, 85, 255)), (12, 4, (60, 36, 15, 255)),
        (10, 3, (60, 36, 15, 255)), (11, 3, (175, 115, 55, 255)), (12, 3, (210, 150, 85, 255)), (13, 3, (60, 36, 15, 255)),
        (11, 2, (60, 36, 15, 255)), (12, 2, (120, 75, 32, 255)), (13, 2, (60, 36, 15, 255)),
    ]
    for x, y, col in pixels:
        p[x, y] = col
    return im

# 2. item_wooden_pegs.png (Bundle of 3 wooden pegs/dowels with fiber ties)
def gen_wooden_pegs():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    p = im.load()
    c_dark = (55, 32, 12, 255)
    c_mid = (130, 82, 36, 255)
    c_light = (195, 135, 65, 255)
    c_hi = (225, 170, 95, 255)
    c_tie = (85, 130, 45, 255) # vine tie
    # Peg 1 (left)
    for y in range(4, 13):
        p[4, y] = c_dark
        p[5, y] = c_light if y < 11 else c_mid
        p[6, y] = c_dark
    p[5, 13] = c_dark # pointed tip
    # Peg 2 (middle, slightly offset)
    for y in range(3, 12):
        p[7, y] = c_dark
        p[8, y] = c_hi if y < 10 else c_light
        p[9, y] = c_dark
    p[8, 12] = c_dark
    # Peg 3 (right)
    for y in range(5, 14):
        p[10, y] = c_dark
        p[11, y] = c_light if y < 12 else c_mid
        p[12, y] = c_dark
    p[11, 14] = c_dark
    # Vine cord binding them in middle
    for x in range(4, 13):
        p[x, 8] = c_tie
    p[8, 7] = c_tie
    return im

# 3. item_strong_rope.png (Coiled rope of fiber and vines)
def gen_strong_rope():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    p = im.load()
    r_dk = (50, 45, 20, 255)
    r_mid = (145, 130, 60, 255)
    r_lt = (195, 180, 95, 255)
    v_grn = (85, 135, 45, 255)
    # Circular coil
    for x in range(3, 13):
        for y in range(3, 13):
            dx = x - 7.5
            dy = y - 7.5
            dist = (dx*dx + dy*dy)**0.5
            if 3.2 <= dist <= 5.5:
                # Braided alternating fiber / vine
                if (x + y) % 3 == 0:
                    p[x, y] = v_grn
                elif (x + y) % 2 == 0:
                    p[x, y] = r_lt
                else:
                    p[x, y] = r_mid
            elif 5.5 < dist <= 6.5 or 2.2 <= dist < 3.2:
                p[x, y] = r_dk
    # Trailing rope end
    p[12, 13] = r_dk
    p[13, 13] = r_mid
    p[14, 14] = v_grn
    return im

# 4. item_reinforced_rope.png (Heavy nautical coil with thick bands)
def gen_reinforced_rope():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    p = im.load()
    c_out = (35, 30, 15, 255)
    c_main = (120, 105, 50, 255)
    c_hi = (175, 160, 80, 255)
    c_band = (45, 80, 30, 255) # dark vine lashings
    for x in range(2, 14):
        for y in range(2, 14):
            dx = x - 7.5
            dy = y - 7.5
            dist = (dx*dx + dy*dy)**0.5
            if 2.8 <= dist <= 6.0:
                if x in (4, 11) or y in (4, 11):
                    p[x, y] = c_band # Reinforcement band
                elif (x * 2 + y) % 3 == 0:
                    p[x, y] = c_hi
                else:
                    p[x, y] = c_main
            elif 6.0 < dist <= 6.8 or 2.0 <= dist < 2.8:
                p[x, y] = c_out
    p[13, 13] = c_main
    p[14, 13] = c_band
    p[14, 14] = c_out
    return im

# 5. item_woven_sailcloth.png (Folded roll of natural sail canvas fabric)
def gen_woven_sailcloth():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    p = im.load()
    c_edge = (90, 80, 60, 255)
    c_cloth = (215, 205, 175, 255)
    c_cloth_hi = (240, 235, 210, 255)
    c_cloth_sh = (170, 160, 135, 255)
    c_tie = (65, 110, 45, 255)
    # Rolled fabric cylinder diagonally
    for i in range(11):
        x = 3 + i
        for dy in range(6):
            y = 5 + dy
            if dy == 0 or dy == 5 or i == 0 or i == 10:
                p[x, y] = c_edge
            elif dy == 1:
                p[x, y] = c_cloth_hi
            elif dy in (2, 3):
                p[x, y] = c_cloth if (x + y)%2 == 0 else c_cloth_sh # woven texture
            else:
                p[x, y] = c_cloth_sh
    # Vine tie around middle
    p[8, 4] = c_edge
    p[8, 5] = c_tie
    p[8, 6] = c_tie
    p[8, 7] = c_tie
    p[8, 8] = c_tie
    p[8, 9] = c_tie
    p[8, 10] = c_edge
    p[9, 11] = c_tie # tie knot
    return im

# 6. item_reinforced_joints.png (Cross wooden joint with pegged dowels and cord)
def gen_reinforced_joints():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    p = im.load()
    c_dk = (50, 30, 12, 255)
    c_mid = (130, 80, 35, 255)
    c_hi = (185, 120, 55, 255)
    c_rope = (150, 135, 70, 255)
    c_peg = (220, 165, 90, 255)
    # Vertical timber
    for y in range(2, 14):
        p[6, y] = c_dk
        p[7, y] = c_hi
        p[8, y] = c_mid
        p[9, y] = c_dk
    # Horizontal timber
    for x in range(2, 14):
        p[x, 6] = c_dk
        p[x, 7] = c_hi
        p[x, 8] = c_mid
        p[x, 9] = c_dk
    # Lashing rope criss-cross at intersection
    for dx in range(6, 10):
        for dy in range(6, 10):
            if (dx == dy) or (dx + dy == 15):
                p[dx, dy] = c_rope
            else:
                p[dx, dy] = c_peg
    return im

# 7. item_paddle.png (Smooth wooden canoe paddle with blade and handle)
def gen_paddle():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    p = im.load()
    c_dk = (55, 32, 12, 255)
    c_mid = (140, 85, 35, 255)
    c_hi = (200, 135, 65, 255)
    # Shaft diagonally from (2, 13) to (9, 6)
    pts = [(2, 13), (3, 12), (4, 11), (5, 10), (6, 9), (7, 8), (8, 7), (9, 6)]
    for x, y in pts:
        p[x, y] = c_hi
        p[x-1, y] = c_dk
        p[x, y+1] = c_dk
    # T-grip at bottom
    p[1, 14] = c_dk
    p[2, 14] = c_mid
    p[3, 14] = c_dk
    # Wide paddle blade from (10, 5) to (14, 1)
    blade = [
        (9, 5, c_dk), (10, 5, c_hi), (10, 6, c_dk),
        (10, 4, c_dk), (11, 4, c_hi), (11, 5, c_mid), (12, 5, c_dk),
        (11, 3, c_dk), (12, 3, c_hi), (12, 4, c_mid), (13, 4, c_dk),
        (12, 2, c_dk), (13, 2, c_hi), (13, 3, c_mid), (14, 3, c_dk),
        (13, 1, c_dk), (14, 1, c_mid), (14, 2, c_dk),
        (14, 0, c_dk), (15, 1, c_dk)
    ]
    for x, y, c in blade:
        if 0 <= x < 16 and 0 <= y < 16:
            p[x, y] = c
    return im

# 8. item_wind_assembly.png (Triangular sail, yardarm spar, stay ropes)
def gen_wind_assembly():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    p = im.load()
    c_wood_dk = (50, 30, 12, 255)
    c_wood = (140, 85, 35, 255)
    c_cloth = (220, 210, 180, 255)
    c_cloth_hi = (245, 240, 215, 255)
    c_cloth_sh = (175, 165, 140, 255)
    c_rope = (90, 130, 55, 255)
    # Mast/Spar timber diagonal from (2, 14) to (13, 2)
    for i in range(12):
        x = 2 + i
        y = 14 - i
        p[x, y] = c_wood
        if y + 1 < 16: p[x, y+1] = c_wood_dk
    # Triangular billowed sailcloth hanging below spar
    for y in range(4, 13):
        # Sail span
        start_x = 14 - y
        end_x = 13
        for x in range(start_x, end_x):
            if x == start_x:
                p[x, y] = c_cloth_sh
            elif x == end_x - 1:
                p[x, y] = c_cloth_sh
            elif (x + y) % 3 == 0:
                p[x, y] = c_cloth_hi
            else:
                p[x, y] = c_cloth
    # Rigging ropes at corners
    p[2, 14] = c_rope
    p[13, 2] = c_rope
    p[13, 13] = c_rope
    p[14, 13] = c_wood_dk
    return im

# 9. item_rope_binding_kit.png (Set of prepared cords, knots, bindings)
def gen_rope_binding_kit():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    p = im.load()
    c_dk = (40, 35, 15, 255)
    c_r1 = (170, 150, 75, 255) # strong rope
    c_r2 = (115, 95, 45, 255) # reinforced rope
    c_vn = (70, 125, 40, 255) # green vine wrap
    # Multiple loops and coils bundled together
    # Left coil
    for x in range(2, 8):
        for y in range(4, 12):
            if x in (2, 7) or y in (4, 11):
                p[x, y] = c_dk
            elif (x + y) % 2 == 0:
                p[x, y] = c_r1
            else:
                p[x, y] = c_vn
    # Right coil
    for x in range(8, 14):
        for y in range(5, 13):
            if x in (8, 13) or y in (5, 12):
                p[x, y] = c_dk
            elif (x + y) % 2 == 0:
                p[x, y] = c_r2
            else:
                p[x, y] = c_r1
    # Binding band around both
    for x in range(4, 12):
        p[x, 8] = c_vn
        p[x, 9] = c_dk
    return im

# 10. item_structural_frame.png (Wooden boat keel and curved ribs)
def gen_structural_frame():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    p = im.load()
    c_dk = (50, 28, 10, 255)
    c_mid = (130, 75, 30, 255)
    c_hi = (185, 120, 55, 255)
    c_peg = (220, 165, 80, 255)
    # Central keel spine (horizontal bottom)
    for x in range(2, 14):
        p[x, 11] = c_hi
        p[x, 12] = c_mid
        p[x, 13] = c_dk
    # 3 Curved rib frames rising up
    for rx in (4, 8, 12):
        for y in range(4, 12):
            p[rx, y] = c_hi
            p[rx-1, y] = c_dk
        p[rx, 4] = c_peg # top peg
        p[rx, 11] = c_peg # joint peg
    # Gunwale upper stringer
    for x in range(3, 13):
        p[x, 5] = c_mid
    return im

# 11. item_reinforced_hull.png (Carved outrigger boat hull with planks and watertight frame)
def gen_reinforced_hull():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    p = im.load()
    c_dk = (45, 24, 8, 255)
    c_sh = (95, 52, 20, 255)
    c_mid = (145, 85, 35, 255)
    c_hi = (205, 135, 65, 255)
    c_lash = (65, 115, 45, 255)
    # Long canoe / outrigger hull shape
    # Bow and stern lifted (y=6 at ends, y=10 in middle)
    for x in range(1, 15):
        # Top gunwale
        top_y = 6 if (x in (1, 14)) else (7 if (x in (2, 13)) else 8)
        bottom_y = 12 if (x in (1, 14)) else (13 if (x in (2, 13)) else 14)
        for y in range(top_y, bottom_y + 1):
            if y == top_y:
                p[x, y] = c_hi
            elif y == bottom_y:
                p[x, y] = c_dk
            elif x in (4, 8, 11):
                p[x, y] = c_lash # vine lashing rib
            elif y < (top_y + bottom_y) // 2:
                p[x, y] = c_mid
            else:
                p[x, y] = c_sh
    # Exterior outline
    for x in range(1, 15):
        top_y = 6 if (x in (1, 14)) else (7 if (x in (2, 13)) else 8)
        bottom_y = 12 if (x in (1, 14)) else (13 if (x in (2, 13)) else 14)
        if top_y - 1 >= 0: p[x, top_y - 1] = c_dk
        if bottom_y + 1 < 16: p[x, bottom_y + 1] = c_dk
    p[0, 6] = c_dk
    p[15, 6] = c_dk
    return im

# 12. plant_vine_bush.png (Lush jungle vine cluster hanging over rocks/trunk)
def gen_plant_vine_bush():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    p = im.load()
    c_dk = (20, 45, 15, 255)
    c_v_dk = (35, 85, 25, 255)
    c_v_mid = (65, 145, 45, 255)
    c_v_lt = (115, 195, 65, 255)
    c_wood = (85, 55, 25, 255)
    # Sturdy jungle trunk/rock base
    for x in range(4, 12):
        for y in range(11, 16):
            p[x, y] = c_wood if (x + y)%2 == 0 else c_dk
    # Tangled creeping vine loops and hanging tendrils
    for x in range(2, 14):
        for y in range(2, 12):
            dx = x - 7.5
            dy = y - 6.5
            dist = (dx*dx + dy*dy)**0.5
            if dist <= 5.2:
                if (x*3 + y*2) % 5 == 0:
                    p[x, y] = c_v_lt
                elif (x + y) % 2 == 0:
                    p[x, y] = c_v_mid
                else:
                    p[x, y] = c_v_dk
            elif dist <= 6.2:
                p[x, y] = c_dk
    # Hanging vine tendrils down to ground
    for y in range(10, 15):
        p[3, y] = c_v_mid
        p[2, y] = c_dk
        p[7, y] = c_v_lt
        p[8, y] = c_v_dk
        p[12, y] = c_v_mid
        p[13, y] = c_dk
    return im

# 13. plant_vine_depleted.png (Stripped vine stems and cut stumps)
def gen_plant_vine_depleted():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    p = im.load()
    c_dk = (25, 30, 15, 255)
    c_cut = (60, 75, 35, 255)
    c_stem = (90, 105, 45, 255)
    c_wood = (75, 48, 20, 255)
    # Cut trunk base
    for x in range(5, 11):
        for y in range(11, 15):
            p[x, y] = c_wood
            p[x, 15] = c_dk
    # Bare short severed stalks
    for x in (4, 7, 10):
        for y in range(8, 12):
            p[x, y] = c_stem
            p[x-1, y] = c_dk
        p[x, 8] = c_cut
    return im

if __name__ == '__main__':
    items_dir = "Assets/Art/Environment/Items"
    plants_dir = "Assets/Art/Environment/Plants"

    save_sprite(os.path.join(items_dir, "item_shaped_wood.png"), gen_shaped_wood())
    save_sprite(os.path.join(items_dir, "item_wooden_pegs.png"), gen_wooden_pegs())
    save_sprite(os.path.join(items_dir, "item_strong_rope.png"), gen_strong_rope())
    save_sprite(os.path.join(items_dir, "item_reinforced_rope.png"), gen_reinforced_rope())
    save_sprite(os.path.join(items_dir, "item_woven_sailcloth.png"), gen_woven_sailcloth())
    save_sprite(os.path.join(items_dir, "item_reinforced_joints.png"), gen_reinforced_joints())
    save_sprite(os.path.join(items_dir, "item_paddle.png"), gen_paddle())
    save_sprite(os.path.join(items_dir, "item_wind_assembly.png"), gen_wind_assembly())
    save_sprite(os.path.join(items_dir, "item_rope_binding_kit.png"), gen_rope_binding_kit())
    save_sprite(os.path.join(items_dir, "item_structural_frame.png"), gen_structural_frame())
    save_sprite(os.path.join(items_dir, "item_reinforced_hull.png"), gen_reinforced_hull())

    save_sprite(os.path.join(plants_dir, "plant_vine_bush.png"), gen_plant_vine_bush())
    save_sprite(os.path.join(plants_dir, "plant_vine_depleted.png"), gen_plant_vine_depleted())

    print("All 13 sprites generated successfully!")
