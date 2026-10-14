import os
from PIL import Image, ImageDraw, ImageFont

def render_camp():
    # 1. Canvas dimensions (representing the camp area around helicopter 130-142 X, 116-128 Y)
    w, h = 960, 640
    img = Image.new('RGBA', (w, h), (46, 88, 48, 255)) # Lush island grass
    draw = ImageDraw.Draw(img)

    # Subtle grass variation grid
    for gx in range(0, w, 32):
        for gy in range(0, h, 32):
            if (gx // 32 + gy // 32) % 2 == 0:
                draw.rectangle([gx, gy, gx + 31, gy + 31], fill=(50, 96, 52, 255))
    
    # Path / clearing around helicopter in warm dirt/sand tone
    draw.ellipse([260, 180, 700, 480], fill=(78, 102, 60, 255))
    draw.ellipse([300, 220, 660, 440], fill=(112, 110, 72, 255))
    draw.ellipse([340, 260, 620, 400], fill=(138, 126, 82, 255))

    # Helper coordinate mapper: (world_x, world_y) -> (screen_x, screen_y)
    # Center camp at (136.5, 122.5) -> (480, 320)
    # Scale: 1 world unit = 48 pixels
    def to_screen(wx, wy):
        sx = int(480 + (wx - 136.5) * 48)
        sy = int(320 - (wy - 122.5) * 48) # Invert Y for screen coords
        return sx, sy

    # Load Assets
    def load_scaled(path, scale):
        im = Image.open(path).convert('RGBA')
        return im.resize((int(im.width * scale), int(im.height * scale)), Image.Resampling.NEAREST)

    heli = load_scaled('Assets/Art/Environment/Camp/helicopter_wreckage.png', 2.0)
    fire = load_scaled('Assets/Art/Environment/Camp/campfire_primitive.png', 2.5)
    boulder = load_scaled('Assets/Art/Environment/Rocks/rock_boulder_large.png', 2.0)
    tree = load_scaled('Assets/Art/Environment/Trees/tree_tropical_mature.png', 1.8)
    pine = load_scaled('Assets/Art/Environment/Trees/tree_pine_mature.png', 1.8)

    sp_poison_shroom = load_scaled('Assets/Art/Environment/Items/item_poison_mushroom.png', 3.0)
    sp_shroom = load_scaled('Assets/Art/Environment/Items/item_mushroom.png', 3.0)
    sp_chanterelle = load_scaled('Assets/Art/Environment/Items/item_chanterelle.png', 3.0)
    sp_poison_berry = load_scaled('Assets/Art/Environment/Items/item_poison_berry.png', 2.8)
    sp_berry = load_scaled('Assets/Art/Environment/Items/item_berry.png', 2.8)
    sp_blackberry = load_scaled('Assets/Art/Environment/Items/item_blackberry.png', 2.8)

    # 1. Draw Background Environment (Trees & Boulders)
    # North trees
    sx, sy = to_screen(132.0, 128.5); img.paste(tree, (sx, sy), tree)
    sx, sy = to_screen(142.0, 128.0); img.paste(pine, (sx, sy), pine)
    sx, sy = to_screen(129.5, 122.0); img.paste(tree, (sx, sy), tree)
    sx, sy = to_screen(144.0, 120.0); img.paste(boulder, (sx, sy), boulder)

    # 2. Draw Helicopter Centerpiece at (134.4, 122.7)
    hx, hy = to_screen(134.4, 122.7)
    img.paste(heli, (hx - heli.width // 2, hy - heli.height // 2), heli)

    # 3. Draw Campfire at (136.8, 121.2)
    fx, fy = to_screen(136.8, 121.2)
    img.paste(fire, (fx - fire.width // 2, fy - fire.height // 2), fire)

    # 4. Draw Player at (135.5, 120.5)
    px, py = to_screen(135.5, 120.5)
    # Draw simple player circle indicator
    draw.ellipse([px - 14, py - 20, px + 14, py + 14], fill=(70, 140, 240, 255), outline=(255, 255, 255, 255), width=2)
    draw.text((px - 18, py - 36), "PLAYER", fill=(255, 255, 255, 255))

    # 5. Place and Annotate the Forage Nodes!
    nodes_to_draw = [
        # (wx, wy, sprite, label, is_poison, yield_text)
        (138.5, 126.5, sp_poison_shroom, "Crimson Toadstool", True, "POISON (-50% HP)"),
        (133.5, 126.5, sp_shroom, "Island Morel", False, "+22 Food, +8 HP"),
        (137.5, 128.5, sp_poison_berry, "Nightshade Berries", True, "POISON (-50% HP)"),
        (134.5, 118.5, sp_berry, "Wild Berries", False, "+15 Food, +5 Energy"),
        (139.5, 121.5, sp_berry, "Wild Berries", False, "+15 Food, +5 Energy"),
        (131.5, 123.5, sp_blackberry, "Wild Blackberry", False, "+16 Food, +4 HP"),
        (136.5, 114.5, sp_chanterelle, "Golden Chanterelle", False, "+24 Food, +12 HP")
    ]

    for wx, wy, sp, name, is_poison, stat in nodes_to_draw:
        nx, ny = to_screen(wx, wy)
        # Paste sprite
        img.paste(sp, (nx - sp.width // 2, ny - sp.height // 2), sp)

        # Highlight ring
        ring_col = (255, 60, 60, 255) if is_poison else (60, 230, 120, 255)
        bg_col = (40, 10, 15, 220) if is_poison else (10, 35, 20, 220)
        draw.ellipse([nx - 22, ny - 22, nx + 22, ny + 22], outline=ring_col, width=2)

        # Tag label
        label_y = ny + 26
        draw.rectangle([nx - 75, label_y, nx + 75, label_y + 32], fill=bg_col, outline=ring_col, width=1)
        draw.text((nx - 68, label_y + 3), name, fill=(255, 255, 255, 255))
        stat_col = (255, 100, 100, 255) if is_poison else (120, 240, 140, 255)
        draw.text((nx - 68, label_y + 17), stat, fill=stat_col)

    # Title & Legend Overlay
    draw.rectangle([15, 15, 360, 80], fill=(20, 24, 30, 245), outline=(210, 160, 60, 255), width=2)
    draw.text((25, 23), "CRASH SITE - FORAGE MAPPING", fill=(255, 230, 160, 255))
    draw.text((25, 42), "Hand-gather with [E] | Eat with [F] / R-Click", fill=(200, 210, 220, 255))
    draw.text((25, 60), "Red: Toxic (-50% HP) | Green: Edible Food", fill=(240, 180, 140, 255))

    out_path = 'C:/Users/PAVILION/.gemini/antigravity-ide/brain/b46c14a7-7143-4bd0-a671-642ef3f589e7/camp_sanctuary_forage_map.png'
    img.save(out_path)
    img.save('scratch/camp_sanctuary_forage_map.png')
    print("Saved camp forage map to", out_path)

if __name__ == '__main__':
    render_camp()
