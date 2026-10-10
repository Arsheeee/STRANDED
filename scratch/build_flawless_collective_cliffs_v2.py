import os
import base64
import json
from PIL import Image

def build_flawless_collective_cliffs():
    brain_dir = r"C:\Users\PAVILION\.gemini\antigravity-ide\brain\84db0e2d-58d2-466d-be05-dbff8f133035"
    scratch_dir = os.path.join(brain_dir, "scratch")
    assets_dir = r"d:\Unity\Projects\STRANDED\Assets\Art\Terrain"
    cliff_dir = os.path.join(assets_dir, "Cliffs")
    preview_path = r"d:\Unity\Projects\STRANDED\cliff_preview.html"

    ref = Image.open(os.path.join(scratch_dir, "stardew_native_512.png")).convert("RGBA")
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
    # 1. NARROW VOLUMETRIC WEST FLANK (cliff_side_w, _top, _bot)
    # =========================================================================
    side_w = Image.new("RGBA", (16, 16))
    for y in range(16):
        # 6px lowland meadow grass
        for x in range(6):
            side_w.putpixel((x, y), grass_base.getpixel((x, y)))
        side_w.putpixel((6, y), PAL_GRASS_BASE if y % 2 == 0 else PAL_GRASS_HI)

        b = 1 if y in [3, 4, 5, 11, 12, 13] else 0
        side_w.putpixel((6 + b, y), PAL_GRASS_SHAD)
        side_w.putpixel((7 + b, y), PAL_ROCK_ON_GR)
        side_w.putpixel((8 + b, y), PAL_SHADOW_DRK)

        for x in range(9 + b, 14):
            side_w.putpixel((x, y), pure_w.getpixel((x, y)))

        side_w.putpixel((14, y), PAL_CREST_HI if y % 2 == 0 else PAL_GOLD_HI)
        side_w.putpixel((15, y), grass_base.getpixel((15, y)))

    # Seamless vertical loop (row 0 == row 15)
    r15_w = [side_w.getpixel((x, 15)) for x in range(16)]
    for x in range(16):
        side_w.putpixel((x, 0), r15_w[x])
        p0 = r15_w[x]
        p2 = side_w.getpixel((x, 2))
        side_w.putpixel((x, 1), tuple(int(p0[i]*0.6 + p2[i]*0.4) for i in range(4)))

    side_w_top = side_w.copy()
    for y in range(4):
        for x in range(16):
            if x < 10 + y:
                side_w_top.putpixel((x, y), grass_base.getpixel((x, y)))
    for x in range(16):
        side_w_top.putpixel((x, 15), side_w.getpixel((x, 0)))

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
    # 2. NARROW VOLUMETRIC EAST FLANK (cliff_side_e, _top, _bot)
    # =========================================================================
    side_e = Image.new("RGBA", (16, 16))
    for y in range(16):
        side_e.putpixel((0, y), grass_base.getpixel((0, y)))
        side_e.putpixel((1, y), PAL_CREST_HI if y % 2 == 0 else PAL_GOLD_HI)

        b = 1 if y in [3, 4, 5, 11, 12, 13] else 0
        for x in range(2, 7 + b):
            side_e.putpixel((x, y), pure_e.getpixel((x + 7, y)))

        side_e.putpixel((7 + b, y), PAL_SHADOW_DRK)
        side_e.putpixel((8 + b, y), PAL_ROCK_ON_GR)
        side_e.putpixel((9 + b, y), PAL_GRASS_SHAD)
        for x in range(10 + b, 16):
            side_e.putpixel((x, y), grass_base.getpixel((x, y)))

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
    # 3. CLEAN SOUTHWEST CORNER TOP & BOT (ROUNDED LOWER CORNER)
    # =========================================================================
    corner_sw_top = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            corner_sw_top.putpixel((x, y), grass_base.getpixel((x, y)))

    for y in range(16):
        for x in range(8, 16):
            corner_sw_top.putpixel((x, y), face_top_01.getpixel((x, y)))

    # Natural crest 90° curve: enters at (14, 0), curves down-right to (15, 1)
    corner_sw_top.putpixel((15, 0), PAL_GRASS_BASE)
    corner_sw_top.putpixel((14, 0), PAL_CREST_HI)
    corner_sw_top.putpixel((13, 0), PAL_GOLD_HI)
    corner_sw_top.putpixel((14, 1), PAL_CREST_HI)
    corner_sw_top.putpixel((15, 1), PAL_CREST_HI)

    for y in range(16):
        corner_sw_top.putpixel((8, y), PAL_SHADOW_DRK)
        corner_sw_top.putpixel((7, y), PAL_ROCK_ON_GR)
        corner_sw_top.putpixel((6, y), PAL_GRASS_SHAD)
        for x in range(6):
            corner_sw_top.putpixel((x, y), grass_base.getpixel((x, y)))

    for x in range(16):
        corner_sw_top.putpixel((x, 0), r0_w[x])
    for y in range(16):
        corner_sw_top.putpixel((15, y), face_top_01.getpixel((0, y)))

    # corner_sw_bot (Clean circular rounded lower corner)
    corner_sw_bot = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            corner_sw_bot.putpixel((x, y), grass_base.getpixel((x, (y + 3) % 16)))

    for y in range(13):
        for x in range(8, 16):
            corner_sw_bot.putpixel((x, y), face_bot_01.getpixel((x, y)))

    arc_sw = {
        0: 8, 1: 8, 2: 8,
        3: 9, 4: 9, 5: 9,
        6: 10, 7: 10, 8: 10,
        9: 11, 10: 11,
        11: 13,
        12: 14
    }

    for y, rx in arc_sw.items():
        for x in range(rx - 2):
            corner_sw_bot.putpixel((x, y), grass_base.getpixel((x, y)))
        if rx - 2 >= 0:
            corner_sw_bot.putpixel((rx - 2, y), PAL_GRASS_SHAD)
        if rx - 1 >= 0:
            corner_sw_bot.putpixel((rx - 1, y), PAL_ROCK_ON_GR)
        corner_sw_bot.putpixel((rx, y), PAL_SHADOW_DRK if y < 11 else PAL_CREVICE)

    for x in range(14):
        corner_sw_bot.putpixel((x, 13), grass_base.getpixel((x, 13)))
        corner_sw_bot.putpixel((x, 14), grass_base.getpixel((x, 14)))
        corner_sw_bot.putpixel((x, 15), grass_base.getpixel((x, 15)))

    for x in [14, 15]:
        corner_sw_bot.putpixel((x, 13), face_bot_01.getpixel((x - 14, 13)))
        corner_sw_bot.putpixel((x, 14), face_bot_01.getpixel((x - 14, 14)))
        corner_sw_bot.putpixel((x, 15), face_bot_01.getpixel((x - 14, 15)))

    for y in range(16):
        corner_sw_bot.putpixel((15, y), face_bot_01.getpixel((0, y)))

    # STRICT ZERO-SEAM HARMONIZATION FOR SW CORNER:
    r0_bot = [corner_sw_bot.getpixel((x, 0)) for x in range(16)]
    for x in range(16):
        corner_sw_top.putpixel((x, 15), r0_bot[x])
        if x < 15:
            p15 = r0_bot[x]
            p13 = corner_sw_top.getpixel((x, 13))
            corner_sw_top.putpixel((x, 14), tuple(int(p15[i]*0.6 + p13[i]*0.4) for i in range(4)))

    for y in range(16):
        corner_sw_top.putpixel((15, y), face_top_01.getpixel((0, y)))
    shared_sw = face_top_01.getpixel((0, 15))
    corner_sw_top.putpixel((15, 15), shared_sw)
    corner_sw_bot.putpixel((15, 0), shared_sw)
    corner_sw_top.putpixel((15, 0), face_top_01.getpixel((0, 0)))

    # =========================================================================
    # 4. CLEAN SOUTHEAST CORNER TOP & BOT (ROUNDED LOWER CORNER)
    # =========================================================================
    corner_se_top = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            corner_se_top.putpixel((x, y), grass_base.getpixel((x, y)))

    for y in range(16):
        for x in range(8):
            corner_se_top.putpixel((x, y), face_top_02.getpixel((x + 8, y)))

    corner_se_top.putpixel((0, 0), PAL_GRASS_BASE)
    corner_se_top.putpixel((1, 0), PAL_CREST_HI)
    corner_se_top.putpixel((2, 0), PAL_GOLD_HI)
    corner_se_top.putpixel((0, 1), PAL_CREST_HI)
    corner_se_top.putpixel((1, 1), PAL_CREST_HI)

    for y in range(16):
        corner_se_top.putpixel((7, y), PAL_SHADOW_DRK)
        corner_se_top.putpixel((8, y), PAL_ROCK_ON_GR)
        corner_se_top.putpixel((9, y), PAL_GRASS_SHAD)
        for x in range(10, 16):
            corner_se_top.putpixel((x, y), grass_base.getpixel((x, y)))

    for x in range(16):
        corner_se_top.putpixel((x, 0), r0_e[x])
    for y in range(16):
        corner_se_top.putpixel((0, y), face_top_02.getpixel((15, y)))

    # corner_se_bot (Clean circular rounded lower corner)
    corner_se_bot = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            corner_se_bot.putpixel((x, y), grass_base.getpixel((x, (y + 4) % 16)))

    for y in range(13):
        for x in range(8):
            corner_se_bot.putpixel((x, y), face_bot_02.getpixel((x + 8, y)))

    arc_se = {
        0: 7, 1: 7, 2: 7,
        3: 6, 4: 6, 5: 6,
        6: 5, 7: 5, 8: 5,
        9: 4, 10: 4,
        11: 2,
        12: 1
    }

    for y, rx in arc_se.items():
        corner_se_bot.putpixel((rx, y), PAL_SHADOW_DRK if y < 11 else PAL_CREVICE)
        if rx + 1 < 16:
            corner_se_bot.putpixel((rx + 1, y), PAL_ROCK_ON_GR)
        if rx + 2 < 16:
            corner_se_bot.putpixel((rx + 2, y), PAL_GRASS_SHAD)
        for x in range(rx + 3, 16):
            corner_se_bot.putpixel((x, y), grass_base.getpixel((x, y)))

    for x in range(2, 16):
        corner_se_bot.putpixel((x, 13), grass_base.getpixel((x, 13)))
        corner_se_bot.putpixel((x, 14), grass_base.getpixel((x, 14)))
        corner_se_bot.putpixel((x, 15), grass_base.getpixel((x, 15)))

    for x in [0, 1]:
        corner_se_bot.putpixel((x, 13), face_bot_02.getpixel((14 + x, 13)))
        corner_se_bot.putpixel((x, 14), face_bot_02.getpixel((14 + x, 14)))
        corner_se_bot.putpixel((x, 15), face_bot_02.getpixel((14 + x, 15)))

    for y in range(16):
        corner_se_bot.putpixel((0, y), face_bot_02.getpixel((15, y)))

    # STRICT ZERO-SEAM HARMONIZATION FOR SE CORNER:
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
    corner_se_top.putpixel((0, 0), face_top_02.getpixel((15, 0)))

    # =========================================================================
    # 5. ZERO-SEAM HARMONIZATION FOR CANYON RAMPS
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

    for x in range(16):
        ramp_left_bot.putpixel((x, 0), ramp_left_top.getpixel((x, 15)))
        ramp_right_bot.putpixel((x, 0), ramp_right_top.getpixel((x, 15)))

    for y in range(16):
        ramp_left_top.putpixel((0, y), face_top_01.getpixel((15, y)))
        ramp_left_bot.putpixel((0, y), face_bot_01.getpixel((15, y)))
    shared_rl = face_top_01.getpixel((15, 15))
    ramp_left_top.putpixel((0, 15), shared_rl)
    ramp_left_bot.putpixel((0, 0), shared_rl)
    for x in range(16):
        ramp_left_top.putpixel((x, 0), r0_e[x])

    for y in range(16):
        ramp_right_top.putpixel((15, y), face_top_02.getpixel((0, y)))
        ramp_right_bot.putpixel((15, y), face_bot_02.getpixel((0, y)))
    shared_rr = face_top_02.getpixel((0, 15))
    ramp_right_top.putpixel((15, 15), shared_rr)
    ramp_right_bot.putpixel((15, 0), shared_rr)
    for x in range(16):
        ramp_right_top.putpixel((x, 0), r0_w[x])

    # =========================================================================
    # 6. OUTER NORTH CORNERS
    # =========================================================================
    outer_tl = Image.open(os.path.join(cliff_dir, "cliff_outer_tl_top.png")).convert("RGBA")
    outer_tr = Image.open(os.path.join(cliff_dir, "cliff_outer_tr_top.png")).convert("RGBA")
    for x in range(16):
        outer_tl.putpixel((x, 15), side_w_top.getpixel((x, 0)))
        outer_tr.putpixel((x, 15), side_e_top.getpixel((x, 0)))

    # =========================================================================
    # 7. SAVE ALL PRODUCTION TILES
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

    print("All production tiles saved.")

    # =========================================================================
    # 8. STRICT MATHEMATICAL ZERO-SEAM AUDIT (ALL 28 JUNCTIONS)
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
    # 9. GENERATE 6X INSPECTION CROPS
    # =========================================================================
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

    # Focused 6x corner views
    sw_view = Image.new("RGBA", (32, 64))
    sw_view.paste(side_w, (0, 0))
    sw_view.paste(side_w_bot, (0, 16))
    sw_view.paste(corner_sw_top, (0, 32))
    sw_view.paste(corner_sw_bot, (0, 48))
    sw_view.paste(face_top_01, (16, 32))
    sw_view.paste(face_bot_01, (16, 48))
    sw_view.resize((32*6, 64*6), Image.NEAREST).save(os.path.join(scratch_dir, "test_clean_sw_assembled_6x.png"))

    se_view = Image.new("RGBA", (32, 64))
    se_view.paste(side_e, (16, 0))
    se_view.paste(side_e_bot, (16, 16))
    se_view.paste(corner_se_top, (16, 32))
    se_view.paste(corner_se_bot, (16, 48))
    se_view.paste(face_top_02, (0, 32))
    se_view.paste(face_bot_02, (0, 48))
    se_view.resize((32*6, 64*6), Image.NEAREST).save(os.path.join(scratch_dir, "test_clean_se_assembled_6x.png"))

    # =========================================================================
    # 10. GENERATE cliff_autotile_sheet.png
    # =========================================================================
    sheet = Image.new("RGBA", (128, 64), (0, 0, 0, 0))
    sheet_grid = [
        ("cliff_outer_tl_top", 0, 0), ("cliff_face_top_01", 1, 0), ("cliff_face_top_02", 2, 0), ("cliff_outer_tr_top", 3, 0),
        ("cliff_ramp_left_top", 4, 0), ("cliff_mud_steps_01_top", 5, 0), ("cliff_mud_steps_02_top", 6, 0), ("cliff_ramp_right_top", 7, 0),
        ("cliff_side_w_top", 0, 1), ("cliff_face_bot_01", 1, 1), ("cliff_face_bot_02", 2, 1), ("cliff_side_e_top", 3, 1),
        ("cliff_ramp_left_bot", 4, 1), ("cliff_mud_steps_01_bot", 5, 1), ("cliff_mud_steps_02_bot", 6, 1), ("cliff_ramp_right_bot", 7, 1),
        ("cliff_side_w", 0, 2), ("cliff_corner_sw_top", 1, 2), ("cliff_corner_se_top", 2, 2), ("cliff_side_e", 3, 2),
        ("cliff_ramp_mid_top", 4, 2), ("cliff_mud_slope_top", 5, 2), ("cliff_mud_steps_top", 6, 2), ("cliff_side_w_bot", 7, 2),
        ("cliff_side_w_bot", 0, 3), ("cliff_corner_sw_bot", 1, 3), ("cliff_corner_se_bot", 2, 3), ("cliff_side_e_bot", 3, 3),
        ("cliff_ramp_mid_bot", 4, 3), ("cliff_mud_slope_bot", 5, 3), ("cliff_mud_steps_bot", 6, 3), ("cliff_side_e_bot", 7, 3),
    ]

    for name, gx, gy in sheet_grid:
        tile_path = os.path.join(cliff_dir, f"{name}.png")
        if os.path.exists(tile_path):
            t_img = Image.open(tile_path).convert("RGBA")
            sheet.paste(t_img, (gx * 16, gy * 16))

    sheet.save(os.path.join(cliff_dir, "cliff_autotile_sheet.png"))
    print("cliff_autotile_sheet.png generated successfully.")

    # =========================================================================
    # 11. RENDER FULL 28x15 PREVIEW SCENE
    # =========================================================================
    SW, SH = 28, 15
    scene = Image.new("RGBA", (SW * 16, SH * 16))
    for y in range(SH):
        for x in range(SW):
            if x in [12, 13]:
                scene.paste(mud_base, (x * 16, y * 16))
            else:
                scene.paste(grass_base, (x * 16, y * 16))

    scene.paste(side_w_top, (3 * 16, 2 * 16))
    scene.paste(side_w,     (3 * 16, 3 * 16))
    scene.paste(side_w,     (3 * 16, 4 * 16))
    scene.paste(side_w_bot, (3 * 16, 5 * 16))
    scene.paste(corner_sw_top, (3 * 16, 6 * 16))
    scene.paste(corner_sw_bot, (3 * 16, 7 * 16))

    for x in range(4, 11):
        t = face_top_01 if (x % 2 == 0) else face_top_02
        b = face_bot_01 if (x % 2 == 0) else face_bot_02
        scene.paste(t, (x * 16, 6 * 16))
        scene.paste(b, (x * 16, 7 * 16))

    scene.paste(side_e_top, (11 * 16, 2 * 16))
    scene.paste(side_e,     (11 * 16, 3 * 16))
    scene.paste(side_e,     (11 * 16, 4 * 16))
    scene.paste(side_e_bot, (11 * 16, 5 * 16))
    scene.paste(ramp_left_top, (11 * 16, 6 * 16))
    scene.paste(ramp_left_bot, (11 * 16, 7 * 16))

    scene.paste(mud_steps_01_top, (12 * 16, 6 * 16))
    scene.paste(mud_steps_01_bot, (12 * 16, 7 * 16))
    scene.paste(mud_steps_02_top, (13 * 16, 6 * 16))
    scene.paste(mud_steps_02_bot, (13 * 16, 7 * 16))

    scene.paste(side_w_top, (14 * 16, 2 * 16))
    scene.paste(side_w,     (14 * 16, 3 * 16))
    scene.paste(side_w,     (14 * 16, 4 * 16))
    scene.paste(side_w_bot, (14 * 16, 5 * 16))
    scene.paste(ramp_right_top, (14 * 16, 6 * 16))
    scene.paste(ramp_right_bot, (14 * 16, 7 * 16))

    for x in range(15, 22):
        t = face_top_01 if (x % 2 == 0) else face_top_02
        b = face_bot_01 if (x % 2 == 0) else face_bot_02
        scene.paste(t, (x * 16, 6 * 16))
        scene.paste(b, (x * 16, 7 * 16))

    scene.paste(corner_se_top, (22 * 16, 6 * 16))
    scene.paste(corner_se_bot, (22 * 16, 7 * 16))
    scene.paste(side_e_top, (22 * 16, 2 * 16))
    scene.paste(side_e,     (22 * 16, 3 * 16))
    scene.paste(side_e,     (22 * 16, 4 * 16))
    scene.paste(side_e_bot, (22 * 16, 5 * 16))

    scene.resize((scene.width * 3, scene.height * 3), Image.NEAREST).save(os.path.join(scratch_dir, "full_preview_scene_3x.png"))
    print("full_preview_scene_3x.png saved successfully.")

    # =========================================================================
    # 12. UPDATE cliff_preview.html WITH ALL BASE64 DATA URIS
    # =========================================================================
    def to_b64(path):
        with open(path, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")

    all_cliff_files = [f for f in os.listdir(cliff_dir) if f.endswith(".png")]
    assets_dict = {}
    for f in all_cliff_files:
        k = f[:-4]
        assets_dict[k] = to_b64(os.path.join(cliff_dir, f))

    grass_path = os.path.join(assets_dir, "Grass", "grass_base_01.png")
    mud_path   = os.path.join(assets_dir, "Dirt", "mud_base_01.png")
    dirt_path  = os.path.join(assets_dir, "Dirt", "dirt_base_01.png")
    if os.path.exists(grass_path): assets_dict["grass_01"] = to_b64(grass_path)
    if os.path.exists(mud_path):   assets_dict["mud_01"]   = to_b64(mud_path)
    if os.path.exists(dirt_path):  assets_dict["dirt_01"]  = to_b64(dirt_path)

    with open(preview_path, "r", encoding="utf-8") as f:
        html = f.read()

    start_tag = "const ASSETS = {"
    start_idx = html.find(start_tag)
    if start_idx != -1:
        end_idx = html.find("};\n", start_idx)
        if end_idx == -1:
            end_idx = html.find("};", start_idx)
        
        assets_json = json.dumps(assets_dict)
        new_assets_block = f"const ASSETS = {assets_json};"
        new_html = html[:start_idx] + new_assets_block + html[end_idx + 2:]
        with open(preview_path, "w", encoding="utf-8") as f:
            f.write(new_html)
        print("cliff_preview.html ASSETS updated successfully.")

if __name__ == "__main__":
    build_flawless_collective_cliffs()
