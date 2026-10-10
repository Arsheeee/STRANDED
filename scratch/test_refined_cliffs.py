import os
from PIL import Image

def test():
    brain_dir = r"C:\Users\PAVILION\.gemini\antigravity-ide\brain\84db0e2d-58d2-466d-be05-dbff8f133035"
    scratch_dir = os.path.join(brain_dir, "scratch")
    assets_dir = r"d:\Unity\Projects\STRANDED\Assets\Art\Terrain"
    cliff_dir = os.path.join(assets_dir, "Cliffs")

    grass_base = Image.open(os.path.join(assets_dir, "Grass", "grass_base_01.png")).convert("RGBA")
    mud_base   = Image.open(os.path.join(assets_dir, "Dirt", "mud_base_01.png")).convert("RGBA")

    face_top_01 = Image.open(os.path.join(cliff_dir, "cliff_face_top_01.png")).convert("RGBA")
    face_bot_01 = Image.open(os.path.join(cliff_dir, "cliff_face_bot_01.png")).convert("RGBA")
    face_top_02 = Image.open(os.path.join(cliff_dir, "cliff_face_top_02.png")).convert("RGBA")
    face_bot_02 = Image.open(os.path.join(cliff_dir, "cliff_face_bot_02.png")).convert("RGBA")

    # Front face row 0 is pure highland grass
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

    PAL_GRASS_BASE = ( 67, 161, 25, 255) # Standard green grass
    PAL_GRASS_HI   = (112, 199, 37, 255) # Grass highlight fleck
    PAL_GRASS_SHAD = ( 45, 115, 18, 255) # Grass shadow
    PAL_ROCK_ON_GR = ( 53,  76, 13, 255) # Contact shadow of rock onto grass

    # Pure 16-row rock slices without any grass rows:
    # face_top rows 4..15 (12 rows), face_bot rows 0..3 (4 rows)
    pure_w = Image.new("RGBA", (16, 16))
    for y in range(12):
        for x in range(16):
            pure_w.putpixel((x, y), face_top_01.getpixel((x, y + 4)))
    for y in range(4):
        for x in range(16):
            pure_w.putpixel((x, y + 12), face_bot_01.getpixel((x, y)))

    pure_e = Image.new("RGBA", (16, 16))
    for y in range(12):
        for x in range(16):
            pure_e.putpixel((x, y), face_top_02.getpixel((x, y + 4)))
    for y in range(4):
        for x in range(16):
            pure_e.putpixel((x, y + 12), face_bot_02.getpixel((x, y)))

    # =========================================================================
    # 1. SLENDER NARROW WEST FLANK (cliff_side_w, _top, _bot)
    # =========================================================================
    # Lowland meadow grass at x=0..6 (7px wide open lawn)
    # Contact shadow at x=7
    # Rock boundary contour at x=8
    # Rock body at x=9..13 (5px textured golden rock)
    # Golden crest rim at x=14
    # Highland plateau grass at x=15
    side_w = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(7):
            side_w.putpixel((x, y), grass_base.getpixel((x, y)))

        # Natural micro-organic wave (+-0 px, solid and clean)
        side_w.putpixel((7, y), PAL_ROCK_ON_GR)
        side_w.putpixel((8, y), PAL_SHADOW_DRK)

        for x in range(9, 14):
            # Sample pure golden rock texture
            side_w.putpixel((x, y), pure_w.getpixel((x, y)))

        side_w.putpixel((14, y), PAL_CREST_HI if (y % 2 == 0) else PAL_GOLD_HI)
        side_w.putpixel((15, y), grass_base.getpixel((15, y)))

    # Seamless vertical looping for infinite vertical walls
    r15_w = [side_w.getpixel((x, 15)) for x in range(16)]
    for x in range(16):
        side_w.putpixel((x, 0), r15_w[x])
        p0 = r15_w[x]
        p2 = side_w.getpixel((x, 2))
        side_w.putpixel((x, 1), tuple(int(p0[i]*0.6 + p2[i]*0.4) for i in range(4)))

    # side_w_top: natural rounded termination into northern terrain
    side_w_top = side_w.copy()
    for y in range(4):
        for x in range(16):
            if x < 10 + y:
                side_w_top.putpixel((x, y), grass_base.getpixel((x, y)))
    for x in range(16):
        side_w_top.putpixel((x, 15), side_w.getpixel((x, 0)))

    # side_w_bot: bottom connector to lower corner / ramp shoulder
    r0_w = [side_w.getpixel((x, 15)) for x in range(16)]
    r0_w[15] = face_top_01.getpixel((0, 0)) # Highland grass vertex

    side_w_bot = side_w.copy()
    for x in range(16):
        side_w_bot.putpixel((x, 0), side_w.getpixel((x, 15)))
        side_w_bot.putpixel((x, 15), r0_w[x])
        pb = r0_w[x]
        p13 = side_w_bot.getpixel((x, 13))
        side_w_bot.putpixel((x, 14), tuple(int(pb[i]*0.6 + p13[i]*0.4) for i in range(4)))

    # =========================================================================
    # 2. SLENDER NARROW EAST FLANK (cliff_side_e, _top, _bot)
    # =========================================================================
    # Highland plateau grass at x=0
    # Golden crest rim at x=1
    # Rock body at x=2..6 (5px textured golden rock)
    # Rock boundary contour at x=7
    # Contact shadow at x=8
    # Lowland meadow grass at x=9..15 (7px wide open lawn)
    side_e = Image.new("RGBA", (16, 16))
    for y in range(16):
        side_e.putpixel((0, y), grass_base.getpixel((0, y)))
        side_e.putpixel((1, y), PAL_CREST_HI if (y % 2 == 0) else PAL_GOLD_HI)

        for x in range(2, 7):
            side_e.putpixel((x, y), pure_e.getpixel((x + 7, y)))

        side_e.putpixel((7, y), PAL_SHADOW_DRK)
        side_e.putpixel((8, y), PAL_ROCK_ON_GR)
        for x in range(9, 16):
            side_e.putpixel((x, y), grass_base.getpixel((x, y)))

    # Seamless vertical looping
    r15_e = [side_e.getpixel((x, 15)) for x in range(16)]
    for x in range(16):
        side_e.putpixel((x, 0), r15_e[x])
        p0 = r15_e[x]
        p2 = side_e.getpixel((x, 2))
        side_e.putpixel((x, 1), tuple(int(p0[i]*0.6 + p2[i]*0.4) for i in range(4)))

    side_e_top = side_e.copy()
    for y in range(4):
        for x in range(16):
            if x > 5 - y:
                side_e_top.putpixel((x, y), grass_base.getpixel((x, y)))
    for x in range(16):
        side_e_top.putpixel((x, 15), side_e.getpixel((x, 0)))

    r0_e = [side_e.getpixel((x, 15)) for x in range(16)]
    r0_e[0] = face_top_02.getpixel((15, 0)) # Highland grass vertex

    side_e_bot = side_e.copy()
    for x in range(16):
        side_e_bot.putpixel((x, 0), side_e.getpixel((x, 15)))
        side_e_bot.putpixel((x, 15), r0_e[x])
        pb = r0_e[x]
        p13 = side_e_bot.getpixel((x, 13))
        side_e_bot.putpixel((x, 14), tuple(int(pb[i]*0.6 + p13[i]*0.4) for i in range(4)))

    # =========================================================================
    # 3. REFINED SOUTHWEST CORNER TOP (Volumetric outer shoulder)
    # =========================================================================
    # Top edge (y=0) connects to side_w_bot row 15 (r0_w):
    #   x=0..6: grass, x=7: shadow, x=8: outline, x=9..13: rock, x=14: crest rim, x=15: highland grass
    # East edge (x=15) connects to face_top_01 column 0:
    #   y=0: highland grass, y=1: crest rim, y=2..15: rock face
    corner_sw_top = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            corner_sw_top.putpixel((x, y), grass_base.getpixel((x, y)))

    # Fill rock body for x=8..15 across rows 0..15 with pure golden rock from face_top_01
    for y in range(16):
        for x in range(8, 16):
            corner_sw_top.putpixel((x, y), face_top_01.getpixel((x - 8, y)))

    # Outline & contact shadow on the west side of the rock
    for y in range(16):
        corner_sw_top.putpixel((8, y), PAL_SHADOW_DRK)
        corner_sw_top.putpixel((7, y), PAL_ROCK_ON_GR)
        corner_sw_top.putpixel((6, y), PAL_GRASS_SHAD)

    # NOW: The crest rim curve!
    # Enters at (14, 0) from side_w_bot.
    # Exits at (15, 1) into face_top_01.
    # Vertex (15, 0) is highland plateau grass!
    corner_sw_top.putpixel((15, 0), grass_base.getpixel((15, 0)))
    corner_sw_top.putpixel((14, 0), PAL_CREST_HI)
    corner_sw_top.putpixel((13, 0), PAL_GOLD_HI)

    corner_sw_top.putpixel((15, 1), face_top_01.getpixel((0, 1))) # PAL_CREST_HI
    corner_sw_top.putpixel((14, 1), PAL_CREST_HI)
    corner_sw_top.putpixel((13, 1), PAL_GOLD_HI)

    # Below y=1, columns 13..15 are natural rock face (NO horizontal crest bar across rock!)
    for y in range(2, 16):
        for x in range(9, 16):
            corner_sw_top.putpixel((x, y), face_top_01.getpixel((x - 8, y)))

    # Exact boundary clamping:
    # Row 0 matches side_w_bot row 15
    for x in range(16):
        corner_sw_top.putpixel((x, 0), r0_w[x])
    # Column 15 matches face_top_01 column 0
    for y in range(16):
        corner_sw_top.putpixel((15, y), face_top_01.getpixel((0, y)))

    # =========================================================================
    # 4. REFINED SOUTHWEST CORNER BOT (CLEAN ORGANIC ROUNDED BASE)
    # =========================================================================
    # Top edge (y=0) connects to corner_sw_top row 15
    # East edge (x=15) connects to face_bot_01 column 0
    # Bottom edge (y=15): lowland grass, with rock base at the bottom
    corner_sw_bot = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            corner_sw_bot.putpixel((x, y), grass_base.getpixel((x, (y + 3) % 16)))

    # Fill base rock texture from face_bot_01
    for y in range(16):
        for x in range(8, 16):
            corner_sw_bot.putpixel((x, y), face_bot_01.getpixel((x - 8, y)))

    # Smooth circular arc for outer boulder edge:
    # y=0..3: x=8 (straight vertical continuation from top tile)
    # y=4..6: x=8
    # y=7..9: x=9
    # y=10..11: x=10
    # y=12: x=11
    # y=13: x=12
    # y=14: x=13
    # y=15: x=14
    arc_sw = {
        0: 8,  1: 8,  2: 8,  3: 8,
        4: 8,  5: 8,  6: 8,
        7: 9,  8: 9,  9: 9,
        10: 10, 11: 10,
        12: 11,
        13: 12,
        14: 13,
        15: 14
    }

    for y, rx in arc_sw.items():
        # Everything to the left of the boulder contour is clean meadow grass:
        for x in range(rx - 2):
            corner_sw_bot.putpixel((x, y), grass_base.getpixel((x, (y + 3) % 16)))
        if rx - 2 >= 0:
            corner_sw_bot.putpixel((rx - 2, y), PAL_GRASS_SHAD)
        if rx - 1 >= 0:
            corner_sw_bot.putpixel((rx - 1, y), PAL_ROCK_ON_GR)
        # Rock border contour:
        corner_sw_bot.putpixel((rx, y), PAL_SHADOW_DRK if y < 12 else PAL_CREVICE)

    # Harmonize the bottom row (y=15) with face_bot_01:
    # face_bot_01 has crevice base at y=15: (64, 42, 6, 255)
    corner_sw_bot.putpixel((15, 15), face_bot_01.getpixel((0, 15)))
    corner_sw_bot.putpixel((14, 15), face_bot_01.getpixel((0, 15)))
    corner_sw_bot.putpixel((15, 14), face_bot_01.getpixel((0, 14)))
    corner_sw_bot.putpixel((14, 14), face_bot_01.getpixel((0, 14)))
    corner_sw_bot.putpixel((15, 13), face_bot_01.getpixel((0, 13)))
    corner_sw_bot.putpixel((14, 13), face_bot_01.getpixel((0, 13)))

    # East edge matches face_bot_01 column 0
    for y in range(16):
        corner_sw_bot.putpixel((15, y), face_bot_01.getpixel((0, y)))

    # Harmonize top row of corner_sw_bot with bottom row of corner_sw_top
    r0_sw_bot = [corner_sw_bot.getpixel((x, 0)) for x in range(16)]
    for x in range(16):
        corner_sw_top.putpixel((x, 15), r0_sw_bot[x])
        if x < 15:
            p15 = r0_sw_bot[x]
            p13 = corner_sw_top.getpixel((x, 13))
            corner_sw_top.putpixel((x, 14), tuple(int(p15[i]*0.6 + p13[i]*0.4) for i in range(4)))

    # Enforce exact column 15 of corner_sw_top matches face_top_01 column 0
    for y in range(16):
        corner_sw_top.putpixel((15, y), face_top_01.getpixel((0, y)))
    shared_sw = face_top_01.getpixel((0, 15))
    corner_sw_top.putpixel((15, 15), shared_sw)
    corner_sw_bot.putpixel((15, 0), shared_sw)

    # =========================================================================
    # 5. REFINED SOUTHEAST CORNER TOP (Volumetric outer shoulder)
    # =========================================================================
    # Top edge (y=0) connects to side_e_bot row 15 (r0_e):
    #   x=0: highland grass, x=1: crest rim, x=2..6: rock, x=7: shadow, x=8: rock on grass, x=9..15: grass
    # West edge (x=0) connects to face_top_02 column 15:
    #   y=0: highland grass, y=1: crest rim, y=2..15: rock face
    corner_se_top = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            corner_se_top.putpixel((x, y), grass_base.getpixel((x, y)))

    # Fill rock body for x=0..7 across rows 0..15 with pure golden rock from face_top_02
    for y in range(16):
        for x in range(8):
            corner_se_top.putpixel((x, y), face_top_02.getpixel((x + 8, y)))

    # Outline & contact shadow on the east side of the rock
    for y in range(16):
        corner_se_top.putpixel((7, y), PAL_SHADOW_DRK)
        corner_se_top.putpixel((8, y), PAL_ROCK_ON_GR)
        corner_se_top.putpixel((9, y), PAL_GRASS_SHAD)

    # NOW: The crest rim curve!
    # Enters at (1, 0) from side_e_bot.
    # Exits at (0, 1) into face_top_02.
    # Vertex (0, 0) is highland plateau grass!
    corner_se_top.putpixel((0, 0), grass_base.getpixel((0, 0)))
    corner_se_top.putpixel((1, 0), PAL_CREST_HI)
    corner_se_top.putpixel((2, 0), PAL_GOLD_HI)

    corner_se_top.putpixel((0, 1), face_top_02.getpixel((15, 1))) # PAL_CREST_HI
    corner_se_top.putpixel((1, 1), PAL_CREST_HI)
    corner_se_top.putpixel((2, 1), PAL_GOLD_HI)

    # Below y=1, columns 0..2 are natural rock face (NO horizontal crest bar across rock!)
    for y in range(2, 16):
        for x in range(7):
            corner_se_top.putpixel((x, y), face_top_02.getpixel((x + 8, y)))

    # Exact boundary clamping:
    # Row 0 matches side_e_bot row 15
    for x in range(16):
        corner_se_top.putpixel((x, 0), r0_e[x])
    # Column 0 matches face_top_02 column 15
    for y in range(16):
        corner_se_top.putpixel((0, y), face_top_02.getpixel((15, y)))

    # =========================================================================
    # 6. REFINED SOUTHEAST CORNER BOT (CLEAN ORGANIC ROUNDED BASE)
    # =========================================================================
    # Top edge (y=0) connects to corner_se_top row 15
    # West edge (x=0) connects to face_bot_02 column 15
    corner_se_bot = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            corner_se_bot.putpixel((x, y), grass_base.getpixel((x, (y + 5) % 16)))

    # Fill base rock texture from face_bot_02
    for y in range(16):
        for x in range(8):
            corner_se_bot.putpixel((x, y), face_bot_02.getpixel((x + 8, y)))

    # Symmetrical circular arc for east outer boulder edge:
    arc_se = {
        0: 7,  1: 7,  2: 7,  3: 7,
        4: 7,  5: 7,  6: 7,
        7: 6,  8: 6,  9: 6,
        10: 5, 11: 5,
        12: 4,
        13: 3,
        14: 2,
        15: 1
    }

    for y, rx in arc_se.items():
        # Rock border contour:
        corner_se_bot.putpixel((rx, y), PAL_SHADOW_DRK if y < 12 else PAL_CREVICE)
        if rx + 1 < 16:
            corner_se_bot.putpixel((rx + 1, y), PAL_ROCK_ON_GR)
        if rx + 2 < 16:
            corner_se_bot.putpixel((rx + 2, y), PAL_GRASS_SHAD)
        for x in range(rx + 3, 16):
            corner_se_bot.putpixel((x, y), grass_base.getpixel((x, (y + 5) % 16)))

    # Harmonize the bottom row (y=15) with face_bot_02:
    corner_se_bot.putpixel((0, 15), face_bot_02.getpixel((15, 15)))
    corner_se_bot.putpixel((1, 15), face_bot_02.getpixel((15, 15)))
    corner_se_bot.putpixel((0, 14), face_bot_02.getpixel((15, 14)))
    corner_se_bot.putpixel((1, 14), face_bot_02.getpixel((15, 14)))
    corner_se_bot.putpixel((0, 13), face_bot_02.getpixel((15, 13)))
    corner_se_bot.putpixel((1, 13), face_bot_02.getpixel((15, 13)))

    # West edge matches face_bot_02 column 15
    for y in range(16):
        corner_se_bot.putpixel((0, y), face_bot_02.getpixel((15, y)))

    # Harmonize top row of corner_se_bot with bottom row of corner_se_top
    r0_se_bot = [corner_se_bot.getpixel((x, 0)) for x in range(16)]
    for x in range(16):
        corner_se_top.putpixel((x, 15), r0_se_bot[x])
        if x > 0:
            p15 = r0_se_bot[x]
            p13 = corner_se_top.getpixel((x, 13))
            corner_se_top.putpixel((x, 14), tuple(int(p15[i]*0.6 + p13[i]*0.4) for i in range(4)))

    for y in range(16):
        corner_se_top.putpixel((0, y), face_top_02.getpixel((15, y)))
    shared_se = face_top_02.getpixel((15, 15))
    corner_se_top.putpixel((0, 15), shared_se)
    corner_se_bot.putpixel((0, 0), shared_se)

    # Save test zoom composites
    sw_comp = Image.new("RGBA", (3*16, 3*16))
    sw_comp.paste(grass_base, (0, 0)); sw_comp.paste(side_w_bot, (16, 0)); sw_comp.paste(grass_base, (32, 0))
    sw_comp.paste(grass_base, (0, 16)); sw_comp.paste(corner_sw_top, (16, 16)); sw_comp.paste(face_top_01, (32, 16))
    sw_comp.paste(grass_base, (0, 32)); sw_comp.paste(corner_sw_bot, (16, 32)); sw_comp.paste(face_bot_01, (32, 32))
    sw_comp.resize((sw_comp.width * 6, sw_comp.height * 6), Image.NEAREST).save(os.path.join(scratch_dir, "test_clean_sw_assembled_6x.png"))

    se_comp = Image.new("RGBA", (3*16, 3*16))
    se_comp.paste(grass_base, (0, 0)); se_comp.paste(side_e_bot, (16, 0)); se_comp.paste(grass_base, (32, 0))
    se_comp.paste(face_top_02, (0, 16)); se_comp.paste(corner_se_top, (16, 16)); se_comp.paste(grass_base, (32, 16))
    se_comp.paste(face_bot_02, (0, 32)); se_comp.paste(corner_se_bot, (16, 32)); se_comp.paste(grass_base, (32, 32))
    se_comp.resize((se_comp.width * 6, se_comp.height * 6), Image.NEAREST).save(os.path.join(scratch_dir, "test_clean_se_assembled_6x.png"))

    print("Test zoom composites saved successfully.")

test()
