import os
from PIL import Image, ImageDraw, ImageFont

def render_batch4_previews():
    base_grove = Image.open('scratch/updated_forest_grove.png').convert('RGBA')
    
    # Load UI elements (using newly generated 64x64 high-res textures)
    slot_bg = Image.open('Assets/Art/UI/ui_slot_background.png').convert('RGBA')
    slot_sel = Image.open('Assets/Art/UI/ui_slot_selected.png').convert('RGBA')
    panel_bg = Image.open('Assets/Art/UI/ui_inventory_panel.png').convert('RGBA')
    close_btn = Image.open('Assets/Art/UI/ui_close_button.png').convert('RGBA')
    
    # Load items and tools
    sp_axe = Image.open('Assets/Art/Environment/Items/tool_stone_axe.png').convert('RGBA')
    sp_pick = Image.open('Assets/Art/Environment/Items/tool_stone_pickaxe.png').convert('RGBA')
    sp_knife = Image.open('Assets/Art/Environment/Items/tool_stone_knife.png').convert('RGBA')
    sp_rod = Image.open('Assets/Art/Environment/Items/tool_fishing_rod.png').convert('RGBA')
    sp_wood = Image.open('Assets/Art/Environment/Items/item_wood.png').convert('RGBA')
    sp_stone = Image.open('Assets/Art/Environment/Items/item_stone.png').convert('RGBA')
    sp_fiber = Image.open('Assets/Art/Environment/Items/item_fiber.png').convert('RGBA')
    sp_berries = Image.open('Assets/Art/Environment/Items/item_berry.png').convert('RGBA')
    sp_coconut = Image.open('Assets/Art/Environment/Items/item_coconut.png').convert('RGBA')

    # Enlarged slot dimensions (42x42 on 960x540 canvas, equivalent to 64x64 on 1080p)
    slot_w, slot_h = 42, 42
    spacing = 4
    slot_bg_scaled = slot_bg.resize((slot_w, slot_h), Image.Resampling.NEAREST)
    slot_sel_scaled = slot_sel.resize((slot_w + 4, slot_h + 4), Image.Resampling.NEAREST)

    # =========================================================================
    # VIEW 1: IN-GAME GAMEPLAY WITH ENLARGED HOTBAR (Stardew Reference Proportions)
    # =========================================================================
    view1 = base_grove.copy()
    draw1 = ImageDraw.Draw(view1, 'RGBA')

    # Top-Left Tracker (Enlarged)
    draw1.rectangle([16, 16, 480, 115], fill=(16, 22, 28, 230), outline=(90, 120, 145, 255), width=2)
    draw1.text((28, 24), "[STRANDED BATCH 4: INVENTORY & TOOL SYSTEM]", fill=(255, 215, 0, 255))
    draw1.text((28, 48), "Wood: 12   Stone: 8   Fiber: 4   Berries: 6   Coconut: 2", fill=(235, 235, 235, 255))
    draw1.text((28, 70), "Equipped: [Stone Axe]   Hotbar: 1-9,0,-,= | Bag: 'I'", fill=(0, 240, 255, 255))
    draw1.text((28, 92), "Storage: 36 Total Slots (12 Hotbar + 24 Backpack)", fill=(150, 200, 150, 255))

    # Context Prompt above hotbar (Enlarged and positioned clearly above bar)
    px0, py0, px1, py1 = 250, 410, 710, 452
    draw1.rectangle([px0, py0, px1, py1], fill=(12, 20, 24, 235), outline=(0, 255, 190, 255), width=2)
    draw1.text((px0 + 55, py0 + 12), "[E] Harvest Tropical Tree [Stone Axe]", fill=(120, 255, 180, 255))

    # Bottom Hotbar (12 slots + 1 Bag slot)
    total_hb_w = 12 * slot_w + 11 * spacing + slot_w + 8
    hb_x = int((960 - total_hb_w) / 2)
    hb_y = 540 - slot_h - 18

    # Hotbar wooden backplate (Warm dark wood)
    draw1.rectangle([hb_x - 8, hb_y - 8, hb_x + total_hb_w + 8, hb_y + slot_h + 8], fill=(42, 24, 10, 240), outline=(105, 58, 25, 255), width=2)

    hotbar_items = [
        (sp_axe, None),     # slot 0 (1): Axe (selected)
        (sp_knife, None),   # slot 1 (2): Knife
        (sp_pick, None),    # slot 2 (3): Pickaxe
        (sp_rod, None),     # slot 3 (4): Rod
        (sp_wood, 12),      # slot 4 (5): Wood x12
        (sp_stone, 8),      # slot 5 (6): Stone x8
        (sp_fiber, 4),      # slot 6 (7): Fiber x4
        (sp_berries, 6),    # slot 7 (8): Berries x6
        (sp_coconut, 2),    # slot 8 (9): Coconut x2
        (None, None),       # slot 9 (0): empty
        (None, None),       # slot 10 (-): empty
        (None, None)        # slot 11 (=): empty
    ]

    keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "="]

    for i in range(12):
        sx = hb_x + i * (slot_w + spacing)
        sy = hb_y
        view1.alpha_composite(slot_bg_scaled, (sx, sy))

        # Item icon
        item_sp, qty = hotbar_items[i]
        if item_sp:
            icon_scaled = item_sp.resize((30, 30), Image.Resampling.NEAREST)
            view1.alpha_composite(icon_scaled, (sx + 6, sy + 6))

        # Stardew Valley red slot numbers
        draw1.text((sx + 3, sy + 2), keys[i], fill=(210, 40, 30, 255))

        # Quantity badge with shadow
        if qty:
            draw1.text((sx + 24, sy + 25), str(qty), fill=(10, 10, 10, 255))
            draw1.text((sx + 23, sy + 24), str(qty), fill=(255, 255, 255, 255))

        # Slot 0 Selected Highlight (Axe active)
        if i == 0:
            view1.alpha_composite(slot_sel_scaled, (sx - 2, sy - 2))

    # Clickable Bag Button on the right of the hotbar
    bag_x = hb_x + 12 * (slot_w + spacing) + 4
    view1.alpha_composite(slot_bg_scaled, (bag_x, hb_y))
    draw1.text((bag_x + 8, hb_y + 6), "BAG", fill=(95, 52, 22, 255))
    draw1.text((bag_x + 8, hb_y + 22), "[ I ]", fill=(210, 40, 30, 255))

    view1.save('scratch/batch4_hotbar_gameplay.png')
    print("Saved scratch/batch4_hotbar_gameplay.png")

    # =========================================================================
    # VIEW 2: ENLARGED INVENTORY WINDOW (STARDEW VALLEY CHARACTER CARD REFERENCE)
    # =========================================================================
    view2 = base_grove.copy()
    dim = Image.new('RGBA', (960, 540), (0, 0, 0, 120))
    view2.alpha_composite(dim)
    draw2 = ImageDraw.Draw(view2, 'RGBA')

    # Big 580x370 Window (matching Stardew reference proportion)
    pw, ph = 580, 370
    px = int((960 - pw) / 2)
    py = int((540 - ph) / 2)

    # Window background (warm wood border with parchment body)
    draw2.rectangle([px, py, px + pw, py + ph], fill=(235, 205, 155, 255), outline=(95, 52, 22, 255), width=6)
    draw2.rectangle([px + 6, py + 6, px + pw - 6, py + ph - 6], outline=(155, 105, 55, 255), width=2)

    # Top Tabs (Inventory active)
    draw2.rectangle([px + 20, py - 20, px + 120, py], fill=(235, 205, 155, 255), outline=(95, 52, 22, 255), width=3)
    draw2.text((px + 32, py - 16), "INVENTORY", fill=(95, 52, 22, 255))

    draw2.rectangle([px + 130, py - 18, px + 220, py], fill=(175, 135, 95, 255), outline=(95, 52, 22, 255), width=2)
    draw2.text((px + 142, py - 14), "SURVIVAL", fill=(240, 230, 215, 255))

    draw2.rectangle([px + 230, py - 18, px + 330, py], fill=(175, 135, 95, 255), outline=(95, 52, 22, 255), width=2)
    draw2.text((px + 242, py - 14), "ISLAND MAP", fill=(240, 230, 215, 255))

    # Close button [X]
    cb_scaled = close_btn.resize((26, 26), Image.Resampling.NEAREST)
    view2.alpha_composite(cb_scaled, (px + pw - 34, py + 10))

    # Header label
    draw2.text((px + 20, py + 12), "HOTBAR (ROW 1) & BACKPACK (ROWS 2-3)", fill=(95, 52, 22, 255))

    # 3 Rows of 12 Slots
    inv_slot_w, inv_slot_h = 38, 38
    inv_spacing = 4
    inv_slot_bg = slot_bg.resize((inv_slot_w, inv_slot_h), Image.Resampling.NEAREST)

    start_gx = px + int((pw - (12 * inv_slot_w + 11 * inv_spacing)) / 2)
    start_gy = py + 34

    for r in range(3):
        for c in range(12):
            idx = r * 12 + c
            sx = start_gx + c * (inv_slot_w + inv_spacing)
            sy = start_gy + r * (inv_slot_h + inv_spacing)
            view2.alpha_composite(inv_slot_bg, (sx, sy))

            # Row 1 red numbers
            if r == 0:
                draw2.text((sx + 2, sy + 1), keys[c], fill=(210, 40, 30, 255))

            # Items inside
            if idx < len(hotbar_items) and hotbar_items[idx][0]:
                it_sp, q = hotbar_items[idx]
                ic = it_sp.resize((26, 26), Image.Resampling.NEAREST)
                view2.alpha_composite(ic, (sx + 6, sy + 6))
                if q:
                    draw2.text((sx + 22, sy + 22), str(q), fill=(10, 10, 10, 255))
                    draw2.text((sx + 21, sy + 21), str(q), fill=(255, 255, 255, 255))

    # Horizontal wood dividing line
    div_y = start_gy + 3 * (inv_slot_h + inv_spacing) + 8
    draw2.rectangle([px + 16, div_y, px + pw - 16, div_y + 3], fill=(125, 75, 35, 255))

    # Bottom Survivor Profile Card (matching Stardew reference picture)
    card_y = div_y + 12

    # Survivor Portrait Frame
    draw2.rectangle([px + 24, card_y, px + 120, card_y + 120], fill=(215, 175, 120, 255), outline=(95, 52, 22, 255), width=3)
    # Inner portrait canvas
    draw2.rectangle([px + 32, card_y + 8, px + 112, card_y + 92], fill=(95, 145, 95, 255), outline=(65, 105, 65, 255), width=2)
    # Silhouette
    draw2.ellipse([px + 56, card_y + 20, px + 88, card_y + 52], fill=(245, 215, 175, 255)) # Head
    draw2.rectangle([px + 48, card_y + 52, px + 96, card_y + 88], fill=(60, 90, 160, 255))  # Blue overalls
    draw2.text((px + 44, card_y + 98), "SURVIVOR", fill=(95, 52, 22, 255))

    # Survivor details on the right
    info_x = px + 140
    draw2.text((info_x, card_y + 4), "STRANDED ISLAND", fill=(95, 52, 22, 255))
    draw2.text((info_x, card_y + 30), "Camp: Tropical Coastline Sanctuary", fill=(125, 75, 35, 255))
    draw2.text((info_x, card_y + 52), "Storage: 36 Total Slots (12 Hotbar + 24 Backpack)", fill=(125, 75, 35, 255))
    draw2.text((info_x, card_y + 74), "Equipped Tool: [Stone Axe]", fill=(40, 120, 40, 255))
    draw2.text((info_x, card_y + 96), "Day 1 - Spring, Year 1", fill=(125, 75, 35, 255))

    # Trash Can on far right
    draw2.rectangle([px + pw - 64, card_y + 20, px + pw - 20, card_y + 80], fill=(195, 155, 105, 255), outline=(95, 52, 22, 255), width=2)
    draw2.text((px + pw - 58, card_y + 35), "TRASH", fill=(95, 52, 22, 255))
    draw2.text((px + pw - 56, card_y + 55), "[Drop]", fill=(125, 75, 35, 255))

    # Tooltip demonstration
    tip_x, tip_y = px + 40, start_gy + 70
    draw2.rectangle([tip_x, tip_y, tip_x + 230, tip_y + 50], fill=(30, 20, 10, 245), outline=(215, 165, 85, 255), width=2)
    draw2.text((tip_x + 10, tip_y + 6), "Stone Axe", fill=(255, 215, 0, 255))
    draw2.text((tip_x + 10, tip_y + 26), "Chipped flint axe. Fells island trees.", fill=(240, 240, 230, 255))

    view2.save('scratch/batch4_inventory_window.png')
    print("Saved scratch/batch4_inventory_window.png")

    # =========================================================================
    # VIEW 3: INVENTORY FULL SAFEGUARD TOAST
    # =========================================================================
    view3 = view1.copy()
    draw3 = ImageDraw.Draw(view3, 'RGBA')
    # Big, bold, centered Inventory Full toast
    fx0, fy0, fx1, fy1 = 280, 140, 680, 194
    draw3.rectangle([fx0, fy0, fx1, fy1], fill=(190, 45, 40, 240), outline=(255, 180, 180, 255), width=3)
    draw3.text((fx0 + 130, fy0 + 16), "Inventory Full", fill=(255, 255, 255, 255))
    view3.save('scratch/batch4_inventory_full_safeguard.png')
    print("Saved scratch/batch4_inventory_full_safeguard.png")

if __name__ == '__main__':
    render_batch4_previews()
