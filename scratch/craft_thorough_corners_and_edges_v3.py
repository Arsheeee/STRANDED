import os
from PIL import Image

def build_tiles():
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
    # 1. CANYON SHOULDERS FROM AUTHENTIC STARDEW SOURCE
    # =========================================================================
    # Left Shoulder: col 14
    # c14_top_rim = ref.crop((14*16, 4*16, 15*16, 5*16))
    # c14_top_bdr = ref.crop((14*16, 5*16, 15*16, 6*16))
    # c14_bot_bdr = ref.crop((14*16, 6*16, 15*16, 7*16))
    # c14_bot_fot = ref.crop((14*16, 7*16, 15*16, 8*16))
    c14_top_rim = ref.crop((14*16, 4*16, 15*16, 5*16))
    c14_top_bdr = ref.crop((14*16, 5*16, 15*16, 6*16))
    c14_bot_bdr = ref.crop((14*16, 6*16, 15*16, 7*16))
    c14_bot_fot = ref.crop((14*16, 7*16, 15*16, 8*16))

    ramp_left_top = Image.new("RGBA", (16, 16))
    ramp_left_top.paste(c14_top_rim.crop((0, 0, 16, 7)), (0, 0))
    ramp_left_top.paste(c14_top_bdr.crop((0, 7, 16, 16)), (0, 7))

    ramp_left_bot = Image.new("RGBA", (16, 16))
    ramp_left_bot.paste(c14_bot_bdr.crop((0, 0, 16, 10)), (0, 0))
    ramp_left_bot.paste(c14_bot_fot.crop((0, 10, 16, 16)), (0, 10))

    # Right Shoulder: col 17
    c17_top_rim = ref.crop((17*16, 4*16, 18*16, 5*16))
    c17_top_bdr = ref.crop((17*16, 5*16, 18*16, 6*16))
    c17_bot_bdr = ref.crop((17*16, 6*16, 18*16, 7*16))
    c17_bot_fot = ref.crop((17*16, 7*16, 18*16, 8*16))

    ramp_right_top = Image.new("RGBA", (16, 16))
    ramp_right_top.paste(c17_top_rim.crop((0, 0, 16, 7)), (0, 0))
    ramp_right_top.paste(c17_top_bdr.crop((0, 7, 16, 16)), (0, 7))

    ramp_right_bot = Image.new("RGBA", (16, 16))
    ramp_right_bot.paste(c17_bot_bdr.crop((0, 0, 16, 10)), (0, 0))
    ramp_right_bot.paste(c17_bot_fot.crop((0, 10, 16, 16)), (0, 10))

    # =========================================================================
    # 2. VERTICAL SIDE FLANKS (cliff_side_w and cliff_side_e)
    # =========================================================================
    # West Flank: Col 17, rows 2 & 3
    # Rock on left (x=4..10), grass on right (x=11..15), path/shadow on left (x=0..3)
    c17_r2 = ref.crop((17*16, 2*16, 18*16, 3*16))
    c17_r3 = ref.crop((17*16, 3*16, 18*16, 4*16))

    # Mid tile: ensure seamless vertical tiling
    side_w = c17_r3.copy()
    # To tile seamlessly with itself:
    # make row 0 match row 15 smoothly
    blend_row_w = [c17_r3.getpixel((x, 15)) for x in range(16)]
    for x in range(16):
        side_w.putpixel((x, 0), blend_row_w[x])
        # Smooth transition into row 1
        p0 = blend_row_w[x]
        p2 = side_w.getpixel((x, 2))
        avg = tuple(int(p0[i]*0.5 + p2[i]*0.5) for i in range(4))
        side_w.putpixel((x, 1), avg)

    # Top tile: rounds off into grass at row 0
    side_w_top = c17_r2.copy()
    # Make its bottom row (y=15) match side_w row 0
    for x in range(16):
        side_w_top.putpixel((x, 15), side_w.getpixel((x, 0)))

    # Bot tile:
    side_w_bot = c17_r3.copy()
    for x in range(16):
        side_w_bot.putpixel((x, 0), side_w.getpixel((x, 15)))

    # East Flank: Col 14, rows 2 & 3
    # Grass on left (x=0..6), rock in middle (x=7..11), path/shadow on right (x=12..15)
    c14_r2 = ref.crop((14*16, 2*16, 15*16, 3*16))
    c14_r3 = ref.crop((14*16, 3*16, 15*16, 4*16))

    side_e = c14_r3.copy()
    blend_row_e = [c14_r3.getpixel((x, 15)) for x in range(16)]
    for x in range(16):
        side_e.putpixel((x, 0), blend_row_e[x])
        p0 = blend_row_e[x]
        p2 = side_e.getpixel((x, 2))
        avg = tuple(int(p0[i]*0.5 + p2[i]*0.5) for i in range(4))
        side_e.putpixel((x, 1), avg)

    side_e_top = c14_r2.copy()
    for x in range(16):
        side_e_top.putpixel((x, 15), side_e.getpixel((x, 0)))

    side_e_bot = c14_r3.copy()
    for x in range(16):
        side_e_bot.putpixel((x, 0), side_e.getpixel((x, 15)))

    # Align side_w_bot bottom (row 15) with ramp_right_top top (row 0)
    for x in range(16):
        p = ramp_right_top.getpixel((x, 0))
        side_w_bot.putpixel((x, 15), p)

    # Align side_e_bot bottom (row 15) with ramp_left_top top (row 0)
    for x in range(16):
        p = ramp_left_top.getpixel((x, 0))
        side_e_bot.putpixel((x, 15), p)

    # =========================================================================
    # 3. OUTER CORNERS (SW and SE)
    # =========================================================================
    # For SW corner:
    # Outer convex corner where the cliff wraps around to the Southwest!
    # Connects on top to side_w_bot, on right to face_top_01
    # We can craft an organic corner based on ramp_right_top (mirrored horizontally and relit)
    # or by blending the outer corner boulders from ConcernedApe's reference!
    corner_sw_top = Image.new("RGBA", (16, 16))
    corner_sw_bot = Image.new("RGBA", (16, 16))
    
    # We take the organic boulder curvature of the corner:
    # The right half (x=8..15) connects to face_top_01 col 0:
    # The top half (y=0..7) connects to side_w_bot row 15:
    # Let's start with face_top_01 as base for the right half, side_w_bot for top-left
    # and create the beautiful rounded 3D corner boulder!
    
    # Let's inspect: ramp_left is an authentic corner that has rock on left and path on right.
    # An outer SW corner has rock in the center-left and low ground on the far left.
    # Let's construct corner_sw using authentic pixels:
    # Top tile:
    for y in range(16):
        for x in range(16):
            if x >= 8:
                # Blend towards face_top_01
                corner_sw_top.putpixel((x, y), face_top_01.getpixel((x, y)))
            else:
                # West flank boulder rock
                corner_sw_top.putpixel((x, y), side_w_bot.getpixel((x, y)))
                
    # Now enforce seamless corner curvature:
    # Top edge must match side_w_bot bottom row:
    for x in range(16):
        corner_sw_top.putpixel((x, 0), side_w_bot.getpixel((x, 15)))
    # Right edge must match face_top_01 left edge (col 0):
    for y in range(16):
        corner_sw_top.putpixel((15, y), face_top_01.getpixel((0, y)))
        
    # Bottom tile:
    for y in range(16):
        for x in range(16):
            if x >= 8:
                corner_sw_bot.putpixel((x, y), face_bot_01.getpixel((x, y)))
            else:
                corner_sw_bot.putpixel((x, y), ramp_left_bot.getpixel((x, y)))
    for y in range(16):
        corner_sw_bot.putpixel((15, y), face_bot_01.getpixel((0, y)))
    for x in range(16):
        corner_sw_bot.putpixel((x, 0), corner_sw_top.getpixel((x, 15)))

    # SE Corner:
    corner_se_top = Image.new("RGBA", (16, 16))
    corner_se_bot = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            if x < 8:
                corner_se_top.putpixel((x, y), face_top_02.getpixel((x, y)))
            else:
                corner_se_top.putpixel((x, y), side_e_bot.getpixel((x, y)))
    for x in range(16):
        corner_se_top.putpixel((x, 0), side_e_bot.getpixel((x, 15)))
    for y in range(16):
        corner_se_top.putpixel((0, y), face_top_02.getpixel((15, y)))

    for y in range(16):
        for x in range(16):
            if x < 8:
                corner_se_bot.putpixel((x, y), face_bot_02.getpixel((x, y)))
            else:
                corner_se_bot.putpixel((x, y), ramp_right_bot.getpixel((x, y)))
    for y in range(16):
        corner_se_bot.putpixel((0, y), face_bot_02.getpixel((15, y)))
    for x in range(16):
        corner_se_bot.putpixel((x, 0), corner_se_top.getpixel((x, 15)))

    # Enforce seam between ramp_left and face_top_01:
    for y in range(16):
        ramp_left_top.putpixel((0, y), face_top_01.getpixel((15, y)))
        ramp_left_bot.putpixel((0, y), face_bot_01.getpixel((15, y)))
    for x in range(16):
        ramp_left_bot.putpixel((x, 0), ramp_left_top.getpixel((x, 15)))

    # Enforce seam between ramp_right and face_top_02:
    for y in range(16):
        ramp_right_top.putpixel((15, y), face_top_02.getpixel((0, y)))
        ramp_right_bot.putpixel((15, y), face_bot_02.getpixel((0, y)))
    for x in range(16):
        ramp_right_bot.putpixel((x, 0), ramp_right_top.getpixel((x, 15)))

    # Save to scratch to preview
    ramp_left_top.save(os.path.join(scratch_dir, "test_v3_ramp_left_top.png"))
    ramp_left_bot.save(os.path.join(scratch_dir, "test_v3_ramp_left_bot.png"))
    ramp_right_top.save(os.path.join(scratch_dir, "test_v3_ramp_right_top.png"))
    ramp_right_bot.save(os.path.join(scratch_dir, "test_v3_ramp_right_bot.png"))
    side_w.save(os.path.join(scratch_dir, "test_v3_side_w.png"))
    side_w_top.save(os.path.join(scratch_dir, "test_v3_side_w_top.png"))
    side_w_bot.save(os.path.join(scratch_dir, "test_v3_side_w_bot.png"))
    side_e.save(os.path.join(scratch_dir, "test_v3_side_e.png"))
    side_e_top.save(os.path.join(scratch_dir, "test_v3_side_e_top.png"))
    side_e_bot.save(os.path.join(scratch_dir, "test_v3_side_e_bot.png"))
    corner_sw_top.save(os.path.join(scratch_dir, "test_v3_corner_sw_top.png"))
    corner_sw_bot.save(os.path.join(scratch_dir, "test_v3_corner_sw_bot.png"))
    corner_se_top.save(os.path.join(scratch_dir, "test_v3_corner_se_top.png"))
    corner_se_bot.save(os.path.join(scratch_dir, "test_v3_corner_se_bot.png"))

    print("Saved all v3 test tiles.")

if __name__ == "__main__":
    build_tiles()
