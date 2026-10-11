import os
import sys
from PIL import Image, ImageDraw, ImageFont

# =============================================================================
# PART 1: LOGIC AND SYSTEM SIMULATION VERIFICATION (38 TEST ASSERTIONS)
# =============================================================================

class MockItemData:
    def __init__(self, id, name, item_type, tool_type, resource_type, max_stack, description):
        self.id = id
        self.name = name
        self.item_type = item_type
        self.tool_type = tool_type
        self.resource_type = resource_type
        self.max_stack = max_stack
        self.description = description

class MockInventorySlot:
    def __init__(self):
        self.item = None
        self.quantity = 0

    @property
    def is_empty(self):
        return self.item is None or self.quantity <= 0

    def can_stack_with(self, item):
        return not self.is_empty and self.item.id == item.id and self.quantity < self.item.max_stack

class MockInventory:
    def __init__(self, total_slots=36):
        self.total_slots = total_slots
        self.slots = [MockInventorySlot() for _ in range(total_slots)]

    def get_item_count(self, item):
        count = 0
        for s in self.slots:
            if not s.is_empty and s.item.id == item.id:
                count += s.quantity
        return count

    def add_item(self, item, quantity=1):
        rem = quantity
        # 1. Fill existing stacks
        for s in self.slots:
            if s.can_stack_with(item):
                space = item.max_stack - s.quantity
                added = min(space, rem)
                s.quantity += added
                rem -= added
                if rem <= 0:
                    return 0
        # 2. Place in empty slots
        for s in self.slots:
            if s.is_empty:
                placed = min(item.max_stack, rem)
                s.item = item
                s.quantity = placed
                rem -= placed
                if rem <= 0:
                    return 0
        return rem

    def remove_item(self, item, quantity=1):
        rem = quantity
        for i in reversed(range(self.total_slots)):
            s = self.slots[i]
            if not s.is_empty and s.item.id == item.id:
                take = min(s.quantity, rem)
                s.quantity -= take
                rem -= take
                if s.quantity <= 0:
                    s.item = None
                    s.quantity = 0
                if rem <= 0:
                    return True
        return rem == 0

    def has_empty_slot(self):
        return any(s.is_empty for s in self.slots)

    def can_fit_output(self, item, quantity):
        # Check stackable space or empty slot
        rem = quantity
        for s in self.slots:
            if s.can_stack_with(item):
                rem -= (item.max_stack - s.quantity)
                if rem <= 0:
                    return True
        empty_count = sum(1 for s in self.slots if s.is_empty)
        slots_needed = (rem + item.max_stack - 1) // item.max_stack
        return empty_count >= slots_needed

class MockRecipeIngredient:
    def __init__(self, item, count):
        self.item = item
        self.count = count

class MockCraftingRecipe:
    def __init__(self, id, name, output_item, output_qty, ingredients, desc):
        self.id = id
        self.name = name
        self.output_item = output_item
        self.output_qty = output_qty
        self.ingredients = ingredients
        self.desc = desc

class MockCraftingManager:
    def can_craft(self, recipe, inventory):
        # 1. Check all materials
        missing = []
        for ing in recipe.ingredients:
            has = inventory.get_item_count(ing.item)
            if has < ing.count:
                missing.append(f"{ing.item.name} x{ing.count - has}")
        if missing:
            return False, f"Missing {', '.join(missing)}"

        # 2. Check inventory capacity (atomic)
        if not inventory.can_fit_output(recipe.output_item, recipe.output_qty):
            return False, f"Inventory Full - No room for {recipe.output_item.name}"

        return True, "Ready to craft"

    def craft(self, recipe, inventory):
        can, msg = self.can_craft(recipe, inventory)
        if not can:
            return False, msg

        # Deduct ingredients
        for ing in recipe.ingredients:
            inventory.remove_item(ing.item, ing.count)

        # Add output item
        inventory.add_item(recipe.output_item, recipe.output_qty)
        return True, f"{recipe.name} crafted!"

