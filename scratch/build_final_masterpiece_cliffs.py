import os
import base64
from PIL import Image

def generate_masterpiece_cliff_tiles():
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

    # Harmonize face_top junctions at row 0 (all grass)
    face_top_01.putpixel((0, 0), (67, 161, 25, 255))
    face_top_01.putpixel((15, 0), (67, 161, 25, 255))
    face_top_02.putpixel((0, 0), (67, 161, 25, 255))
    face_top_02.putpixel((15, 0), (67, 161, 25, 255))
    face_top_01.save(os.path.join(cliff_dir, "cliff_face_top_01.png"))
    face_top_02.save(os.path.join(cliff_dir, "cliff_face_top_02.png"))

    # =========================================================================
    # 1. CANYON SHOULDERS (CONCERNEDAPE NATIVE)
    # =========================================================================
    # Left Shoulder (col 14)
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

    # Clean top corners of shoulders to pure grass:
    ramp_left_top.putpixel((0, 0), (67, 161, 25, 255))
    ramp_right_top.putpixel((15, 0), (67, 161, 25, 255))

    # =========================================================================
    # 2. VERTICAL SIDE FLANKS (COLUMNS 17 & 14, ROWS 2 & 3)
    # =========================================================================
    # West Flank (faces West / grass on left, rock mid, grass on right)
    c17_r2 = ref.crop((17*16, 2*16, 18*16, 3*16))
    c17_r3 = ref.crop((17*16, 3*16, 18*16, 4*16))

    for im in [c17_r2, c17_r3]:
        for y in range(16):
            im.putpixel((0, y), grass_base.getpixel((0, y)))
            im.putpixel((1, y), grass_base.getpixel((1, y)))
            gp2 = grass_base.getpixel((2, y))
            gp3 = grass_base.getpixel((3, y))
            im.putpixel((2, y), (int(gp2[0]*0.55 + 18), int(gp2[1]*0.55 + 40), int(gp2[2]*0.55 + 8), 255))
            im.putpixel((3, y), (int(gp3[0]*0.35 + 20), int(gp3[1]*0.35 + 45), int(gp3[2]*0.35 + 8), 255))

    side_w = c17_r3.copy()
    r15_w = [side_w.getpixel((x, 15)) for x in range(16)]
    for x in range(16):
        side_w.putpixel((x, 0), r15_w[x])
        p0 = r15_w[x]
        p2 = side_w.getpixel((x, 2))
        side_w.putpixel((x, 1), tuple(int(p0[i]*0.6 + p2[i]*0.4) for i in range(4)))

    side_w_top = c17_r2.copy()
    for x in range(16):
        side_w_top.putpixel((x, 15), side_w.getpixel((x, 0)))

    side_w_bot = c17_r3.copy()
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
            im.putpixel((13, y), (int(gp13[0]*0.55 + 18), int(gp13[1]*0.55 + 40), int(gp13[2]*0.55 + 8), 255))
            im.putpixel((12, y), (int(gp12[0]*0.35 + 20), int(gp12[1]*0.35 + 45), int(gp12[2]*0.35 + 8), 255))

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

    # Align side_w_bot bottom row with ramp_right_top top row
    for x in range(16):
        side_w_bot.putpixel((x, 15), ramp_right_top.getpixel((x, 0)))
    # Align side_e_bot bottom row with ramp_left_top top row
    for x in range(16):
        side_e_bot.putpixel((x, 15), ramp_left_top.getpixel((x, 0)))

    # Harmonize junction corners
    side_w_bot.putpixel((15, 15), (67, 161, 25, 255))
    side_e_bot.putpixel((0, 15), (67, 161, 25, 255))

    # =========================================================================
    # 3. AUTHENTIC CORNERS (SW & SE) BUILT FROM CONCERNEDAPE BOULDERS
    # =========================================================================
    # SW Corner: derived from ramp_right_top & ramp_right_bot
    corner_sw_top = ramp_right_top.copy()
    corner_sw_bot = ramp_right_bot.copy()

    # Low ground (x=0..3) on SW is grass meadow with soft rock drop shadow
    for y in range(16):
        corner_sw_top.putpixel((0, y), grass_base.getpixel((0, y)))
        corner_sw_top.putpixel((1, y), grass_base.getpixel((1, y)))
        gp2 = grass_base.getpixel((2, y))
        gp3 = grass_base.getpixel((3, y))
        corner_sw_top.putpixel((2, y), (int(gp2[0]*0.55 + 18), int(gp2[1]*0.55 + 40), int(gp2[2]*0.55 + 8), 255))
        corner_sw_top.putpixel((3, y), (int(gp3[0]*0.35 + 20), int(gp3[1]*0.35 + 45), int(gp3[2]*0.35 + 8), 255))

        corner_sw_bot.putpixel((0, y), grass_base.getpixel((0, y)))
        corner_sw_bot.putpixel((1, y), grass_base.getpixel((1, y)))
        gp2_b = grass_base.getpixel((2, y))
        gp3_b = grass_base.getpixel((3, y))
        corner_sw_bot.putpixel((2, y), (int(gp2_b[0]*0.55 + 18), int(gp2_b[1]*0.55 + 40), int(gp2_b[2]*0.55 + 8), 255))
        corner_sw_bot.putpixel((3, y), (int(gp3_b[0]*0.35 + 20), int(gp3_b[1]*0.35 + 45), int(gp3_b[2]*0.35 + 8), 255))

    # Clean base row of corner_sw_bot (y=13..15, x=0..7) to grass + shadow
    for y in range(13, 16):
        for x in range(8):
            gp = grass_base.getpixel((x, y))
            corner_sw_bot.putpixel((x, y), (int(gp[0]*0.5 + 15), int(gp[1]*0.5 + 38), int(gp[2]*0.5 + 8), 255))

    # SE Corner: derived from ramp_left_top & ramp_left_bot
    corner_se_top = ramp_left_top.copy()
    corner_se_bot = ramp_left_bot.copy()

    # Low ground (x=12..15) on SE is grass meadow with soft rock drop shadow
    for y in range(16):
        corner_se_top.putpixel((15, y), grass_base.getpixel((15, y)))
        corner_se_top.putpixel((14, y), grass_base.getpixel((14, y)))
        gp13 = grass_base.getpixel((13, y))
        gp12 = grass_base.getpixel((12, y))
        corner_se_top.putpixel((13, y), (int(gp13[0]*0.55 + 18), int(gp13[1]*0.55 + 40), int(gp13[2]*0.55 + 8), 255))
        corner_se_top.putpixel((12, y), (int(gp12[0]*0.35 + 20), int(gp12[1]*0.35 + 45), int(gp12[2]*0.35 + 8), 255))

        corner_se_bot.putpixel((15, y), grass_base.getpixel((15, y)))
        corner_se_bot.putpixel((14, y), grass_base.getpixel((14, y)))
        gp13_b = grass_base.getpixel((13, y))
        gp12_b = grass_base.getpixel((12, y))
        corner_se_bot.putpixel((13, y), (int(gp13_b[0]*0.55 + 18), int(gp13_b[1]*0.55 + 40), int(gp13_b[2]*0.55 + 8), 255))
        corner_se_bot.putpixel((12, y), (int(gp12_b[0]*0.35 + 20), int(gp12_b[1]*0.35 + 45), int(gp12_b[2]*0.35 + 8), 255))

    # Clean base row of corner_se_bot (y=13..15, x=8..15) to grass + shadow
    for y in range(13, 16):
        for x in range(8, 16):
            gp = grass_base.getpixel((x, y))
            corner_se_bot.putpixel((x, y), (int(gp[0]*0.5 + 15), int(gp[1]*0.5 + 38), int(gp[2]*0.5 + 8), 255))

    # =========================================================================
    # 4. STRICT MATHEMATICAL ZERO-SEAM ENFORCEMENT
    # =========================================================================
    # A. TOP HORIZONTAL BOUNDARIES:
    # 1. SW Corner top edge matches side_w_bot bottom row (y=15):
    for x in range(16):
        corner_sw_top.putpixel((x, 0), side_w_bot.getpixel((x, 15)))

    # 2. SE Corner top edge matches side_e_bot bottom row (y=15):
    for x in range(16):
        corner_se_top.putpixel((x, 0), side_e_bot.getpixel((x, 15)))

    # 3. Left Shoulder top edge matches side_e_bot bottom row:
    for x in range(16):
        ramp_left_top.putpixel((x, 0), side_e_bot.getpixel((x, 15)))

    # 4. Right Shoulder top edge matches side_w_bot bottom row:
    for x in range(16):
        ramp_right_top.putpixel((x, 0), side_w_bot.getpixel((x, 15)))

    # B. VERTICAL BOUNDARY COLUMNS (CONNECTING TO FRONT CLIFF FACES):
    # SW Corner col 15 matches face_top_01 col 0:
    for y in range(16):
        corner_sw_top.putpixel((15, y), face_top_01.getpixel((0, y)))
        corner_sw_bot.putpixel((15, y), face_bot_01.getpixel((0, y)))

    # SE Corner col 0 matches face_top_02 col 15:
    for y in range(16):
        corner_se_top.putpixel((0, y), face_top_02.getpixel((15, y)))
        corner_se_bot.putpixel((0, y), face_bot_02.getpixel((15, y)))

    # Left Shoulder col 0 matches face_top_01 col 15:
    for y in range(16):
        ramp_left_top.putpixel((0, y), face_top_01.getpixel((15, y)))
        ramp_left_bot.putpixel((0, y), face_bot_01.getpixel((15, y)))

    # Right Shoulder col 15 matches face_top_02 col 0:
    for y in range(16):
        ramp_right_top.putpixel((15, y), face_top_02.getpixel((0, y)))
        ramp_right_bot.putpixel((15, y), face_bot_02.getpixel((0, y)))

    # C. INTERNAL TOP-TO-BOTTOM BOUNDARIES:
    for x in range(16):
        corner_sw_bot.putpixel((x, 0), corner_sw_top.getpixel((x, 15)))
        corner_se_bot.putpixel((x, 0), corner_se_top.getpixel((x, 15)))
        ramp_left_bot.putpixel((x, 0), ramp_left_top.getpixel((x, 15)))
        ramp_right_bot.putpixel((x, 0), ramp_right_top.getpixel((x, 15)))

    # Plateau crown caps (top outer corners)
    outer_tl = grass_base.copy()
    outer_tr = grass_base.copy()
    for y in range(16):
        for x in range(16):
            if x <= 7 and y <= 7:
                outer_tl.putpixel((x, y), side_w_top.getpixel((x, y)))
            if x >= 8 and y <= 7:
                outer_tr.putpixel((x, y), side_e_top.getpixel((x, y)))

    # Save all 16 tiles to Assets/Art/Terrain/Cliffs/
    tiles = {
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

    for name, img in tiles.items():
        img.save(os.path.join(cliff_dir, name))
        img.save(os.path.join(scratch_dir, name))

    print("All 16 masterpiece cliff tiles saved successfully.")

    # Run verification audit
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

    print("\n--- FINAL SEAM VERIFICATION AUDIT ---")
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
        print("\nSUCCESS: 100% ZERO-SEAM PERFECTION ACROSS ALL 22 BOUNDARIES!")
    else:
        print("\nWARNING: Some seams have mismatches!")

if __name__ == "__main__":
    generate_masterpiece_cliff_tiles()
