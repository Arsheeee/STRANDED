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

    # Load front cliff face tiles
    t1 = Image.open(os.path.join(cliffs_dir, "cliff_face_top_01.png")).convert("RGBA")
    t2 = Image.open(os.path.join(cliffs_dir, "cliff_face_top_02.png")).convert("RGBA")
    b1 = Image.open(os.path.join(cliffs_dir, "cliff_face_bot_01.png")).convert("RGBA")
    b2 = Image.open(os.path.join(cliffs_dir, "cliff_face_bot_02.png")).convert("RGBA")

    # -------------------------------------------------------------
    # COLOR PALETTES
    # -------------------------------------------------------------
    G_LIGHT   = (112, 199, 37, 255)   # #70c725
    G_MID     = (68, 163, 24, 255)    # #44a318
    G_DARK    = (58, 147, 17, 255)    # #3a9311
    G_DEEP    = (50, 133, 48, 255)    # #328530
    G_SHADOW  = (35, 95, 10, 255)     # #235f0a

    # Sunlit Rock (West-facing wall)
    R_HILITE  = (209, 175, 24, 255)   # #d1af18
    R_GOLD    = (198, 145, 18, 255)   # #c69112
    R_MID     = (160, 120, 15, 255)   # #a0780f
    R_WARM    = (143, 108, 14, 255)   # #8f6c0e
    R_SHADOW  = (122, 93, 12, 255)    # #7a5d0c
    R_DARK    = (103, 82, 10, 255)    # #67520a
    R_CREVICE = (64, 42, 6, 255)      # #402a06
    R_BASE    = (45, 30, 4, 255)      # #2d1e04

    # Shaded Rock (East-facing wall)
    E_HILITE  = (182, 145, 20, 255)
    E_GOLD    = (165, 122, 16, 255)
    E_MID     = (136, 100, 13, 255)
    E_WARM    = (120, 90, 12, 255)
    E_SHADOW  = (102, 76, 10, 255)
    E_DARK    = (78, 58, 8, 255)
    E_CREVICE = (52, 34, 5, 255)

    # Mud palette
    M_LIGHT   = (187, 126, 29, 255)
    M_MID     = (181, 111, 40, 255)
    M_BASE    = (179, 119, 41, 255)
    M_WARM    = (175, 109, 40, 255)
    M_DARK    = (145, 88, 28, 255)
    M_PEBBLE  = (210, 160, 55, 255)

    # Timber Log Lip & Riser
    LIP_HI    = (245, 195, 66, 255)
    LIP_MID   = (218, 160, 45, 255)
    LIP_GRAIN = (140, 83, 27, 255)
    RISER_DIRT= (95, 55, 18, 255)
    RISER_SHAD= (56, 30, 5, 255)
    RISER_DEEP= (35, 18, 3, 255)

    # -------------------------------------------------------------
    # 1. ORGANIC WEST-FACING ROCK FLANK (cliff_side_w_top, _w, _w_bot)
    # -------------------------------------------------------------
    # Rock wall on left x=0..7 (8px wide)
    # Grass overhang x=8..10
    # Meadow grass x=11..15
    def make_organic_west_flank_mid():
        im = grass_base.copy()
        # Define organic boulder shapes across 16 vertical pixels:
        # Boulder A: y=0..8, Boulder B: y=8..15 (with curved boundary between them)
        for y in range(16):
            # Grass overhang at x=8..10:
            im.putpixel((10, y), G_MID if (y*3)%4 == 0 else G_DARK)
            im.putpixel((9, y), G_LIGHT if (y*5)%3 == 0 else G_MID)
            im.putpixel((8, y), G_SHADOW)

            # Rock face at x=0..7:
            for x in range(8):
                if y in [0, 8]:
                    # Crevice line between boulders (curved)
                    c = R_CREVICE if x < 6 else R_BASE
                elif y < 8:
                    # Boulder A (crest around x=3, y=3)
                    dist = abs(x - 3) * 1.1 + abs(y - 3)
                    if x == 7: c = R_DARK if y in [2, 3, 4] else R_CREVICE
                    elif x == 6: c = R_SHADOW if y in [2, 3, 4] else R_DARK
                    elif dist <= 1.2: c = R_HILITE if y in [2, 3] else R_GOLD
                    elif dist <= 2.5: c = R_GOLD if y <= 3 else R_MID
                    elif dist <= 4.0: c = R_MID if y <= 4 else R_WARM
                    else: c = R_SHADOW if y >= 5 else R_WARM
                else:
                    # Boulder B (crest around x=2, y=11)
                    dist = abs(x - 2) * 1.1 + abs(y - 11)
                    if x == 7: c = R_DARK if y in [10, 11, 12] else R_CREVICE
                    elif x == 6: c = R_SHADOW if y in [10, 11, 12] else R_DARK
                    elif dist <= 1.2: c = R_HILITE if y in [10, 11] else R_GOLD
                    elif dist <= 2.5: c = R_GOLD if y <= 11 else R_MID
                    elif dist <= 4.0: c = R_MID if y <= 12 else R_WARM
                    else: c = R_SHADOW if y >= 13 else R_WARM
                im.putpixel((x, y), c)
        return im

    def make_organic_west_flank_top(mid_tile):
        im = mid_tile.copy()
        # Round the top of the cliff naturally into plateau meadow:
        for y in range(4):
            for x in range(16):
                if y == 0:
                    im.putpixel((x, y), grass_base.getpixel((x, y)))
                elif y == 1:
                    if x < 4: im.putpixel((x, y), grass_base.getpixel((x, y)))
                    elif x == 4: im.putpixel((x, y), G_SHADOW)
                    elif x < 7: im.putpixel((x, y), R_MID if x == 5 else R_SHADOW)
                elif y == 2:
                    if x < 2: im.putpixel((x, y), grass_base.getpixel((x, y)))
                    elif x == 2: im.putpixel((x, y), G_SHADOW)
                    elif x < 7: im.putpixel((x, y), R_GOLD if x in [3, 4] else R_MID)
                elif y == 3:
                    if x == 0: im.putpixel((x, y), grass_base.getpixel((x, y)))
                    elif x == 1: im.putpixel((x, y), G_SHADOW)
        return im

    def make_organic_west_flank_bot(mid_tile):
        im = mid_tile.copy()
        for y in range(13, 16):
            for x in range(8):
                if y == 15: im.putpixel((x, y), R_BASE if x < 6 else R_CREVICE)
                elif y == 14: im.putpixel((x, y), R_CREVICE if x < 5 else R_BASE)
        return im

    cliff_side_w     = make_organic_west_flank_mid()
    cliff_side_w_top = make_organic_west_flank_top(cliff_side_w)
    cliff_side_w_bot = make_organic_west_flank_bot(cliff_side_w)

    # -------------------------------------------------------------
    # 2. ORGANIC EAST-FACING ROCK FLANK (cliff_side_e_top, _e, _e_bot)
    # -------------------------------------------------------------
    # Meadow grass x=0..4 (100% clean, matching grass_base_01)
    # Grass overhang x=5..7
    # Rock wall on right x=8..15 (8px wide)
    def make_organic_east_flank_mid():
        im = grass_base.copy()
        for y in range(16):
            # Grass overhang at x=5..7:
            im.putpixel((5, y), G_MID if (y*3)%4 == 0 else G_DARK)
            im.putpixel((6, y), G_LIGHT if (y*5)%3 == 0 else G_MID)
            im.putpixel((7, y), G_SHADOW)

            # Rock face at x=8..15:
            for x in range(8, 16):
                rx = x - 8
                if y in [0, 8]:
                    c = E_CREVICE if rx > 1 else E_BASE if 'E_BASE' in globals() else E_DARK
                elif y < 8:
                    dist = abs(rx - 4) * 1.1 + abs(y - 3)
                    if rx == 0: c = E_DARK if y in [2, 3, 4] else E_CREVICE
                    elif rx == 1: c = E_SHADOW if y in [2, 3, 4] else E_DARK
                    elif dist <= 1.2: c = E_HILITE if y in [2, 3] else E_GOLD
                    elif dist <= 2.5: c = E_GOLD if y <= 3 else E_MID
                    elif dist <= 4.0: c = E_MID if y <= 4 else E_WARM
                    else: c = E_SHADOW if y >= 5 else E_WARM
                else:
                    dist = abs(rx - 5) * 1.1 + abs(y - 11)
                    if rx == 0: c = E_DARK if y in [10, 11, 12] else E_CREVICE
                    elif rx == 1: c = E_SHADOW if y in [10, 11, 12] else E_DARK
                    elif dist <= 1.2: c = E_HILITE if y in [10, 11] else E_GOLD
                    elif dist <= 2.5: c = E_GOLD if y <= 11 else E_MID
                    elif dist <= 4.0: c = E_MID if y <= 12 else E_WARM
                    else: c = E_SHADOW if y >= 13 else E_WARM
                im.putpixel((x, y), c)
        return im

    def make_organic_east_flank_top(mid_tile):
        im = mid_tile.copy()
        for y in range(4):
            for x in range(16):
                if y == 0:
                    im.putpixel((x, y), grass_base.getpixel((x, y)))
                elif y == 1:
                    if x > 11: im.putpixel((x, y), grass_base.getpixel((x, y)))
                    elif x == 11: im.putpixel((x, y), G_SHADOW)
                    elif x >= 8: im.putpixel((x, y), E_MID if x == 10 else E_SHADOW)
                elif y == 2:
                    if x > 13: im.putpixel((x, y), grass_base.getpixel((x, y)))
                    elif x == 13: im.putpixel((x, y), G_SHADOW)
                    elif x >= 8: im.putpixel((x, y), E_GOLD if x in [10, 11] else E_MID)
                elif y == 3:
                    if x == 15: im.putpixel((x, y), grass_base.getpixel((x, y)))
                    elif x == 14: im.putpixel((x, y), G_SHADOW)
        return im

    def make_organic_east_flank_bot(mid_tile):
        im = mid_tile.copy()
        for y in range(13, 16):
            for x in range(8, 16):
                if y == 15: im.putpixel((x, y), E_CREVICE if x > 10 else E_DARK)
                elif y == 14: im.putpixel((x, y), E_DARK if x > 10 else E_SHADOW)
        return im

    cliff_side_e     = make_organic_east_flank_mid()
    cliff_side_e_top = make_organic_east_flank_top(cliff_side_e)
    cliff_side_e_bot = make_organic_east_flank_bot(cliff_side_e)

    # -------------------------------------------------------------
    # 3. CANYON SHOULDERS
    # -------------------------------------------------------------
    ramp_left_top = t2.copy()
    for x in range(16): ramp_left_top.putpixel((x, 0), cliff_side_e_bot.getpixel((x, 15)))
    for y in range(1, 16):
        for x in range(11, 16):
            if x == 15:
                ramp_left_top.putpixel((x, y), E_DARK if y in [4, 5, 6, 12, 13] else E_CREVICE)
            elif x == 14:
                ramp_left_top.putpixel((x, y), E_SHADOW if y in [3, 4, 11, 12] else E_DARK)
            elif x in [12, 13]:
                ramp_left_top.putpixel((x, y), E_MID if y in [2, 3, 10, 11] else E_WARM)

    ramp_left_bot = b2.copy()
    for x in range(16): ramp_left_bot.putpixel((x, 0), ramp_left_top.getpixel((x, 15)))
    for y in range(1, 16):
        for x in range(11, 16):
            if y >= 14: ramp_left_bot.putpixel((x, y), R_BASE if x < 15 else R_CREVICE)
            elif x == 15: ramp_left_bot.putpixel((x, y), E_CREVICE if y < 14 else R_BASE)
            elif x == 14: ramp_left_bot.putpixel((x, y), E_DARK if y < 12 else R_CREVICE)

    ramp_right_top = t1.copy()
    for x in range(16): ramp_right_top.putpixel((x, 0), cliff_side_w_bot.getpixel((x, 15)))
    for y in range(1, 16):
        for x in range(5):
            if x == 0:
                ramp_right_top.putpixel((x, y), R_CREVICE if y in [4, 5, 6, 12, 13] else R_DARK)
            elif x == 1:
                ramp_right_top.putpixel((x, y), R_DARK if y in [3, 4, 11, 12] else R_SHADOW)
            elif x in [2, 3]:
                ramp_right_top.putpixel((x, y), R_MID if y in [2, 3, 10, 11] else R_GOLD)

    ramp_right_bot = b1.copy()
    for x in range(16): ramp_right_bot.putpixel((x, 0), ramp_right_top.getpixel((x, 15)))
    for y in range(1, 16):
        for x in range(5):
            if y >= 14: ramp_right_bot.putpixel((x, y), R_BASE if x > 0 else R_CREVICE)
            elif x == 0: ramp_right_bot.putpixel((x, y), R_CREVICE if y < 14 else R_BASE)
            elif x == 1: ramp_right_bot.putpixel((x, y), R_DARK if y < 12 else R_CREVICE)

    # -------------------------------------------------------------
    # 4. POLISHED CARVED MUD STEPS (WITH SOFT SHADOW GRADIENT)
    # -------------------------------------------------------------
    # Shade factor function:
    # is_shadowed: if True, applies soft gradient from 1.0 (at x=0, center of stairs)
    # to 0.78 (at x=15, right against eastern rock wall). ZERO vertical seam at center!
    def get_shade(x, is_shadowed):
        if not is_shadowed: return 1.0
        if x <= 4: return 1.0
        elif x <= 10: return 1.0 - (x - 4) * 0.022 # 0.978 .. 0.868
        else: return 0.868 - (x - 10) * 0.018      # 0.850 .. 0.778

    def draw_polished_step(im, y_start, y_end, is_top_step=False, is_bot_step=False, is_shadowed=False):
        tread_end = y_end - 3
        lip_y     = y_end - 2
        riser_y   = y_end - 1
        shad_y    = y_end

        # 1. Textured mud tread:
        for y in range(y_start, tread_end + 1):
            for x in range(16):
                bm = mud_base.getpixel((x, y % 16))
                r, g, b = bm[0], bm[1], bm[2]

                if (x * 7 + y * 13) % 19 == 0:
                    r, g, b = M_PEBBLE[0], M_PEBBLE[1], M_PEBBLE[2]
                elif (x + y) % 3 == 0:
                    r, g, b = M_LIGHT[0], M_LIGHT[1], M_LIGHT[2]
                elif (x * 3 + y * 5) % 7 == 0:
                    r, g, b = M_WARM[0], M_WARM[1], M_WARM[2]

                s = get_shade(x, is_shadowed)
                im.putpixel((x, y), (int(r * s), int(g * s), int(b * s), 255))

        # 2. Hand-hewn timber log lip with organic contour:
        for x in range(16):
            curr_lip_y = lip_y
            # Slight natural earthen bank curve at outer sides
            if not is_shadowed and x == 0 and not is_top_step: curr_lip_y = lip_y - 1
            if is_shadowed and x == 15 and not is_top_step: curr_lip_y = lip_y - 1

            s = get_shade(x, is_shadowed)
            # Log top highlight
            im.putpixel((x, curr_lip_y), (int(LIP_HI[0] * s), int(LIP_HI[1] * s), int(LIP_HI[2] * s), 255))
            # Log core wood
            if curr_lip_y + 1 <= 15:
                im.putpixel((x, curr_lip_y + 1), (int(LIP_MID[0] * s), int(LIP_MID[1] * s), int(LIP_MID[2] * s), 255))

        # 3. Riser Face & Undershadow:
        for x in range(16):
            s = get_shade(x, is_shadowed)
            if riser_y <= 15:
                im.putpixel((x, riser_y), (int(RISER_DIRT[0] * s), int(RISER_DIRT[1] * s), int(RISER_DIRT[2] * s), 255))
            if shad_y <= 15:
                im.putpixel((x, shad_y), (int(RISER_SHAD[0] * s), int(RISER_SHAD[1] * s), int(RISER_SHAD[2] * s), 255))

    def make_polished_steps_top(is_shadowed=False):
        im = Image.new("RGBA", (16, 16))
        draw_polished_step(im, 0, 6, is_top_step=True, is_bot_step=False, is_shadowed=is_shadowed)
        draw_polished_step(im, 7, 15, is_top_step=False, is_bot_step=False, is_shadowed=is_shadowed)
        return im

    def make_polished_steps_bot(is_shadowed=False):
        im = Image.new("RGBA", (16, 16))
        draw_polished_step(im, 0, 6, is_top_step=False, is_bot_step=False, is_shadowed=is_shadowed)
        draw_polished_step(im, 7, 15, is_top_step=False, is_bot_step=True, is_shadowed=is_shadowed)
        for x in range(16):
            s = get_shade(x, is_shadowed)
            im.putpixel((x, 15), (int(RISER_DEEP[0] * s), int(RISER_DEEP[1] * s), int(RISER_DEEP[2] * s), 255))
        return im

    mud_steps_01_top = make_polished_steps_top(is_shadowed=False)
    mud_steps_01_bot = make_polished_steps_bot(is_shadowed=False)
    mud_steps_02_top = make_polished_steps_top(is_shadowed=True)
    mud_steps_02_bot = make_polished_steps_bot(is_shadowed=True)
    mud_steps_top    = make_polished_steps_top(is_shadowed=False)
    mud_steps_bot    = make_polished_steps_bot(is_shadowed=False)

    # -------------------------------------------------------------
    # 5. ENFORCE 100% MATHEMATICAL ZERO-SEAM MATCHING
    # -------------------------------------------------------------
    # Flank vertical stacking:
    for x in range(16): cliff_side_w.putpixel((x, 0), cliff_side_w_top.getpixel((x, 15)))
    for x in range(16): cliff_side_w_bot.putpixel((x, 0), cliff_side_w.getpixel((x, 15)))
    for x in range(16): ramp_right_top.putpixel((x, 0), cliff_side_w_bot.getpixel((x, 15)))
    for x in range(16): ramp_right_bot.putpixel((x, 0), ramp_right_top.getpixel((x, 15)))

    for x in range(16): cliff_side_e.putpixel((x, 0), cliff_side_e_top.getpixel((x, 15)))
    for x in range(16): cliff_side_e_bot.putpixel((x, 0), cliff_side_e.getpixel((x, 15)))
    for x in range(16): ramp_left_top.putpixel((x, 0), cliff_side_e_bot.getpixel((x, 15)))
    for x in range(16): ramp_left_bot.putpixel((x, 0), ramp_left_top.getpixel((x, 15)))

    # Shoulders horizontal connection:
    for y in range(16): ramp_left_top.putpixel((0, y), t2.getpixel((15, y)))
    for y in range(16): ramp_left_bot.putpixel((0, y), b2.getpixel((15, y)))
    for y in range(16): ramp_right_top.putpixel((15, y), t1.getpixel((0, y)))
    for y in range(16): ramp_right_bot.putpixel((15, y), b1.getpixel((0, y)))

    # Mud steps vertical stacking:
    for x in range(16): mud_steps_01_bot.putpixel((x, 0), mud_steps_01_top.getpixel((x, 15)))
    for x in range(16): mud_steps_02_bot.putpixel((x, 0), mud_steps_02_top.getpixel((x, 15)))
    for x in range(16): mud_steps_bot.putpixel((x, 0), mud_steps_top.getpixel((x, 15)))

    # Mud steps center horizontal seam (x=15 of 01 <-> x=0 of 02):
    # Because get_shade(0, True) is 1.0, they already match lip height and tread color!
    # Let's verify and enforce exact pixel match on step lip lines:
    for y in range(16):
        p_left_edge = mud_steps_01_top.getpixel((15, y))
        p_right_edge = mud_steps_02_top.getpixel((0, y))
        # Ensure lip rows (5, 6, 13, 14) are identical across the joint:
        if y in [5, 6, 13, 14]:
            mud_steps_02_top.putpixel((0, y), p_left_edge)
        p_bot_left = mud_steps_01_bot.getpixel((15, y))
        if y in [5, 6, 13, 14]:
            mud_steps_02_bot.putpixel((0, y), p_bot_left)

    tiles_to_save = {
        "cliff_side_w_top": cliff_side_w_top,
        "cliff_side_w":     cliff_side_w,
        "cliff_side_w_bot": cliff_side_w_bot,
        "cliff_side_e_top": cliff_side_e_top,
        "cliff_side_e":     cliff_side_e,
        "cliff_side_e_bot": cliff_side_e_bot,
        "cliff_ramp_left_top": ramp_left_top,
        "cliff_ramp_left_bot": ramp_left_bot,
        "cliff_ramp_right_top": ramp_right_top,
        "cliff_ramp_right_bot": ramp_right_bot,
        "cliff_mud_steps_01_top": mud_steps_01_top,
        "cliff_mud_steps_01_bot": mud_steps_01_bot,
        "cliff_mud_steps_02_top": mud_steps_02_top,
        "cliff_mud_steps_02_bot": mud_steps_02_bot,
        "cliff_mud_steps_top": mud_steps_top,
        "cliff_mud_steps_bot": mud_steps_bot,
    }

    for name, img in tiles_to_save.items():
        img.save(os.path.join(cliffs_dir, f"{name}.png"))
        img.save(os.path.join(scratch_dir, f"{name}.png"))

    print(f"Successfully refined and saved all {len(tiles_to_save)} master tiles!")

    # -------------------------------------------------------------
    # 6. RENDER MASTER CANYON DIAGNOSTIC SCENE
    # -------------------------------------------------------------
    canyon = Image.new('RGBA', (4 * 16, 6 * 16))
    canyon.paste(cliff_side_e_top, (0, 0))
    canyon.paste(cliff_side_e,     (0, 16))
    canyon.paste(cliff_side_e,     (0, 32))
    canyon.paste(cliff_side_e_bot, (0, 48))
    canyon.paste(ramp_left_top,    (0, 64))
    canyon.paste(ramp_left_bot,    (0, 80))

    canyon.paste(mud_base, (16, 0))
    canyon.paste(mud_base, (32, 0))
    canyon.paste(mud_base, (16, 16))
    canyon.paste(mud_base, (32, 16))
    canyon.paste(mud_base, (16, 32))
    canyon.paste(mud_base, (32, 32))
    canyon.paste(mud_base, (16, 48))
    canyon.paste(mud_base, (32, 48))

    canyon.paste(mud_steps_01_top, (16, 64))
    canyon.paste(mud_steps_01_bot, (16, 80))
    canyon.paste(mud_steps_02_top, (32, 64))
    canyon.paste(mud_steps_02_bot, (32, 80))

    canyon.paste(cliff_side_w_top, (48, 0))
    canyon.paste(cliff_side_w,     (48, 16))
    canyon.paste(cliff_side_w,     (48, 32))
    canyon.paste(cliff_side_w_bot, (48, 48))
    canyon.paste(ramp_right_top,   (48, 64))
    canyon.paste(ramp_right_bot,   (48, 80))

    canyon_4x = canyon.resize((canyon.width * 4, canyon.height * 4), Image.NEAREST)
    diag_path = os.path.join(scratch_dir, "canyon_master_diagnostic_4x.png")
    canyon_4x.save(diag_path)
    print("Saved refined canyon master diagnostic 4x to:", diag_path)

if __name__ == "__main__":
    main()
