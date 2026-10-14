import os
import math
from PIL import Image, ImageDraw

os.makedirs("Assets/Art/Environment/Camp", exist_ok=True)
os.makedirs("Assets/Art/Environment/Items", exist_ok=True)
os.makedirs("Assets/Art/Environment/Nodes", exist_ok=True)
os.makedirs("Assets/Art/UI", exist_ok=True)

# =============================================================================
# 1. ENHANCED CRASHED HELICOPTER (112 x 64 pixels, 16 PPU -> 7.0m x 4.0m)
# =============================================================================
def generate_enhanced_helicopter():
    w, h = 112, 64
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Palette
    c_hull_dark = (42, 54, 40, 255)       # Dark olive drab
    c_hull_mid = (65, 82, 60, 255)        # Mid olive
    c_hull_light = (90, 112, 82, 255)     # Highlight olive
    c_hull_rust = (115, 62, 38, 255)      # Scorched rust/dirt
    c_metal_dark = (30, 34, 38, 255)      # Dark steel
    c_metal_mid = (60, 68, 76, 255)       # Structural steel
    c_metal_light = (110, 122, 134, 255)  # Light rim steel
    c_glass_frame = (35, 45, 50, 255)     # Windscreen frame
    c_glass = (75, 120, 140, 190)         # Cracked canopy glass
    c_glass_hi = (140, 200, 220, 230)     # Glass glare
    c_interior_shadow = (18, 14, 16, 255) # Deep cabin shadows
    c_interior_floor = (45, 40, 38, 255)  # Corrugated cabin floor
    c_bed_canvas = (140, 110, 75, 255)    # Makeshift sleeping cot / canvas
    c_bed_blanket = (60, 85, 110, 255)    # Blue emergency wool blanket
    c_pillow = (210, 195, 175, 255)       # Pillow / rolled coat
    c_wire_yellow = (210, 170, 30, 255)   # Dangling wires
    c_wire_red = (190, 40, 30, 255)

    # 1. Snapped Tail Boom (trailing up and right: x=75..110, y=10..30)
    for x in range(75, 108):
        y_top = int(24 - (x - 75) * 0.35)
        y_bot = y_top + int(12 - (x - 75) * 0.18)
        for y in range(y_top, y_bot):
            shade = c_hull_mid if (x % 4 != 0) else c_hull_dark
            if y == y_top: shade = c_hull_light
            elif y >= y_bot - 2: shade = c_hull_dark
            img.putpixel((x, y), shade)

    # Tail fin / broken tail rotor stump (x=102..110, y=8..28)
    for y in range(10, 26):
        img.putpixel((104, y), c_metal_mid)
        img.putpixel((105, y), c_metal_dark)
    # Snapped tail blade angled
    for i in range(12):
        bx = 104 + i // 2
        by = 12 - i
        if 0 <= bx < w and 0 <= by < h:
            img.putpixel((bx, by), c_metal_light)

    # 2. Main Fuselage Outer Shell (x=12..78, y=20..54)
    for y in range(22, 54):
        for x in range(14, 76):
            # Nose curve on left
            if x < 28:
                dx = 28 - x
                if y < 22 + dx * 0.7 or y > 53 - dx * 0.6:
                    continue
            img.putpixel((x, y), c_hull_mid)

    # Fuselage shading & metallic panel seams
    for x in range(14, 76):
        for y in range(22, 54):
            cur = img.getpixel((x, y))
            if cur[3] == 0: continue
            if y <= 25:
                img.putpixel((x, y), c_hull_light)
            elif y >= 50:
                img.putpixel((x, y), c_hull_dark)
            elif (x % 14 == 0):
                img.putpixel((x, y), c_metal_dark) # Rivet seam

    # Rust streaks & scorch marks
    for sx in [24, 38, 62, 70]:
        for sy in range(28, 48):
            if img.getpixel((sx, sy))[3] > 0 and (sy % 2 == 0):
                img.putpixel((sx, sy), c_hull_rust)

    # 3. Cockpit Canopy & Windscreen (x=15..32, y=24..40)
    for y in range(24, 39):
        for x in range(16, 32):
            if x < 28 and y < 24 + (28 - x) * 0.6: continue
            # Glass border
            if x == 16 or x == 31 or y == 24 or y == 38:
                img.putpixel((x, y), c_glass_frame)
            else:
                img.putpixel((x, y), c_glass)

    # Cracked glass spiderweb
    cracks = [(19, 28), (20, 29), (21, 29), (22, 30), (23, 31), (24, 31), (25, 30),
              (22, 28), (22, 27), (23, 26), (20, 32), (21, 33), (27, 28), (28, 27)]
    for cx, cy in cracks:
        if 0 <= cx < w and 0 <= cy < h:
            img.putpixel((cx, cy), c_glass_hi)

    # Cockpit console inside
    for cy in range(35, 38):
        for cx in range(26, 31):
            img.putpixel((cx, cy), (25, 30, 35, 255))
    img.putpixel((28, 36), (60, 220, 100, 255)) # Green indicator glow
    img.putpixel((30, 36), (220, 60, 50, 255))  # Red indicator glow

    # 4. LARGE OPEN CARGO / PASSENGER CABIN DOOR (x=34..68, y=28..51)
    # The user says: "the inside of hellicopter must see and when resting it shoukd look like the player is sleeping inside it"
    # We carve out a large open interior cabin with jagged torn doorway!
    for y in range(28, 51):
        for x in range(35, 67):
            # Jagged frame around door
            if x == 35 or x == 66 or y == 28:
                img.putpixel((x, y), c_metal_dark)
            elif y == 50:
                img.putpixel((x, y), c_interior_floor)
            else:
                # Deep interior floor and rear wall
                depth_shade = (24 + (y - 28) * 2, 22 + (y - 28) * 2, 25 + (y - 28) * 2, 255)
                img.putpixel((x, y), depth_shade)

    # Cabin Ribs / Bulkheads inside
    for rx in [42, 50, 58]:
        for ry in range(29, 50):
            img.putpixel((rx, ry), (35, 38, 44, 255))

    # Makeshift Sleeping Cot / Mat on Cabin Floor (x=38..62, y=43..49)
    # Wooden pallet frame / cot
    for bx in range(38, 62):
        img.putpixel((bx, 49), (70, 48, 28, 255)) # Wood cot base
    # Canvas mattress
    for bx in range(39, 61):
        for by in range(45, 49):
            img.putpixel((bx, by), c_bed_canvas)
    # Pillow at head of bed (left side: x=39..44)
    for px in range(39, 45):
        for py in range(45, 48):
            img.putpixel((px, py), c_pillow)
    # Folded emergency blanket at foot of bed (x=52..60)
    for fx in range(52, 60):
        for fy in range(45, 49):
            img.putpixel((fx, fy), c_bed_blanket)

    # First aid box lashed to inner bulkhead (x=62..65, y=36..41)
    for ax in range(62, 66):
        for ay in range(37, 42):
            img.putpixel((ax, ay), (210, 210, 205, 255))
    img.putpixel((63, 39), (200, 30, 30, 255)) # Red cross
    img.putpixel((64, 39), (200, 30, 30, 255))
    img.putpixel((63, 38), (200, 30, 30, 255))
    img.putpixel((63, 40), (200, 30, 30, 255))

    # Dangling wires from ceiling (x=46, 54)
    for wy in range(29, 36):
        img.putpixel((46, wy), c_wire_yellow if wy % 2 == 0 else c_metal_dark)
    for wy in range(29, 34):
        img.putpixel((54, wy), c_wire_red if wy % 2 == 0 else c_metal_dark)

    # 5. Rotor Hub & Bent Blades (x=44..52, y=14..22)
    # Rotor mast
    for my in range(16, 23):
        for mx in range(47, 51):
            img.putpixel((mx, my), c_metal_dark)
    # Hub gearbox
    for hx in range(45, 53):
        for hy in range(14, 18):
            img.putpixel((hx, hy), c_metal_mid)

    # Bent Rotor Blades (One snapped left, one angled right)
    # Left blade snapped downward (x=10..45)
    for bx in range(10, 46):
        by = int(14 + (45 - bx) * 0.22)
        if 0 <= by < h:
            img.putpixel((bx, by), c_metal_light)
            if by + 1 < h: img.putpixel((bx, by + 1), c_metal_mid)
    # Right blade angled up and back (x=52..94)
    for bx in range(52, 95):
        by = int(14 - (bx - 52) * 0.18)
        if 0 <= by < h:
            img.putpixel((bx, by), c_metal_light)
            if by + 1 < h: img.putpixel((bx, by + 1), c_metal_mid)

    # 6. Landing Skids (bent and buckled into ground at bottom)
    # Left bent skid (x=20..38, y=54..59)
    for sx in range(20, 38):
        img.putpixel((sx, 57), c_metal_dark)
        img.putpixel((sx, 58), c_metal_mid)
    # Right crumpled skid (x=48..72, y=55..61)
    for sx in range(48, 72):
        sy = 58 + int(math.sin(sx * 0.3) * 2)
        if 0 <= sy < h:
            img.putpixel((sx, sy), c_metal_mid)
            if sy + 1 < h: img.putpixel((sx, sy + 1), c_metal_dark)

    # Ground impact debris & scorched earth under fuselage
    for x in range(16, 76):
        if x % 3 == 0:
            img.putpixel((x, 60), (32, 28, 20, 210))
        if x % 5 == 0:
            img.putpixel((x, 61), (50, 42, 28, 180))

    img.save("Assets/Art/Environment/Camp/helicopter_wreckage.png")
    print("Generated enhanced crashed helicopter (112x64)")

