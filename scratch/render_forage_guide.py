import os
from PIL import Image, ImageDraw, ImageFont

def create_forage_guide():
    w, h = 960, 680
    bg = Image.new('RGBA', (w, h), (24, 28, 36, 255))
    draw = ImageDraw.Draw(bg)
    
    # Header
    draw.rectangle([0, 0, w, 70], fill=(18, 22, 28, 255))
    draw.rectangle([0, 68, w, 70], fill=(210, 160, 60, 255)) # Gold trim
    draw.text((30, 20), "STRANDED - ISLAND FORAGE GUIDE: MUSHROOMS & BERRIES", fill=(255, 230, 160, 255))
    draw.text((30, 44), "Authentic Pixel-Art Forage Extracted From Stardew Valley Environment Assets", fill=(170, 185, 200, 255))
    
    # Load Sprites
    sprites = {
        'poison_mushroom': Image.open('Assets/Art/Environment/Items/item_poison_mushroom.png').convert('RGBA'),
        'poison_berry': Image.open('Assets/Art/Environment/Items/item_poison_berry.png').convert('RGBA'),
        'mushroom': Image.open('Assets/Art/Environment/Items/item_mushroom.png').convert('RGBA'),
        'morel': Image.open('Assets/Art/Environment/Items/item_morel.png').convert('RGBA'),
        'chanterelle': Image.open('Assets/Art/Environment/Items/item_chanterelle.png').convert('RGBA'),
        'purple_mushroom': Image.open('Assets/Art/Environment/Items/item_purple_mushroom.png').convert('RGBA'),
        'berry': Image.open('Assets/Art/Environment/Items/item_berry.png').convert('RGBA'),
        'blackberry': Image.open('Assets/Art/Environment/Items/item_blackberry.png').convert('RGBA'),
    }
    
    # Column 1: POISONOUS FORAGE (WARNING)
    col1_x = 30
    draw.rectangle([col1_x, 90, col1_x + 435, 640], fill=(36, 24, 28, 255), outline=(180, 50, 60, 255), width=2)
    # Header badge
    draw.rectangle([col1_x, 90, col1_x + 435, 130], fill=(140, 30, 40, 255))
    draw.text((col1_x + 20, 102), "DANGER: POISONOUS VARIETIES (-50% MAX HP)", fill=(255, 240, 240, 255))
    
    # Item 1: Crimson Toadstool
    card1_y = 145
    draw.rectangle([col1_x + 15, card1_y, col1_x + 420, card1_y + 115], fill=(48, 30, 35, 255), outline=(120, 45, 55, 255))
    sp1 = sprites['poison_mushroom'].resize((64, 64), Image.Resampling.NEAREST)
    bg.paste(sp1, (col1_x + 25, card1_y + 25), sp1)
    draw.text((col1_x + 105, card1_y + 15), "Crimson Toadstool (Poisonous)", fill=(255, 120, 120, 255))
    draw.text((col1_x + 105, card1_y + 35), "Visual: Scarlet cap with pale white warts", fill=(210, 200, 200, 255))
    draw.text((col1_x + 105, card1_y + 55), "Effect: -50 HP (Takes 50% Life Loss!)", fill=(255, 80, 80, 255))
    draw.text((col1_x + 105, card1_y + 75), "Energy: -25 Energy | Gather: By Hand [E]", fill=(180, 160, 160, 255))
    draw.text((col1_x + 105, card1_y + 92), "Locations: 10 patches (Camp North, East, River)", fill=(160, 200, 230, 255))

    # Item 2: Nightshade Berries
    card2_y = 275
    draw.rectangle([col1_x + 15, card2_y, col1_x + 420, card2_y + 115], fill=(48, 30, 35, 255), outline=(120, 45, 55, 255))
    sp2 = sprites['poison_berry'].resize((64, 64), Image.Resampling.NEAREST)
    bg.paste(sp2, (col1_x + 25, card2_y + 25), sp2)
    draw.text((col1_x + 105, card2_y + 15), "Nightshade Berries (Poisonous)", fill=(255, 120, 120, 255))
    draw.text((col1_x + 105, card2_y + 35), "Visual: Deceptively shiny dark red clusters", fill=(210, 200, 200, 255))
    draw.text((col1_x + 105, card2_y + 55), "Effect: -50 HP (Takes 50% Life Loss!)", fill=(255, 80, 80, 255))
    draw.text((col1_x + 105, card2_y + 75), "Energy: -25 Energy | Yield: 2 Berries", fill=(180, 160, 160, 255))
    draw.text((col1_x + 105, card2_y + 92), "Locations: 7 bushes (Thicket, Camp Edge, River)", fill=(160, 200, 230, 255))

    # Warning Box
    draw.rectangle([col1_x + 15, 405, col1_x + 420, 625], fill=(30, 20, 24, 255), outline=(180, 50, 60, 255), width=2)
    draw.text((col1_x + 25, 420), "SURVIVAL WARNING:", fill=(255, 80, 80, 255))
    draw.text((col1_x + 25, 445), "- Consuming any poisonous item drops health by 50%.", fill=(240, 220, 220, 255))
    draw.text((col1_x + 25, 470), "- If HP is under 50%, eating poison triggers Game Over!", fill=(255, 160, 160, 255))
    draw.text((col1_x + 25, 495), "- Visual feedback: Screen flashes red alert banner:", fill=(210, 210, 210, 255))
    draw.rectangle([col1_x + 35, 525, col1_x + 400, 565], fill=(120, 25, 35, 255), outline=(220, 60, 70, 255))
    draw.text((col1_x + 50, 536), "\"Agh! That was poisonous! (-50 HP)\"", fill=(255, 255, 255, 255))
    draw.text((col1_x + 25, 580), "- Keybindings: [E] Pick up, [F] or Right-Click to Eat", fill=(140, 220, 160, 255))

    # Column 2: EDIBLE & RESTORATIVE FORAGE
    col2_x = 495
    draw.rectangle([col2_x, 90, col2_x + 435, 640], fill=(24, 36, 30, 255), outline=(50, 160, 90, 255), width=2)
    # Header badge
    draw.rectangle([col2_x, 90, col2_x + 435, 130], fill=(30, 110, 65, 255))
    draw.text((col2_x + 20, 102), "EDIBLE & NOURISHING VARIETIES (SAFE TO EAT)", fill=(240, 255, 240, 255))

    # List of safe items
    safe_items = [
        ('Island Morel', 'mushroom', "+22 Hunger, +8 HP, +12 Energy", "Camp trail & woods (7 nodes)", (180, 140, 90, 255)),
        ('Golden Chanterelle', 'chanterelle', "+24 Hunger, +12 HP, +15 Energy", "Clearing & river trail (6 nodes)", (240, 200, 70, 255)),
        ('Purple Cave Mushroom', 'purple_mushroom', "+20 Hunger, +15 HP, +20 Energy", "Shaded cliffs & ridges (5 nodes)", (200, 120, 240, 255)),
        ('Honeycomb Morel', 'morel', "+25 Hunger, +10 HP, +15 Energy", "Ancient woods & deep grove", (200, 170, 110, 255)),
        ('Wild Berries', 'berry', "+15 Hunger, +5 Energy (Sweet Salmonberry)", "Directly beside camp (7 bushes)", (240, 90, 100, 255)),
        ('Wild Blackberry', 'blackberry', "+16 Hunger, +4 HP, +8 Energy", "Camp west & pine trail (6 bushes)", (120, 110, 200, 255)),
    ]

    for idx, (title, key, stats, loc, color) in enumerate(safe_items):
        item_y = 145 + idx * 80
        draw.rectangle([col2_x + 15, item_y, col2_x + 420, item_y + 72], fill=(30, 45, 38, 255), outline=(55, 95, 75, 255))
        sp = sprites[key].resize((48, 48), Image.Resampling.NEAREST)
        bg.paste(sp, (col2_x + 25, item_y + 12), sp)
        draw.text((col2_x + 85, item_y + 10), title, fill=color)
        draw.text((col2_x + 85, item_y + 28), stats, fill=(120, 240, 150, 255))
        draw.text((col2_x + 85, item_y + 46), loc, fill=(180, 200, 210, 255))

    out_path = 'C:/Users/PAVILION/.gemini/antigravity-ide/brain/b46c14a7-7143-4bd0-a671-642ef3f589e7/forage_mushroom_berry_guide.png'
    bg.save(out_path)
    bg.save('scratch/forage_mushroom_berry_guide.png')
    print("Saved guide to", out_path)

if __name__ == '__main__':
    create_forage_guide()
