import os
import json
from PIL import Image

def build_view(bg_path, target_coords, objects, output_path, desc):
    # Take background capture as base or template
    if not os.path.exists(bg_path):
        print(f"Background {bg_path} missing")
        return
    base = Image.open(bg_path).convert('RGBA')
    
    # Render updated objects over matching positions
    # Scale factor from world coordinates:
    # 960x540 camera with orthoSize 6.5 -> 13 units high -> ~41.538 pixels per unit!
    ppu = 540.0 / 13.0
    cam_x, cam_y = target_coords
    
    # Sort objects by -Y for correct Y-depth sorting
    objects.sort(key=lambda o: -o[1])
    
    for sprite, wx, wy in objects:
        # Screen position
        screen_x = 480.0 + (wx - cam_x) * ppu
        screen_y = 270.0 - (wy - cam_y) * ppu
        
        # Sprite scale to match world units at 16 PPU in world:
        # 16 sprite pixels = 1.0 world unit = 41.538 screen pixels
        # Scale = 41.538 / 16.0 = ~2.596
        scale = ppu / 16.0
        sw = int(sprite.width * scale)
        sh = int(sprite.height * scale)
        scaled_sp = sprite.resize((sw, sh), Image.Resampling.NEAREST)
        
        # Pivot is {0.5, 0} (bottom center)
        paste_x = int(screen_x - (sw / 2.0))
        paste_y = int(screen_y - sh)
        
        if 0 <= paste_x < 960 and 0 <= paste_y < 540:
            base.paste(scaled_sp, (paste_x, paste_y), scaled_sp)
            
    base.save(output_path)
    print(f"Saved {output_path} ({desc})")

def main():
    boulder = Image.open('Assets/Art/Environment/Rocks/rock_boulder_large.png').convert('RGBA')
    driftwood = Image.open('Assets/Art/Environment/Trees/driftwood_log.png').convert('RGBA')
    bush = Image.open('Assets/Art/Environment/Plants/bush_berry_full.png').convert('RGBA')
    tree_tropical = Image.open('Assets/Art/Environment/Trees/tree_tropical_mature.png').convert('RGBA')
    tree_pine = Image.open('Assets/Art/Environment/Trees/tree_pine_mature.png').convert('RGBA')
    tree_sakura = Image.open('Assets/Art/Environment/Trees/tree_sakura_mature.png').convert('RGBA')
    tree_birch = Image.open('Assets/Art/Environment/Trees/tree_birch_mature.png').convert('RGBA')
    tree_palm = Image.open('Assets/Art/Environment/Trees/palm_coconut_full.png').convert('RGBA')
    
    # 1. Mountain Plateau
    plateau_objs = [
        (boulder, 235.0, 198.0),
        (boulder, 242.0, 194.0),
        (boulder, 237.5, 192.5),
        (tree_pine, 239.0, 199.0),
        (tree_pine, 233.0, 195.0),
    ]
    build_view('scratch/batch2_mountain_plateau_rocks.png', (238.0, 196.0), plateau_objs, 'scratch/updated_mountain_plateau.png', "Mountain Plateau with Boulder Rocks & Pines")
    
    # 2. South Beach
    beach_objs = [
        (driftwood, 133.0, 74.0),
        (driftwood, 138.5, 73.5),
        (tree_palm, 132.0, 76.5),
        (tree_palm, 139.0, 77.0),
    ]
    build_view('scratch/batch2_tropical_beach_coconuts.png', (135.5, 75.0), beach_objs, 'scratch/updated_south_beach.png', "South Beach with Driftwood Logs & Palms")
    
    # 3. Forest Grove
    forest_objs = [
        (tree_sakura, 103.0, 178.0),
        (tree_birch, 108.0, 177.5),
        (tree_pine, 101.5, 173.0),
        (tree_tropical, 107.5, 172.5),
        (bush, 104.5, 174.5),
        (bush, 106.0, 175.0),
    ]
    build_view('scratch/batch2_lush_forest_grove.png', (105.0, 175.0), forest_objs, 'scratch/updated_forest_grove.png', "Lush Forest Grove with Tree Varieties & Smaller Bushes")

main()