# =============================================================================
# 2. SLEEPING SURVIVOR VISUAL (32 x 24 pixels, shown inside cabin when resting)
# =============================================================================
def generate_sleeping_survivor():
    w, h = 32, 24
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    c_hair = (45, 30, 20, 255)          # Dark brown survivor hair
    c_skin = (225, 185, 145, 255)       # Sleeping face
    c_skin_shadow = (185, 145, 110, 255)
    c_eye_closed = (70, 45, 30, 255)    # Closed eyelid
    c_pillow = (215, 200, 180, 255)     # Soft canvas pillow
    c_blanket_main = (50, 80, 115, 255) # Blue wool blanket
    c_blanket_hi = (75, 115, 155, 255)  # Fold highlight
    c_blanket_shadow = (30, 50, 75, 255)# Fold shadow
    c_zzz = (255, 240, 160, 255)        # Floating Zzz

    # Pillow (x=4..12, y=10..18)
    for x in range(4, 13):
        for y in range(11, 18):
            img.putpixel((x, y), c_pillow)
    for x in range(4, 13):
        img.putpixel((x, 11), (235, 225, 205, 255)) # highlight

    # Head & Face resting on pillow (x=7..13, y=10..15)
    for x in range(7, 14):
        for y in range(10, 16):
            img.putpixel((x, y), c_skin)
    # Hair
    for x in range(6, 12):
        img.putpixel((x, 10), c_hair)
        img.putpixel((x, 11), c_hair)
    img.putpixel((6, 12), c_hair)
    # Closed sleeping eyelid
    img.putpixel((11, 13), c_eye_closed)
    img.putpixel((12, 13), c_eye_closed)

    # Body covered by blanket (x=13..28, y=11..19)
    for x in range(13, 29):
        for y in range(11, 20):
            # Gentle curved sleeping posture
            if y == 11 and (x < 15 or x > 26): continue
            img.putpixel((x, y), c_blanket_main)

    # Blanket fold highlights and shadow
    for x in range(14, 27):
        img.putpixel((x, 12), c_blanket_hi)
        img.putpixel((x, 16), c_blanket_shadow)
        img.putpixel((x, 19), (20, 35, 55, 255))

    # Floating "Z z z"
    # Small z at (16, 8)
    z_small = [(16, 7), (17, 7), (17, 8), (16, 9), (17, 9)]
    for zx, zy in z_small: img.putpixel((zx, zy), (255, 230, 130, 200))
    # Bigger Z at (20, 4)
    z_big = [(20, 3), (21, 3), (22, 3), (23, 3),
             (22, 4), (21, 5),
             (20, 6), (21, 6), (22, 6), (23, 6)]
    for zx, zy in z_big: img.putpixel((zx, zy), c_zzz)

    img.save("Assets/Art/Environment/Camp/survivor_sleeping.png")
    print("Generated sleeping survivor visual (32x24)")

