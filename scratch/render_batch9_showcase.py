import os
from PIL import Image, ImageDraw, ImageFont

def render_showcase():
    os.makedirs("scratch", exist_ok=True)

    # 1. Boat Visual Stages Showcase (6 stages side by side, scaled up 4x with point filter)
    stage_files = [
        ("Assets/Art/Environment/Boat/boat_stage_0_slipway.png", "Stage 0: Slipway Cradle"),
        ("Assets/Art/Environment/Boat/boat_stage_1_hull.png", "Stage 1: Reinforced Hull"),
        ("Assets/Art/Environment/Boat/boat_stage_2_frame.png", "Stage 2: Structural Frame"),
        ("Assets/Art/Environment/Boat/boat_stage_3_bindings.png", "Stage 3: Rope Bindings"),
        ("Assets/Art/Environment/Boat/boat_stage_4_paddle.png", "Stage 4: Stowed Paddle"),
        ("Assets/Art/Environment/Boat/boat_stage_5_completed.png", "Stage 5: Hoisted Sail (Complete)")
    ]

    card_w, card_h = 180, 220
    spacing = 15
    total_w = 6 * card_w + 7 * spacing
    total_h = card_h + 60

    img = Image.new("RGBA", (total_w, total_h), (24, 28, 36, 255))
    draw = ImageDraw.Draw(img)

    # Title
    draw.text((spacing, 15), "STRANDED — ESCAPE BOAT VISUAL PROGRESSION (STAGES 0 TO 5)", fill=(245, 210, 110, 255))

    for idx, (path, label) in enumerate(stage_files):
        x = spacing + idx * (card_w + spacing)
        y = 50

        # Card bg
        draw.rectangle([x, y, x + card_w, y + card_h], fill=(36, 42, 54, 255), outline=(70, 80, 100, 255), width=2)

        if os.path.exists(path):
            spr = Image.open(path).convert("RGBA")
            # Scale 32x32 -> 128x128 with nearest neighbor
            spr_scaled = spr.resize((128, 128), Image.Resampling.NEAREST)
            img.paste(spr_scaled, (x + (card_w - 128)//2, y + 20), spr_scaled)

        # Label
        draw.text((x + 10, y + card_h - 45), label, fill=(230, 235, 240, 255))
        draw.text((x + 10, y + card_h - 25), f"Status: {'Active' if idx==5 else 'Installed'}", fill=(80, 220, 120, 255) if idx==5 else (140, 180, 240, 255))

    img.save("scratch/batch9_boat_visual_stages.png")
    print("Saved scratch/batch9_boat_visual_stages.png")

    # 2. Construction UI Simulation (980x640 window mock)
    ui_w, ui_h = 1280, 720
    ui_img = Image.new("RGBA", (ui_w, ui_h), (18, 30, 49, 255)) # Island ambient backdrop
    ui_draw = ImageDraw.Draw(ui_img)

    # Ambient beach scenery backdrop
    ui_draw.rectangle([0, 500, ui_w, ui_h], fill=(225, 205, 150, 255)) # Sand
    ui_draw.rectangle([0, 0, ui_w, 500], fill=(45, 115, 160, 255)) # Ocean

    # In-game HUD Tracker (Top-Left)
    ui_draw.rectangle([20, 20, 660, 155], fill=(26, 31, 38, 220), outline=(50, 60, 75, 255), width=2)
    ui_draw.text((35, 30), "[STRANDED: INVENTORY, HOTBAR & CRAFTING]", fill=(180, 215, 255, 255))
    ui_draw.text((35, 60), "Wood: 12  |  Stone: 8  |  Fiber: 15  |  Vines: 6  |  Berries: 5", fill=(235, 240, 245, 255))
    ui_draw.text((35, 95), "Equipped: [None]  (Hotbar: 1-9,0,-,= | Bag: 'I' | Craft: 'C')", fill=(115, 230, 255, 255))

    # In-game Objective HUD (Below Tracker)
    ui_draw.rectangle([20, 165, 660, 241], fill=(31, 36, 46, 225), outline=(215, 165, 70, 255), width=2)
    ui_draw.text((35, 175), "★ OBJECTIVE:  BUILD THE ESCAPE BOAT", fill=(255, 220, 115, 255))
    ui_draw.text((480, 175), "2 / 5 Stages", fill=(190, 210, 230, 255))
    ui_draw.text((35, 200), "Install Rope Binding Kit at the slipway (2/5).", fill=(235, 240, 245, 255))
    # Mini-bar
    ui_draw.rectangle([35, 224, 645, 232], fill=(20, 23, 28, 255))
    ui_draw.rectangle([35, 224, 35 + int(610 * 0.4), 232], fill=(90, 215, 115, 255))

    # Main Stardew-Style Construction Window (Center 980x640)
    pan_x = (ui_w - 980) // 2
    pan_y = (ui_h - 640) // 2
    ui_draw.rectangle([pan_x, pan_y, pan_x + 980, pan_y + 640], fill=(232, 218, 188, 255), outline=(92, 60, 36, 255), width=5)
    ui_draw.rectangle([pan_x + 6, pan_y + 6, pan_x + 974, pan_y + 634], outline=(184, 150, 108, 255), width=2)

    # Title & Close Button
    ui_draw.text((pan_x + 35, pan_y + 25), "ESCAPE BOAT CONSTRUCTION", fill=(61, 36, 21, 255))
    ui_draw.text((pan_x + 35, pan_y + 55), "Northeastern Escape Cove Shipyard — Firm Beach Shoreline", fill=(120, 90, 60, 255))
    ui_draw.rectangle([pan_x + 920, pan_y + 20, pan_x + 955, pan_y + 55], fill=(180, 60, 50, 255), outline=(92, 60, 36, 255))
    ui_draw.text((pan_x + 933, pan_y + 27), "X", fill=(255, 255, 255, 255))

    # Progress Banner
    ui_draw.rectangle([pan_x + 35, pan_y + 85, pan_x + 945, pan_y + 125], fill=(61, 36, 21, 255))
    ui_draw.text((pan_x + 55, pan_y + 98), "CONSTRUCTION PROGRESS: 2 / 5 STAGES COMPLETED (40%)", fill=(255, 225, 130, 255))

    # Left Column: 5 Stages Blueprint List
    col_x = pan_x + 35
    col_y = pan_y + 140
    ui_draw.text((col_x, col_y), "CONSTRUCTION BLUEPRINT & CHECKLIST", fill=(80, 45, 25, 255))

    items = [
        ("Stage 1: Reinforced Hull", "[INSTALLED]", (40, 140, 50, 255)),
        ("Stage 2: Structural Frame", "[INSTALLED]", (40, 140, 50, 255)),
        ("Stage 3: Rope Binding Kit", "[NEXT] In Bag: 1 / 1", (180, 110, 20, 255)),
        ("Stage 4: Paddle", "[LOCKED] Requires previous stages", (130, 110, 90, 255)),
        ("Stage 5: Wind-Catching Assembly", "[LOCKED] Requires previous stages", (130, 110, 90, 255))
    ]

    card_y = col_y + 30
    for idx, (title, status, st_col) in enumerate(items):
        bg_col = (245, 238, 220, 255) if idx != 2 else (255, 248, 210, 255)
        border_col = (200, 140, 30, 255) if idx == 2 else (180, 150, 115, 255)
        ui_draw.rectangle([col_x, card_y, col_x + 420, card_y + 70], fill=bg_col, outline=border_col, width=2 if idx==2 else 1)
        ui_draw.text((col_x + 65, card_y + 12), title, fill=(50, 30, 15, 255))
        ui_draw.text((col_x + 65, card_y + 40), status, fill=st_col)
        card_y += 78

    # Right Column: Active Stage Details & Big Install Button
    r_x = col_x + 445
    r_y = col_y
    ui_draw.text((r_x, r_y), "ACTIVE STAGE DETAILS", fill=(80, 45, 25, 255))

    ui_draw.rectangle([r_x, r_y + 30, r_x + 465, r_y + 420], fill=(245, 238, 220, 255), outline=(180, 150, 115, 255), width=1)
    ui_draw.text((r_x + 20, r_y + 50), "UPCOMING COMPONENT:", fill=(110, 75, 45, 255))
    ui_draw.text((r_x + 20, r_y + 75), "Rope Binding Kit", fill=(60, 35, 15, 255))
    ui_draw.text((r_x + 20, r_y + 115), "Required Nautical lashings and loops securing all timber", fill=(90, 70, 50, 255))
    ui_draw.text((r_x + 20, r_y + 135), "framing joints of the outrigger boat structure.", fill=(90, 70, 50, 255))

    ui_draw.rectangle([r_x + 20, r_y + 180, r_x + 445, r_y + 250], fill=(235, 222, 195, 255), outline=(170, 135, 95, 255))
    ui_draw.text((r_x + 35, r_y + 195), "Requirement Check:", fill=(70, 45, 20, 255))
    ui_draw.text((r_x + 35, r_y + 220), "Ready in Backpack: 1 / 1 available", fill=(30, 130, 40, 255))

    # Big Green Install Button
    ui_draw.rectangle([r_x + 20, r_y + 280, r_x + 445, r_y + 350], fill=(55, 150, 65, 255), outline=(35, 95, 40, 255), width=2)
    ui_draw.text((r_x + 85, r_y + 305), "INSTALL ROPE BINDING KIT (PRESS E)", fill=(255, 255, 255, 255))

    ui_draw.text((r_x + 20, r_y + 375), "Consumes 1x item from backpack and advances boat to Stage 3.", fill=(120, 95, 75, 255))

    ui_img.save("scratch/batch9_boat_construction_ui.png")
    print("Saved scratch/batch9_boat_construction_ui.png")

if __name__ == "__main__":
    render_showcase()