def run_all_tests():
    print("=====================================================================")
    print("RUNNING STRANDED BATCH 5: CRAFTING SYSTEM VERIFICATION TESTS")
    print("=====================================================================")

    # Setup Item catalog
    wood = MockItemData("item_wood", "Wood", "Resource", "None", "Wood", 99, "Timber")
    stone = MockItemData("item_stone", "Stone", "Resource", "None", "Stone", 99, "Stone")
    fiber = MockItemData("item_fiber", "Fiber", "Resource", "None", "Fiber", 99, "Plant fibers")
    knife = MockItemData("tool_knife", "Stone Knife", "Tool", "StoneKnife", "None", 1, "Sharp knife")
    axe = MockItemData("tool_axe", "Stone Axe", "Tool", "StoneAxe", "None", 1, "Stone axe")
    pick = MockItemData("tool_pick", "Stone Pickaxe", "Tool", "StonePickaxe", "None", 1, "Stone pickaxe")
    rod = MockItemData("tool_rod", "Fishing Rod", "Tool", "FishingRod", "None", 1, "Fishing rod")

    # Setup 4 Primitive Recipes
    recipes = [
        MockCraftingRecipe("recipe_stone_knife", "Stone Knife", knife, 1, [MockRecipeIngredient(stone, 2), MockRecipeIngredient(fiber, 1)], "Flint blade"),
        MockCraftingRecipe("recipe_stone_axe", "Stone Axe", axe, 1, [MockRecipeIngredient(stone, 3), MockRecipeIngredient(wood, 2), MockRecipeIngredient(fiber, 1)], "Timber axe"),
        MockCraftingRecipe("recipe_stone_pickaxe", "Stone Pickaxe", pick, 1, [MockRecipeIngredient(stone, 3), MockRecipeIngredient(wood, 2), MockRecipeIngredient(fiber, 2)], "Heavy pick"),
        MockCraftingRecipe("recipe_fishing_rod", "Fishing Rod", rod, 1, [MockRecipeIngredient(wood, 3), MockRecipeIngredient(fiber, 2)], "Fishing rod")
    ]

    cm = MockCraftingManager()
    passed = 0

    # Test 1-4: Recipe database integrity
    assert len(recipes) == 4; passed += 1
    assert recipes[0].name == "Stone Knife" and len(recipes[0].ingredients) == 2; passed += 1
    assert recipes[1].name == "Stone Axe" and len(recipes[1].ingredients) == 3; passed += 1
    assert recipes[2].name == "Stone Pickaxe" and len(recipes[2].ingredients) == 3; passed += 1
    assert recipes[3].name == "Fishing Rod" and len(recipes[3].ingredients) == 2; passed += 1
    print(f"[{passed}/38] Recipe registry definitions verified")

    # Test 5: Strictly primitive materials check
    all_ing_names = {ing.item.name for r in recipes for ing in r.ingredients}
    assert all_ing_names == {"Wood", "Stone", "Fiber"}; passed += 1
    assert "Iron" not in all_ing_names and "Steel" not in all_ing_names and "Metal" not in all_ing_names; passed += 1
    print(f"[{passed}/38] Primitive materials constraint verified (NO metal/iron/steel/ore)")

    # Test 7-10: Empty inventory cannot craft any recipe
    inv = MockInventory(36)
    for r in recipes:
        can, msg = cm.can_craft(r, inv)
        assert not can and "Missing" in msg; passed += 1
    print(f"[{passed}/38] Empty inventory rejection verified")

    # Test 11-14: Partial materials rejection & zero consumption
    inv.add_item(stone, 1) # Knife needs stone 2, fiber 1
    can, msg = cm.can_craft(recipes[0], inv)
    assert not can and "Stone x1" in msg and "Fiber x1" in msg; passed += 1
    success, res_msg = cm.craft(recipes[0], inv)
    assert not success and inv.get_item_count(stone) == 1; passed += 1 # Zero materials consumed
    print(f"[{passed}/38] Partial materials rejection & zero consumption verified")

    # Test 13-17: Successful Stone Knife craft
    inv.add_item(stone, 1) # Stone now 2
    inv.add_item(fiber, 1) # Fiber now 1
    can, msg = cm.can_craft(recipes[0], inv)
    assert can; passed += 1
    success, res_msg = cm.craft(recipes[0], inv)
    assert success and "Stone Knife crafted!" in res_msg; passed += 1
    assert inv.get_item_count(stone) == 0; passed += 1
    assert inv.get_item_count(fiber) == 0; passed += 1
    assert inv.get_item_count(knife) == 1; passed += 1
    print(f"[{passed}/38] Stone Knife atomic crafting verified")

    # Test 18-23: Successful Stone Axe craft
    inv.add_item(wood, 10)
    inv.add_item(stone, 10)
    inv.add_item(fiber, 10)
    can, msg = cm.can_craft(recipes[1], inv)
    assert can; passed += 1
    success, res_msg = cm.craft(recipes[1], inv)
    assert success; passed += 1
    assert inv.get_item_count(wood) == 8; passed += 1  # 10 - 2 = 8
    assert inv.get_item_count(stone) == 7; passed += 1 # 10 - 3 = 7
    assert inv.get_item_count(fiber) == 9; passed += 1 # 10 - 1 = 9
    assert inv.get_item_count(axe) == 1; passed += 1
    print(f"[{passed}/38] Stone Axe atomic crafting verified")

    # Test 24-28: Successful Stone Pickaxe craft
    can, msg = cm.can_craft(recipes[2], inv)
    assert can; passed += 1
    success, res_msg = cm.craft(recipes[2], inv)
    assert success; passed += 1
    assert inv.get_item_count(wood) == 6; passed += 1  # 8 - 2 = 6
    assert inv.get_item_count(stone) == 4; passed += 1 # 7 - 3 = 4
    assert inv.get_item_count(fiber) == 7; passed += 1 # 9 - 2 = 7
    assert inv.get_item_count(pick) == 1; passed += 1
    print(f"[{passed}/38] Stone Pickaxe atomic crafting verified")

    # Test 29-33: Successful Fishing Rod craft
    can, msg = cm.can_craft(recipes[3], inv)
    assert can; passed += 1
    success, res_msg = cm.craft(recipes[3], inv)
    assert success; passed += 1
    assert inv.get_item_count(wood) == 3; passed += 1  # 6 - 3 = 3
    assert inv.get_item_count(fiber) == 5; passed += 1 # 7 - 2 = 5
    assert inv.get_item_count(rod) == 1; passed += 1
    print(f"[{passed}/38] Fishing Rod atomic crafting verified")

    # Test 34-38: Full inventory capacity safeguard
    full_inv = MockInventory(36)
    filler = MockItemData("item_berry", "Berries", "Resource", "None", "Berries", 1, "Berry")
    for _ in range(36):
        full_inv.add_item(filler, 1) # Fill all 36 slots completely
    full_inv.slots[0].item = wood; full_inv.slots[0].quantity = 99
    full_inv.slots[1].item = fiber; full_inv.slots[1].quantity = 99
    # Inventory is full: 36 slots used. Output (Fishing Rod, max stack 1) cannot fit.
    can, msg = cm.can_craft(recipes[3], full_inv)
    assert not can and "Inventory Full" in msg; passed += 1
    initial_wood = full_inv.get_item_count(wood)
    initial_fiber = full_inv.get_item_count(fiber)
    success, res_msg = cm.craft(recipes[3], full_inv)
    assert not success; passed += 1
    assert full_inv.get_item_count(wood) == initial_wood; passed += 1 # Zero consumed!
    assert full_inv.get_item_count(fiber) == initial_fiber; passed += 1 # Zero consumed!
    assert full_inv.get_item_count(rod) == 0; passed += 1
    print(f"[{passed}/38] Inventory capacity safeguard verified (Zero materials consumed on full bag)")

    print(f"ALL {passed}/38 TESTS PASSED WITH 100% SUCCESS!\n")

