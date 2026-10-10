import os
from PIL import Image

TERRAIN_DIR = "Assets/Art/Terrain"

paths_to_test = [
    f"{TERRAIN_DIR}/Grass/grass_base_01.png",
    f"{TERRAIN_DIR}/Sand/sand_base_01.png",
    f"{TERRAIN_DIR}/Dirt/mud_base_01.png",
    f"{TERRAIN_DIR}/Water/Sea/sea_deep_base_01.png",
    f"{TERRAIN_DIR}/Water/Sea/sea_shallow_base_01.png",
    f"{TERRAIN_DIR}/Water/River/river_water_base_01.png",
    f"{TERRAIN_DIR}/Cliffs/cliff_face_top_01.png",
    f"{TERRAIN_DIR}/Cliffs/cliff_face_bot_01.png",
    f"{TERRAIN_DIR}/Cliffs/cliff_mud_steps_top.png",
    f"{TERRAIN_DIR}/Cliffs/cliff_mud_steps_bot.png",
    f"{TERRAIN_DIR}/Transitions/Sand_Water/sand_water_edge_n_01.png",
    f"{TERRAIN_DIR}/Transitions/Grass_Sand/grass_sand_edge_n_01.png",
    f"{TERRAIN_DIR}/Transitions/Grass_Dirt/grass_dirt_edge_n_01.png",
    f"{TERRAIN_DIR}/Transitions/Grass_RiverWater/grass_riverwater_edge_n_01.png",
]

all_ok = True
for p in paths_to_test:
    if os.path.exists(p):
        im = Image.open(p)
        print(f"OK: {p} ({im.size}, {im.mode})")
    else:
        print(f"MISSING: {p}")
        all_ok = False

print(f"All tested: {all_ok}")
