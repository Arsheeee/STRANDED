import os
from PIL import Image

def main():
    brain_dir = r"C:\Users\PAVILION\.gemini\antigravity-ide\brain\84db0e2d-58d2-466d-be05-dbff8f133035"
    scratch_dir = os.path.join(brain_dir, "scratch")
    cliffs_dir = r"d:\Unity\Projects\STRANDED\Assets\Art\Terrain\Cliffs"
    grass_dir  = r"d:\Unity\Projects\STRANDED\Assets\Art\Terrain\Grass"
    dirt_dir   = r"d:\Unity\Projects\STRANDED\Assets\Art\Terrain\Dirt"

    grass_base = Image.open(os.path.join(grass_dir, "grass_base_01.png")).convert("RGBA")
    mud_base   = Image.open(os.path.join(dirt_dir, "mud_base_01.png")).convert("RGBA")

    # Master front cliff face tiles
    t1 = Image.open(os.path.join(cliffs_dir, "cliff_face_top_01.png")).convert("RGBA")
    t2 = Image.open(os.path.join(cliffs_dir, "cliff_face_top_02.png")).convert("RGBA")
    b1 = Image.open(os.path.join(cliffs_dir, "cliff_face_bot_01.png")).convert("RGBA")
    b2 = Image.open(os.path.join(cliffs_dir, "cliff_face_bot_02.png")).convert("RGBA")

    # Palette
    G_LIGHT   = (112, 199, 37, 255)   # #70c725
    G_MID     = (68, 163, 24, 255)    # #44a318
    G_DARK    = (58, 147, 17, 255)    # #3a9311
    G_DEEP    = (50, 133, 48, 255)    # #328530
    G_SHADOW  = (35, 95, 10, 255)     # #235f0a

    R_HILITE  = (209, 175, 24, 255)   # #d1af18
    R_GOLD    = (198, 145, 18, 255)   # #c69112
    R_MID     = (160, 120, 15, 255)   # #a0780f
    R_WARM    = (143, 108, 14, 255)   # #8f6c0e
    R_SHADOW  = (122, 93, 12, 255)    # #7a5d0c
    R_DARK    = (103, 82, 10, 255)    # #67520a
    R_CREVICE = (64, 42, 6, 255)      # #402a06
    R_BASE    = (45, 30, 4, 255)      # #2d1e04

    E_HILITE  = (182, 145, 20, 255)
    E_GOLD    = (165, 122, 16, 255)
    E_MID     = (136, 100, 13, 255)
    E_WARM    = (120, 90, 12, 255)
    E_SHADOW  = (102, 76, 10, 255)
    E_DARK    = (78, 58, 8, 255)
    E_CREVICE = (52, 34, 5, 255)

    # =============================================================
    # 1. ORGANIC WEST FLANK (cliff_side_w_top, _w, _w_bot)
    # =============================================================
    # Rock wall on left x=0..7 (8px wide)
    # Grass overhang x=8..10
    # Meadow grass x=11..15
    def craft_west_flank():
        im = grass_base.copy()
        for y in range(16):
            im.putpixel((10, y), G_MID if (y*3)%4 == 0 else G_DARK)
            im.putpixel((9, y), G_LIGHT if (y*5)%3 == 0 else G_MID)
            im.putpixel((8, y), G_SHADOW)

            for x in range(8):
                if y == 7:
                    im.putpixel((x, y), R_CREVICE if x < 6 else R_BASE)
                elif y < 7:
                    dx = abs(x - 3)
                    dy = abs(y - 3)
                    dist = dx * 1.1 + dy
                    if x == 7: im.putpixel((x, y), R_DARK if y in [2, 3, 4] else R_CREVICE)
                    elif x == 6: im.putpixel((x, y), R_SHADOW if y in [2, 3, 4] else R_DARK)
                    elif dist <= 1.2: im.putpixel((x, y), R_HILITE if y in [2, 3] else R_GOLD)
                    elif dist <= 2.5: im.putpixel((x, y), R_GOLD if y <= 3 else R_MID)
                    elif dist <= 4.0: im.putpixel((x, y), R_MID if y <= 4 else R_WARM)
                    else: im.putpixel((x, y), R_SHADOW if y >= 5 else R_WARM)
                else:
                    dx = abs(x - 2)
                    dy = abs(y - 11)
                    dist = dx * 1.1 + dy
                    if x == 7: im.putpixel((x, y), R_DARK if y in [10, 11, 12] else R_CREVICE)
                    elif x == 6: im.putpixel((x, y), R_SHADOW if y in [10, 11, 12] else R_DARK)
                    elif dist <= 1.2: im.putpixel((x, y), R_HILITE if y in [10, 11] else R_GOLD)
                    elif dist <= 2.5: im.putpixel((x, y), R_GOLD if y <= 11 else R_MID)
                    elif dist <= 4.0: im.putpixel((x, y), R_MID if y <= 12 else R_WARM)
                    else: im.putpixel((x, y), R_SHADOW if y >= 13 else R_WARM)
        return im

    side_w = craft_west_flank()

    side_w_top = side_w.copy()
    for y in range(4):
        for x in range(16):
            if y == 0: side_w_top.putpixel((x, y), grass_base.getpixel((x, y)))
            elif y == 1:
                if x < 4: side_w_top.putpixel((x, y), grass_base.getpixel((x, y)))
                elif x == 4: side_w_top.putpixel((x, y), G_SHADOW)
                elif x < 7: side_w_top.putpixel((x, y), R_MID if x == 5 else R_SHADOW)
            elif y == 2:
                if x < 2: side_w_top.putpixel((x, y), grass_base.getpixel((x, y)))
                elif x == 2: side_w_top.putpixel((x, y), G_SHADOW)
                elif x < 7: side_w_top.putpixel((x, y), R_GOLD if x in [3, 4] else R_MID)
            elif y == 3:
                if x == 0: side_w_top.putpixel((x, y), grass_base.getpixel((x, y)))
                elif x == 1: side_w_top.putpixel((x, y), G_SHADOW)

    side_w_bot = side_w.copy()
    for y in range(13, 16):
        for x in range(8):
            if y == 15: side_w_bot.putpixel((x, y), R_BASE if x < 6 else R_CREVICE)
            elif y == 14: side_w_bot.putpixel((x, y), R_CREVICE if x < 5 else R_BASE)

    # =============================================================
    # 2. ORGANIC EAST FLANK (cliff_side_e_top, _e, _e_bot)
    # =============================================================
    # Grass on left x=0..4, Overhang x=5..7, Rock wall on right x=8..15
    def craft_east_flank():
        im = grass_base.copy()
        for y in range(16):
            im.putpixel((5, y), G_MID if (y*3)%4 == 0 else G_DARK)
            im.putpixel((6, y), G_LIGHT if (y*5)%3 == 0 else G_MID)
            im.putpixel((7, y), G_SHADOW)

            for x in range(8, 16):
                rx = x - 8
                if y == 7:
                    im.putpixel((x, y), E_CREVICE if rx > 1 else E_DARK)
                elif y < 7:
                    dx = abs(rx - 4)
                    dy = abs(y - 3)
                    dist = dx * 1.1 + dy
                    if rx == 0: im.putpixel((x, y), E_DARK if y in [2, 3, 4] else E_CREVICE)
                    elif rx == 1: im.putpixel((x, y), E_SHADOW if y in [2, 3, 4] else E_DARK)
                    elif dist <= 1.2: im.putpixel((x, y), E_HILITE if y in [2, 3] else E_GOLD)
                    elif dist <= 2.5: im.putpixel((x, y), E_GOLD if y <= 3 else E_MID)
                    elif dist <= 4.0: im.putpixel((x, y), E_MID if y <= 4 else E_WARM)
                    else: im.putpixel((x, y), E_SHADOW if y >= 5 else E_WARM)
                else:
                    dx = abs(rx - 5)
                    dy = abs(y - 11)
                    dist = dx * 1.1 + dy
                    if rx == 0: im.putpixel((x, y), E_DARK if y in [10, 11, 12] else E_CREVICE)
                    elif rx == 1: im.putpixel((x, y), E_SHADOW if y in [10, 11, 12] else E_DARK)
                    elif dist <= 1.2: im.putpixel((x, y), E_HILITE if y in [10, 11] else E_GOLD)
                    elif dist <= 2.5: im.putpixel((x, y), E_GOLD if y <= 11 else E_MID)
                    elif dist <= 4.0: im.putpixel((x, y), E_MID if y <= 12 else E_WARM)
                    else: im.putpixel((x, y), E_SHADOW if y >= 13 else E_WARM)
        return im

    side_e = craft_east_flank()

    side_e_top = side_e.copy()
    for y in range(4):
        for x in range(16):
            if y == 0: side_e_top.putpixel((x, y), grass_base.getpixel((x, y)))
            elif y == 1:
                if x > 11: side_e_top.putpixel((x, y), grass_base.getpixel((x, y)))
                elif x == 11: side_e_top.putpixel((x, y), G_SHADOW)
                elif x >= 8: side_e_top.putpixel((x, y), E_MID if x == 10 else E_SHADOW)
            elif y == 2:
                if x > 13: side_e_top.putpixel((x, y), grass_base.getpixel((x, y)))
                elif x == 13: side_e_top.putpixel((x, y), G_SHADOW)
                elif x >= 8: side_e_top.putpixel((x, y), E_GOLD if x in [10, 11] else E_MID)
            elif y == 3:
                if x == 15: side_e_top.putpixel((x, y), grass_base.getpixel((x, y)))
                elif x == 14: side_e_top.putpixel((x, y), G_SHADOW)

    side_e_bot = side_e.copy()
    for y in range(13, 16):
        for x in range(8, 16):
            if y == 15: side_e_bot.putpixel((x, y), E_CREVICE if x > 10 else E_DARK)
            elif y == 14: side_e_bot.putpixel((x, y), E_DARK if x > 10 else E_SHADOW)

    # =============================================================
    # 3. SOUTHWEST OUTER CORNER (cliff_corner_sw_top & bot)
    # =============================================================
    # Top edge y=0 connects to side_w_bot (y=15): rock at x=0..7, grass at x=8..15.
    # Right edge x=15 connects to t1 (x=0).
    # Curves 90° from vertical flank (top) around to front face (right)!
    # Left side x=0..7 is the outer vertical drop.
    # Top-right x=8..15 is plateau grass crowning the corner.

    sw_top = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            sw_top.putpixel((x, y), grass_base.getpixel((x, y)))

    # Draw rounded corner boulder:
    for y in range(16):
        for x in range(16):
            # Distance from inner corner rim:
            # Grass overhang curves from (8, 0) through (10, 4) down to (15, 4)
            # Underneath overhang is the golden corner boulder!
            if y <= 4 and x >= 8:
                # Grass overhang
                if y == 4: sw_top.putpixel((x, y), G_SHADOW)
                elif y == 3: sw_top.putpixel((x, y), G_MID if x % 2 == 0 else G_LIGHT)
                else: sw_top.putpixel((x, y), grass_base.getpixel((x, y)))
            elif x <= 7:
                # West outer rock face (matches side_w_bot on top!):
                if y == 0:
                    sw_top.putpixel((x, y), side_w_bot.getpixel((x, 15)))
                elif y <= 4:
                    # Boulder crest flowing from flank down to corner
                    if x in [1, 2, 3]: sw_top.putpixel((x, y), R_HILITE if y in [1, 2] else R_GOLD)
                    elif x in [4, 5]: sw_top.putpixel((x, y), R_GOLD if y <= 2 else R_MID)
                    elif x == 0: sw_top.putpixel((x, y), R_SHADOW if y in [1, 2] else R_DARK)
                    else: sw_top.putpixel((x, y), R_WARM if y <= 3 else R_SHADOW)
                elif y <= 10:
                    # Center of corner boulder
                    dx = abs(x - 3)
                    dy = abs(y - 7)
                    dist = dx + dy
                    if x == 0: sw_top.putpixel((x, y), R_DARK if y in [6, 7, 8] else R_CREVICE)
                    elif dist <= 2: sw_top.putpixel((x, y), R_GOLD if y == 7 else R_MID)
                    elif dist <= 4: sw_top.putpixel((x, y), R_MID if y <= 7 else R_WARM)
                    else: sw_top.putpixel((x, y), R_SHADOW)
                else:
                    # Lower corner boulder
                    if x == 0: sw_top.putpixel((x, y), R_CREVICE if y == 15 else R_BASE)
                    elif x <= 5: sw_top.putpixel((x, y), R_WARM if y < 13 else R_SHADOW)
                    else: sw_top.putpixel((x, y), R_SHADOW if y < 14 else R_DARK)
            else:
                # Front face section (x=8..15):
                # Merges into t1 at x=15:
                t1_p = t1.getpixel((x, y))
                # Soft blend towards t1:
                sw_top.putpixel((x, y), t1_p)

    # Southwest Outer Corner Bot:
    sw_bot = b1.copy()
    # Left side (x=0..7) has the lower tier of the west corner boulder:
    for y in range(16):
        for x in range(8):
            if y == 15:
                # Ground contact shadow
                sw_bot.putpixel((x, y), R_BASE)
            elif y == 14:
                sw_bot.putpixel((x, y), R_CREVICE if x < 6 else R_BASE)
            elif x == 0:
                sw_bot.putpixel((x, y), R_BASE if y >= 10 else R_CREVICE)
            elif x in [1, 2]:
                sw_bot.putpixel((x, y), R_CREVICE if y >= 8 else R_DARK)
            elif x in [3, 4]:
                sw_bot.putpixel((x, y), R_DARK if y >= 6 else R_SHADOW)
            else:
                sw_bot.putpixel((x, y), R_WARM if y < 8 else R_SHADOW)

    # Match exact edges:
    for y in range(16): sw_top.putpixel((15, y), t1.getpixel((0, y)))
    for y in range(16): sw_bot.putpixel((15, y), b1.getpixel((0, y)))
    for x in range(16): sw_top.putpixel((x, 0), side_w_bot.getpixel((x, 15)))
    for x in range(16): sw_bot.putpixel((x, 0), sw_top.getpixel((x, 15)))


    # =============================================================
    # 4. SOUTHEAST OUTER CORNER (cliff_corner_se_top & bot)
    # =============================================================
    # Top edge y=0 connects to side_e_bot (y=15): grass at x=0..7, rock at x=8..15.
    # Left edge x=0 connects to t2 (x=15).
    # Curves 90° from vertical flank (top) around to front face (left)!

    se_top = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            se_top.putpixel((x, y), grass_base.getpixel((x, y)))

    for y in range(16):
        for x in range(16):
            if y <= 4 and x <= 7:
                # Grass overhang
                if y == 4: se_top.putpixel((x, y), G_SHADOW)
                elif y == 3: se_top.putpixel((x, y), G_MID if x % 2 == 0 else G_LIGHT)
                else: se_top.putpixel((x, y), grass_base.getpixel((x, y)))
            elif x >= 8:
                # East outer rock face (matches side_e_bot on top!):
                rx = x - 8
                if y == 0:
                    se_top.putpixel((x, y), side_e_bot.getpixel((x, 15)))
                elif y <= 4:
                    if rx in [3, 4, 5]: se_top.putpixel((x, y), E_HILITE if y in [1, 2] else E_GOLD)
                    elif rx in [1, 2]: se_top.putpixel((x, y), E_GOLD if y <= 2 else E_MID)
                    elif rx == 7: se_top.putpixel((x, y), E_SHADOW if y in [1, 2] else E_DARK)
                    else: se_top.putpixel((x, y), E_WARM if y <= 3 else E_SHADOW)
                elif y <= 10:
                    dx = abs(rx - 4)
                    dy = abs(y - 7)
                    dist = dx + dy
                    if rx == 7: se_top.putpixel((x, y), E_DARK if y in [6, 7, 8] else E_CREVICE)
                    elif dist <= 2: se_top.putpixel((x, y), E_GOLD if y == 7 else E_MID)
                    elif dist <= 4: se_top.putpixel((x, y), E_MID if y <= 7 else E_WARM)
                    else: se_top.putpixel((x, y), E_SHADOW)
                else:
                    if rx == 7: se_top.putpixel((x, y), E_CREVICE if y == 15 else E_DARK)
                    elif rx >= 2: se_top.putpixel((x, y), E_WARM if y < 13 else E_SHADOW)
                    else: se_top.putpixel((x, y), E_SHADOW if y < 14 else E_DARK)
            else:
                # Front face section (x=0..7) matches t2:
                t2_p = t2.getpixel((x, y))
                se_top.putpixel((x, y), t2_p)

    # Southeast Outer Corner Bot:
    se_bot = b2.copy()
    for y in range(16):
        for x in range(8, 16):
            rx = x - 8
            if y == 15:
                se_bot.putpixel((x, y), R_BASE)
            elif y == 14:
                se_bot.putpixel((x, y), R_CREVICE if rx > 2 else R_BASE)
            elif rx == 7:
                se_bot.putpixel((x, y), R_BASE if y >= 10 else R_CREVICE)
            elif rx in [5, 6]:
                se_bot.putpixel((x, y), E_CREVICE if y >= 8 else E_DARK)
            elif rx in [3, 4]:
                se_bot.putpixel((x, y), E_DARK if y >= 6 else E_SHADOW)
            else:
                se_bot.putpixel((x, y), E_WARM if y < 8 else E_SHADOW)

    for y in range(16): se_top.putpixel((0, y), t2.getpixel((15, y)))
    for y in range(16): se_bot.putpixel((0, y), b2.getpixel((15, y)))
    for x in range(16): se_top.putpixel((x, 0), side_e_bot.getpixel((x, 15)))
    for x in range(16): se_bot.putpixel((x, 0), se_top.getpixel((x, 15)))


    # =============================================================
    # 5. CANYON SHOULDERS (cliff_ramp_left & cliff_ramp_right)
    # =============================================================
    ramp_left_top = t2.copy()
    for x in range(16): ramp_left_top.putpixel((x, 0), side_e_bot.getpixel((x, 15)))
    for y in range(1, 16):
        for x in range(11, 16):
            if x == 15: ramp_left_top.putpixel((x, y), E_DARK if y in [4, 5, 6, 12, 13] else E_CREVICE)
            elif x == 14: ramp_left_top.putpixel((x, y), E_SHADOW if y in [3, 4, 11, 12] else E_DARK)
            elif x in [12, 13]: ramp_left_top.putpixel((x, y), E_MID if y in [2, 3, 10, 11] else E_WARM)

    ramp_left_bot = b2.copy()
    for x in range(16): ramp_left_bot.putpixel((x, 0), ramp_left_top.getpixel((x, 15)))
    for y in range(1, 16):
        for x in range(11, 16):
            if y >= 14: ramp_left_bot.putpixel((x, y), R_BASE if x < 15 else R_CREVICE)
            elif x == 15: ramp_left_bot.putpixel((x, y), E_CREVICE if y < 14 else R_BASE)
            elif x == 14: ramp_left_bot.putpixel((x, y), E_DARK if y < 12 else R_CREVICE)

    ramp_right_top = t1.copy()
    for x in range(16): ramp_right_top.putpixel((x, 0), side_w_bot.getpixel((x, 15)))
    for y in range(1, 16):
        for x in range(5):
            if x == 0: ramp_right_top.putpixel((x, y), R_CREVICE if y in [4, 5, 6, 12, 13] else R_DARK)
            elif x == 1: ramp_right_top.putpixel((x, y), R_DARK if y in [3, 4, 11, 12] else R_SHADOW)
            elif x in [2, 3]: ramp_right_top.putpixel((x, y), R_MID if y in [2, 3, 10, 11] else R_GOLD)

    ramp_right_bot = b1.copy()
    for x in range(16): ramp_right_bot.putpixel((x, 0), ramp_right_top.getpixel((x, 15)))
    for y in range(1, 16):
        for x in range(5):
            if y >= 14: ramp_right_bot.putpixel((x, y), R_BASE if x > 0 else R_CREVICE)
            elif x == 0: ramp_right_bot.putpixel((x, y), R_CREVICE if y < 14 else R_BASE)
            elif x == 1: ramp_right_bot.putpixel((x, y), R_DARK if y < 12 else R_CREVICE)

    for y in range(16): ramp_left_top.putpixel((0, y), t2.getpixel((15, y)))
    for y in range(16): ramp_left_bot.putpixel((0, y), b2.getpixel((15, y)))
    for y in range(16): ramp_right_top.putpixel((15, y), t1.getpixel((0, y)))
    for y in range(16): ramp_right_bot.putpixel((15, y), b1.getpixel((0, y)))


    # =============================================================
    # 6. NORTH OUTER CORNERS (cliff_outer_tl_top & cliff_outer_tr_top)
    # =============================================================
    outer_tl = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            if x <= 4 or y <= 4: outer_tl.putpixel((x, y), grass_base.getpixel((x, y)))
            elif x == 5 or y == 5: outer_tl.putpixel((x, y), R_CREVICE)
            elif x == 6 or y == 6: outer_tl.putpixel((x, y), R_GOLD if (x+y)%2 == 0 else R_HILITE)
            elif x == 7 or y == 7: outer_tl.putpixel((x, y), G_SHADOW)
            else: outer_tl.putpixel((x, y), grass_base.getpixel((x, y)))

    outer_tr = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            if x >= 11 or y <= 4: outer_tr.putpixel((x, y), grass_base.getpixel((x, y)))
            elif x == 10 or y == 5: outer_tr.putpixel((x, y), E_CREVICE)
            elif x == 9 or y == 6: outer_tr.putpixel((x, y), E_GOLD if (x+y)%2 == 0 else E_HILITE)
            elif x == 8 or y == 7: outer_tr.putpixel((x, y), G_SHADOW)
            else: outer_tr.putpixel((x, y), grass_base.getpixel((x, y)))


    # Save all tiles
    fixed_tiles = {
        "cliff_corner_sw_top": sw_top,
        "cliff_corner_sw_bot": sw_bot,
        "cliff_corner_se_top": se_top,
        "cliff_corner_se_bot": se_bot,
        "cliff_side_w_top":    side_w_top,
        "cliff_side_w":        side_w,
        "cliff_side_w_bot":    side_w_bot,
        "cliff_side_e_top":    side_e_top,
        "cliff_side_e":        side_e,
        "cliff_side_e_bot":    side_e_bot,
        "cliff_ramp_left_top": ramp_left_top,
        "cliff_ramp_left_bot": ramp_left_bot,
        "cliff_ramp_right_top": ramp_right_top,
        "cliff_ramp_right_bot": ramp_right_bot,
        "cliff_outer_tl_top":  outer_tl,
        "cliff_outer_tr_top":  outer_tr,
    }

    for name, img in fixed_tiles.items():
        img.save(os.path.join(cliffs_dir, f"{name}.png"))
        img.save(os.path.join(scratch_dir, f"{name}.png"))

    print(f"Successfully saved all {len(fixed_tiles)} thoroughly fixed corners & edges!")

    # -------------------------------------------------------------
    # BUILD COMPLETE PANORAMA SCENE (Full Hill Panorama)
    # -------------------------------------------------------------
    scene = Image.new("RGBA", (26 * 16, 16 * 16))
    for y in range(16):
        for x in range(26):
            if 12 <= x <= 13: scene.paste(mud_base, (x*16, y*16))
            else: scene.paste(grass_base, (x*16, y*16))

    def load_tile(name):
        return Image.open(os.path.join(cliffs_dir, f"{name}.png")).convert("RGBA")

    # West wall (col 3, rows 2..5)
    scene.paste(load_tile("cliff_side_w_top"), (3*16, 2*16))
    scene.paste(load_tile("cliff_side_w"),     (3*16, 3*16))
    scene.paste(load_tile("cliff_side_w"),     (3*16, 4*16))
    scene.paste(load_tile("cliff_side_w_bot"), (3*16, 5*16))

    # SW Corner (col 3, rows 6..7)
    scene.paste(load_tile("cliff_corner_sw_top"), (3*16, 6*16))
    scene.paste(load_tile("cliff_corner_sw_bot"), (3*16, 7*16))

    # South cliff face left (cols 4..10, rows 6..7)
    for x in range(4, 11):
        scene.paste(load_tile("cliff_face_top_01" if x % 2 == 0 else "cliff_face_top_02"), (x*16, 6*16))
        scene.paste(load_tile("cliff_face_bot_01" if x % 2 == 0 else "cliff_face_bot_02"), (x*16, 7*16))

    # Left canyon wall (col 11)
    scene.paste(load_tile("cliff_side_e_top"), (11*16, 2*16))
    scene.paste(load_tile("cliff_side_e"),     (11*16, 3*16))
    scene.paste(load_tile("cliff_side_e"),     (11*16, 4*16))
    scene.paste(load_tile("cliff_side_e_bot"), (11*16, 5*16))
    scene.paste(load_tile("cliff_ramp_left_top"), (11*16, 6*16))
    scene.paste(load_tile("cliff_ramp_left_bot"), (11*16, 7*16))

    # Mud steps (cols 12 & 13, rows 6 & 7)
    scene.paste(load_tile("cliff_mud_steps_01_top"), (12*16, 6*16))
    scene.paste(load_tile("cliff_mud_steps_01_bot"), (12*16, 7*16))
    scene.paste(load_tile("cliff_mud_steps_02_top"), (13*16, 6*16))
    scene.paste(load_tile("cliff_mud_steps_02_bot"), (13*16, 7*16))

    # Right canyon wall (col 14)
    scene.paste(load_tile("cliff_side_w_top"), (14*16, 2*16))
    scene.paste(load_tile("cliff_side_w"),     (14*16, 3*16))
    scene.paste(load_tile("cliff_side_w"),     (14*16, 4*16))
    scene.paste(load_tile("cliff_side_w_bot"), (14*16, 5*16))
    scene.paste(load_tile("cliff_ramp_right_top"), (14*16, 6*16))
    scene.paste(load_tile("cliff_ramp_right_bot"), (14*16, 7*16))

    # South cliff face right (cols 15..21, rows 6..7)
    for x in range(15, 22):
        scene.paste(load_tile("cliff_face_top_01" if x % 2 == 0 else "cliff_face_top_02"), (x*16, 6*16))
        scene.paste(load_tile("cliff_face_bot_01" if x % 2 == 0 else "cliff_face_bot_02"), (x*16, 7*16))

    # SE Corner (col 22, rows 6..7)
    scene.paste(load_tile("cliff_corner_se_top"), (22*16, 6*16))
    scene.paste(load_tile("cliff_corner_se_bot"), (22*16, 7*16))

    # East wall (col 22, rows 2..5)
    scene.paste(load_tile("cliff_side_e_top"), (22*16, 2*16))
    scene.paste(load_tile("cliff_side_e"),     (22*16, 3*16))
    scene.paste(load_tile("cliff_side_e"),     (22*16, 4*16))
    scene.paste(load_tile("cliff_side_e_bot"), (22*16, 5*16))

    scene_3x = scene.resize((scene.width * 3, scene.height * 3), Image.NEAREST)
    insp_path = os.path.join(scratch_dir, "thorough_corners_and_edges_fixed_3x.png")
    scene_3x.save(insp_path)
    print("Saved panorama inspection image to:", insp_path)

if __name__ == "__main__":
    main()
