import os
from PIL import Image, ImageDraw, ImageFont

def main():
    brain_dir = r"C:\Users\PAVILION\.gemini\antigravity-ide\brain\84db0e2d-58d2-466d-be05-dbff8f133035"
    scratch_dir = os.path.join(brain_dir, "scratch")
    
    # Load reference image crop around canyon
    full_ref = Image.open(os.path.join(scratch_dir, "stardew_native_512.png")).convert("RGBA")
    # Reference canyon area: x=192..352 (160px = 10 tiles), y=0..160 (160px = 10 tiles)
    ref_crop = full_ref.crop((184, 0, 360, 160)) # 176 x 160
    
    # Load our simulated canyon pass
    sim = Image.open(os.path.join(scratch_dir, "simulated_canyon_pass_native.png")).convert("RGBA")
    # Crop our simulated canyon pass: x=128..304 (176px), y=16..176 (160px)
    sim_crop = sim.crop((128, 0, 304, 160))
    
    # Upscale 3x
    scale = 3
    ref_3x = ref_crop.resize((ref_crop.width * scale, ref_crop.height * scale), Image.NEAREST)
    sim_3x = sim_crop.resize((sim_crop.width * scale, sim_crop.height * scale), Image.NEAREST)
    
    # Also load the tile gallery:
    tiles_names = [
        ("Front Top 01", "cliff_face_top_01"),
        ("Front Top 02", "cliff_face_top_02"),
        ("Front Bot 01", "cliff_face_bot_01"),
        ("Front Bot 02", "cliff_face_bot_02"),
        ("West Flank Top", "cliff_side_w_top"),
        ("West Flank Mid", "cliff_side_w"),
        ("West Flank Bot", "cliff_side_w_bot"),
        ("East Flank Top", "cliff_side_e_top"),
        ("East Flank Mid", "cliff_side_e"),
        ("East Flank Bot", "cliff_side_e_bot"),
        ("Shoulder Left Top", "cliff_ramp_left_top"),
        ("Shoulder Left Bot", "cliff_ramp_left_bot"),
        ("Shoulder Right Top", "cliff_ramp_right_top"),
        ("Shoulder Right Bot", "cliff_ramp_right_bot"),
        ("Mud Incline Top", "cliff_ramp_mid_top"),
        ("Mud Incline Bot", "cliff_ramp_mid_bot"),
    ]
    
    # Create showcase canvas
    card_w = sim_3x.width
    card_h = sim_3x.height
    header_h = 100
    gallery_h = 240
    pad = 30
    
    total_w = card_w * 2 + pad * 3
    total_h = header_h + card_h + gallery_h + pad * 2
    
    out = Image.new("RGBA", (total_w, total_h), (11, 19, 32, 255))
    draw = ImageDraw.Draw(out)
    
    # Header Banner
    draw.text((pad, 20), "STRANDED - Volumetric Cliff & Natural Mud Canyon Incline", fill=(255, 255, 255))
    draw.text((pad, 48), "Authentic pillow boulders, organic East/West flanks, and 100% pure earthen mud elevation (no steps/stairs).", fill=(170, 195, 220))
    draw.text((pad, 70), "Handcrafted to match Stardew Valley reference palette, boulder volume, and canyon pass geometry.", fill=(225, 175, 45))
    
    # Left Card: Stardew Valley Reference
    draw.text((pad, header_h - 22), "Original Reference (Stardew Valley Farm Canyon)", fill=(110, 225, 120))
    out.paste(ref_3x, (pad, header_h))
    draw.rectangle([pad, header_h, pad + card_w, header_h + card_h], outline=(45, 85, 125, 255), width=2)
    
    # Right Card: STRANDED Assembled Tiles
    x_right = pad * 2 + card_w
    draw.text((x_right, header_h - 22), "STRANDED In-Game Production Tiles (Assembled Scene)", fill=(245, 205, 55))
    out.paste(sim_3x, (x_right, header_h))
    draw.rectangle([x_right, header_h, x_right + card_w, header_h + card_h], outline=(200, 150, 40, 255), width=2)
    
    # Bottom Section: Tile Gallery
    gy = header_h + card_h + pad
    draw.text((pad, gy - 20), "Authentic 16x16 Autotile Library (Sample Tiles at 3x Native Scale):", fill=(200, 220, 245))
    
    tile_col_w = (total_w - pad * 2) // 8
    for idx, (label, tname) in enumerate(tiles_names):
        r = idx // 8
        c = idx % 8
        tp = os.path.join(r"d:\Unity\Projects\STRANDED\Assets\Art\Terrain\Cliffs", f"{tname}.png")
        if os.path.exists(tp):
            tim = Image.open(tp).convert("RGBA")
            tim_3x = tim.resize((48, 48), Image.NEAREST)
            bx = pad + c * tile_col_w
            by = gy + r * 90 + 10
            # Tile frame
            draw.rectangle([bx, by, bx + 52, by + 52], fill=(16, 28, 46, 255), outline=(45, 85, 125, 255))
            out.paste(tim_3x, (bx + 2, by + 2), tim_3x)
            draw.text((bx, by + 56), label, fill=(180, 200, 220))
            
    # Save to scratch & artifacts
    showcase_scratch = os.path.join(scratch_dir, "cliff_mud_elevation_showcase.png")
    showcase_brain   = os.path.join(brain_dir, "cliff_mud_elevation_showcase.png")
    out.save(showcase_scratch)
    out.save(showcase_brain)
    print(f"Saved showcase to {showcase_brain} ({total_w}x{total_h})!")

if __name__ == "__main__":
    main()
