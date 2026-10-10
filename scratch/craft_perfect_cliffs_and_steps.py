import os
from PIL import Image

def main():
    cdir = r"d:\Unity\Projects\STRANDED\Assets\Art\Terrain\Cliffs"
    scratch_dir = r"C:\Users\PAVILION\.gemini\antigravity-ide\brain\84db0e2d-58d2-466d-be05-dbff8f133035\scratch"
    
    # Load all existing tiles
    tiles = {}
    for f in os.listdir(cdir):
        if f.endswith(".png") and not f.endswith("sheet.png"):
            tiles[f[:-4]] = Image.open(os.path.join(cdir, f)).convert("RGBA")

    print(f"Loaded {len(tiles)} tiles to fix seams and add mud steps.")

    # -------------------------------------------------------------
    # 1. ENFORCE 100% MATHEMATICAL SEAMLESSNESS ACROSS ALL JUNCTIONS
    # -------------------------------------------------------------

    # A. Front wall horizontal seamlessness (01 and 02)
    # We want 01 -> 02 -> 01 -> 02 to tile infinitely horizontally:
    # 01 right edge (x=15) must match 02 left edge (x=0)
    # 02 right edge (x=15) must match 01 left edge (x=0)
    for y in range(16):
        # Blend seam between 01 right and 02 left
        p_01_right = tiles["cliff_face_top_01"].getpixel((15, y))
        tiles["cliff_face_top_02"].putpixel((0, y), p_01_right)
        
        p_02_right = tiles["cliff_face_top_02"].getpixel((15, y))
        tiles["cliff_face_top_01"].putpixel((0, y), p_02_right)
        
        # Same for bot
        p_bot_01_right = tiles["cliff_face_bot_01"].getpixel((15, y))
        tiles["cliff_face_bot_02"].putpixel((0, y), p_bot_01_right)
        
        p_bot_02_right = tiles["cliff_face_bot_02"].getpixel((15, y))
        tiles["cliff_face_bot_01"].putpixel((0, y), p_bot_02_right)

    # B. Front wall vertical seamlessness (top on bot)
    # Top bottom row (y=15) must exactly match Bot top row (y=0)
    for x in range(16):
        tiles["cliff_face_bot_01"].putpixel((x, 0), tiles["cliff_face_top_01"].getpixel((x, 15)))
        tiles["cliff_face_bot_02"].putpixel((x, 0), tiles["cliff_face_top_02"].getpixel((x, 15)))

    # C. Left canyon shoulder connection:
    # Left shoulder sits to the right of cliff_face_top_02:
    # ramp_left_top (x=0) must match cliff_face_top_02 (x=15)
    # ramp_left_bot (x=0) must match cliff_face_bot_02 (x=15)
    for y in range(16):
        tiles["cliff_ramp_left_top"].putpixel((0, y), tiles["cliff_face_top_02"].getpixel((15, y)))
        tiles["cliff_ramp_left_bot"].putpixel((0, y), tiles["cliff_face_bot_02"].getpixel((15, y)))

    # D. Right canyon shoulder connection:
    # Right shoulder sits to the left of cliff_face_top_01:
    # ramp_right_top (x=15) must match cliff_face_top_01 (x=0)
    # ramp_right_bot (x=15) must match cliff_face_bot_01 (x=0)
    for y in range(16):
        tiles["cliff_ramp_right_top"].putpixel((15, y), tiles["cliff_face_top_01"].getpixel((0, y)))
        tiles["cliff_ramp_right_bot"].putpixel((15, y), tiles["cliff_face_bot_01"].getpixel((0, y)))

    # E. Left vertical wall continuous vertical seams:
    # side_e_top (y=15) -> side_e (y=0)
    # side_e (y=15) -> side_e_bot (y=0)
    # side_e_bot (y=15) -> ramp_left_top (y=0)
    # ramp_left_top (y=15) -> ramp_left_bot (y=0)
    for x in range(16):
        tiles["cliff_side_e"].putpixel((x, 0), tiles["cliff_side_e_top"].getpixel((x, 15)))
        tiles["cliff_side_e_bot"].putpixel((x, 0), tiles["cliff_side_e"].getpixel((x, 15)))
        tiles["cliff_ramp_left_top"].putpixel((x, 0), tiles["cliff_side_e_bot"].getpixel((x, 15)))
        tiles["cliff_ramp_left_bot"].putpixel((x, 0), tiles["cliff_ramp_left_top"].getpixel((x, 15)))

    # F. Right vertical wall continuous vertical seams:
    # side_w_top (y=15) -> side_w (y=0)
    # side_w (y=15) -> side_w_bot (y=0)
    # side_w_bot (y=15) -> ramp_right_top (y=0)
    # ramp_right_top (y=15) -> ramp_right_bot (y=0)
    for x in range(16):
        tiles["cliff_side_w"].putpixel((x, 0), tiles["cliff_side_w_top"].getpixel((x, 15)))
        tiles["cliff_side_w_bot"].putpixel((x, 0), tiles["cliff_side_w"].getpixel((x, 15)))
        tiles["cliff_ramp_right_top"].putpixel((x, 0), tiles["cliff_side_w_bot"].getpixel((x, 15)))
        tiles["cliff_ramp_right_bot"].putpixel((x, 0), tiles["cliff_ramp_right_top"].getpixel((x, 15)))

    # -------------------------------------------------------------
    # 2. CRAFT BEAUTIFUL, AUTHENTIC MUD STEPS TILES
    # -------------------------------------------------------------
    # We craft authentic carved earthen terrace steps cut into the dirt incline.
    # 4 distinct steps across 32 vertical pixels (2 tiles tall).
    
    C_MUD_SUN     = (237, 173, 35, 255)   # #edad23
    C_MUD_LIGHT   = (216, 159, 42, 255)   # #d89f2a
    C_MUD_BASE    = (182, 122, 41, 255)   # #b67a29
    C_MUD_DARK    = (150, 81, 12, 255)    # #96510c
    C_STEP_LIP    = (245, 195, 66, 255)   # #f5c342 (wood/stone highlight lip)
    C_STEP_RISER  = (110, 68, 20, 255)    # #6e4414 (earthen/wood riser)
    C_STEP_SHADOW = (61, 38, 10, 255)     # #3d260a (riser ambient shadow)
    C_BASE_SHAD   = (24, 16, 2, 255)      # #181002 (deep contact shadow)

    # Top step tile (steps 1 & 2):
    mud_steps_top = Image.new("RGBA", (16, 16), C_MUD_BASE)
    for y in range(16):
        for x in range(16):
            if y in [0, 1, 2, 3]:
                # Step 1 landing
                c = C_MUD_SUN if (x + y) % 3 == 0 else C_MUD_LIGHT
                mud_steps_top.putpixel((x, y), c)
            elif y == 4:
                # Step 1 riser lip
                mud_steps_top.putpixel((x, y), C_STEP_LIP if x % 2 == 0 else C_MUD_SUN)
            elif y in [5, 6]:
                # Step 1 riser face
                mud_steps_top.putpixel((x, y), C_STEP_RISER)
            elif y == 7:
                # Step 1 riser shadow
                mud_steps_top.putpixel((x, y), C_STEP_SHADOW)
            elif y in [8, 9, 10, 11]:
                # Step 2 tread
                c = C_MUD_LIGHT if (x + y) % 2 == 0 else C_MUD_BASE
                mud_steps_top.putpixel((x, y), c)
            elif y == 12:
                # Step 2 riser lip
                mud_steps_top.putpixel((x, y), C_STEP_LIP if x % 2 == 0 else C_MUD_SUN)
            elif y in [13, 14]:
                # Step 2 riser face
                mud_steps_top.putpixel((x, y), C_STEP_RISER)
            elif y == 15:
                # Step 2 riser shadow
                mud_steps_top.putpixel((x, y), C_STEP_SHADOW)

    # Bottom step tile (steps 3 & 4):
    mud_steps_bot = Image.new("RGBA", (16, 16), C_MUD_BASE)
    for y in range(16):
        for x in range(16):
            if y in [0, 1, 2, 3]:
                # Step 3 tread
                c = C_MUD_LIGHT if (x + y) % 3 == 0 else C_MUD_BASE
                mud_steps_bot.putpixel((x, y), c)
            elif y == 4:
                # Step 3 riser lip
                mud_steps_bot.putpixel((x, y), C_STEP_LIP if x % 2 == 0 else C_MUD_SUN)
            elif y in [5, 6]:
                # Step 3 riser face
                mud_steps_bot.putpixel((x, y), C_STEP_RISER)
            elif y == 7:
                # Step 3 riser shadow
                mud_steps_bot.putpixel((x, y), C_STEP_SHADOW)
            elif y in [8, 9, 10, 11]:
                # Step 4 tread
                c = C_MUD_BASE if (x + y) % 2 == 0 else C_MUD_DARK
                mud_steps_bot.putpixel((x, y), c)
            elif y == 12:
                # Step 4 riser lip
                mud_steps_bot.putpixel((x, y), C_STEP_LIP if x % 2 == 0 else C_MUD_LIGHT)
            elif y in [13, 14]:
                # Step 4 riser face
                mud_steps_bot.putpixel((x, y), C_STEP_RISER)
            elif y == 15:
                # Step 4 base shadow
                mud_steps_bot.putpixel((x, y), C_BASE_SHAD if x % 2 == 0 else C_STEP_SHADOW)

    # Shadowed variant (for right side of 2-tile wide staircase under the east cliff):
    def make_shadowed_steps(tile):
        t = tile.copy()
        for y in range(16):
            for x in range(12, 16):
                p = t.getpixel((x, y))
                # Darken RGB by 25% for ambient cliff shadow
                shaded = (int(p[0] * 0.75), int(p[1] * 0.75), int(p[2] * 0.75), 255)
                t.putpixel((x, y), shaded)
        return t

    mud_steps_01_top = mud_steps_top.copy()
    mud_steps_01_bot = mud_steps_bot.copy()
    mud_steps_02_top = make_shadowed_steps(mud_steps_top)
    mud_steps_02_bot = make_shadowed_steps(mud_steps_bot)

    # Add mud steps to tile set
    tiles["cliff_mud_steps_top"]    = mud_steps_top
    tiles["cliff_mud_steps_bot"]    = mud_steps_bot
    tiles["cliff_mud_steps_01_top"] = mud_steps_01_top
    tiles["cliff_mud_steps_01_bot"] = mud_steps_01_bot
    tiles["cliff_mud_steps_02_top"] = mud_steps_02_top
    tiles["cliff_mud_steps_02_bot"] = mud_steps_02_bot

    # Save all updated tiles
    meta_template = '''fileFormatVersion: 2
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
  priority: 0
  psdMetaData:
    canvasSize: {{x: 0, y: 0}}
  textureType: 8
  textureShape: 1
  singleChannelComponent: 0
  maxTextureSizeSet: 0
  compressionQuality: 50
  textureFormat: -1
  textureSubImage: {{}}
  compressionQualitySet: 0
  textureFormatSet: 0
  applyGammaDecoding: 0
  platformSettings:
  - serializedVersion: 3
    buildTarget: DefaultTexturePlatform
    maxTextureSize: 2048
    resizeAlgorithm: 0
    format: -1
    textureCompression: 0
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceServerData: 0
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
  textureTypeSet: 0
  customData: 
  userData: 
  assetBundleName: 
  assetBundleVariant: 
'''

    import uuid
    for name, img in tiles.items():
        img_p = os.path.join(cdir, f"{name}.png")
        img.save(img_p)
        img.save(os.path.join(scratch_dir, f"{name}.png"))
        
        meta_p = img_p + ".meta"
        if not os.path.exists(meta_p):
            guid = uuid.uuid4().hex
            with open(meta_p, 'w') as f:
                f.write(meta_template.format(guid=guid))

    print(f"Successfully processed and saved all {len(tiles)} tiles!")

if __name__ == "__main__":
    main()
