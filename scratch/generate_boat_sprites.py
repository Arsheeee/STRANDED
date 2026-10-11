import os
import uuid
from PIL import Image

TEMPLATE_META = """fileFormatVersion: 2
guid: {GUID}
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
  spritePivot: {x: 0.5, y: 0.5}
  spritePixelsToUnits: 16
  spriteBorder: {x: 0, y: 0, z: 0, w: 0}
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
    nameFileIdTable: {}
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

# Palettes
C_WOOD_DK = (45, 26, 12, 255)
C_WOOD_MID = (120, 72, 32, 255)
C_WOOD_LT = (180, 118, 58, 255)
C_WOOD_HI = (220, 160, 88, 255)
C_PEG = (235, 185, 110, 255)
C_ROPE = (70, 120, 45, 255) # vine lashing
C_ROPE_DK = (35, 30, 15, 255)
C_SAIL = (225, 215, 185, 255)
C_SAIL_HI = (248, 242, 220, 255)
C_SAIL_SH = (175, 165, 138, 255)
C_SAND = (210, 180, 130, 180) # transparent sand shadow

def draw_slipway(im):
    p = im.load()
    # 2 horizontal launch skid logs on sand
    # Skid 1 (top, y=10..13, x=4..27)
    for x in range(5, 27):
        p[x, 10] = C_WOOD_DK
        p[x, 11] = C_WOOD_HI if x % 3 == 0 else C_WOOD_LT
        p[x, 12] = C_WOOD_MID
        p[x, 13] = C_WOOD_DK
    # Skid 2 (bottom, y=22..25, x=4..27)
    for x in range(5, 27):
        p[x, 22] = C_WOOD_DK
        p[x, 23] = C_WOOD_HI if x % 3 == 0 else C_WOOD_LT
        p[x, 24] = C_WOOD_MID
        p[x, 25] = C_WOOD_DK
    # 4 Vertical ground stakes pinning the skids
    for sx in (6, 25):
        for sy in (8, 9, 14, 15, 20, 21, 26, 27):
            p[sx, sy] = C_WOOD_MID
            p[sx-1, sy] = C_WOOD_DK
            p[sx+1, sy] = C_WOOD_DK
        p[sx, 8] = C_PEG
        p[sx, 20] = C_PEG

def draw_hull(im):
    p = im.load()
    # Main canoe hull: curved elongated body horizontally from x=3 to x=28, y=14 to y=21
    # Bow (left, x=3..7) and Stern (right, x=24..28) tapered
    for x in range(3, 29):
        # Height span
        if x in (3, 28):
            y_range = (16, 19)
        elif x in (4, 5, 26, 27):
            y_range = (15, 20)
        else:
            y_range = (14, 21)

        y_top, y_bot = y_range
        for y in range(y_top, y_bot + 1):
            if y == y_top:
                p[x, y] = C_WOOD_HI
            elif y == y_bot:
                p[x, y] = C_WOOD_DK
            elif y == y_top + 1:
                p[x, y] = C_WOOD_LT
            elif y == y_bot - 1:
                p[x, y] = C_WOOD_MID
            else:
                p[x, y] = C_WOOD_LT if (x + y) % 2 == 0 else C_WOOD_MID

    # Outrigger float at top (y=6..8, x=8..23) connected by 2 crossbeams
    for x in range(8, 24):
        p[x, 6] = C_WOOD_HI
        p[x, 7] = C_WOOD_MID
        p[x, 8] = C_WOOD_DK
    # Crossbeams (akas) at x=10 and x=21
    for cx in (11, 20):
        for y in range(8, 15):
            p[cx, y] = C_WOOD_LT
            p[cx-1, y] = C_WOOD_DK
            p[cx+1, y] = C_WOOD_DK

def draw_frame(im):
    p = im.load()
    # Internal curved wooden ribs inside the hull cavity
    for rx in (8, 12, 16, 19, 23):
        for y in range(15, 21):
            p[rx, y] = C_WOOD_HI
            if y in (15, 20):
                p[rx, y] = C_PEG # wooden dowel peg
    # Gunwale stringers along the sides
    for x in range(6, 26):
        p[x, 15] = C_WOOD_HI
        p[x, 20] = C_WOOD_MID
    # Outrigger crossbeam joint braces
    for cx in (11, 20):
        p[cx, 7] = C_PEG
        p[cx, 14] = C_PEG

def draw_bindings(im):
    p = im.load()
    # Dark reinforced rope and vine lashings wrapped tightly around crossbeams and hull ribs
    for cx in (11, 20):
        for y in range(6, 9):
            p[cx, y] = C_ROPE
        for y in range(13, 16):
            p[cx, y] = C_ROPE
    # Hull rib binding bands
    for rx in (8, 16, 23):
        p[rx, 15] = C_ROPE
        p[rx, 18] = C_ROPE
        p[rx, 20] = C_ROPE
    # Bow and stern lashing wraps
    p[4, 17] = C_ROPE
    p[5, 17] = C_ROPE
    p[26, 17] = C_ROPE
    p[27, 17] = C_ROPE

def draw_paddle(im):
    p = im.load()
    # Wooden paddle laid diagonally along the cockpit (from x=14, y=16 to x=22, y=19)
    pts = [(14, 16), (15, 16), (16, 17), (17, 17), (18, 18), (19, 18)]
    for x, y in pts:
        p[x, y] = C_WOOD_HI
        p[x, y+1] = C_WOOD_DK
    # Paddle blade at right
    for bx in (20, 21, 22):
        for by in (18, 19):
            p[bx, by] = C_WOOD_HI if by == 18 else C_WOOD_MID
    # T-grip at left
    p[13, 15] = C_WOOD_DK
    p[13, 16] = C_WOOD_HI

def draw_sail_assembly(im):
    p = im.load()
    # Central mast stepped at (x=15, y=17) rising up to (x=15, y=2)
    for y in range(2, 17):
        p[15, y] = C_WOOD_HI
        p[16, y] = C_WOOD_DK
    # Diagonal yardarm spar from (x=7, y=13) to (x=24, y=2)
    for step in range(18):
        sx = 7 + step
        sy = 13 - int(step * 0.65)
        if 0 <= sx < 32 and 0 <= sy < 32:
            p[sx, sy] = C_WOOD_LT
            p[sx, sy+1] = C_WOOD_DK

    # Billowing woven sail canvas suspended from the spar down to mast base
    for x in range(8, 24):
        # Top of sail follows spar
        spar_y = 13 - int((x - 7) * 0.65)
        # Bottom edge of sail curves down
        bot_y = 14 if x < 15 else (14 - int((x - 15) * 0.5))
        for y in range(spar_y + 1, bot_y):
            if y == spar_y + 1:
                p[x, y] = C_SAIL_HI
            elif y == bot_y - 1:
                p[x, y] = C_SAIL_SH
            elif (x + y) % 2 == 0:
                p[x, y] = C_SAIL
            else:
                p[x, y] = C_SAIL_HI

    # Rigging stay lines from mast head (15, 2) to bow (4, 17) and stern (27, 17)
    for t in range(12):
        bx = 4 + t
        by = 17 - int(t * 1.25)
        if by >= 2:
            p[bx, by] = C_ROPE
    for t in range(12):
        sx = 15 + t
        sy = 2 + int(t * 1.25)
        if sy <= 17 and sx < 28:
            p[sx, sy] = C_ROPE

def generate_all():
    boat_dir = "Assets/Art/Environment/Boat"
    os.makedirs(boat_dir, exist_ok=True)

    # 0. Slipway only
    im0 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw_slipway(im0)
    save_sprite(os.path.join(boat_dir, "boat_stage_0_slipway.png"), im0)

    # 1. Slipway + Hull
    im1 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw_slipway(im1)
    draw_hull(im1)
    save_sprite(os.path.join(boat_dir, "boat_stage_1_hull.png"), im1)

    # 2. Slipway + Hull + Frame
    im2 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw_slipway(im2)
    draw_hull(im2)
    draw_frame(im2)
    save_sprite(os.path.join(boat_dir, "boat_stage_2_frame.png"), im2)

    # 3. Slipway + Hull + Frame + Bindings
    im3 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw_slipway(im3)
    draw_hull(im3)
    draw_frame(im3)
    draw_bindings(im3)
    save_sprite(os.path.join(boat_dir, "boat_stage_3_bindings.png"), im3)

    # 4. Slipway + Hull + Frame + Bindings + Paddle
    im4 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw_slipway(im4)
    draw_hull(im4)
    draw_frame(im4)
    draw_bindings(im4)
    draw_paddle(im4)
    save_sprite(os.path.join(boat_dir, "boat_stage_4_paddle.png"), im4)

    # 5. Completed: All above + Mast & Sail
    im5 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw_slipway(im5)
    draw_hull(im5)
    draw_frame(im5)
    draw_bindings(im5)
    draw_paddle(im5)
    draw_sail_assembly(im5)
    save_sprite(os.path.join(boat_dir, "boat_stage_5_completed.png"), im5)

    print("All 6 boat stage sprites generated successfully!")

if __name__ == "__main__":
    generate_all()