# =============================================================================
# PART 2: VISUAL PREVIEW RENDERING (VERY VERY BIG UI LAYOUTS)
# =============================================================================

def render_previews():
    base_grove = Image.open('scratch/updated_forest_grove.png').convert('RGBA')
    
    # UI Textures
    slot_bg = Image.open('Assets/Art/UI/ui_slot_background.png').convert('RGBA')
    slot_sel = Image.open('Assets/Art/UI/ui_slot_selected.png').convert('RGBA')
    close_btn = Image.open('Assets/Art/UI/ui_close_button.png').convert('RGBA')

    # Item & Tool Icons
    sp_axe = Image.open('Assets/Art/Environment/Items/tool_stone_axe.png').convert('RGBA')
    sp_pick = Image.open('Assets/Art/Environment/Items/tool_stone_pickaxe.png').convert('RGBA')
    sp_knife = Image.open('Assets/Art/Environment/Items/tool_stone_knife.png').convert('RGBA')
    sp_rod = Image.open('Assets/Art/Environment/Items/tool_fishing_rod.png').convert('RGBA')
    sp_wood = Image.open('Assets/Art/Environment/Items/item_wood.png').convert('RGBA')
    sp_stone = Image.open('Assets/Art/Environment/Items/item_stone.png').convert('RGBA')
    sp_fiber = Image.open('Assets/Art/Environment/Items/item_fiber.png').convert('RGBA')
    sp_berries = Image.open('Assets/Art/Environment/Items/item_berry.png').convert('RGBA')
    sp_coconut = Image.open('Assets/Art/Environment/Items/item_coconut.png').convert('RGBA')

    # Dimensions for 960x540 preview representation (equivalent to 1920x1080 scaled)
    # Hotbar slot size: 48x48 (Very Very Big), 12 slots + BAG + CRAFT
    hb_slot_size = 46
    hb_spacing = 4
    total_slots = 14 # 12 + BAG + CRAFT
    total_hb_w = total_slots * hb_slot_size + (total_slots - 1) * hb_spacing
    hb_x = int((960 - total_hb_w) / 2)
    hb_y = 540 - hb_slot_size - 14

    slot_bg_hb = slot_bg.resize((hb_slot_size, hb_slot_size), Image.Resampling.NEAREST)
    slot_sel_hb = slot_sel.resize((hb_slot_size + 4, hb_slot_size + 4), Image.Resampling.NEAREST)

    # -------------------------------------------------------------------------
    # VIEW 1: ENLARGED GAMEPLAY HUD & HOTBAR (WITH BAG AND CRAFT BUTTONS)
    # -------------------------------------------------------------------------
    view1 = base_grove.copy()
    draw1 = ImageDraw.Draw(view1, 'RGBA')

    # Top-Left Tracker (VERY VERY BIG)
    draw1.rectangle([16, 14, 520, 118], fill=(16, 22, 28, 235), outline=(90, 120, 145, 255), width=2)
    draw1.text((28, 22), "[STRANDED BATCH 5: CRAFTING SYSTEM & UI]", fill=(255, 215, 0, 255))
    draw1.text((28, 46), "Wood: 12   Stone: 8   Fiber: 4   Berries: 6   Coconut: 2", fill=(235, 235, 235, 255))
    draw1.text((28, 68), "Equipped: [Stone Axe]   Controls: 1-9,0,-,= | Bag: 'I' | Craft: 'C'", fill=(0, 240, 255, 255))
    draw1.text((28, 90), "Bench: Primitive Tools (Knife, Axe, Pickaxe, Fishing Rod)", fill=(150, 215, 150, 255))

    # Center Context Prompt
    px0, py0, px1, py1 = 250, 412, 710, 456
    draw1.rectangle([px0, py0, px1, py1], fill=(12, 20, 24, 240), outline=(0, 255, 190, 255), width=2)
    draw1.text((px0 + 55, py0 + 13), "[E] Harvest Tropical Tree [Stone Axe]", fill=(120, 255, 180, 255))

    # Hotbar Wooden Container
    draw1.rectangle([hb_x - 8, hb_y - 8, hb_x + total_hb_w + 8, hb_y + hb_slot_size + 8], fill=(42, 24, 10, 245), outline=(105, 58, 25, 255), width=2)

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

    # Draw 12 hotbar slots
    for i in range(12):
        sx = hb_x + i * (hb_slot_size + hb_spacing)
        sy = hb_y
        view1.alpha_composite(slot_bg_hb, (sx, sy))

        item_sp, qty = hotbar_items[i]
        if item_sp:
            icon_sc = item_sp.resize((34, 34), Image.Resampling.NEAREST)
            view1.alpha_composite(icon_sc, (sx + 6, sy + 6))

        draw1.text((sx + 4, sy + 2), keys[i], fill=(215, 45, 35, 255))
        if qty:
            draw1.text((sx + 26, sy + 28), str(qty), fill=(10, 10, 10, 255))
            draw1.text((sx + 25, sy + 27), str(qty), fill=(255, 255, 255, 255))

        if i == 0:
            view1.alpha_composite(slot_sel_hb, (sx - 2, sy - 2))

    # Slot 13: Clickable BAG [I]
    bag_x = hb_x + 12 * (hb_slot_size + hb_spacing)
    view1.alpha_composite(slot_bg_hb, (bag_x, hb_y))
    draw1.text((bag_x + 10, hb_y + 8), "BAG", fill=(95, 52, 22, 255))
    draw1.text((bag_x + 10, hb_y + 26), "[ I ]", fill=(215, 45, 35, 255))

    # Slot 14: Clickable CRAFT [C]
    craft_btn_x = hb_x + 13 * (hb_slot_size + hb_spacing)
    view1.alpha_composite(slot_bg_hb, (craft_btn_x, hb_y))
    draw1.text((craft_btn_x + 4, hb_y + 8), "CRAFT", fill=(95, 52, 22, 255))
    draw1.text((craft_btn_x + 8, hb_y + 26), "[ C ]", fill=(215, 45, 35, 255))

    view1.save('scratch/batch5_hotbar_gameplay_enlarged.png')
    print("Saved scratch/batch5_hotbar_gameplay_enlarged.png")

    # -------------------------------------------------------------------------
    # VIEW 2: CRAFTING MENU WINDOW (1120x720 PROPORTIONS ON SCREEN)
    # -------------------------------------------------------------------------
    view2 = base_grove.copy()
    dim = Image.new('RGBA', (960, 540), (0, 0, 0, 130))
    view2.alpha_composite(dim)
    draw2 = ImageDraw.Draw(view2, 'RGBA')

    # Crafting Window (640x410 on 960x540 canvas - Very Very Big)
    cw, ch = 640, 410
    cx = int((960 - cw) / 2)
    cy = int((540 - ch) / 2)

    # Window background & parchment
    draw2.rectangle([cx, cy, cx + cw, cy + ch], fill=(235, 205, 155, 255), outline=(95, 52, 22, 255), width=6)
    draw2.rectangle([cx + 6, cy + 6, cx + cw - 6, cy + ch - 6], outline=(155, 105, 55, 255), width=2)

    # Top Tabs
    # Inactive INVENTORY tab
    draw2.rectangle([cx + 24, cy - 22, cx + 124, cy], fill=(175, 135, 95, 255), outline=(95, 52, 22, 255), width=2)
    draw2.text((cx + 36, cy - 18), "INVENTORY", fill=(240, 230, 215, 255))

    # Active CRAFTING tab
    draw2.rectangle([cx + 132, cy - 24, cx + 236, cy], fill=(235, 205, 155, 255), outline=(95, 52, 22, 255), width=3)
    draw2.text((cx + 148, cy - 18), "CRAFTING", fill=(95, 52, 22, 255))

    # Close button [X]
    cb_scaled = close_btn.resize((26, 26), Image.Resampling.NEAREST)
    view2.alpha_composite(cb_scaled, (cx + cw - 36, cy + 10))

    # Header title
    draw2.text((cx + 24, cy + 14), "PRIMITIVE CRAFTING BENCH", fill=(95, 52, 22, 255))

    # LEFT COLUMN: RECIPES (Stone Knife, Stone Axe, Stone Pickaxe, Fishing Rod)
    col_w = 230
    draw2.text((cx + 24, cy + 42), "AVAILABLE RECIPES", fill=(125, 75, 35, 255))

    recipe_cards = [
        ("Stone Axe", sp_axe, "Stone x3, Wood x2, Fiber x1", True, True),      # Selected & Ready
        ("Stone Knife", sp_knife, "Stone x2, Fiber x1", True, False),           # Ready
        ("Stone Pickaxe", sp_pick, "Stone x3, Wood x2, Fiber x2", True, False), # Ready
        ("Fishing Rod", sp_rod, "Wood x3, Fiber x2", True, False)               # Ready
    ]

    card_y = cy + 62
    for name, icon, ings, can_c, is_sel in recipe_cards:
        # Card box
        border_col = (200, 140, 40, 255) if is_sel else (145, 95, 45, 255)
        bg_col = (245, 225, 185, 255) if is_sel else (225, 195, 145, 255)
        draw2.rectangle([cx + 24, card_y, cx + 24 + col_w, card_y + 74], fill=bg_col, outline=border_col, width=2 if is_sel else 1)

        # Icon
        ic_scaled = icon.resize((36, 36), Image.Resampling.NEAREST)
        view2.alpha_composite(ic_scaled, (cx + 30, card_y + 18))

        # Title
        draw2.text((cx + 72, card_y + 10), name, fill=(95, 52, 22, 255))
        # Materials summary
        draw2.text((cx + 72, card_y + 30), ings, fill=(125, 75, 35, 255))
        # Badge
        draw2.text((cx + 72, card_y + 50), "[READY TO CRAFT]", fill=(30, 130, 40, 255))

        card_y += 82

    # RIGHT COLUMN: RECIPE DETAILS & CRAFT BUTTON
    det_x = cx + col_w + 38
    det_w = cw - (col_w + 58)
    draw2.rectangle([det_x, cy + 42, det_x + det_w, cy + ch - 16], fill=(225, 195, 145, 255), outline=(145, 95, 45, 255), width=2)

    # Big Icon and Header
    big_axe = sp_axe.resize((56, 56), Image.Resampling.NEAREST)
    view2.alpha_composite(big_axe, (det_x + 16, cy + 54))
    draw2.text((det_x + 82, cy + 56), "STONE AXE", fill=(95, 52, 22, 255))
    draw2.text((det_x + 82, cy + 78), "Chipped stone wedge tied to a sturdy timber haft.\nFells island trees to harvest wood logs.", fill=(115, 65, 30, 255))

    # Divider
    draw2.rectangle([det_x + 14, cy + 124, det_x + det_w - 14, cy + 126], fill=(145, 95, 45, 255))

    # Required Materials list
    draw2.text((det_x + 16, cy + 134), "REQUIRED MATERIALS", fill=(95, 52, 22, 255))

    # Ingredient 1: Stone
    sp_stone_sc = sp_stone.resize((30, 30), Image.Resampling.NEAREST)
    view2.alpha_composite(sp_stone_sc, (det_x + 18, cy + 160))
    draw2.text((det_x + 56, cy + 168), "Stone:  8 / 3", fill=(95, 52, 22, 255))
    draw2.text((det_x + 180, cy + 168), "[SATISFIED]", fill=(30, 130, 40, 255))

    # Ingredient 2: Wood
    sp_wood_sc = sp_wood.resize((30, 30), Image.Resampling.NEAREST)
    view2.alpha_composite(sp_wood_sc, (det_x + 18, cy + 200))
    draw2.text((det_x + 56, cy + 208), "Wood:  12 / 2", fill=(95, 52, 22, 255))
    draw2.text((det_x + 180, cy + 208), "[SATISFIED]", fill=(30, 130, 40, 255))

    # Ingredient 3: Fiber
    sp_fiber_sc = sp_fiber.resize((30, 30), Image.Resampling.NEAREST)
    view2.alpha_composite(sp_fiber_sc, (det_x + 18, cy + 240))
    draw2.text((det_x + 56, cy + 248), "Fiber:  4 / 1", fill=(95, 52, 22, 255))
    draw2.text((det_x + 180, cy + 248), "[SATISFIED]", fill=(30, 130, 40, 255))

    # Craftability banner
    draw2.rectangle([det_x + 16, cy + 288, det_x + det_w - 16, cy + 322], fill=(235, 215, 175, 255), outline=(95, 52, 22, 255), width=2)
    draw2.text((det_x + 38, cy + 296), "CRAFTABLE: ALL MATERIALS READY", fill=(30, 130, 40, 255))

    # Big CRAFT Button
    draw2.rectangle([det_x + 16, cy + 332, det_x + det_w - 16, cy + 384], fill=(75, 135, 65, 255), outline=(45, 95, 40, 255), width=3)
    draw2.text((det_x + 88, cy + 348), "CRAFT STONE AXE", fill=(255, 255, 255, 255))

    view2.save('scratch/batch5_crafting_menu.png')
    print("Saved scratch/batch5_crafting_menu.png")

    # -------------------------------------------------------------------------
    # VIEW 3: INVENTORY WINDOW WITH CRAFTING TAB (VERY VERY BIG)
    # -------------------------------------------------------------------------
    view3 = base_grove.copy()
    view3.alpha_composite(dim)
    draw3 = ImageDraw.Draw(view3, 'RGBA')

    draw3.rectangle([cx, cy, cx + cw, cy + ch], fill=(235, 205, 155, 255), outline=(95, 52, 22, 255), width=6)
    draw3.rectangle([cx + 6, cy + 6, cx + cw - 6, cy + ch - 6], outline=(155, 105, 55, 255), width=2)

    # Active INVENTORY tab
    draw3.rectangle([cx + 24, cy - 24, cx + 128, cy], fill=(235, 205, 155, 255), outline=(95, 52, 22, 255), width=3)
    draw3.text((cx + 36, cy - 18), "INVENTORY", fill=(95, 52, 22, 255))

    # Clickable CRAFTING tab
    draw3.rectangle([cx + 136, cy - 22, cx + 236, cy], fill=(175, 135, 95, 255), outline=(95, 52, 22, 255), width=2)
    draw3.text((cx + 148, cy - 18), "CRAFTING", fill=(240, 230, 215, 255))

    # Close button [X]
    view3.alpha_composite(cb_scaled, (cx + cw - 36, cy + 10))

    # Header label
    draw3.text((cx + 24, cy + 14), "HOTBAR (ROW 1) & BACKPACK (ROWS 2-3)", fill=(95, 52, 22, 255))

    # 3 Rows of 12 Slots (Enlarged to 44x44)
    inv_slot_w, inv_slot_h = 44, 44
    inv_spacing = 4
    inv_slot_bg = slot_bg.resize((inv_slot_w, inv_slot_h), Image.Resampling.NEAREST)

    start_gx = cx + int((cw - (12 * inv_slot_w + 11 * inv_spacing)) / 2)
    start_gy = cy + 42

    for r in range(3):
        for c in range(12):
            idx = r * 12 + c
            sx = start_gx + c * (inv_slot_w + inv_spacing)
            sy = start_gy + r * (inv_slot_h + inv_spacing)
            view3.alpha_composite(inv_slot_bg, (sx, sy))

            if r == 0:
                draw3.text((sx + 3, sy + 2), keys[c], fill=(215, 45, 35, 255))

            if idx < len(hotbar_items) and hotbar_items[idx][0]:
                it_sp, q = hotbar_items[idx]
                ic = it_sp.resize((32, 32), Image.Resampling.NEAREST)
                view3.alpha_composite(ic, (sx + 6, sy + 6))
                if q:
                    draw3.text((sx + 26, sy + 26), str(q), fill=(10, 10, 10, 255))
                    draw3.text((sx + 25, sy + 25), str(q), fill=(255, 255, 255, 255))

    # Divider line
    div_y = start_gy + 3 * (inv_slot_h + inv_spacing) + 10
    draw3.rectangle([cx + 20, div_y, cx + cw - 20, div_y + 3], fill=(125, 75, 35, 255))

    # Survivor Card
    card_y = div_y + 14
    draw3.rectangle([cx + 24, card_y, cx + 130, card_y + 120], fill=(215, 175, 120, 255), outline=(95, 52, 22, 255), width=3)
    draw3.rectangle([cx + 34, card_y + 8, cx + 120, card_y + 92], fill=(95, 145, 95, 255), outline=(65, 105, 65, 255), width=2)
    draw3.ellipse([cx + 62, card_y + 20, cx + 92, card_y + 50], fill=(245, 215, 175, 255))
    draw3.rectangle([cx + 54, card_y + 50, cx + 100, card_y + 88], fill=(60, 90, 160, 255))
    draw3.text((cx + 50, card_y + 98), "SURVIVOR", fill=(95, 52, 22, 255))

    info_x = cx + 150
    draw3.text((info_x, card_y + 4), "STRANDED ISLAND - SURVIVOR'S INVENTORY", fill=(95, 52, 22, 255))
    draw3.text((info_x, card_y + 28), "Camp: Tropical Coastline Sanctuary", fill=(125, 75, 35, 255))
    draw3.text((info_x, card_y + 50), "Storage: 36 Total Slots (12 Hotbar + 24 Backpack)", fill=(125, 75, 35, 255))
    draw3.text((info_x, card_y + 72), "Equipped Tool: [Stone Axe] (Slot 1)", fill=(40, 130, 40, 255))
    draw3.text((info_x, card_y + 94), "Primitive Crafting Bench: Press [C] or Click CRAFTING tab", fill=(125, 75, 35, 255))

    view3.save('scratch/batch5_inventory_window_enlarged.png')
    print("Saved scratch/batch5_inventory_window_enlarged.png")

if __name__ == '__main__':
    run_all_tests()
    render_previews()
