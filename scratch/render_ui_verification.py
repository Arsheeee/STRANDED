import os
from PIL import Image, ImageDraw, ImageFont

def render_ui_showcase():
    os.makedirs("scratch", exist_ok=True)

    # 1. Load textures
    slot_bg = Image.open("Assets/Art/UI/ui_slot_background.png").convert("RGBA")
    slot_sel = Image.open("Assets/Art/UI/ui_slot_selected.png").convert("RGBA")
    panel = Image.open("Assets/Art/UI/ui_inventory_panel.png").convert("RGBA")
    menu_panel = Image.open("Assets/Art/UI/ui_menu_panel.png").convert("RGBA")

    # Fonts
    f_title = ImageFont.truetype("scratch/fonts/PressStart2P.ttf", 14)
    f_header = ImageFont.truetype("scratch/fonts/PressStart2P.ttf", 12)
    f_body = ImageFont.truetype("scratch/fonts/Silkscreen.ttf", 13)
    f_body_b = ImageFont.truetype("scratch/fonts/SilkscreenBold.ttf", 14)
    f_small = ImageFont.truetype("scratch/fonts/Silkscreen.ttf", 11)

    # Canvas
    cw, ch = 960, 680
    bg_color = (25, 45, 35) # Dark tropical forest backdrop
    canvas = Image.new("RGBA", (cw, ch), bg_color)
    draw = ImageDraw.Draw(canvas)

    # Top title
    draw.text((30, 20), "STRANDED - RESTORED UI COLOR & PIXEL ART TYPOGRAPHY", fill=(245, 215, 140), font=f_title)
    draw.text((30, 45), "Warm Parchment Color Scheme  |  Ruby Red Selector  |  8-Bit/16-Bit Font Rendering", fill=(180, 200, 180), font=f_body)

    # Section 1: Inventory Window (Left: 500x380)
    inv_x, inv_y = 30, 80
    inv_scaled = panel.resize((500, 380), Image.Resampling.NEAREST)
    canvas.paste(inv_scaled, (inv_x, inv_y), inv_scaled)

    # Inventory Title
    draw.text((inv_x + 35, inv_y + 25), "INVENTORY", fill=(85, 48, 22), font=f_header)
    draw.text((inv_x + 35, inv_y + 48), "36 SLOTS (HOTBAR & BACKPACK)", fill=(100, 55, 22), font=f_small)

    # Draw a 4x3 grid of slots inside the inventory panel
    slot_w = 48
    spacing = 6
    start_grid_x = inv_x + 35
    start_grid_y = inv_y + 70

    items_sample = [
        ("Axe", "1"), ("Pick", "1"), ("Knife", "1"), ("Fish", "3"),
        ("Wood", "12"), ("Stone", "8"), ("Vine", "6"), ("Fiber", "15"),
        ("Berry", "4"), ("Mush", "2"), ("", ""), ("", "")
    ]

    for row in range(3):
        for col in range(4):
            idx = row * 4 + col
            sx = start_grid_x + col * (slot_w + spacing)
            sy = start_grid_y + row * (slot_w + spacing)
            s_img = slot_bg.resize((slot_w, slot_w), Image.Resampling.NEAREST)
            canvas.paste(s_img, (sx, sy), s_img)

            # Slot number in red
            draw.text((sx + 3, sy + 2), str(idx + 1), fill=(210, 45, 30), font=f_small)

            if idx < len(items_sample) and items_sample[idx][0]:
                name, qty = items_sample[idx]
                draw.text((sx + 8, sy + 18), name[:4], fill=(70, 40, 18), font=f_body_b)
                draw.text((sx + slot_w - 14, sy + slot_w - 14), qty, fill=(255, 255, 255), font=f_small)

            # Highlight slot 2 (Knife) with the restored Ruby Red selector
            if idx == 2:
                sel_img = slot_sel.resize((slot_w, slot_w), Image.Resampling.NEAREST)
                canvas.paste(sel_img, (sx, sy), sel_img)

    # Right side of inventory panel: Selected Item Details Card
    card_x = inv_x + 270
    card_y = inv_y + 70
    draw.text((card_x, card_y), "STONE KNIFE", fill=(90, 50, 25), font=f_header)
    draw.text((card_x, card_y + 24), "[Tool / Foraging]", fill=(180, 50, 30), font=f_body_b)
    desc_lines = [
        "Crafted with coastal stone",
        "and plant fiber.",
        "",
        "Required to harvest palm",
        "fronds, vines, and fibers.",
        "",
        "Attack Power: 8",
        "Durability: 100 / 100"
    ]
    for i, line in enumerate(desc_lines):
        draw.text((card_x, card_y + 48 + i * 16), line, fill=(70, 40, 18), font=f_body)

    # Section 2: Escape / Restart Window (Right: 380x380)
    esc_x, esc_y = 550, 80
    esc_scaled = menu_panel.resize((380, 380), Image.Resampling.NEAREST)
    canvas.paste(esc_scaled, (esc_x, esc_y), esc_scaled)

    draw.text((esc_x + 80, esc_y + 30), "* GAME PAUSED *", fill=(100, 55, 22), font=f_header)
    draw.text((esc_x + 65, esc_y + 55), "STRANDED - Base Camp", fill=(120, 70, 30), font=f_small)

    buttons = [
        ("RESUME GAME", (110, 60, 25), (255, 245, 220)),
        ("RESTART GAME", (160, 30, 20), (255, 220, 210)),
        ("SAVE GAME (F5)", (110, 60, 25), (255, 245, 220)),
        ("LOAD GAME (F9)", (110, 60, 25), (255, 245, 220))
    ]
    bw, bh = 260, 36
    bx = esc_x + 60
    for bi, (btn_text, btn_border_col, btn_text_col) in enumerate(buttons):
        by = esc_y + 85 + bi * 48
        draw.rectangle([bx, by, bx + bw, by + bh], fill=(75, 42, 18), outline=btn_border_col, width=2)
        draw.text((bx + 35, by + 10), btn_text, fill=btn_text_col, font=f_body_b)

    draw.text((esc_x + 85, esc_y + 340), "[ESC] to Resume Game", fill=(100, 55, 22), font=f_small)

    # Section 3: Hotbar Preview along bottom (width 900)
    hb_y = 520
    draw.text((30, hb_y - 25), "HOTBAR HUD (12 SLOTS + BAG / CRAFT QUICK BUTTONS)", fill=(245, 215, 140), font=f_header)

    hb_container_w = 12 * 56 + 11 * 6 + 140
    hb_x = 30
    draw.rectangle([hb_x, hb_y, hb_x + hb_container_w, hb_y + 72], fill=(45, 28, 14), outline=(100, 65, 30), width=2)

    hotbar_items = ["Axe", "Pick", "Knife", "Fish", "Wood", "Stone", "Vine", "Fiber", "Berry", "Mush", "", ""]
    for i in range(12):
        sx = hb_x + 10 + i * 62
        sy = hb_y + 8
        s_img = slot_bg.resize((56, 56), Image.Resampling.NEAREST)
        canvas.paste(s_img, (sx, sy), s_img)

        # Slot key binding number in red
        key_num = str((i + 1) % 10) if i < 10 else ("-" if i == 10 else "=")
        draw.text((sx + 3, sy + 2), key_num, fill=(210, 45, 30), font=f_small)

        if i < len(hotbar_items) and hotbar_items[i]:
            draw.text((sx + 10, sy + 22), hotbar_items[i][:4], fill=(70, 40, 18), font=f_body_b)

        # Selected slot 3 (Knife)
        if i == 2:
            sel_img = slot_sel.resize((56, 56), Image.Resampling.NEAREST)
            canvas.paste(sel_img, (sx, sy), sel_img)

    # Quick Bag and Craft side buttons
    quick_btn_x = hb_x + 10 + 12 * 62 + 6
    draw.rectangle([quick_btn_x, hb_y + 8, quick_btn_x + 56, hb_y + 64], fill=(222, 184, 126), outline=(85, 48, 22), width=2)
    draw.text((quick_btn_x + 14, hb_y + 16), "BAG", fill=(85, 48, 22), font=f_body_b)
    draw.text((quick_btn_x + 18, hb_y + 36), "[I]", fill=(210, 45, 30), font=f_small)

    quick_craft_x = quick_btn_x + 62
    draw.rectangle([quick_craft_x, hb_y + 8, quick_craft_x + 56, hb_y + 64], fill=(222, 184, 126), outline=(85, 48, 22), width=2)
    draw.text((quick_craft_x + 8, hb_y + 16), "CRAFT", fill=(85, 48, 22), font=f_body_b)
    draw.text((quick_craft_x + 18, hb_y + 36), "[C]", fill=(210, 45, 30), font=f_small)

    out_path = "scratch/ui_showcase_final.png"
    canvas.save(out_path)
    print("Saved showcase to", out_path)

if __name__ == "__main__":
    render_ui_showcase()