# =============================================================================
# 3. FORAGING ITEMS: BERRIES, POISONOUS BERRIES, MUSHROOMS, POISONOUS TOADSTOOLS
# =============================================================================
def generate_foraging_items():
    # 3a. item_berry.png (16x16, Edible Sweet Berries)
    img_berry = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    # Juicy red cluster with green stem
    stem_col = (45, 110, 35, 255)
    leaf_col = (90, 175, 45, 255)
    berry_dark = (120, 15, 25, 255)
    berry_mid = (205, 30, 45, 255)
    berry_light = (245, 95, 105, 255)
    # stem
    for (x, y) in [(8, 2), (8, 3), (7, 4), (9, 3), (10, 2)]: img_berry.putpixel((x, y), stem_col)
    for (x, y) in [(9, 2), (10, 3), (6, 4)]: img_berry.putpixel((x, y), leaf_col)
    # berry cluster
    berries = [(5, 7), (9, 6), (7, 10), (11, 10)]
    for bx, by in berries:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx*dx + dy*dy <= 4:
                    col = berry_mid
                    if dx < 0 and dy < 0: col = berry_light
                    elif dx > 0 or dy > 0: col = berry_dark
                    img_berry.putpixel((bx + dx, by + dy), col)
    img_berry.save("Assets/Art/Environment/Items/item_berry.png")

    # 3b. item_poison_berry.png (16x16, Toxic Nightshade Berries)
    img_p_berry = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    p_stem = (40, 60, 45, 255)
    p_dark = (35, 15, 55, 255)       # Deep ominous purple/black
    p_mid = (95, 25, 135, 255)       # Toxic violet
    p_glow = (185, 75, 245, 255)     # Glowing unnatural highlight
    for (x, y) in [(8, 2), (8, 3), (7, 4), (9, 3)]: img_p_berry.putpixel((x, y), p_stem)
    for bx, by in [(5, 7), (10, 6), (7, 10), (11, 10)]:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx*dx + dy*dy <= 4:
                    col = p_mid
                    if dx == -1 and dy == -1: col = p_glow
                    elif dx > 0 or dy > 0: col = p_dark
                    img_p_berry.putpixel((bx + dx, by + dy), col)
    img_p_berry.save("Assets/Art/Environment/Items/item_poison_berry.png")

    # 3c. item_mushroom.png (16x16, Island Morel / Brown Edible Mushroom)
    img_shroom = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    stem_base = (215, 205, 185, 255)
    stem_shadow = (170, 155, 135, 255)
    cap_dark = (95, 55, 25, 255)
    cap_mid = (165, 105, 50, 255)
    cap_light = (215, 155, 85, 255)
    # Stem (x=7..9, y=8..14)
    for y in range(8, 15):
        for x in range(7, 10):
            img_shroom.putpixel((x, y), stem_base if x < 9 else stem_shadow)
    # Cap (x=4..12, y=3..8)
    for y in range(3, 9):
        for x in range(4, 13):
            dx = abs(x - 8)
            if y == 3 and dx > 2: continue
            if y == 4 and dx > 3: continue
            col = cap_mid
            if y <= 5 and dx <= 2: col = cap_light
            elif y >= 7 or dx >= 3: col = cap_dark
            img_shroom.putpixel((x, y), col)
    # Morel honeycomb pits
    pits = [(6, 5), (8, 4), (10, 5), (7, 7), (9, 7)]
    for px, py in pits: img_shroom.putpixel((px, py), cap_dark)
    img_shroom.save("Assets/Art/Environment/Items/item_mushroom.png")

    # 3d. item_poison_mushroom.png (16x16, Crimson Poisonous Toadstool)
    img_p_shroom = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    p_stem_base = (235, 235, 230, 255)
    p_stem_sh = (185, 185, 180, 255)
    p_cap_dark = (140, 15, 20, 255)
    p_cap_mid = (215, 30, 40, 255)
    p_cap_light = (255, 75, 80, 255)
    p_wart = (255, 255, 250, 255) # White toxic spots
    # Stem
    for y in range(8, 15):
        for x in range(7, 10):
            img_p_shroom.putpixel((x, y), p_stem_base if x < 9 else p_stem_sh)
    # Skirt / ring on stem
    for x in range(6, 11): img_p_shroom.putpixel((x, 10), p_stem_base)
    # Bright red domed cap
    for y in range(3, 9):
        for x in range(4, 13):
            dx = abs(x - 8)
            if y == 3 and dx > 2: continue
            if y == 4 and dx > 3: continue
            col = p_cap_mid
            if y <= 5 and dx <= 2: col = p_cap_light
            elif y >= 7 or dx >= 3: col = p_cap_dark
            img_p_shroom.putpixel((x, y), col)
    # White toxic warts / spots
    warts = [(6, 4), (8, 4), (10, 5), (6, 7), (8, 6), (11, 7)]
    for wx, wy in warts: img_p_shroom.putpixel((wx, wy), p_wart)
    img_p_shroom.save("Assets/Art/Environment/Items/item_poison_mushroom.png")

    print("Generated 4 foraging item sprites")

