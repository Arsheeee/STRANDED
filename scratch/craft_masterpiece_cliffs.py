import os
from PIL import Image

def main():
    brain_dir = r"C:\Users\PAVILION\.gemini\antigravity-ide\brain\84db0e2d-58d2-466d-be05-dbff8f133035"
    scratch_dir = os.path.join(brain_dir, "scratch")
    assets_dir = r"d:\Unity\Projects\STRANDED\Assets\Art\Terrain"
    cliff_dir = os.path.join(assets_dir, "Cliffs")

    ref = Image.open(os.path.join(scratch_dir, "stardew_native_512.png")).convert("RGBA")
    
    face_top_01 = Image.open(os.path.join(cliff_dir, "cliff_face_top_01.png")).convert("RGBA")
    face_bot_01 = Image.open(os.path.join(cliff_dir, "cliff_face_bot_01.png")).convert("RGBA")
    face_top_02 = Image.open(os.path.join(cliff_dir, "cliff_face_top_02.png")).convert("RGBA")
    face_bot_02 = Image.open(os.path.join(cliff_dir, "cliff_face_bot_02.png")).convert("RGBA")
    grass_base  = Image.open(os.path.join(assets_dir, "Grass", "grass_base_01.png")).convert("RGBA")
    mud_base    = Image.open(os.path.join(assets_dir, "Dirt", "mud_base_01.png")).convert("RGBA")

    # =========================================================================
    # STEP 1: CANYON SHOULDERS (EXTRACTED DIRECTLY FROM CONCERNEDAPE REF)
    # =========================================================================
    # Left Shoulder (col 14)
    # Stardew rows 4, 5, 6, 7
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
    # Stardew rows 4, 5, 6, 7
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

    # =========================================================================
    # STEP 2: VERTICAL FLANKS (COLUMNS 14 & 17, ROWS 2 & 3)
    # =========================================================================
    # West Flank (faces West / grass on left, rock mid, grass right)
    c17_r2 = ref.crop((17*16, 2*16, 18*16, 3*16))
    c17_r3 = ref.crop((17*16, 3*16, 18*16, 4*16))
    # Replace low-ground mud with grass meadow + shadow
    for im in [c17_r2, c17_r3]:
        for y in range(16):
            im.putpixel((0, y), grass_base.getpixel((0, y)))
            im.putpixel((1, y), grass_base.getpixel((1, y)))
            gp2 = grass_base.getpixel((2, y))
            gp3 = grass_base.getpixel((3, y))
            im.putpixel((2, y), (int(gp2[0]*0.6 + 18), int(gp2[1]*0.6 + 42), int(gp2[2]*0.6 + 8), 255))
            im.putpixel((3, y), (int(gp3[0]*0.4 + 22), int(gp3[1]*0.4 + 50), int(gp3[2]*0.4 + 8), 255))

    side_w = c17_r3.copy()
    # Seamless vertical looping: row 0 must equal row 15
    r15_w = [side_w.getpixel((x, 15)) for x in range(16)]
    for x in range(16):
        side_w.putpixel((x, 0), r15_w[x])
        # Smooth transition into row 1
        p0 = r15_w[x]
        p2 = side_w.getpixel((x, 2))
        side_w.putpixel((x, 1), tuple(int(p0[i]*0.6 + p2[i]*0.4) for i in range(4)))

    side_w_top = c17_r2.copy()
    # Connect bottom of side_w_top to top of side_w
    for x in range(16):
        side_w_top.putpixel((x, 15), side_w.getpixel((x, 0)))

    side_w_bot = c17_r3.copy()
    # Connect top of side_w_bot to bottom of side_w
    for x in range(16):
        side_w_bot.putpixel((x, 0), side_w.getpixel((x, 15)))

    # East Flank (faces East / grass on left, rock mid, grass on right)
    c14_r2 = ref.crop((14*16, 2*16, 15*16, 3*16))
    c14_r3 = ref.crop((14*16, 3*16, 15*16, 4*16))
    for im in [c14_r2, c14_r3]:
        for y in range(16):
            im.putpixel((15, y), grass_base.getpixel((15, y)))
            im.putpixel((14, y), grass_base.getpixel((14, y)))
            gp13 = grass_base.getpixel((13, y))
            gp12 = grass_base.getpixel((12, y))
            im.putpixel((13, y), (int(gp13[0]*0.6 + 18), int(gp13[1]*0.6 + 42), int(gp13[2]*0.6 + 8), 255))
            im.putpixel((12, y), (int(gp12[0]*0.4 + 22), int(gp12[1]*0.4 + 50), int(gp12[2]*0.4 + 8), 255))

    side_e = c14_r3.copy()
    r15_e = [side_e.getpixel((x, 15)) for x in range(16)]
    for x in range(16):
        side_e.putpixel((x, 0), r15_e[x])
        p0 = r15_e[x]
        p2 = side_e.getpixel((x, 2))
        side_e.putpixel((x, 1), tuple(int(p0[i]*0.6 + p2[i]*0.4) for i in range(4)))

    side_e_top = c14_r2.copy()
    for x in range(16):
        side_e_top.putpixel((x, 15), side_e.getpixel((x, 0)))

    side_e_bot = c14_r3.copy()
    for x in range(16):
        side_e_bot.putpixel((x, 0), side_e.getpixel((x, 15)))

    # Connect bottom of side_w_bot to top of ramp_right_top
    for x in range(16):
        side_w_bot.putpixel((x, 15), ramp_right_top.getpixel((x, 0)))

    # Connect bottom of side_e_bot to top of ramp_left_top
    for x in range(16):
        side_e_bot.putpixel((x, 15), ramp_left_top.getpixel((x, 0)))

    # =========================================================================
    # STEP 3: HANDCRAFTED AUTHENTIC OUTER CORNERS (SW & SE)
    # =========================================================================
    # SW Outer Corner:
    # Top tile: Connects on top to side_w_bot (row 15), on right to face_top_01 (col 0)
    # High ground grass in top-right quadrant (x=9..15, y=0..5)
    # Boulder wraps around from West crest to South crest!
    corner_sw_top = grass_base.copy()
    corner_sw_bot = Image.new("RGBA", (16, 16))

    # Palettes
    R_PEAK    = (243, 215, 33, 255)  # #f3d721
    R_HILITE  = (209, 175, 24, 255)  # #d1af18
    R_GOLD    = (198, 145, 18, 255)  # #c69112
    R_WARM    = (160, 120, 15, 255)  # #a0780f
    R_MID     = (143, 108, 14, 255)  # #8f6c0e
    R_SHADOW  = (122, 93, 12, 255)   # #7a5d0c
    R_DARK    = (103, 82, 10, 255)   # #67520a
    R_DEEP    = (89, 73, 9, 255)     # #594909
    R_CREVICE = (64, 42, 6, 255)     # #402a06
    R_BASE    = (45, 30, 4, 255)     # #2d1e04
    G_TIP     = (186, 179, 39, 255)  # #bab327
    G_GOLD    = (209, 175, 24, 255)  # #d1af18
    # Grass ground shadow for outer corners
    D_SHADOW  = (38, 92, 14, 255)    # #265c0e dark grass shadow
    D_DEEP    = (26, 68, 10, 255)    # #1a440a deep grass shadow

    # Sculpt corner_sw_top:
    # Corner boulder center is at (x=6, y=10)
    for y in range(16):
        for x in range(16):
            # Distance from high ground grass curve
            # Grass boundary runs along arc from (x=8, y=0) to (x=15, y=6)
            # In the grass quadrant (x >= 8 and y <= 6)
            is_grass = False
            if x >= 8 and y <= 5:
                # Elliptical grass zone
                dx = (x - 15) / 7.0
                dy = (y - 0) / 6.0
                if dx*dx + dy*dy <= 1.0:
                    is_grass = True
            
            if is_grass:
                # Keep grass base pixel
                pass
            else:
                # Rock boulder face
                # Distance from top-left sunlit apex (approx x=5, y=7)
                dx = (x - 5)
                dy = (y - 7)
                dist = (dx*dx*0.9 + dy*dy)**0.5
                
                # Grass fringe overhang right below grass:
                if (x >= 7 and y == 6) or (x == 7 and y <= 5):
                    corner_sw_top.putpixel((x, y), G_TIP if (x+y)%2 == 0 else G_GOLD)
                elif dist <= 2.2:
                    corner_sw_top.putpixel((x, y), R_PEAK if (x==5 and y==7) else R_HILITE)
                elif dist <= 4.2:
                    corner_sw_top.putpixel((x, y), R_GOLD if dy <= 1 else R_WARM)
                elif dist <= 6.5:
                    corner_sw_top.putpixel((x, y), R_WARM if dy <= 2 else R_MID)
                elif dist <= 9.0:
                    corner_sw_top.putpixel((x, y), R_MID if dy <= 3 else R_SHADOW)
                else:
                    corner_sw_top.putpixel((x, y), R_SHADOW if y < 14 else R_DARK)

    # Sculpt corner_sw_bot:
    # Lower boulder center is at (x=6, y=5)
    for y in range(16):
        for x in range(16):
            dx = (x - 6)
            dy = (y - 4)
            dist = (dx*dx*0.9 + dy*dy)**0.5
            if y >= 13:
                # Base ground contact shadow
                corner_sw_bot.putpixel((x, y), D_DEEP if dist <= 8 else D_SHADOW)
            elif y == 12:
                corner_sw_bot.putpixel((x, y), R_BASE if dist <= 7 else R_CREVICE)
            elif dist <= 3.0:
                corner_sw_bot.putpixel((x, y), R_WARM if dy <= 0 else R_MID)
            elif dist <= 5.5:
                corner_sw_bot.putpixel((x, y), R_MID if dy <= 1 else R_SHADOW)
            elif dist <= 8.0:
                corner_sw_bot.putpixel((x, y), R_SHADOW if dy <= 2 else R_DARK)
            else:
                corner_sw_bot.putpixel((x, y), R_DARK if y < 11 else R_CREVICE)

    # SE Outer Corner:
    corner_se_top = grass_base.copy()
    corner_se_bot = Image.new("RGBA", (16, 16))

    for y in range(16):
        for x in range(16):
            is_grass = False
            if x <= 7 and y <= 5:
                dx = (x - 0) / 7.0
                dy = (y - 0) / 6.0
                if dx*dx + dy*dy <= 1.0:
                    is_grass = True
            if is_grass:
                pass
            else:
                dx = (x - 10)
                dy = (y - 7)
                dist = (dx*dx*0.9 + dy*dy)**0.5
                if (x <= 8 and y == 6) or (x == 8 and y <= 5):
                    corner_se_top.putpixel((x, y), G_TIP if (x+y)%2 == 0 else G_GOLD)
                elif dist <= 2.2:
                    corner_se_top.putpixel((x, y), R_GOLD if (x<=10 and y<=7) else R_WARM)
                elif dist <= 4.2:
                    corner_se_top.putpixel((x, y), R_WARM if dy <= 1 else R_MID)
                elif dist <= 6.5:
                    corner_se_top.putpixel((x, y), R_MID if dy <= 2 else R_SHADOW)
                elif dist <= 9.0:
                    corner_se_top.putpixel((x, y), R_SHADOW if dy <= 3 else R_DARK)
                else:
                    corner_se_top.putpixel((x, y), R_DARK if y < 14 else R_DEEP)

    for y in range(16):
        for x in range(16):
            dx = (x - 9)
            dy = (y - 4)
            dist = (dx*dx*0.9 + dy*dy)**0.5
            if y >= 13:
                corner_se_bot.putpixel((x, y), D_DEEP if dist <= 8 else D_SHADOW)
            elif y == 12:
                corner_se_bot.putpixel((x, y), R_BASE if dist <= 7 else R_CREVICE)
            elif dist <= 3.0:
                corner_se_bot.putpixel((x, y), R_MID if dy <= 0 else R_SHADOW)
            elif dist <= 5.5:
                corner_se_bot.putpixel((x, y), R_SHADOW if dy <= 1 else R_DARK)
            elif dist <= 8.0:
                corner_se_bot.putpixel((x, y), R_DARK if dy <= 2 else R_DEEP)
            else:
                corner_se_bot.putpixel((x, y), R_DEEP if y < 11 else R_CREVICE)

    # =========================================================================
    # STEP 4: STRICT MATHEMATICAL ZERO-SEAM ENFORCEMENT
    # =========================================================================
    # A. TOP/BOTTOM HORIZONTAL EDGES FIRST:
    # 1. SW Corner top edge matches side_w_bot bottom row (y=15):
    for x in range(16):
        corner_sw_top.putpixel((x, 0), side_w_bot.getpixel((x, 15)))
        p0 = side_w_bot.getpixel((x, 15))
        p2 = corner_sw_top.getpixel((x, 2))
        corner_sw_top.putpixel((x, 1), tuple(int(p0[i]*0.6 + p2[i]*0.4) for i in range(4)))

    # 2. SE Corner top edge matches side_e_bot bottom row:
    for x in range(16):
        corner_se_top.putpixel((x, 0), side_e_bot.getpixel((x, 15)))
        p0 = side_e_bot.getpixel((x, 15))
        p2 = corner_se_top.getpixel((x, 2))
        corner_se_top.putpixel((x, 1), tuple(int(p0[i]*0.6 + p2[i]*0.4) for i in range(4)))

    # 3. Left Shoulder top matches side_e_bot bottom row:
    for x in range(16):
        ramp_left_top.putpixel((x, 0), side_e_bot.getpixel((x, 15)))
        p0 = side_e_bot.getpixel((x, 15))
        p2 = ramp_left_top.getpixel((x, 2))
        ramp_left_top.putpixel((x, 1), tuple(int(p0[i]*0.6 + p2[i]*0.4) for i in range(4)))

    # 4. Right Shoulder top matches side_w_bot bottom row:
    for x in range(16):
        ramp_right_top.putpixel((x, 0), side_w_bot.getpixel((x, 15)))
        p0 = side_w_bot.getpixel((x, 15))
        p2 = ramp_right_top.getpixel((x, 2))
        ramp_right_top.putpixel((x, 1), tuple(int(p0[i]*0.6 + p2[i]*0.4) for i in range(4)))

    # B. VERTICAL SEAMS (COLUMNS) SECOND - CANNOT BE OVERWRITTEN:
    # SW Corner -> face_top_01 / face_bot_01 (col 15 of SW matches col 0 of face 01)
    for y in range(16):
        corner_sw_top.putpixel((15, y), face_top_01.getpixel((0, y)))
        corner_sw_bot.putpixel((15, y), face_bot_01.getpixel((0, y)))
        if y > 0:
            p15_t = face_top_01.getpixel((0, y))
            p13_t = corner_sw_top.getpixel((13, y))
            corner_sw_top.putpixel((14, y), tuple(int(p15_t[i]*0.6 + p13_t[i]*0.4) for i in range(4)))
            p15_b = face_bot_01.getpixel((0, y))
            p13_b = corner_sw_bot.getpixel((13, y))
            corner_sw_bot.putpixel((14, y), tuple(int(p15_b[i]*0.6 + p13_b[i]*0.4) for i in range(4)))

    # SE Corner -> face_top_02 / face_bot_02 (col 0 of SE matches col 15 of face 02)
    for y in range(16):
        corner_se_top.putpixel((0, y), face_top_02.getpixel((15, y)))
        corner_se_bot.putpixel((0, y), face_bot_02.getpixel((15, y)))
        if y > 0:
            p0_t = face_top_02.getpixel((15, y))
            p2_t = corner_se_top.getpixel((2, y))
            corner_se_top.putpixel((1, y), tuple(int(p0_t[i]*0.6 + p2_t[i]*0.4) for i in range(4)))
            p0_b = face_bot_02.getpixel((15, y))
            p2_b = corner_se_bot.getpixel((2, y))
            corner_se_bot.putpixel((1, y), tuple(int(p0_b[i]*0.6 + p2_b[i]*0.4) for i in range(4)))

    # Left Shoulder -> face_top_01 / face_bot_01 (col 0 of ramp_left matches col 15 of face 01)
    for y in range(16):
        ramp_left_top.putpixel((0, y), face_top_01.getpixel((15, y)))
        ramp_left_bot.putpixel((0, y), face_bot_01.getpixel((15, y)))
        if y > 0:
            p0_t = face_top_01.getpixel((15, y))
            p2_t = ramp_left_top.getpixel((2, y))
            ramp_left_top.putpixel((1, y), tuple(int(p0_t[i]*0.6 + p2_t[i]*0.4) for i in range(4)))
            p0_b = face_bot_01.getpixel((15, y))
            p2_b = ramp_left_bot.getpixel((2, y))
            ramp_left_bot.putpixel((1, y), tuple(int(p0_b[i]*0.6 + p2_b[i]*0.4) for i in range(4)))

    # Right Shoulder -> face_top_02 / face_bot_02 (col 15 of ramp_right matches col 0 of face 02)
    for y in range(16):
        ramp_right_top.putpixel((15, y), face_top_02.getpixel((0, y)))
        ramp_right_bot.putpixel((15, y), face_bot_02.getpixel((0, y)))
        if y > 0:
            p15_t = face_top_02.getpixel((0, y))
            p13_t = ramp_right_top.getpixel((13, y))
            ramp_right_top.putpixel((14, y), tuple(int(p15_t[i]*0.6 + p13_t[i]*0.4) for i in range(4)))
            p15_b = face_bot_02.getpixel((0, y))
            p13_b = ramp_right_bot.getpixel((13, y))
            ramp_right_bot.putpixel((14, y), tuple(int(p15_b[i]*0.6 + p13_b[i]*0.4) for i in range(4)))

    # C. HARMONIZE JUNCTION PIXELS ON BOTTOM OF SIDE FLANKS:
    side_w_bot.putpixel((15, 15), corner_sw_top.getpixel((15, 0)))
    side_e_bot.putpixel((0, 15), ramp_left_top.getpixel((0, 0)))

    # D. VERTICAL TOP/BOT SEAMS WITHIN TILES:
    for x in range(16):
        corner_sw_bot.putpixel((x, 0), corner_sw_top.getpixel((x, 15)))
        corner_se_bot.putpixel((x, 0), corner_se_top.getpixel((x, 15)))
        ramp_left_bot.putpixel((x, 0), ramp_left_top.getpixel((x, 15)))
        ramp_right_bot.putpixel((x, 0), ramp_right_top.getpixel((x, 15)))

    # Top outer corners (plateau crown caps)
    outer_tl = grass_base.copy()
    outer_tr = grass_base.copy()
    for y in range(16):
        for x in range(16):
            if x <= 7 and y <= 7:
                outer_tl.putpixel((x, y), side_w_top.getpixel((x, y)))
            if x >= 8 and y <= 7:
                outer_tr.putpixel((x, y), side_e_top.getpixel((x, y)))

    # Save all tiles to scratch
    saved = {
        "cliff_side_w_top.png": side_w_top,
        "cliff_side_w.png": side_w,
        "cliff_side_w_bot.png": side_w_bot,
        "cliff_side_e_top.png": side_e_top,
        "cliff_side_e.png": side_e,
        "cliff_side_e_bot.png": side_e_bot,
        "cliff_ramp_left_top.png": ramp_left_top,
        "cliff_ramp_left_bot.png": ramp_left_bot,
        "cliff_ramp_right_top.png": ramp_right_top,
        "cliff_ramp_right_bot.png": ramp_right_bot,
        "cliff_corner_sw_top.png": corner_sw_top,
        "cliff_corner_sw_bot.png": corner_sw_bot,
        "cliff_corner_se_top.png": corner_se_top,
        "cliff_corner_se_bot.png": corner_se_bot,
        "cliff_outer_tl_top.png": outer_tl,
        "cliff_outer_tr_top.png": outer_tr,
    }

    for name, img in saved.items():
        img.save(os.path.join(scratch_dir, "master_" + name))
        # Also copy to Assets/Art/Terrain/Cliffs/
        img.save(os.path.join(cliff_dir, name))

    print("Masterpiece cliff tiles created and deployed to Assets/Art/Terrain/Cliffs/!")

    # Verify zero-seam on every connection
    seam_checks = [
        ("side_w vertical loop", side_w, (slice(None), 15), side_w, (slice(None), 0)),
        ("side_w_top -> side_w", side_w_top, (slice(None), 15), side_w, (slice(None), 0)),
        ("side_w -> side_w_bot", side_w, (slice(None), 15), side_w_bot, (slice(None), 0)),
        ("side_w_bot -> ramp_right_top", side_w_bot, (slice(None), 15), ramp_right_top, (slice(None), 0)),
        ("side_w_bot -> corner_sw_top", side_w_bot, (slice(None), 15), corner_sw_top, (slice(None), 0)),
        
        ("side_e vertical loop", side_e, (slice(None), 15), side_e, (slice(None), 0)),
        ("side_e_top -> side_e", side_e_top, (slice(None), 15), side_e, (slice(None), 0)),
        ("side_e -> side_e_bot", side_e, (slice(None), 15), side_e_bot, (slice(None), 0)),
        ("side_e_bot -> ramp_left_top", side_e_bot, (slice(None), 15), ramp_left_top, (slice(None), 0)),
        ("side_e_bot -> corner_se_top", side_e_bot, (slice(None), 15), corner_se_top, (slice(None), 0)),

        ("ramp_left_top -> ramp_left_bot", ramp_left_top, (slice(None), 15), ramp_left_bot, (slice(None), 0)),
        ("ramp_right_top -> ramp_right_bot", ramp_right_top, (slice(None), 15), ramp_right_bot, (slice(None), 0)),
        ("corner_sw_top -> corner_sw_bot", corner_sw_top, (slice(None), 15), corner_sw_bot, (slice(None), 0)),
        ("corner_se_top -> corner_se_bot", corner_se_top, (slice(None), 15), corner_se_bot, (slice(None), 0)),

        ("corner_sw_top -> face_top_01", corner_sw_top, (15, slice(None)), face_top_01, (0, slice(None))),
        ("corner_sw_bot -> face_bot_01", corner_sw_bot, (15, slice(None)), face_bot_01, (0, slice(None))),

        ("face_top_01 -> ramp_left_top", face_top_01, (15, slice(None)), ramp_left_top, (0, slice(None))),
        ("face_bot_01 -> ramp_left_bot", face_bot_01, (15, slice(None)), ramp_left_bot, (0, slice(None))),

        ("ramp_right_top -> face_top_02", ramp_right_top, (15, slice(None)), face_top_02, (0, slice(None))),
        ("ramp_right_bot -> face_bot_02", ramp_right_bot, (15, slice(None)), face_bot_02, (0, slice(None))),

        ("face_top_02 -> corner_se_top", face_top_02, (15, slice(None)), corner_se_top, (0, slice(None))),
        ("face_bot_02 -> corner_se_bot", face_bot_02, (15, slice(None)), corner_se_bot, (0, slice(None))),
    ]

    print("\n--- ZERO-SEAM VERIFICATION AUDIT ---")
    all_ok = True
    for name, imgA, (xA, yA), imgB, (xB, yB) in seam_checks:
        pixA = [imgA.getpixel((x, yA if isinstance(yA, int) else y)) for x in (range(16) if isinstance(xA, slice) else [xA]) for y in (range(16) if isinstance(yA, slice) else [yA])]
        pixB = [imgB.getpixel((x, yB if isinstance(yB, int) else y)) for x in (range(16) if isinstance(xB, slice) else [xB]) for y in (range(16) if isinstance(yB, slice) else [yB])]
        mismatches = sum(a != b for a, b in zip(pixA, pixB))
        status = "PERFECT (0/16)" if mismatches == 0 else f"FAILED ({mismatches}/16)"
        print(f"{name:35}: {status}")
        if mismatches > 0:
            all_ok = False
            
    if all_ok:
        print("\nALL 22 SEAM BOUNDARIES ACHIEVED 100% MATHEMATICAL ZERO-SEAM PERFECTION!")
    else:
        print("\nWARNING: Some seams have mismatches!")

if __name__ == "__main__":
    main()
