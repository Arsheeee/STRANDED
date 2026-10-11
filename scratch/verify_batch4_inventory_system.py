import os
from PIL import Image, ImageDraw, ImageFont

def render_batch4_previews():
    base_grove = Image.open('scratch/updated_forest_grove.png').convert('RGBA')
    
    # Load UI elements
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

    # Scaled slot size: 36x36
    slot_w, slot_h = 36, 36
    spacing = 3

    # =========================================================================
    # VIEW 1: IN-GAME GAMEPLAY WITH ACTIVE HOTBAR (Stardew Style)
    # =========================================================================
    view1 = base_grove.copy()
    draw1 = ImageDraw.Draw(view1, 'RGBA')

    # Top-Left Tracker
    draw1.rectangle([15, 15, 410, 105], fill=(15, 20, 25, 225), outline=(90, 115, 135, 255), width=2)
    draw1.text((27, 23), "STRANDED - Inventory & Tool System [BATCH 4]", fill=(255, 215, 0, 255))
    draw1.text((27, 43), "Wood: 12   Stone: 8   Fiber: 4   Berries: 6   Coconut: 2", fill=(230, 230, 230, 255))
    draw1.text((27, 63), "Equipped: [Stone Axe]   Hotbar: 1-9,0,-,= | Bag: 'I'", fill=(0, 255, 255, 255))
    draw1.text((27, 83), "Atomic Resource Collection & 36-Slot Backpack Active", fill=(140, 185, 140, 255))

    # Context Prompt above hotbar
    px0, py0, px1, py1 = 300, 420, 660, 456
    draw1.rectangle([px0, py0, px1, py1], fill=(10, 15, 20, 235), outline=(0, 255, 200, 255), width=2)
    draw1.text((px0 + 35, py0 + 10), "[E] Harvest Tropical Tree [Stone Axe]", fill=(255, 255, 255, 255))

    # Bottom Hotbar (12 slots)
    total_hb_w = 12 * slot_w + 11 * spacing
    hb_x = int((960 - total_hb_w) / 2)
    hb_y = 540 - slot_h - 14

    # Hotbar wooden backplate
    draw1.rectangle([hb_x - 6, hb_y - 6, hb_x + total_hb_w + 6, hb_y + slot_h + 6], fill=(45, 26, 12, 235), outline=(95, 52, 22, 255), width=2)

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

    key_labels = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "="]

    for i in range(12):
        sx = hb_x + i * (slot_w + spacing)
        sy = hb_y
        view1.paste(slot_bg, (sx, sy), slot_bg)
        
        # Slot number label
        draw1.text((sx + 3, sy + 2), key_labels[i], fill=(115, 70, 35, 255))

        item_sp, qty = hotbar_items[i]
        if item_sp:
            # Scaled to 24x24 inside 36x36 slot
            scaled_item = item_sp.resize((24, 24), Image.Resampling.NEAREST)
            view1.paste(scaled_item, (sx + 6, sy + 6), scaled_item)
            if qty is not None:
                draw1.text((sx + slot_w - 14, sy + slot_h - 13), str(qty), fill=(255, 255, 255, 255))

        # Active selection outline on slot 0
        if i == 0:
            view1.paste(slot_sel, (sx - 2, sy - 2), slot_sel)

    view1.save('scratch/batch4_hotbar_gameplay.png')
    print("Saved scratch/batch4_hotbar_gameplay.png")

    # =========================================================================
    # VIEW 2: FULL INVENTORY GRID WINDOW (3 rows x 12 columns = 36 slots)
    # =========================================================================
    view2 = base_grove.copy()
    # Dark semi-transparent backdrop
    dim = Image.new('RGBA', (960, 540), (0, 0, 0, 110))
    view2 = Image.alpha_composite(view2, dim)
    draw2 = ImageDraw.Draw(view2, 'RGBA')

    # Inventory Panel: 500x230 centered
    pw, ph = 500, 230
    px = int((960 - pw) / 2)
    py = int((540 - ph) / 2)

    scaled_panel = panel_bg.resize((pw, ph), Image.Resampling.NEAREST)
    view2.paste(scaled_panel, (px, py), scaled_panel)

    # Title & Section Headers
    draw2.text((px + 22, py + 14), "INVENTORY", fill=(80, 45, 18, 255))
    draw2.text((px + 22, py + 36), "Row 1: Hotbar | Rows 2-3: Backpack", fill=(120, 80, 45, 255))
    
    # Close button [X]
    view2.paste(close_btn, (px + pw - 34, py + 12), close_btn)

    # 3x12 Grid
    grid_x = px + 20
    grid_y = py + 56

    backpack_items = hotbar_items + [
        (sp_wood, 99), (sp_stone, 45), (sp_fiber, 20), (None, None), (None, None), (None, None),
        (None, None), (None, None), (None, None), (None, None), (None, None), (None, None),
        (None, None), (None, None), (None, None), (None, None), (None, None), (None, None),
        (None, None), (None, None), (None, None), (None, None), (None, None), (None, None)
    ]

    for r in range(3):
        for c in range(12):
            idx = r * 12 + c
            sx = grid_x + c * (slot_w + spacing)
            sy = grid_y + r * (slot_h + spacing)
            view2.paste(slot_bg, (sx, sy), slot_bg)

            item_sp, qty = backpack_items[idx]
            if item_sp:
                scaled_item = item_sp.resize((24, 24), Image.Resampling.NEAREST)
                view2.paste(scaled_item, (sx + 6, sy + 6), scaled_item)
                if qty is not None:
                    draw2.text((sx + slot_w - 14, sy + slot_h - 13), str(qty), fill=(255, 255, 255, 255))

    # Tooltip for hovered slot (Axe)
    tip_x, tip_y = grid_x + 10, grid_y + 40
    draw2.rectangle([tip_x, tip_y, tip_x + 220, tip_y + 44], fill=(25, 18, 10, 235), outline=(130, 85, 45, 255), width=2)
    draw2.text((tip_x + 8, tip_y + 6), "Stone Axe", fill=(255, 215, 120, 255))
    draw2.text((tip_x + 8, tip_y + 24), "Chipped flint axe. Fells island trees.", fill=(210, 195, 175, 255))

    view2.save('scratch/batch4_inventory_window.png')
    print("Saved scratch/batch4_inventory_window.png")

    # =========================================================================
    # VIEW 3: INVENTORY FULL SAFEGUARD NOTIFICATION
    # =========================================================================
    view3 = view1.copy()
    draw3 = ImageDraw.Draw(view3, 'RGBA')
    # Center toast: "Inventory Full"
    tx0, ty0, tx1, ty1 = 340, 130, 620, 168
    draw3.rectangle([tx0, ty0, tx1, ty1], fill=(180, 40, 40, 240), outline=(255, 90, 80, 255), width=2)
    draw3.text((tx0 + 55, ty0 + 10), "Inventory Full", fill=(255, 255, 255, 255))
    view3.save('scratch/batch4_inventory_full_safeguard.png')
    print("Saved scratch/batch4_inventory_full_safeguard.png")

if __name__ == '__main__':
    render_batch4_previews()