# =============================================================================
# 4. FORAGING WORLD NODES (BUSHES & MUSHROOM CLUSTERS)
# =============================================================================
def generate_foraging_nodes():
    # 4a. node_berry_bush.png (32x32)
    bush = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    # Base shrub
    c_leaf_dark = (35, 75, 30, 255)
    c_leaf_mid = (65, 135, 50, 255)
    c_leaf_light = (115, 195, 75, 255)
    for y in range(8, 28):
        for x in range(6, 26):
            dx = (x - 16) / 9.0
            dy = (y - 18) / 9.0
            if dx*dx + dy*dy <= 1.0:
                col = c_leaf_mid
                if dy < -0.3: col = c_leaf_light
                elif dy > 0.4: col = c_leaf_dark
                bush.putpixel((x, y), col)
    # Red berries sprinkled across bush
    red_berries = [(11, 14), (12, 14), (18, 12), (19, 12), (14, 19), (15, 19),
                   (22, 16), (23, 16), (10, 22), (11, 22), (20, 22), (21, 22)]
    for bx, by in red_berries:
        bush.putpixel((bx, by), (225, 35, 45, 255))
    bush.save("Assets/Art/Environment/Nodes/node_berry_bush.png")

    # 4b. node_poison_berry_bush.png (32x32)
    p_bush = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    c_p_leaf_dark = (25, 45, 35, 255)
    c_p_leaf_mid = (45, 85, 60, 255)
    c_p_leaf_light = (75, 135, 95, 255)
    for y in range(8, 28):
        for x in range(6, 26):
            dx = (x - 16) / 9.0
            dy = (y - 18) / 9.0
            if dx*dx + dy*dy <= 1.0:
                col = c_p_leaf_mid
                if dy < -0.3: col = c_p_leaf_light
                elif dy > 0.4: col = c_p_leaf_dark
                p_bush.putpixel((x, y), col)
    # Poisonous violet berries
    purple_berries = [(11, 14), (12, 14), (18, 12), (19, 12), (14, 19), (15, 19),
                      (22, 16), (23, 16), (10, 22), (11, 22), (20, 22), (21, 22)]
    for bx, by in purple_berries:
        p_bush.putpixel((bx, by), (145, 35, 195, 255))
    p_bush.save("Assets/Art/Environment/Nodes/node_poison_berry_bush.png")

    # 4c. node_mushroom_cluster.png (24x24)
    m_cluster = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    # Moss patch on ground
    for y in range(14, 22):
        for x in range(4, 20):
            dx = (x - 12) / 7.0
            dy = (y - 18) / 3.5
            if dx*dx + dy*dy <= 1.0:
                m_cluster.putpixel((x, y), (40, 75, 35, 220))
    # 3 brown mushrooms at (8, 14), (14, 12), (17, 16)
    shroom_coords = [(8, 14, 3), (14, 12, 4), (17, 16, 2)]
    for cx, cy, rad in shroom_coords:
        # stem
        for sy in range(cy, cy + rad + 3):
            m_cluster.putpixel((cx, sy), (210, 195, 170, 255))
        # cap
        for dx in range(-rad, rad + 1):
            for dy in range(-rad + 1, 1):
                if dx*dx + dy*dy <= rad*rad:
                    m_cluster.putpixel((cx + dx, cy + dy), (160, 100, 45, 255))
    m_cluster.save("Assets/Art/Environment/Nodes/node_mushroom_cluster.png")

    # 4d. node_poison_mushroom_cluster.png (24x24)
    pm_cluster = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    for y in range(14, 22):
        for x in range(4, 20):
            dx = (x - 12) / 7.0
            dy = (y - 18) / 3.5
            if dx*dx + dy*dy <= 1.0:
                pm_cluster.putpixel((x, y), (30, 60, 40, 220))
    # 3 red toadstools
    red_coords = [(7, 14, 3), (13, 11, 4), (18, 15, 3)]
    for cx, cy, rad in red_coords:
        for sy in range(cy, cy + rad + 3):
            pm_cluster.putpixel((cx, sy), (225, 225, 220, 255))
        for dx in range(-rad, rad + 1):
            for dy in range(-rad + 1, 1):
                if dx*dx + dy*dy <= rad*rad:
                    pm_cluster.putpixel((cx + dx, cy + dy), (215, 30, 40, 255))
        # white spots
        pm_cluster.putpixel((cx - 1, cy - 1), (255, 255, 255, 255))
        pm_cluster.putpixel((cx + 1, cy), (255, 255, 255, 255))
    pm_cluster.save("Assets/Art/Environment/Nodes/node_poison_mushroom_cluster.png")

    print("Generated 4 foraging world node sprites")

