import os
from PIL import Image, ImageDraw, ImageFont

def render_batch8_showcase():
    print("Rendering Batch 8 Showcase Visuals...")

    items_dir = "Assets/Art/Environment/Items"
    plants_dir = "Assets/Art/Environment/Plants"

    def load_spr(filename, scale=4):
        p = os.path.join(items_dir, filename)
        if not os.path.exists(p):
            p = os.path.join(plants_dir, filename)
        if os.path.exists(p):
            im = Image.open(p).convert("RGBA")
            return im.resize((im.width * scale, im.height * scale), Image.NEAREST)
        return Image.new("RGBA", (16 * scale, 16 * scale), (200, 200, 200, 255))

    # 1. Boat Components & Special Materials Grid Showcase
    w, h = 1000, 680
    im = Image.new("RGBA", (w, h), (26, 22, 18, 255))
    d = ImageDraw.Draw(im)

    # Title Banner
    d.rectangle([(0, 0), (w, 64)], fill=(44, 34, 24, 255))
    d.text((24, 18), "STRANDED — BATCH 8: HIERARCHICAL CRAFTING & BOAT COMPONENTS", fill=(245, 215, 160, 255))

    # Columns: Advanced Equipment, Processed Materials, Boat Components
    sections = [
        ("ADVANCED EQUIPMENT", [
            ("item_vines.png", "Vines", "Raw Creeper", "Forest Harvest (Stone Knife)"),
            ("tool_improved_knife.png", "Improved Knife", "Shaping Tool", "Wood x2, Stone x3, Vines x2"),
            ("tool_wooden_mallet.png", "Wooden Mallet", "Assembly Tool", "Wood x4, Vines x2"),
            ("tool_fiber_twister.png", "Fiber Twister", "Cordage Tool", "Wood x3, Fiber x2, Vines x1"),
            ("tool_weaving_frame.png", "Weaving Frame", "Loom Station", "Wood x6, Vines x4, Fiber x2"),
        ]),
        ("PROCESSED MATERIALS", [
            ("item_shaped_wood.png", "Shaped Wood", "x2 Yield", "Wood x2 + Improved Knife"),
            ("item_wooden_pegs.png", "Wooden Pegs", "x4 Yield", "Wood x1 + Improved Knife"),
            ("item_strong_rope.png", "Strong Rope", "Braided Cord", "Fiber x3, Vines x2 + Twister"),
            ("item_reinforced_rope.png", "Reinforced Rope", "Rigging Cord", "Strong Rope x1, Vines x2, Fiber x1"),
            ("item_woven_sailcloth.png", "Woven Sailcloth", "Canvas Fabric", "Fiber x4, Vines x4 + Frame"),
            ("item_reinforced_joints.png", "Reinforced Joints", "Structural Mortise", "Shaped Wood x2, Pegs x2, Rope x1"),
        ]),
        ("BOAT COMPONENTS", [
            ("item_paddle.png", "Paddle", "Navigation", "Shaped Wood x2, Pegs x2, Rope x1"),
            ("item_wind_assembly.png", "Wind Assembly", "Propulsion", "Sailcloth x2, Spars x3, Rope x2, Pegs x4"),
            ("item_rope_binding_kit.png", "Rope Binding Kit", "Lashings", "Strong Rope x2, Reinf Rope x2, Vines x3"),
            ("item_structural_frame.png", "Structural Frame", "Keel & Ribs", "Shaped Wood x4, Pegs x6, Joints x2, Kit x1"),
            ("item_reinforced_hull.png", "Reinforced Hull", "Buoyant Body", "Shaped Wood x6, Joints x4, Kit x1, Rope x3"),
        ])
    ]

    col_w = 310
    for col_idx, (sec_title, items) in enumerate(sections):
        cx = 24 + col_idx * (col_w + 14)
        cy = 84
        d.rectangle([(cx, cy), (cx + col_w, cy + 30)], fill=(55, 42, 28, 255))
        d.text((cx + 12, cy + 8), sec_title, fill=(230, 200, 140, 255))

        item_y = cy + 40
        for icon_file, name, subtitle, recipe in items:
            box_h = 74
            d.rectangle([(cx, item_y), (cx + col_w, item_y + box_h)], fill=(38, 32, 25, 255), outline=(70, 56, 38, 255))
            # Icon
            spr = load_spr(icon_file, scale=3)
            im.paste(spr, (cx + 10, item_y + 13), spr)
            # Text
            d.text((cx + 70, item_y + 10), name, fill=(240, 230, 210, 255))
            d.text((cx + 70, item_y + 30), f"[{subtitle}]", fill=(130, 185, 110, 255))
            d.text((cx + 70, item_y + 48), recipe, fill=(195, 175, 145, 255))
            item_y += box_h + 8

    out_path = "scratch/batch8_boat_components_showcase.png"
    im.save(out_path)
    print(f"Saved: {out_path}")

    # 2. Crafting UI In-Game Parchment Mockup
    ui_w, ui_h = 1120, 720
    im_ui = Image.new("RGBA", (ui_w, ui_h), (218, 198, 162, 255)) # parchment
    d_ui = ImageDraw.Draw(im_ui)

    # Outer border
    d_ui.rectangle([(0, 0), (ui_w-1, ui_h-1)], outline=(72, 44, 20, 255), width=4)

    # Top Tabs
    d_ui.rectangle([(36, 12), (186, 46)], fill=(140, 97, 56, 255))
    d_ui.text((64, 22), "INVENTORY", fill=(225, 210, 185, 255))
    d_ui.rectangle([(194, 12), (344, 46)], fill=(225, 184, 122, 255))
    d_ui.text((228, 22), "CRAFTING", fill=(76, 40, 15, 255))

    # Close button
    d_ui.rectangle([(ui_w - 48, 14), (ui_w - 12, 50)], fill=(185, 45, 45, 255))
    d_ui.text((ui_w - 36, 24), "X", fill=(255, 255, 255, 255))

    # Title
    d_ui.text((36, 56), "PRIMITIVE CRAFTING BENCH", fill=(82, 46, 20, 255))

    # Category Tabs
    cat_names = ["ALL", "TOOLS", "MATERIALS", "BOAT"]
    cat_w = 90
    for idx, cname in enumerate(cat_names):
        col = (225, 184, 122, 255) if cname == "BOAT" else (140, 97, 56, 255)
        text_col = (76, 40, 15, 255) if cname == "BOAT" else (225, 210, 185, 255)
        d_ui.rectangle([(36 + idx * (cat_w + 6), 94), (36 + idx * (cat_w + 6) + cat_w, 122)], fill=col)
        d_ui.text((54 + idx * (cat_w + 6), 102), cname, fill=text_col)

    # Left Column: Recipe Cards
    recipes_display = [
        ("item_paddle.png", "Paddle", "[Tool: Improved Knife]", "Shaped Wood x2, Wooden Pegs x2, Strong Rope x1", "[READY TO CRAFT]", True),
        ("item_wind_assembly.png", "Wind-Catching Assembly", "[Tool: Mallet] [Weaving Frame]", "Woven Sailcloth x2, Shaped Wood x3, Reinforced Rope x2...", "[READY TO CRAFT]", True),
        ("item_rope_binding_kit.png", "Rope Binding Kit", "[Tool: Fiber Twister]", "Strong Rope x2, Reinforced Rope x2, Vines x3", "[READY TO CRAFT]", True),
        ("item_structural_frame.png", "Structural Frame", "[Tool: Wooden Mallet]", "Shaped Wood x4, Wooden Pegs x6, Reinforced Joints x2...", "[TOOL REQUIRED]", False),
        ("item_reinforced_hull.png", "Reinforced Hull", "[Tool: Wooden Mallet]", "Shaped Wood x6, Reinforced Joints x4, Rope Binding Kit x1...", "[TOOL REQUIRED]", False),
    ]

    card_y = 132
    for icon_f, rname, req, ings, status, ready in recipes_display:
        d_ui.rectangle([(36, card_y), (426, card_y + 98)], fill=(195, 172, 134, 255), outline=(130, 95, 60, 255), width=2)
        spr = load_spr(icon_f, scale=4)
        im_ui.paste(spr, (46, card_y + 17), spr)
        d_ui.text((120, card_y + 10), rname, fill=(60, 32, 12, 255))
        d_ui.text((120, card_y + 30), req, fill=(30, 123, 36, 255) if "Tool" in req else (168, 50, 40, 255))
        d_ui.text((120, card_y + 50), ings[:42] + "...", fill=(90, 60, 30, 255))
        badge_col = (30, 123, 36, 255) if ready else (168, 50, 40, 255)
        d_ui.text((120, card_y + 70), status, fill=badge_col)
        card_y += 106

    # Right Column: Selected Recipe Details (Wind-Catching Assembly)
    dx = 450
    dy = 94
    dw = ui_w - dx - 36
    dh = 590
    d_ui.rectangle([(dx, dy), (dx + dw, dy + dh)], fill=(195, 172, 134, 255), outline=(130, 95, 60, 255), width=2)

    big_spr = load_spr("item_wind_assembly.png", scale=5)
    im_ui.paste(big_spr, (dx + 24, dy + 20), big_spr)
    d_ui.text((dx + 120, dy + 16), "WIND-CATCHING ASSEMBLY  [BOAT COMPONENTS]", fill=(72, 38, 14, 255))
    d_ui.text((dx + 120, dy + 44), "Yields: 1x Wind-Catching Assembly", fill=(30, 123, 36, 255))
    d_ui.text((dx + 120, dy + 66), "Primitive triangular sail rigged to shaped spars with heavy ropes.\nEssential propulsion component for the escape boat.", fill=(85, 55, 25, 255))

    # Prerequisites box
    d_ui.rectangle([(dx + 20, dy + 120), (dx + dw - 20, dy + 180)], fill=(210, 188, 150, 255), outline=(150, 115, 75, 255))
    d_ui.text((dx + 30, dy + 128), "REQUIRED EQUIPMENT & STATION PREREQUISITES:", fill=(72, 38, 14, 255))
    d_ui.text((dx + 30, dy + 152), "• Required Tool: Wooden Mallet — [OWNED IN INVENTORY]", fill=(30, 123, 36, 255))
    d_ui.text((dx + 30, dy + 166), "• Required Station: Weaving Frame — [AVAILABLE]", fill=(30, 123, 36, 255))

    # Ingredients list
    d_ui.text((dx + 24, dy + 196), "REQUIRED INGREDIENTS:", fill=(72, 38, 14, 255))
    ing_rows = [
        ("item_woven_sailcloth.png", "Woven Sailcloth", "2 / 2", "[SATISFIED]"),
        ("item_shaped_wood.png", "Shaped Wooden Parts", "3 / 3", "[SATISFIED]"),
        ("item_reinforced_rope.png", "Reinforced Rope", "2 / 2", "[SATISFIED]"),
        ("item_wooden_pegs.png", "Wooden Pegs", "4 / 4", "[SATISFIED]")
    ]
    iy = dy + 224
    for ispr_f, iname, icnt, istat in ing_rows:
        d_ui.rectangle([(dx + 24, iy), (dx + dw - 24, iy + 44)], fill=(205, 182, 144, 255))
        ispr = load_spr(ispr_f, scale=2)
        im_ui.paste(ispr, (dx + 30, iy + 6), ispr)
        d_ui.text((dx + 74, iy + 14), f"{iname}: {icnt}", fill=(60, 35, 15, 255))
        d_ui.text((dx + 360, iy + 14), istat, fill=(30, 123, 36, 255))
        iy += 50

    # Banner
    d_ui.rectangle([(dx + 24, dy + dh - 130), (dx + dw - 24, dy + dh - 86)], fill=(225, 184, 122, 255), outline=(130, 95, 60, 255))
    d_ui.text((dx + 120, dy + dh - 114), "CRAFTABLE: ALL PREREQUISITES AND MATERIALS READY", fill=(55, 30, 10, 255))

    # Craft button
    d_ui.rectangle([(dx + 24, dy + dh - 78), (dx + dw - 24, dy + dh - 18)], fill=(61, 148, 56, 255))
    d_ui.text((dx + 160, dy + dh - 54), "CRAFT WIND-CATCHING ASSEMBLY", fill=(255, 255, 255, 255))

    out_ui = "scratch/batch8_crafting_ui_hierarchical.png"
    im_ui.save(out_ui)
    print(f"Saved: {out_ui}")

    print("All Batch 8 visuals rendered successfully!")

if __name__ == "__main__":
    render_batch8_showcase()
