import os
from PIL import Image

def main():
    scratch_dir = r"C:\Users\PAVILION\.gemini\antigravity-ide\brain\84db0e2d-58d2-466d-be05-dbff8f133035\scratch"
    assets_dir = r"d:\Unity\Projects\STRANDED\Assets\Art\Terrain\Cliffs"
    
    full_path = os.path.join(scratch_dir, "stardew_native_512.png")
    full = Image.open(full_path).convert("RGBA")
    
    # 1. Left column (authentic 16x80 strip at x=220, y=20):
    # This strip gives us 5 tiles that naturally connect vertically:
    # y=0..16:   cliff_side_e_top
    # y=16..32:  cliff_side_e (mid 1)
    # y=32..48:  cliff_side_e_bot (mid 2)
    # y=48..64:  cliff_ramp_left_top (shoulder top)
    # y=64..80:  cliff_ramp_left_bot (shoulder bot)
    l_strip = full.crop((220, 20, 236, 100))
    side_e_top       = l_strip.crop((0, 0,  16, 16))
    side_e_mid       = l_strip.crop((0, 16, 16, 32))
    side_e_bot       = l_strip.crop((0, 32, 16, 48))
    ramp_left_top    = l_strip.crop((0, 48, 16, 64))
    ramp_left_bot    = l_strip.crop((0, 64, 16, 80))

    # 2. Right column (authentic 16x80 strip at x=268, y=20):
    # This strip gives us 5 tiles that naturally connect vertically:
    # y=0..16:   cliff_side_w_top
    # y=16..32:  cliff_side_w (mid 1)
    # y=32..48:  cliff_side_w_bot (mid 2)
    # y=48..64:  cliff_ramp_right_top (shoulder top)
    # y=64..80:  cliff_ramp_right_bot (shoulder bot)
    r_strip = full.crop((268, 20, 284, 100))
    side_w_top       = r_strip.crop((0, 0,  16, 16))
    side_w_mid       = r_strip.crop((0, 16, 16, 32))
    side_w_bot       = r_strip.crop((0, 32, 16, 48))
    ramp_right_top   = r_strip.crop((0, 48, 16, 64))
    ramp_right_bot   = r_strip.crop((0, 64, 16, 80))

    # 3. Front wall slices from x=86..118, y=68..100:
    fw = full.crop((86, 68, 118, 100))
    front_top_01 = fw.crop((0, 0, 16, 16))
    front_top_02 = fw.crop((16, 0, 32, 16))
    front_bot_01 = fw.crop((0, 16, 16, 32))
    front_bot_02 = fw.crop((16, 16, 32, 32))

    # Seamless horizontal tiling between front_01 and front_02:
    for y in range(16):
        # Match t1 left edge with t2 right edge
        p_seam = front_top_01.getpixel((0, y))
        front_top_02.putpixel((15, y), p_seam)
        p_seam_b = front_bot_01.getpixel((0, y))
        front_bot_02.putpixel((15, y), p_seam_b)

    # Seamless connection between front wall and shoulders:
    # Left shoulder connects to front_top_02 on its left (x=0 of ramp_left_top matches x=15 of front_top_02)
    for y in range(16):
        ramp_left_top.putpixel((0, y), front_top_02.getpixel((15, y)))
        ramp_left_bot.putpixel((0, y), front_bot_02.getpixel((15, y)))
    # Right shoulder connects to front_top_01 on its right (x=15 of ramp_right_top matches x=0 of front_top_01)
    for y in range(16):
        ramp_right_top.putpixel((15, y), front_top_01.getpixel((0, y)))
        ramp_right_bot.putpixel((15, y), front_bot_01.getpixel((0, y)))

    # 4. Natural Mud Path (between the shoulders at x=244..260, y=68..100):
    mud_strip = full.crop((244, 68, 260, 100))
    ramp_mid_top = mud_strip.crop((0, 0, 16, 16))
    ramp_mid_bot = mud_strip.crop((0, 16, 16, 32))
    mud_slope_top = ramp_mid_top.copy()
    mud_slope_bot = ramp_mid_bot.copy()

    # 5. Outer Corners:
    corner_sw_top = side_w_top.transpose(Image.FLIP_LEFT_RIGHT).copy()
    corner_sw_bot = front_bot_01.copy()
    for y in range(16):
        for x in range(16):
            if x < 4 and y > 10:
                corner_sw_bot.putpixel((x, y), (182, 122, 41, 255))
            elif x < 2:
                corner_sw_top.putpixel((x, y), (182, 122, 41, 255))

    corner_se_top = side_e_top.transpose(Image.FLIP_LEFT_RIGHT).copy()
    corner_se_bot = front_bot_02.copy()
    for y in range(16):
        for x in range(16):
            if x > 11 and y > 10:
                corner_se_bot.putpixel((x, y), (182, 122, 41, 255))
            elif x > 13:
                corner_se_top.putpixel((x, y), (182, 122, 41, 255))

    outer_tl_top = corner_sw_top.copy()
    outer_tr_top = corner_se_top.copy()

    # Save all 24 tiles into Assets and scratch
    tiles = {
        "cliff_face_top_01": front_top_01,
        "cliff_face_top_02": front_top_02,
        "cliff_face_bot_01": front_bot_01,
        "cliff_face_bot_02": front_bot_02,
        
        "cliff_side_w_top":  side_w_top,
        "cliff_side_w":      side_w_mid,
        "cliff_side_w_bot":  side_w_bot,
        
        "cliff_side_e_top":  side_e_top,
        "cliff_side_e":      side_e_mid,
        "cliff_side_e_bot":  side_e_bot,
        
        "cliff_corner_sw_top": corner_sw_top,
        "cliff_corner_sw_bot": corner_sw_bot,
        "cliff_corner_se_top": corner_se_top,
        "cliff_corner_se_bot": corner_se_bot,
        
        "cliff_outer_tl_top": outer_tl_top,
        "cliff_outer_tr_top": outer_tr_top,
        
        "cliff_ramp_left_top":  ramp_left_top,
        "cliff_ramp_left_bot":  ramp_left_bot,
        "cliff_ramp_right_top": ramp_right_top,
        "cliff_ramp_right_bot": ramp_right_bot,
        "cliff_ramp_mid_top":   ramp_mid_top,
        "cliff_ramp_mid_bot":   ramp_mid_bot,
        
        "cliff_mud_slope_top":  mud_slope_top,
        "cliff_mud_slope_bot":  mud_slope_bot
    }

    for name, img in tiles.items():
        img.save(os.path.join(assets_dir, f"{name}.png"))
        img.save(os.path.join(scratch_dir, f"{name}.png"))

    # Autotile sheet
    sheet = Image.new("RGBA", (128, 64), (0, 0, 0, 0))
    sheet_layout = [
        ["cliff_face_top_01", "cliff_face_top_02", "cliff_ramp_left_top", "cliff_ramp_mid_top", "cliff_ramp_right_top", "cliff_side_w_top", "cliff_side_e_top", "cliff_outer_tl_top"],
        ["cliff_face_bot_01", "cliff_face_bot_02", "cliff_ramp_left_bot", "cliff_ramp_mid_bot", "cliff_ramp_right_bot", "cliff_side_w",     "cliff_side_e",     "cliff_outer_tr_top"],
        ["cliff_corner_sw_top", "cliff_corner_se_top", "cliff_mud_slope_top", "cliff_mud_slope_bot", "", "", "cliff_side_w_bot", "cliff_side_e_bot"],
        ["cliff_corner_sw_bot", "cliff_corner_se_bot", "", "", "", "", "", ""]
    ]
    for r, row in enumerate(sheet_layout):
        for c, key in enumerate(row):
            if key and key in tiles:
                sheet.paste(tiles[key], (c * 16, r * 16))

    sheet.save(os.path.join(assets_dir, "cliff_autotile_sheet.png"))
    sheet.save(os.path.join(scratch_dir, "cliff_autotile_sheet.png"))
    print("Saved all 24 improved tiles + sheet!")

if __name__ == "__main__":
    main()
