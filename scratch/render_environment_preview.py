"""
Render Environment Preview for STRANDED Batch 11 / Polish.
Visualizes:
1. Shrunk Wild Fern & Coastal Fiber tuft
2. Shrunk Driftwood log
3. New Tree varieties (Sakura, Maple, Mahogany, Spruce, Pine, Birch, Tropical)
4. New Bush varieties (Berry, Small green shrub, Medium foliage, Flowering pink, Flowering white, Autumn golden)
5. Clean, open interior meadow (no oversized boulders blocking paths)
"""
import os
from PIL import Image, ImageDraw, ImageFont

def create_preview():
    W, H = 1200, 750
    img = Image.new("RGBA", (W, H), (26, 32, 44, 255))
    draw = ImageDraw.Draw(img)

    # Title Banner
    draw.rectangle([0, 0, W, 70], fill=(15, 23, 42, 255))
    draw.line([(0, 70), (W, 70)], fill=(71, 85, 105, 255), width=2)

    # Draw Title text
    try:
        font_title = ImageFont.truetype("arial.ttf", 26)
        font_sub = ImageFont.truetype("arial.ttf", 16)
        font_card = ImageFont.truetype("arial.ttf", 14)
        font_label = ImageFont.truetype("arial.ttf", 12)
    except:
        font_title = font_sub = font_card = font_label = None

    draw.text((30, 15), "STRANDED — Environmental Art & Resource Polish", fill=(248, 250, 252), font=font_title)
    draw.text((30, 45), "Pixel-Perfect Handcrafted Proportions, Shrunk Ferns/Driftwood & Boulder-Free Interior Plains", fill=(148, 163, 184), font=font_sub)

    # Panels
    panels = [
        ("1. Proportion Fix: Shrunk Fern & Driftwood", 30, 90, 560, 300),
        ("2. Tree Diversity: 7 Seasonal & Tropical Species", 610, 90, 560, 300),
        ("3. Bush & Shrub Variations (Berries + Foliage)", 30, 410, 560, 310),
        ("4. Clean Interior Plains (Zero Giant Boulders)", 610, 410, 560, 310)
    ]

    for title, x, y, w, h in panels:
        draw.rectangle([x, y, x + w, y + h], fill=(30, 41, 59, 255), outline=(51, 65, 85, 255), width=2)
        draw.rectangle([x, y, x + w, y + 34], fill=(15, 23, 42, 255))
        draw.text((x + 15, y + 8), title, fill=(226, 232, 240), font=font_card)

    # Panel 1: Shrunk fern & driftwood
    # Load and paste plant_fiber_fern and driftwood_log
    assets = {
        "fern": "Assets/Art/Environment/Plants/plant_fiber_fern.png",
        "tuft": "Assets/Art/Environment/Plants/plant_fiber_tuft.png",
        "grass": "Assets/Art/Environment/Plants/plant_grass_wild.png",
        "driftwood": "Assets/Art/Environment/Trees/driftwood_log.png",
    }
    loaded = {}
    for k, p in assets.items():
        if os.path.exists(p):
            loaded[k] = Image.open(p).convert("RGBA")

    # Display Fern (scaled 3x pixel art)
    if "fern" in loaded:
        f_img = loaded["fern"].resize((loaded["fern"].width * 3, loaded["fern"].height * 3), Image.NEAREST)
        img.paste(f_img, (70, 160), f_img)
        draw.text((60, 260), "Wild Fern (32x32)\nTile-accurate 1x1\nYields: 1 Fiber", fill=(203, 213, 225), font=font_label)

    if "tuft" in loaded:
        t_img = loaded["tuft"].resize((loaded["tuft"].width * 3, loaded["tuft"].height * 3), Image.NEAREST)
        img.paste(t_img, (200, 170), t_img)
        draw.text((190, 260), "Coastal Fiber (24x24)\nBeach/coastal tuft\nYields: 1 Fiber", fill=(203, 213, 225), font=font_label)

    if "driftwood" in loaded:
        d_img = loaded["driftwood"].resize((loaded["driftwood"].width * 2, loaded["driftwood"].height * 2), Image.NEAREST)
        img.paste(d_img, (330, 185), d_img)
        draw.text((330, 260), "Driftwood Log (48x24)\nCompact beach log\nYields: 2 Wood", fill=(203, 213, 225), font=font_label)

    # Panel 2: Trees
    trees = [
        ("Spruce", "Assets/Art/Environment/Trees/tree_spruce_mature.png"),
        ("Maple", "Assets/Art/Environment/Trees/tree_maple_mature.png"),
        ("Birch", "Assets/Art/Environment/Trees/tree_birch_mature.png"),
        ("Pine", "Assets/Art/Environment/Trees/tree_pine_mature.png"),
        ("Mahogany", "Assets/Art/Environment/Trees/tree_mahogany_mature.png"),
        ("Tropical", "Assets/Art/Environment/Trees/tree_tropical_mature.png"),
    ]
    t_x = 625
    for name, p in trees:
        if os.path.exists(p):
            t_im = Image.open(p).convert("RGBA")
            # Scale down to fit preview height ~110px
            ratio = 110.0 / t_im.height
            nw, nh = int(t_im.width * ratio), int(t_im.height * ratio)
            t_im_scaled = t_im.resize((nw, nh), Image.NEAREST)
            img.paste(t_im_scaled, (t_x, 150), t_im_scaled)
            draw.text((t_x + 5, 275), name, fill=(203, 213, 225), font=font_label)
            t_x += nw + 12

    # Panel 3: Bushes
    bushes = [
        ("Berry Bush", "Assets/Art/Environment/Plants/bush_berry_full.png"),
        ("Pink Flower", "Assets/Art/Environment/Plants/bush_flowering_pink.png"),
        ("White Flower", "Assets/Art/Environment/Plants/bush_flowering_white.png"),
        ("Forest Foliage", "Assets/Art/Environment/Plants/bush_foliage_medium.png"),
        ("Small Shrub", "Assets/Art/Environment/Plants/bush_shrub_small.png"),
        ("Golden Shrub", "Assets/Art/Environment/Plants/bush_autumn_golden.png"),
    ]
    b_x = 45
    for name, p in bushes:
        if os.path.exists(p):
            b_im = Image.open(p).convert("RGBA")
            nw, nh = b_im.width * 2, b_im.height * 2
            b_im_scaled = b_im.resize((nw, nh), Image.NEAREST)
            img.paste(b_im_scaled, (b_x, 490), b_im_scaled)
            draw.text((b_x, 570), name, fill=(203, 213, 225), font=font_label)
            b_x += 88

    # Panel 4: Interior Plains without boulders
    # Draw simulated meadow with player, small pebbles, shrubs, birch tree
    draw.rectangle([620, 455, 1150, 690], fill=(74, 128, 48, 255), outline=(45, 90, 25, 255))
    draw.text((635, 465), "Interior Grassy Clearing (Clean & Open Navigation):", fill=(255, 255, 255), font=font_card)
    draw.text((635, 490), "• Giant Boulders moved to Mountain Highlands (Tile 7)\n• Plains decorated with small pebbles, slate rocks & shrubs\n• Player can freely traverse without path obstruction\n• Balanced yield & pristine visual clarity", fill=(220, 245, 200), font=font_label)

    # Paste some rocks/shrubs
    rock_small_p = "Assets/Art/Environment/Rocks/rock_slate_small.png"
    rock_med_p = "Assets/Art/Environment/Rocks/rock_slate_medium.png"
    shrub_p = "Assets/Art/Environment/Plants/bush_shrub_small.png"
    if os.path.exists(rock_small_p):
        r1 = Image.open(rock_small_p).convert("RGBA")
        r1 = r1.resize((r1.width*2, r1.height*2), Image.NEAREST)
        img.paste(r1, (700, 610), r1)
        img.paste(r1, (950, 630), r1)
    if os.path.exists(rock_med_p):
        r2 = Image.open(rock_med_p).convert("RGBA")
        r2 = r2.resize((r2.width*2, r2.height*2), Image.NEAREST)
        img.paste(r2, (830, 590), r2)
    if os.path.exists(shrub_p):
        s1 = Image.open(shrub_p).convert("RGBA")
        s1 = s1.resize((s1.width*2, s1.height*2), Image.NEAREST)
        img.paste(s1, (640, 580), s1)
        img.paste(s1, (1040, 600), s1)

    os.makedirs("scratch", exist_ok=True)
    out_path = "scratch/environment_polish_showcase.png"
    img.save(out_path)
    print("Saved preview to:", out_path)

if __name__ == "__main__":
    create_preview()