# =============================================================================
# 5. STARDEW VALLEY ARTISTIC UI TEXTURES (Rich Warm Wood, Parchment, Bevels)
# =============================================================================
def generate_stardew_ui_textures():
    # 5a. ui_inventory_panel.png (480 x 320, warm carved wood frame, inner parchment)
    w, h = 480, 320
    panel = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(panel)

    c_border_outer = (45, 24, 10, 255)    # Very dark walnut rim
    c_wood_dark = (75, 42, 18, 255)       # Deep mahogany wood
    c_wood_mid = (118, 68, 32, 255)       # Rich warm walnut
    c_wood_light = (165, 102, 50, 255)    # Honey wood highlight
    c_gold_border = (220, 165, 55, 255)   # Stardew golden inner filigree
    c_parchment_bg = (232, 202, 152, 255) # Warm creamy parchment inlay
    c_parchment_sh = (212, 180, 130, 255) # Subtle parchment grain

    # 1. Outer Frame (16px border)
    # Outer dark edge
    draw.rectangle([0, 0, w - 1, h - 1], fill=c_wood_dark, outline=c_border_outer, width=3)
    # Beveled wood planks
    draw.rectangle([4, 4, w - 5, h - 5], fill=c_wood_mid, outline=c_wood_light, width=2)
    # Horizontal wood grain lines
    for gy in range(8, 20):
        if gy % 3 == 0:
            draw.line([(8, gy), (w - 9, gy)], fill=c_wood_light)
            draw.line([(8, h - 1 - gy), (w - 9, h - 1 - gy)], fill=c_wood_dark)

    # Golden Filigree Inset Line
    draw.rectangle([14, 14, w - 15, h - 15], outline=c_gold_border, width=2)

    # 2. Inner Parchment Inlay (where slots and tabs sit)
    draw.rectangle([18, 18, w - 19, h - 19], fill=c_parchment_bg, outline=c_border_outer, width=2)
    # Subtle parchment texture
    for py in range(22, h - 22, 6):
        draw.line([(22, py), (w - 23, py)], fill=c_parchment_sh)

    # 3. Corner Brass Rivets / Metal Braces
    corners = [(8, 8), (w - 14, 8), (8, h - 14), (w - 14, h - 14)]
    for cx, cy in corners:
        draw.rectangle([cx, cy, cx + 5, cy + 5], fill=(240, 190, 70, 255), outline=c_border_outer, width=1)
        draw.point((cx + 1, cy + 1), fill=(255, 240, 160, 255))

    panel.save("Assets/Art/UI/ui_inventory_panel.png")

    # 5b. ui_slot_background.png (64x64, Recessed leather/wood slot)
    slot = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(slot)
    # Outer wooden slot bevel
    sdraw.rectangle([0, 0, 63, 63], fill=(85, 48, 22, 255), outline=(42, 22, 10, 255), width=2)
    sdraw.rectangle([2, 2, 61, 61], outline=(145, 90, 42, 255), width=1)
    # Recessed dark slot well
    sdraw.rectangle([4, 4, 59, 59], fill=(52, 32, 18, 255), outline=(28, 16, 8, 255), width=2)
    # Inner subtle corner shadow
    sdraw.line([(6, 6), (57, 6)], fill=(22, 12, 6, 255))
    sdraw.line([(6, 6), (6, 57)], fill=(22, 12, 6, 255))
    sdraw.line([(6, 57), (57, 57)], fill=(80, 50, 28, 255)) # bottom rim light
    sdraw.line([(57, 6), (57, 57)], fill=(80, 50, 28, 255))
    slot.save("Assets/Art/UI/ui_slot_background.png")

    # 5c. ui_slot_selected.png (64x64, Radiant golden Stardew selection box)
    sel = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    seldraw = ImageDraw.Draw(sel)
    # Golden outer glowing border
    seldraw.rectangle([0, 0, 63, 63], outline=(255, 215, 0, 255), width=3)
    seldraw.rectangle([2, 2, 61, 61], outline=(255, 245, 140, 255), width=1)
    # Prominent 5px corner brackets
    c_len = 10
    for corner in [(0, 0), (63, 0), (0, 63), (63, 63)]:
        x0, y0 = corner
        dx = -1 if x0 > 0 else 1
        dy = -1 if y0 > 0 else 1
        seldraw.line([(x0, y0), (x0 + dx*c_len, y0)], fill=(255, 255, 200, 255), width=3)
        seldraw.line([(x0, y0), (x0, y0 + dy*c_len)], fill=(255, 255, 200, 255), width=3)
    sel.save("Assets/Art/UI/ui_slot_selected.png")

    # 5d. ui_menu_panel.png (360x280, Rustic wooden notice plaque for Escape Menu)
    menu_p = Image.new("RGBA", (360, 280), (0, 0, 0, 0))
    mdraw = ImageDraw.Draw(menu_p)
    # Dark border
    mdraw.rectangle([0, 0, 359, 279], fill=(68, 38, 16, 255), outline=(32, 16, 8, 255), width=3)
    mdraw.rectangle([4, 4, 355, 275], fill=(105, 60, 28, 255), outline=(155, 95, 45, 255), width=2)
    # Golden line
    mdraw.rectangle([12, 12, 347, 267], outline=(225, 175, 65, 255), width=2)
    # Inner parchment center
    mdraw.rectangle([16, 16, 343, 263], fill=(228, 198, 148, 255), outline=(42, 24, 10, 255), width=2)
    # Corner brackets
    for cx, cy in [(6, 6), (347, 6), (6, 267), (347, 267)]:
        mdraw.rectangle([cx, cy, cx + 6, cy + 6], fill=(245, 195, 75, 255), outline=(35, 18, 8, 255), width=1)
    menu_p.save("Assets/Art/UI/ui_menu_panel.png")

    print("Generated 4 Stardew Valley artistic UI textures")

generate_enhanced_helicopter()
generate_sleeping_survivor()
generate_foraging_items()
generate_foraging_nodes()
generate_stardew_ui_textures()
