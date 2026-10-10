import os
import base64
from PIL import Image

def craft_flawless_cliffs():
    brain_dir = r"C:\Users\PAVILION\.gemini\antigravity-ide\brain\84db0e2d-58d2-466d-be05-dbff8f133035"
    scratch_dir = os.path.join(brain_dir, "scratch")
    assets_dir = r"d:\Unity\Projects\STRANDED\Assets\Art\Terrain"
    cliff_dir = os.path.join(assets_dir, "Cliffs")

    ref = Image.open(os.path.join(scratch_dir, "stardew_native_512.png")).convert("RGBA")
    grass_base = Image.open(os.path.join(assets_dir, "Grass", "grass_base_01.png")).convert("RGBA")
    mud_base   = Image.open(os.path.join(assets_dir, "Dirt", "mud_base_01.png")).convert("RGBA")

    face_top_01 = Image.open(os.path.join(cliff_dir, "cliff_face_top_01.png")).convert("RGBA")
    face_bot_01 = Image.open(os.path.join(cliff_dir, "cliff_face_bot_01.png")).convert("RGBA")
    face_top_02 = Image.open(os.path.join(cliff_dir, "cliff_face_top_02.png")).convert("RGBA")
    face_bot_02 = Image.open(os.path.join(cliff_dir, "cliff_face_bot_02.png")).convert("RGBA")

    # Clean front face row 0 to pure highland grass
    for x in range(16):
        gp = grass_base.getpixel((x, 15))
        face_top_01.putpixel((x, 0), gp)
        face_top_02.putpixel((x, 0), gp)

    # PALETTE
    PAL_CREST_HI   = (243, 215, 33, 255) # Brightest golden crest rim
    PAL_GOLD_HI    = (236, 172, 34, 255) # Bright gold highlight
    PAL_GOLD_MID   = (209, 175, 24, 255) # Primary sunlit boulder body
    PAL_OLIVE_MID  = (160, 120, 15, 255) # Mid-tone olive-gold rock
    PAL_OLIVE_DARK = (142, 106, 14, 255) # Deeper olive body
    PAL_SHADOW_MED = (122,  93, 12, 255) # Rock shadow
    PAL_SHADOW_DRK = ( 89,  73,  9, 255) # Crevice shadow
    PAL_CREVICE    = ( 64,  42,  6, 255) # Deep rock crevice
    PAL_DEEP_HOLE  = ( 24,  16,  2, 255) # Deepest crevice black-brown
    
    PAL_GRASS_BASE = ( 67, 161, 25, 255) # Standard green grass
    PAL_GRASS_HI   = (112, 199, 37, 255) # Grass highlight fleck
    PAL_GRASS_SHAD = ( 45, 115, 18, 255) # Grass shadow
    PAL_ROCK_ON_GR = ( 53,  76, 13, 255) # Contact shadow of rock onto grass

    # =========================================================================
    # 1. CANYON RAMPS / SHOULDERS (Authentic ConcernedApe c14 and c17)
    # =========================================================================
    c14_r4 = ref.crop((14*16, 4*16, 15*16, 5*16))
    c14_r5 = ref.crop((14*16, 5*16, 15*16, 6*16))
    c14_r6 = ref.crop((14*16, 6*16, 15*16, 7*16))
    c14_r7 = ref.crop((14*16, 7*16, 15*16, 8*16))

    ramp_left_top = Image.new("RGBA", (16, 16))
    ramp_left_top.paste(c14_r4.crop((0, 0, 16, 7)), (0, 0))
    ramp_left_top.paste(c14_r5.crop((0, 7, 16, 16)), (0, 7))

    ramp_left_bot = Image.new("RGBA", (16, 16))
    ramp_left_bot.paste(c14_r6.crop((0, 0, 16, 10)), (0, 0))
    ramp_left_bot.paste(c14_r7.crop((0, 10, 16, 16)), (0, 10))

    # Right Shoulder (col 17)
    c17_r4 = ref.crop((17*16, 4*16, 18*16, 5*16))
    c17_r5 = ref.crop((17*16, 5*16, 18*16, 6*16))
    c17_r6 = ref.crop((17*16, 6*16, 18*16, 7*16))
    c17_r7 = ref.crop((17*16, 7*16, 18*16, 8*16))

    ramp_right_top = Image.new("RGBA", (16, 16))
    ramp_right_top.paste(c17_r4.crop((0, 0, 16, 7)), (0, 0))
    ramp_right_top.paste(c17_r5.crop((0, 7, 16, 16)), (0, 7))

    ramp_right_bot = Image.new("RGBA", (16, 16))
    ramp_right_bot.paste(c17_r6.crop((0, 0, 16, 10)), (0, 0))
    ramp_right_bot.paste(c17_r7.crop((0, 10, 16, 16)), (0, 10))

    # Vertical seamless loop between ramp top and bot:
    # make ramp_left_bot row 0 match ramp_left_top row 15 exactly
    for x in range(16):
        ramp_left_bot.putpixel((x, 0), ramp_left_top.getpixel((x, 15)))
    for x in range(16):
        ramp_right_bot.putpixel((x, 0), ramp_right_top.getpixel((x, 15)))

    # CANONICAL ROW 0 PROFILES FOR VERTICAL FLANKS:
    # 1. West-facing wall top profile (r0_w):
    r0_w = [ramp_right_top.getpixel((x, 0)) for x in range(16)]
    r0_w[0] = grass_base.getpixel((0, 0))
    r0_w[1] = grass_base.getpixel((1, 0))
    r0_w[2] = grass_base.getpixel((2, 0))
    r0_w[3] = grass_base.getpixel((3, 0))
    r0_w[4] = PAL_GRASS_SHAD
    r0_w[5] = PAL_ROCK_ON_GR
    r0_w[6] = PAL_SHADOW_DRK
    r0_w[13] = PAL_GRASS_HI
    r0_w[14] = PAL_GRASS_BASE
    r0_w[15] = face_top_01.getpixel((0, 0)) # Exact match with face_top_01(0, 0)
    for x in range(16):
        ramp_right_top.putpixel((x, 0), r0_w[x])

    # 2. East-facing wall top profile (r0_e):
    r0_e = [ramp_left_top.getpixel((x, 0)) for x in range(16)]
    r0_e[0] = face_top_02.getpixel((15, 0)) # Exact match with face_top_02(15, 0)
    r0_e[1] = PAL_GRASS_BASE
    r0_e[2] = PAL_GRASS_HI
    r0_e[11] = PAL_ROCK_ON_GR
    r0_e[12] = PAL_GRASS_SHAD
    r0_e[13] = grass_base.getpixel((13, 0))
    r0_e[14] = grass_base.getpixel((14, 0))
    r0_e[15] = grass_base.getpixel((15, 0))
    for x in range(16):
        ramp_left_top.putpixel((x, 0), r0_e[x])

    # =========================================================================
    # 2. CRAFT VOLUMETRIC WEST VERTICAL FLANK (cliff_side_w, _top, _bot)
    # =========================================================================
    side_w = Image.new("RGBA", (16, 16))
    raw_w = c17_r4.copy() # Authentic ConcernedApe golden rock

    for y in range(16):
        # Lowland grass on left x=0..4
        side_w.putpixel((0, y), grass_base.getpixel((0, y)))
        side_w.putpixel((1, y), grass_base.getpixel((1, y)))
        side_w.putpixel((2, y), grass_base.getpixel((2, y)))
        side_w.putpixel((3, y), grass_base.getpixel((3, y)))
        # Undulating rock contour & shadow
        bulge = 1 if (y in [2, 3, 4, 10, 11, 12]) else 0
        side_w.putpixel((3 + bulge, y), PAL_GRASS_SHAD)
        side_w.putpixel((4 + bulge, y), PAL_ROCK_ON_GR)
        side_w.putpixel((5 + bulge, y), PAL_SHADOW_DRK)

        # Volumetric rock body
        for x in range(6 + bulge, 14):
            side_w.putpixel((x, y), raw_w.getpixel((x, y)))

        # Two distinct spherical lobes:
        if y in [2, 3, 4]:
            side_w.putpixel((9, y), PAL_CREST_HI)
            side_w.putpixel((10, y), PAL_GOLD_HI)
            side_w.putpixel((8, y), PAL_GOLD_MID)
        elif y in [10, 11, 12]:
            side_w.putpixel((9, y), PAL_GOLD_HI)
            side_w.putpixel((10, y), PAL_GOLD_MID)
        elif y in [7, 8]: # Crevice dividing lobes
            side_w.putpixel((7, y), PAL_CREVICE)
            side_w.putpixel((8, y), PAL_CREVICE)
            side_w.putpixel((9, y), PAL_SHADOW_DRK)
            side_w.putpixel((10, y), PAL_SHADOW_MED)

        # Highland grass on right
        side_w.putpixel((14, y), PAL_GRASS_HI if y % 4 == 1 else PAL_GRASS_BASE)
        side_w.putpixel((15, y), grass_base.getpixel((15, y)))

    # Seamless vertical loop (row 0 == row 15)
    r15_w = [side_w.getpixel((x, 15)) for x in range(16)]
    for x in range(16):
        side_w.putpixel((x, 0), r15_w[x])
        p0 = r15_w[x]
        p2 = side_w.getpixel((x, 2))
        side_w.putpixel((x, 1), tuple(int(p0[i]*0.6 + p2[i]*0.4) for i in range(4)))

    # side_w_top
    side_w_top = side_w.copy()
    for y in range(4):
        for x in range(16):
            if x < 8 + y:
                side_w_top.putpixel((x, y), grass_base.getpixel((x, y)))
    for x in range(16):
        side_w_top.putpixel((x, 15), side_w.getpixel((x, 0)))

    # side_w_bot: bottom matches r0_w exactly!
    side_w_bot = side_w.copy()
    for x in range(16):
        side_w_bot.putpixel((x, 0), side_w.getpixel((x, 15)))
        side_w_bot.putpixel((x, 15), r0_w[x])
        pb = r0_w[x]
        p13 = side_w_bot.getpixel((x, 13))
        side_w_bot.putpixel((x, 14), tuple(int(pb[i]*0.6 + p13[i]*0.4) for i in range(4)))

    # =========================================================================
    # 3. CRAFT VOLUMETRIC EAST VERTICAL FLANK (cliff_side_e, _top, _bot)
    # =========================================================================
    side_e = Image.new("RGBA", (16, 16))
    raw_e = c14_r4.copy() # Authentic ConcernedApe golden rock

    for y in range(16):
        side_e.putpixel((0, y), grass_base.getpixel((0, y)))
        side_e.putpixel((1, y), PAL_GRASS_HI if y % 3 == 1 else PAL_GRASS_BASE)
        side_e.putpixel((2, y), PAL_GRASS_SHAD)

        # Volumetric rock body
        bulge = 1 if (y in [2, 3, 4, 10, 11, 12]) else 0
        for x in range(3, 10 + bulge):
            side_e.putpixel((x, y), raw_e.getpixel((x, y)))

        # Two distinct spherical lobes:
        if y in [2, 3, 4]:
            side_e.putpixel((5, y), PAL_CREST_HI)
            side_e.putpixel((6, y), PAL_GOLD_HI)
            side_e.putpixel((7, y), PAL_GOLD_MID)
        elif y in [10, 11, 12]:
            side_e.putpixel((5, y), PAL_GOLD_HI)
            side_e.putpixel((6, y), PAL_GOLD_MID)
        elif y in [7, 8]:
            side_e.putpixel((5, y), PAL_CREVICE)
            side_e.putpixel((6, y), PAL_CREVICE)
            side_e.putpixel((7, y), PAL_SHADOW_DRK)

        side_e.putpixel((10 + bulge, y), PAL_SHADOW_DRK)
        side_e.putpixel((11 + bulge, y), PAL_ROCK_ON_GR)
        if 12 + bulge < 16:
            side_e.putpixel((12 + bulge, y), PAL_GRASS_SHAD)
        for x in range(13 + bulge, 16):
            side_e.putpixel((x, y), grass_base.getpixel((x, y)))

    # Seamless vertical loop (row 0 == row 15)
    r15_e = [side_e.getpixel((x, 15)) for x in range(16)]
    for x in range(16):
        side_e.putpixel((x, 0), r15_e[x])
        p0 = r15_e[x]
        p2 = side_e.getpixel((x, 2))
        side_e.putpixel((x, 1), tuple(int(p0[i]*0.6 + p2[i]*0.4) for i in range(4)))

    # side_e_top
    side_e_top = side_e.copy()
    for y in range(4):
        for x in range(16):
            if x > 5 - y:
                side_e_top.putpixel((x, y), grass_base.getpixel((x, y)))
    for x in range(16):
        side_e_top.putpixel((x, 15), side_e.getpixel((x, 0)))

    # side_e_bot: bottom matches r0_e exactly!
    side_e_bot = side_e.copy()
    for x in range(16):
        side_e_bot.putpixel((x, 0), side_e.getpixel((x, 15)))
        side_e_bot.putpixel((x, 15), r0_e[x])
        pb = r0_e[x]
        p13 = side_e_bot.getpixel((x, 13))
        side_e_bot.putpixel((x, 14), tuple(int(pb[i]*0.6 + p13[i]*0.4) for i in range(4)))

    # =========================================================================
    # 4. CRAFT FLAWLESS SOUTHWEST CORNERS (corner_sw_top & bot)
    # =========================================================================
    corner_sw_top = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            corner_sw_top.putpixel((x, y), grass_base.getpixel((x, y)))

    # Paste corner boulder body from face_top_01
    for y in range(16):
        for x in range(5, 16):
            corner_sw_top.putpixel((x, y), face_top_01.getpixel((min(15, x + 2), y)))

    # Sculpt organic crest curvature
    corner_sw_top.putpixel((15, 0), PAL_GRASS_BASE)
    corner_sw_top.putpixel((14, 0), PAL_GRASS_BASE)
    corner_sw_top.putpixel((15, 1), PAL_GRASS_BASE)
    corner_sw_top.putpixel((14, 1), PAL_GRASS_HI)
    corner_sw_top.putpixel((13, 0), PAL_GRASS_HI)
    corner_sw_top.putpixel((15, 2), PAL_CREST_HI)
    corner_sw_top.putpixel((14, 2), PAL_GOLD_HI)
    corner_sw_top.putpixel((13, 1), PAL_CREST_HI)

    # Outer rock boundary shadow along curved left contour
    for y in range(16):
        bx = 5
        if y < 4:
            bx = 5 + (3 - y) // 2
        corner_sw_top.putpixel((bx, y), PAL_ROCK_ON_GR)
        if bx - 1 >= 0:
            corner_sw_top.putpixel((bx - 1, y), PAL_GRASS_SHAD)
        for x in range(bx - 1):
            corner_sw_top.putpixel((x, y), grass_base.getpixel((x, y)))

    # corner_sw_bot:
    corner_sw_bot = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            corner_sw_bot.putpixel((x, y), grass_base.getpixel((x, (y + 3) % 16)))

    for y in range(13):
        for x in range(5, 16):
            corner_sw_bot.putpixel((x, y), face_bot_01.getpixel((x, y)))

    for y in range(13):
        corner_sw_bot.putpixel((5, y), PAL_SHADOW_DRK if y % 2 == 0 else PAL_CREVICE)
        corner_sw_bot.putpixel((4, y), PAL_ROCK_ON_GR)
        corner_sw_bot.putpixel((3, y), PAL_GRASS_SHAD)
        for x in range(3):
            corner_sw_bot.putpixel((x, y), grass_base.getpixel((x, y)))

    for x in range(4, 16):
        corner_sw_bot.putpixel((x, 12), PAL_CREVICE if x > 6 else PAL_ROCK_ON_GR)
        corner_sw_bot.putpixel((x, 13), PAL_ROCK_ON_GR)
        corner_sw_bot.putpixel((x, 14), PAL_GRASS_SHAD)
        corner_sw_bot.putpixel((x, 15), grass_base.getpixel((x, 15)))

    # STRICT ZERO-SEAM HARMONIZATION FOR SW CORNER:
    # 1. Left col 0 of both tiles is pure lowland grass:
    for y in range(16):
        corner_sw_top.putpixel((0, y), grass_base.getpixel((0, y)))
        corner_sw_bot.putpixel((0, y), grass_base.getpixel((0, y)))

    # 2. Top row 0 of corner_sw_top == r0_w (matches side_w_bot row 15 exactly):
    for x in range(16):
        corner_sw_top.putpixel((x, 0), r0_w[x])

    # 3. Right col 15 of corner_sw_top == face_top_01 col 0:
    for y in range(16):
        corner_sw_top.putpixel((15, y), face_top_01.getpixel((0, y)))

    # 4. Right col 15 of corner_sw_bot == face_bot_01 col 0:
    for y in range(16):
        corner_sw_bot.putpixel((15, y), face_bot_01.getpixel((0, y)))

    # 5. Bottom row 15 of corner_sw_bot is pure lowland grass, except vertex (15, 15):
    for x in range(15):
        corner_sw_bot.putpixel((x, 15), grass_base.getpixel((x, 15)))
    corner_sw_bot.putpixel((15, 15), face_bot_01.getpixel((0, 15)))

    # 6. corner_sw_top row 15 == corner_sw_bot row 0:
    sw_bot_r0 = [corner_sw_bot.getpixel((x, 0)) for x in range(16)]
    for x in range(16):
        corner_sw_top.putpixel((x, 15), sw_bot_r0[x])
        if x < 15:
            p15 = sw_bot_r0[x]
            p13 = corner_sw_top.getpixel((x, 13))
            corner_sw_top.putpixel((x, 14), tuple(int(p15[i]*0.6 + p13[i]*0.4) for i in range(4)))

    # Re-enforce entire right col 15 of corner_sw_top == face_top_01 col 0:
    for y in range(16):
        corner_sw_top.putpixel((15, y), face_top_01.getpixel((0, y)))

    # 7. Shared 4-way corner vertex (15, 15) of top and (15, 0) of bot:
    shared_sw = face_top_01.getpixel((0, 15))
    corner_sw_top.putpixel((15, 15), shared_sw)
    corner_sw_bot.putpixel((15, 0), shared_sw)

    # Re-enforce (15, 0) of corner_sw_top == face_top_01(0, 0) == r0_w[15]:
    corner_sw_top.putpixel((15, 0), face_top_01.getpixel((0, 0)))

    # =========================================================================
    # 5. CRAFT FLAWLESS SOUTHEAST CORNERS (corner_se_top & bot)
    # =========================================================================
    corner_se_top = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            corner_se_top.putpixel((x, y), grass_base.getpixel((x, y)))

    for y in range(16):
        for x in range(11):
            corner_se_top.putpixel((x, y), face_top_02.getpixel((x, y)))

    corner_se_top.putpixel((0, 0), PAL_GRASS_BASE)
    corner_se_top.putpixel((1, 0), PAL_GRASS_BASE)
    corner_se_top.putpixel((0, 1), PAL_GRASS_BASE)
    corner_se_top.putpixel((1, 1), PAL_GRASS_HI)
    corner_se_top.putpixel((2, 0), PAL_GRASS_HI)
    corner_se_top.putpixel((0, 2), PAL_CREST_HI)
    corner_se_top.putpixel((1, 2), PAL_GOLD_HI)
    corner_se_top.putpixel((2, 1), PAL_CREST_HI)

    for y in range(16):
        bx = 10
        if y < 4:
            bx = 10 - (3 - y) // 2
        corner_se_top.putpixel((bx, y), PAL_SHADOW_DRK)
        corner_se_top.putpixel((bx + 1, y), PAL_ROCK_ON_GR)
        if bx + 2 < 16:
            corner_se_top.putpixel((bx + 2, y), PAL_GRASS_SHAD)
        for x in range(bx + 3, 16):
            corner_se_top.putpixel((x, y), grass_base.getpixel((x, y)))

    corner_se_bot = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            corner_se_bot.putpixel((x, y), grass_base.getpixel((x, (y + 4) % 16)))

    for y in range(13):
        for x in range(11):
            corner_se_bot.putpixel((x, y), face_bot_02.getpixel((x, y)))

    for y in range(13):
        corner_se_bot.putpixel((10, y), PAL_SHADOW_DRK if y % 2 == 0 else PAL_CREVICE)
        corner_se_bot.putpixel((11, y), PAL_ROCK_ON_GR)
        corner_se_bot.putpixel((12, y), PAL_GRASS_SHAD)
        for x in range(13, 16):
            corner_se_bot.putpixel((x, y), grass_base.getpixel((x, y)))

    for x in range(12):
        corner_se_bot.putpixel((x, 12), PAL_CREVICE if x < 9 else PAL_ROCK_ON_GR)
        corner_se_bot.putpixel((x, 13), PAL_ROCK_ON_GR)
        corner_se_bot.putpixel((x, 14), PAL_GRASS_SHAD)
        corner_se_bot.putpixel((x, 15), grass_base.getpixel((x, 15)))

    # STRICT ZERO-SEAM HARMONIZATION FOR SE CORNER:
    # 1. Right col 15 of both tiles is pure lowland grass:
    for y in range(16):
        corner_se_top.putpixel((15, y), grass_base.getpixel((15, y)))
        corner_se_bot.putpixel((15, y), grass_base.getpixel((15, y)))

    # 2. Top row 0 of corner_se_top == r0_e (matches side_e_bot row 15 exactly):
    for x in range(16):
        corner_se_top.putpixel((x, 0), r0_e[x])

    # 3. Left col 0 of corner_se_top == face_top_02 col 15:
    for y in range(16):
        corner_se_top.putpixel((0, y), face_top_02.getpixel((15, y)))

    # 4. Left col 0 of corner_se_bot == face_bot_02 col 15:
    for y in range(16):
        corner_se_bot.putpixel((0, y), face_bot_02.getpixel((15, y)))

    # 5. Bottom row 15 of corner_se_bot is pure lowland grass, except vertex (0, 15):
    for x in range(1, 16):
        corner_se_bot.putpixel((x, 15), grass_base.getpixel((x, 15)))
    corner_se_bot.putpixel((0, 15), face_bot_02.getpixel((15, 15)))

    # 6. corner_se_top row 15 == corner_se_bot row 0:
    se_bot_r0 = [corner_se_bot.getpixel((x, 0)) for x in range(16)]
    for x in range(16):
        corner_se_top.putpixel((x, 15), se_bot_r0[x])
        if x > 0:
            p15 = se_bot_r0[x]
            p13 = corner_se_top.getpixel((x, 13))
            corner_se_top.putpixel((x, 14), tuple(int(p15[i]*0.6 + p13[i]*0.4) for i in range(4)))

    # Re-enforce entire left col 0 of corner_se_top == face_top_02 col 15:
    for y in range(16):
        corner_se_top.putpixel((0, y), face_top_02.getpixel((15, y)))

    # 7. Shared 4-way corner vertex (0, 15) of top and (0, 0) of bot:
    shared_se = face_top_02.getpixel((15, 15))
    corner_se_top.putpixel((0, 15), shared_se)
    corner_se_bot.putpixel((0, 0), shared_se)

    # Re-enforce (0, 0) of corner_se_top == face_top_02(15, 0) == r0_e[0]:
    corner_se_top.putpixel((0, 0), face_top_02.getpixel((15, 0)))

    # =========================================================================
    # 6. ZERO-SEAM HARMONIZATION FOR CANYON RAMPS
    # =========================================================================
    # ramp_left:
    for y in range(16):
        ramp_left_top.putpixel((0, y), face_top_01.getpixel((15, y)))
        ramp_left_bot.putpixel((0, y), face_bot_01.getpixel((15, y)))
    shared_rl = face_top_01.getpixel((15, 15))
    ramp_left_top.putpixel((0, 15), shared_rl)
    ramp_left_bot.putpixel((0, 0), shared_rl)
    for x in range(16):
        ramp_left_top.putpixel((x, 0), r0_e[x])

    # ramp_right:
    for y in range(16):
        ramp_right_top.putpixel((15, y), face_top_02.getpixel((0, y)))
        ramp_right_bot.putpixel((15, y), face_bot_02.getpixel((0, y)))
    shared_rr = face_top_02.getpixel((0, 15))
    ramp_right_top.putpixel((15, 15), shared_rr)
    ramp_right_bot.putpixel((15, 0), shared_rr)
    for x in range(16):
        ramp_right_top.putpixel((x, 0), r0_w[x])

    # =========================================================================
    # 7. OUTER NORTH CORNERS
    # =========================================================================
    outer_tl = Image.open(os.path.join(cliff_dir, "cliff_outer_tl_top.png")).convert("RGBA")
    outer_tr = Image.open(os.path.join(cliff_dir, "cliff_outer_tr_top.png")).convert("RGBA")
    for x in range(16):
        outer_tl.putpixel((x, 15), side_w_top.getpixel((x, 0)))
        outer_tr.putpixel((x, 15), side_e_top.getpixel((x, 0)))

    # =========================================================================
    # 8. SAVE ALL TILES
    # =========================================================================
    tiles = {
        "cliff_face_top_01": face_top_01,
        "cliff_face_bot_01": face_bot_01,
        "cliff_face_top_02": face_top_02,
        "cliff_face_bot_02": face_bot_02,
        "cliff_side_w": side_w,
        "cliff_side_w_top": side_w_top,
        "cliff_side_w_bot": side_w_bot,
        "cliff_side_e": side_e,
        "cliff_side_e_top": side_e_top,
        "cliff_side_e_bot": side_e_bot,
        "cliff_corner_sw_top": corner_sw_top,
        "cliff_corner_sw_bot": corner_sw_bot,
        "cliff_corner_se_top": corner_se_top,
        "cliff_corner_se_bot": corner_se_bot,
        "cliff_ramp_left_top": ramp_left_top,
        "cliff_ramp_left_bot": ramp_left_bot,
        "cliff_ramp_right_top": ramp_right_top,
        "cliff_ramp_right_bot": ramp_right_bot,
        "cliff_outer_tl_top": outer_tl,
        "cliff_outer_tr_top": outer_tr
    }

    for name, img in tiles.items():
        img.save(os.path.join(cliff_dir, f"{name}.png"))
        img.save(os.path.join(scratch_dir, f"flawless_{name}.png"))

    print("All tiles saved.")

    # =========================================================================
    # 9. STRICT MATHEMATICAL ZERO-SEAM AUDIT
    # =========================================================================
    def check_h(l_img, r_img):
        return sum(1 for y in range(16) if l_img.getpixel((15, y)) != r_img.getpixel((0, y)))

    def check_v(t_img, b_img):
        return sum(1 for x in range(16) if t_img.getpixel((x, 15)) != b_img.getpixel((x, 0)))

    checks = [
        ("Horizontal: face_top_01 -> face_top_02", check_h(face_top_01, face_top_02)),
        ("Horizontal: face_top_02 -> face_top_01", check_h(face_top_02, face_top_01)),
        ("Horizontal: face_bot_01 -> face_bot_02", check_h(face_bot_01, face_bot_02)),
        ("Horizontal: face_bot_02 -> face_bot_01", check_h(face_bot_02, face_bot_01)),
        ("Vertical: face_top_01 -> face_bot_01", check_v(face_top_01, face_bot_01)),
        ("Vertical: face_top_02 -> face_bot_02", check_v(face_top_02, face_bot_02)),

        ("Vertical: side_w_top -> side_w", check_v(side_w_top, side_w)),
        ("Vertical: side_w -> side_w (self-loop)", check_v(side_w, side_w)),
        ("Vertical: side_w -> side_w_bot", check_v(side_w, side_w_bot)),
        ("Vertical: side_w_bot -> corner_sw_top", check_v(side_w_bot, corner_sw_top)),
        ("Vertical: side_w_bot -> ramp_right_top", check_v(side_w_bot, ramp_right_top)),

        ("Vertical: side_e_top -> side_e", check_v(side_e_top, side_e)),
        ("Vertical: side_e -> side_e (self-loop)", check_v(side_e, side_e)),
        ("Vertical: side_e -> side_e_bot", check_v(side_e, side_e_bot)),
        ("Vertical: side_e_bot -> corner_se_top", check_v(side_e_bot, corner_se_top)),
        ("Vertical: side_e_bot -> ramp_left_top", check_v(side_e_bot, ramp_left_top)),

        ("Horizontal: corner_sw_top -> face_top_01", check_h(corner_sw_top, face_top_01)),
        ("Horizontal: corner_sw_bot -> face_bot_01", check_h(corner_sw_bot, face_bot_01)),
        ("Vertical: corner_sw_top -> corner_sw_bot", check_v(corner_sw_top, corner_sw_bot)),

        ("Horizontal: face_top_02 -> corner_se_top", check_h(face_top_02, corner_se_top)),
        ("Horizontal: face_bot_02 -> corner_se_bot", check_h(face_bot_02, corner_se_bot)),
        ("Vertical: corner_se_top -> corner_se_bot", check_v(corner_se_top, corner_se_bot)),

        ("Horizontal: face_top_01 -> ramp_left_top", check_h(face_top_01, ramp_left_top)),
        ("Horizontal: face_bot_01 -> ramp_left_bot", check_h(face_bot_01, ramp_left_bot)),
        ("Vertical: ramp_left_top -> ramp_left_bot", check_v(ramp_left_top, ramp_left_bot)),

        ("Horizontal: ramp_right_top -> face_top_02", check_h(ramp_right_top, face_top_02)),
        ("Horizontal: ramp_right_bot -> face_bot_02", check_h(ramp_right_bot, face_bot_02)),
        ("Vertical: ramp_right_top -> ramp_right_bot", check_v(ramp_right_top, ramp_right_bot)),
    ]

    total_mismatches = 0
    print("\n================== 28-BOUNDARY ZERO-SEAM AUDIT ==================")
    for name, m in checks:
        status = "PASSED (0/16)" if m == 0 else f"FAILED ({m}/16 mismatches)"
        print(f"{name:46s}: {status}")
        total_mismatches += m
    print(f"TOTAL MISMATCHES ACROSS ALL 28 JUNCTIONS: {total_mismatches}")
    print("=================================================================\n")

    # =========================================================================
    # 10. RENDER 6X INSPECTION CROPS
    # =========================================================================
    # A. West Flank & Corner (col 3 rows 2..7 + col 4 rows 6..7)
    iw = Image.new("RGBA", (3 * 16, 7 * 16))
    for y in range(7 * 16):
        for x in range(3 * 16):
            iw.putpixel((x, y), grass_base.getpixel((x % 16, y % 16)))
    iw.paste(side_w_top,   (1 * 16, 1 * 16))
    iw.paste(side_w,       (1 * 16, 2 * 16))
    iw.paste(side_w,       (1 * 16, 3 * 16))
    iw.paste(side_w_bot,   (1 * 16, 4 * 16))
    iw.paste(corner_sw_top,(1 * 16, 5 * 16))
    iw.paste(corner_sw_bot,(1 * 16, 6 * 16))
    iw.paste(face_top_01,  (2 * 16, 5 * 16))
    iw.paste(face_bot_01,  (2 * 16, 6 * 16))
    iw.resize((iw.width * 6, iw.height * 6), Image.NEAREST).save(os.path.join(scratch_dir, "flawless_inspect_west_6x.png"))

    # B. East Flank & Corner
    ie = Image.new("RGBA", (3 * 16, 7 * 16))
    for y in range(7 * 16):
        for x in range(3 * 16):
            ie.putpixel((x, y), grass_base.getpixel((x % 16, y % 16)))
    ie.paste(side_e_top,   (1 * 16, 1 * 16))
    ie.paste(side_e,       (1 * 16, 2 * 16))
    ie.paste(side_e,       (1 * 16, 3 * 16))
    ie.paste(side_e_bot,   (1 * 16, 4 * 16))
    ie.paste(corner_se_top,(1 * 16, 5 * 16))
    ie.paste(corner_se_bot,(1 * 16, 6 * 16))
    ie.paste(face_top_02,  (0 * 16, 5 * 16))
    ie.paste(face_bot_02,  (0 * 16, 6 * 16))
    ie.resize((ie.width * 6, ie.height * 6), Image.NEAREST).save(os.path.join(scratch_dir, "flawless_inspect_east_6x.png"))

    # C. Canyon Pass & Ramps
    mud_steps_01_top = Image.open(os.path.join(cliff_dir, "cliff_mud_steps_01_top.png")).convert("RGBA")
    mud_steps_01_bot = Image.open(os.path.join(cliff_dir, "cliff_mud_steps_01_bot.png")).convert("RGBA")
    mud_steps_02_top = Image.open(os.path.join(cliff_dir, "cliff_mud_steps_02_top.png")).convert("RGBA")
    mud_steps_02_bot = Image.open(os.path.join(cliff_dir, "cliff_mud_steps_02_bot.png")).convert("RGBA")
    
    ic = Image.new("RGBA", (6 * 16, 7 * 16))
    for y in range(7 * 16):
        for x in range(6 * 16):
            if x >= 2 * 16 and x < 4 * 16:
                ic.putpixel((x, y), mud_base.getpixel((x % 16, y % 16)))
            else:
                ic.putpixel((x, y), grass_base.getpixel((x % 16, y % 16)))
    ic.paste(face_top_01, (0 * 16, 5 * 16))
    ic.paste(face_bot_01, (0 * 16, 6 * 16))
    ic.paste(side_e_bot,    (1 * 16, 4 * 16))
    ic.paste(ramp_left_top, (1 * 16, 5 * 16))
    ic.paste(ramp_left_bot, (1 * 16, 6 * 16))
    ic.paste(mud_steps_01_top, (2 * 16, 5 * 16))
    ic.paste(mud_steps_01_bot, (2 * 16, 6 * 16))
    ic.paste(mud_steps_02_top, (3 * 16, 5 * 16))
    ic.paste(mud_steps_02_bot, (3 * 16, 6 * 16))
    ic.paste(side_w_bot,     (4 * 16, 4 * 16))
    ic.paste(ramp_right_top, (4 * 16, 5 * 16))
    ic.paste(ramp_right_bot, (4 * 16, 6 * 16))
    ic.paste(face_top_02, (5 * 16, 5 * 16))
    ic.paste(face_bot_02, (5 * 16, 6 * 16))
    ic.resize((ic.width * 6, ic.height * 6), Image.NEAREST).save(os.path.join(scratch_dir, "flawless_inspect_canyon_6x.png"))

craft_flawless_cliffs()
