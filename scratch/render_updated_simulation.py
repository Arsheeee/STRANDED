import os
import json
from PIL import Image, ImageDraw

def render():
    # 1. Load assets
    boulder = Image.open('Assets/Art/Environment/Rocks/rock_boulder_large.png').convert('RGBA')
    driftwood = Image.open('Assets/Art/Environment/Trees/driftwood_log.png').convert('RGBA')
    bush_full = Image.open('Assets/Art/Environment/Plants/bush_berry_full.png').convert('RGBA')
    bush_empty = Image.open('Assets/Art/Environment/Plants/bush_berry_empty.png').convert('RGBA')
    
    tree_tropical = Image.open('Assets/Art/Environment/Trees/tree_tropical_mature.png').convert('RGBA')
    tree_pine = Image.open('Assets/Art/Environment/Trees/tree_pine_mature.png').convert('RGBA')
    tree_sakura = Image.open('Assets/Art/Environment/Trees/tree_sakura_mature.png').convert('RGBA')
    tree_birch = Image.open('Assets/Art/Environment/Trees/tree_birch_mature.png').convert('RGBA')
    tree_palm = Image.open('Assets/Art/Environment/Trees/palm_coconut_full.png').convert('RGBA')
    
    # 2. Build Showcase Images
    # Showcase 1: The Fixes (White Tent -> Boulder, Wooden Fence -> Driftwood, Bush -> Smaller Bush)
    card_w, card_h = 760, 260
    showcase1 = Image.new('RGBA', (card_w, card_h), (34, 38, 46, 255))
    draw = ImageDraw.Draw(showcase1)
    
    # Draw comparison sections
    # A: Boulder replacement
    draw.rectangle([20, 20, 240, 240], fill=(45, 52, 64, 255), outline=(70, 80, 100, 255), width=2)
    draw.text((35, 30), "REPLACED: Rock Boulder", fill=(255, 255, 255, 255))
    draw.text((35, 50), "Old: White Tent Removed", fill=(240, 120, 120, 255))
    draw.text((35, 68), "New: Natural Stone Boulder", fill=(120, 230, 140, 255))
    # Paste boulder scaled 3x
    boulder_3x = boulder.resize((96, 96), Image.Resampling.NEAREST)
    showcase1.paste(boulder_3x, (82, 110), boulder_3x)
    
    # B: Driftwood replacement
    draw.rectangle([260, 20, 480, 240], fill=(45, 52, 64, 255), outline=(70, 80, 100, 255), width=2)
    draw.text((275, 30), "REPLACED: Driftwood Log", fill=(255, 255, 255, 255))
    draw.text((275, 50), "Old: Wooden Fence Removed", fill=(240, 120, 120, 255))
    draw.text((275, 68), "New: Hollow Driftwood Log", fill=(120, 230, 140, 255))
    # Paste driftwood scaled 3x
    driftwood_3x = driftwood.resize((96, 96), Image.Resampling.NEAREST)
    showcase1.paste(driftwood_3x, (322, 110), driftwood_3x)
    
    # C: Bush Resizing
    draw.rectangle([500, 20, 740, 240], fill=(45, 52, 64, 255), outline=(70, 80, 100, 255), width=2)
    draw.text((515, 30), "RESIZED: Berry Bush", fill=(255, 255, 255, 255))
    draw.text((515, 50), "Old: 32x32 (Oversized)", fill=(240, 120, 120, 255))
    draw.text((515, 68), "New: Compact 24x24 Bush", fill=(120, 230, 140, 255))
    # Paste bush full & empty scaled 3x
    bush_f3x = bush_full.resize((72, 72), Image.Resampling.NEAREST)
    bush_e3x = bush_empty.resize((72, 72), Image.Resampling.NEAREST)
    showcase1.paste(bush_f3x, (530, 122), bush_f3x)
    showcase1.paste(bush_e3x, (635, 122), bush_e3x)
    
    showcase1.save('scratch/showcase_replacements.png')
    print('Saved scratch/showcase_replacements.png')
    
    # Showcase 2: Tree Varieties Showcase
    tree_w, tree_h = 820, 280
    showcase2 = Image.new('RGBA', (tree_w, tree_h), (28, 34, 42, 255))
    draw2 = ImageDraw.Draw(showcase2)
    
    draw2.text((20, 15), "STRANDED: Tree Varieties Added From Attachment", fill=(255, 220, 120, 255))
    
    tree_defs = [
        ("Tropical Oak", tree_tropical, 30, "Lush Forest & Camp"),
        ("Conifer Pine", tree_pine, 190, "Plateau & Highlands"),
        ("Pink Sakura", tree_sakura, 350, "Scenic Groves & Meadows"),
        ("Slender Birch", tree_birch, 520, "Forest & Clearings"),
        ("Coconut Palm", tree_palm, 670, "Tropical Beaches"),
    ]
    
    for name, sp, x_pos, desc in tree_defs:
        # box
        draw2.rectangle([x_pos - 10, 45, x_pos + 130, 260], fill=(40, 48, 60, 255), outline=(65, 78, 95, 255), width=1)
        draw2.text((x_pos - 4, 52), name, fill=(255, 255, 255, 255))
        draw2.text((x_pos - 4, 70), desc, fill=(180, 200, 220, 255))
        
        # Scale tree 2x
        scaled = sp.resize((sp.width * 2, sp.height * 2), Image.Resampling.NEAREST)
        # bottom align inside box
        by = 250 - scaled.height
        bx = x_pos + 60 - (scaled.width // 2)
        showcase2.paste(scaled, (bx, by), scaled)
        
    showcase2.save('scratch/showcase_trees.png')
    print('Saved scratch/showcase_trees.png')

render()
