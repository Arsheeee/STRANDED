import os
import math
import random
from PIL import Image

WORLD_W = 350
WORLD_H = 350
TILE_SIZE = 16

OCEAN_DEEP = 0
OCEAN_SHALLOW = 1
BEACH_SAND = 2
GRASS_BASE = 3
DIRT_PATH = 4
RIVER_WATER = 5
CLIFF_WALL = 6
CLIFF_TOP = 7

# Assets root
TERRAIN_DIR = "Assets/Art/Terrain"

class ValueNoise2D:
    def __init__(self, seed=42):
        rng = random.Random(seed)
        self.p = list(range(256))
        rng.shuffle(self.p)
        self.p = self.p + self.p

    def _fade(self, t):
        return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)

    def _lerp(self, a, b, t):
        return a + t * (b - a)

    def _grad(self, hash_val, x, y):
        h = hash_val & 3
        u = x if h & 1 == 0 else -x
        v = y if h & 2 == 0 else -y
        return u + v

    def sample(self, x, y):
        xi = int(math.floor(x)) & 255
        yi = int(math.floor(y)) & 255
        xf = x - math.floor(x)
        yf = y - math.floor(y)

        u = self._fade(xf)
        v = self._fade(yf)

        aa = self.p[self.p[xi] + yi]
        ab = self.p[self.p[xi] + yi + 1]
        ba = self.p[self.p[xi + 1] + yi]
        bb = self.p[self.p[xi + 1] + yi + 1]

        x1 = self._lerp(self._grad(aa, xf, yf), self._grad(ba, xf - 1.0, yf), u)
        x2 = self._lerp(self._grad(ab, xf, yf - 1.0), self._grad(bb, xf - 1.0, yf - 1.0), u)
        return self._lerp(x1, x2, v)

    def fbm(self, x, y, octaves=4, lacunarity=2.0, persistence=0.5):
        total = 0.0
        freq = 1.0
        amp = 1.0
        max_val = 0.0
        for _ in range(octaves):
            total += self.sample(x * freq, y * freq) * amp
            max_val += amp
            amp *= persistence
            freq *= lacunarity
        return total / max_val


def compute_dist_to_water(land_mask):
    INF = 9999.0
    dist = [[0.0 if not land_mask[y][x] else INF for x in range(WORLD_W)] for y in range(WORLD_H)]
    SQ2 = 1.4142

    for y in range(WORLD_H):
        for x in range(WORLD_W):
            if dist[y][x] == 0.0: continue
            min_d = dist[y][x]
            if y > 0:
                min_d = min(min_d, dist[y - 1][x] + 1.0)
                if x > 0: min_d = min(min_d, dist[y - 1][x - 1] + SQ2)
                if x < WORLD_W - 1: min_d = min(min_d, dist[y - 1][x + 1] + SQ2)
            if x > 0:
                min_d = min(min_d, dist[y][x - 1] + 1.0)
            dist[y][x] = min_d

    for y in range(WORLD_H - 1, -1, -1):
        for x in range(WORLD_W - 1, -1, -1):
            if dist[y][x] == 0.0: continue
            min_d = dist[y][x]
            if y < WORLD_H - 1:
                min_d = min(min_d, dist[y + 1][x] + 1.0)
                if x > 0: min_d = min(min_d, dist[y + 1][x - 1] + SQ2)
                if x < WORLD_W - 1: min_d = min(min_d, dist[y + 1][x + 1] + SQ2)
            if x < WORLD_W - 1:
                min_d = min(min_d, dist[y][x + 1] + 1.0)
            dist[y][x] = min_d

    return dist


def compute_dist_to_land(land_mask):
    INF = 9999.0
    dist = [[0.0 if land_mask[y][x] else INF for x in range(WORLD_W)] for y in range(WORLD_H)]
    SQ2 = 1.4142

    for y in range(WORLD_H):
        for x in range(WORLD_W):
            if dist[y][x] == 0.0: continue
            min_d = dist[y][x]
            if y > 0:
                min_d = min(min_d, dist[y - 1][x] + 1.0)
                if x > 0: min_d = min(min_d, dist[y - 1][x - 1] + SQ2)
                if x < WORLD_W - 1: min_d = min(min_d, dist[y - 1][x + 1] + SQ2)
            if x > 0:
                min_d = min(min_d, dist[y][x - 1] + 1.0)
            dist[y][x] = min_d

    for y in range(WORLD_H - 1, -1, -1):
        for x in range(WORLD_W - 1, -1, -1):
            if dist[y][x] == 0.0: continue
            min_d = dist[y][x]
            if y < WORLD_H - 1:
                min_d = min(min_d, dist[y + 1][x] + 1.0)
                if x > 0: min_d = min(min_d, dist[y + 1][x - 1] + SQ2)
                if x < WORLD_W - 1: min_d = min(min_d, dist[y + 1][x + 1] + SQ2)
            if x < WORLD_W - 1:
                min_d = min(min_d, dist[y][x + 1] + 1.0)
            dist[y][x] = min_d

    return dist


def generate_island_mask(seed=2026):
    noise_macro = ValueNoise2D(seed)
    noise_detail = ValueNoise2D(seed + 101)
    noise_micro = ValueNoise2D(seed + 202)

    cx, cy = 175.0, 175.0
    land_mask = [[False for _ in range(WORLD_W)] for _ in range(WORLD_H)]

    for y in range(WORLD_H):
        for x in range(WORLD_W):
            # Strict safety margin: at least 42 tiles of deep ocean around all edges
            if x < 42 or x > WORLD_W - 43 or y < 42 or y > WORLD_H - 43:
                continue

            dx = x - cx
            dy = y - cy
            dist = math.sqrt(dx * dx + dy * dy)
            angle = math.atan2(dy, dx)

            base_r = 114.0

            # 1. Eastern Highlands Lobe (+x, angle ~ 0)
            r_mod = 1.0 + 0.19 * math.cos(angle - 0.10)
            
            # 2. Southwestern Camp & Savanna Lobe (-x, -y, angle ~ -2.25)
            diff_sw = angle - (-2.25)
            while diff_sw > math.pi: diff_sw -= 2*math.pi
            while diff_sw < -math.pi: diff_sw += 2*math.pi
            r_mod += 0.18 * math.exp(-(diff_sw ** 2) / 0.65)

            # 3. Northwestern Hook Peninsula (+y, -x, angle ~ 2.22)
            diff_nw = angle - 2.22
            while diff_nw > math.pi: diff_nw -= 2*math.pi
            while diff_nw < -math.pi: diff_nw += 2*math.pi
            r_mod += 0.29 * math.exp(-(diff_nw ** 2) / 0.38)

            # 4. Northern Rainforest Headland (+y, angle ~ 1.25)
            diff_n = angle - 1.25
            while diff_n > math.pi: diff_n -= 2*math.pi
            while diff_n < -math.pi: diff_n += 2*math.pi
            r_mod += 0.13 * math.exp(-(diff_n ** 2) / 0.35)

            # 5. Southern Crescent Lagoon Bay (-y, angle ~ -1.20)
            diff_s = angle - (-1.20)
            while diff_s > math.pi: diff_s -= 2*math.pi
            while diff_s < -math.pi: diff_s += 2*math.pi
            r_mod -= 0.23 * math.exp(-(diff_s ** 2) / 0.35)

            # 6. Northwestern Escape Cove Bay (angle ~ 1.76)
            diff_nwb = angle - 1.76
            while diff_nwb > math.pi: diff_nwb -= 2*math.pi
            while diff_nwb < -math.pi: diff_nwb += 2*math.pi
            r_mod -= 0.29 * math.exp(-(diff_nwb ** 2) / 0.20)

            # 7. Western Mid-Coast Bay indentation (angle ~ 2.90)
            diff_w = angle - 2.90
            while diff_w > math.pi: diff_w -= 2*math.pi
            while diff_w < -math.pi: diff_w += 2*math.pi
            r_mod -= 0.18 * math.exp(-(diff_w ** 2) / 0.28)

            # 8. Southwestern Coastal Cape (angle ~ -2.95)
            diff_swc = angle - (-2.95)
            while diff_swc > math.pi: diff_swc -= 2*math.pi
            while diff_swc < -math.pi: diff_swc += 2*math.pi
            r_mod += 0.12 * math.exp(-(diff_swc ** 2) / 0.20)

            target_r = base_r * r_mod

            # Multi-octave natural fractal noise
            n_macro = noise_macro.fbm(x * 0.018, y * 0.018, octaves=3) * 25.0
            n_det = noise_detail.fbm(x * 0.048, y * 0.048, octaves=3) * 11.0
            n_mic = noise_micro.sample(x * 0.12, y * 0.12) * 3.5

            perturbed_dist = dist - (n_macro + n_det + n_mic)

            if perturbed_dist < target_r:
                land_mask[y][x] = True

    # Cellular smoothing pass
    for _ in range(2):
        new_land = [row[:] for row in land_mask]
        for y in range(1, WORLD_H - 1):
            for x in range(1, WORLD_W - 1):
                cnt = sum(land_mask[ny][nx] for ny in range(y - 1, y + 2) for nx in range(x - 1, x + 2))
                if land_mask[y][x] and cnt < 4:
                    new_land[y][x] = False
                elif not land_mask[y][x] and cnt >= 6:
                    new_land[y][x] = True
        land_mask = new_land

    return land_mask


def generate_base_island():
    print("Generating base island geometry (350x350) - Iteration 3...")
    land_mask = generate_island_mask(seed=2026)
    
    print("Calculating coastal distance fields...")
    dist_to_land = compute_dist_to_land(land_mask)
    dist_to_water = compute_dist_to_water(land_mask)

    world = [[OCEAN_DEEP for _ in range(WORLD_W)] for _ in range(WORLD_H)]
    cliff_map = [[None for _ in range(WORLD_W)] for _ in range(WORLD_H)]

    noise_shelf = ValueNoise2D(seed=3033)
    noise_beach = ValueNoise2D(seed=4044)

    # 1. Water & Beach Classification
    for y in range(WORLD_H):
        for x in range(WORLD_W):
            if not land_mask[y][x]:
                # Variable shallow water shelf (5 to 11 tiles)
                ns = noise_shelf.sample(x * 0.03, y * 0.03) * 2.5
                shelf_w = 6.0 + ns
                # In bays, widen shelf (coral reef lagoons)
                if (160 < x < 230 and 50 < y < 110) or (80 < x < 140 and 200 < y < 265):
                    shelf_w += 4.5

                if dist_to_land[y][x] <= shelf_w:
                    world[y][x] = OCEAN_SHALLOW
                else:
                    world[y][x] = OCEAN_DEEP
            else:
                # Land: Beach Sand vs Interior Grass
                nb = noise_beach.sample(x * 0.035, y * 0.035) * 2.5
                beach_w = 4.5 + nb
                # Broad white sand beaches in bays (Escape Cove & South Crescent Lagoon)
                if (80 < x < 140 and 200 < y < 265) or (140 < x < 220 and 60 < y < 115):
                    beach_w += 5.0
                # Narrow beach on rocky eastern/northern bluffs
                if (x > 260 and 150 < y < 245) or (y > 270 and 165 < x < 225):
                    beach_w = max(2.5, beach_w - 2.5)

                if dist_to_water[y][x] <= beach_w:
                    world[y][x] = BEACH_SAND
                else:
                    world[y][x] = GRASS_BASE

    # 2. Handcrafted Eastern Cliff Plateau (X: 236..282, Y: 190..236)
    print("Sculpting Handcrafted Eastern Cliff Plateau...")
    cliff_mask = [[False for _ in range(WORLD_W)] for _ in range(WORLD_H)]
    noise_cliff = ValueNoise2D(seed=5055)

    # The plateau is an elevated tableland
    # South cliff wall is at Y=190..192
    # West cliff flank is at X=236..240
    # North and East face open toward the sea / bluffs
    for y in range(190, 238):
        for x in range(236, 282):
            if world[y][x] in (GRASS_BASE, BEACH_SAND):
                edge_noise = noise_cliff.fbm(x * 0.05, y * 0.05, octaves=2) * 5.0
                dx = (x - 258.0) / 22.0
                dy = (y - 214.0) / 23.0
                # Shape with southern flat wall and west canyon flank
                if dy > -0.85 and (dx*dx*0.8 + dy*dy) + edge_noise * 0.08 < 0.85:
                    cliff_mask[y][x] = True

    # Assign Plateau Top Ground
    for y in range(WORLD_H):
        for x in range(WORLD_W):
            if cliff_mask[y][x]:
                world[y][x] = CLIFF_TOP

    # Assign authentic Cliff Autotiles:
    # South wall: row Y=190 is bot, row Y=191 is top
    # West wall: X=leftmost is side_w
    # Corners: sw, se
    for y in range(1, WORLD_H - 2):
        for x in range(1, WORLD_W - 1):
            if not cliff_mask[y][x] and cliff_mask[y+1][x]:
                world[y][x] = CLIFF_WALL
                # South wall bot
                cliff_map[y][x] = "cliff_face_bot"
                cliff_map[y+1][x] = "cliff_face_top"
            elif cliff_mask[y][x]:
                if not cliff_mask[y][x-1]: # West edge
                    cliff_map[y][x] = "cliff_side_w_top"
                    cliff_map[y-1][x] = "cliff_side_w_bot"
                elif not cliff_mask[y][x+1]: # East edge
                    cliff_map[y][x] = "cliff_side_e_top"
                    cliff_map[y-1][x] = "cliff_side_e_bot"

    # Walkable Access Routes into Plateau:
    # 1. Southwestern Mud Steps at (X: 242..243, Y: 188..192)
    for sx in [242, 243]:
        for sy in [188, 189, 190, 191, 192]:
            world[sy][sx] = DIRT_PATH
            cliff_mask[sy][sx] = False
            cliff_map[sy][sx] = "cliff_mud_steps"

    # 2. Northwestern Cliff Ramp at (X: 236..238, Y: 226..229)
    for rx in [236, 237, 238]:
        for ry in [226, 227, 228, 229]:
            world[ry][rx] = DIRT_PATH
            cliff_mask[ry][rx] = False
            cliff_map[ry][rx] = "cliff_ramp"

    # 3. Winding Natural River System
    print("Simulating Winding River with Natural Meanders & Estuary Delta...")
    waypoints = [
        (262, 228), # Highland spring pool on plateau
        (248, 222), # Cascade through cliff canyon
        (235, 214), # Gorge exit into forest
        (215, 212), # Upper forest loop (curves west)
        (196, 196), # Meander around northern jungle spur
        (186, 174), # Upper valley reach
        (174, 155), # Central Ford / Shallow River Crossing
        (178, 136), # Curves southeast past central clearing
        (196, 126), # Broad eastern meander bend
        (198, 106), # Curves back southwest
        (186, 88),  # Approach to coastal plain
        (192, 74),  # Delta entrance
        (193, 62),  # Ocean mouth
    ]

    river_path = []
    for i in range(len(waypoints) - 1):
        p0 = waypoints[max(0, i - 1)]
        p1 = waypoints[i]
        p2 = waypoints[i + 1]
        p3 = waypoints[min(len(waypoints) - 1, i + 2)]

        steps = 45
        for s in range(steps):
            t = s / float(steps)
            t2 = t * t
            t3 = t2 * t
            x = 0.5 * ((2.0 * p1[0]) + (-p0[0] + p2[0]) * t + (2.0*p0[0] - 5.0*p1[0] + 4.0*p2[0] - p3[0]) * t2 + (-p0[0] + 3.0*p1[0] - 3.0*p2[0] + p3[0]) * t3)
            y = 0.5 * ((2.0 * p1[1]) + (-p0[1] + p2[1]) * t + (2.0*p0[1] - 5.0*p1[1] + 4.0*p2[1] - p3[1]) * t2 + (-p0[1] + 3.0*p1[1] - 3.0*p2[1] + p3[1]) * t3)
            river_path.append((x, y))

    river_mask = [[False for _ in range(WORLD_W)] for _ in range(WORLD_H)]
    ford_center = (174, 155)

    for idx, (rx, ry) in enumerate(river_path):
        progress = idx / float(len(river_path))
        # Variable width: 2 tiles near source, 4 tiles near delta
        r_rad = 1.2 + 1.0 * progress
        # Narrow crossing at Ford (1.0 rad = 2 tiles wide)
        d_to_ford = math.hypot(rx - ford_center[0], ry - ford_center[1])
        if d_to_ford < 6.0:
            r_rad = 1.0

        irx, iry = int(round(rx)), int(round(ry))
        rad_ceil = int(math.ceil(r_rad))
        for dy in range(-rad_ceil, rad_ceil + 1):
            for dx in range(-rad_ceil, rad_ceil + 1):
                if dx*dx + dy*dy <= r_rad * r_rad:
                    tx, ty = irx + dx, iry + dy
                    if 0 <= tx < WORLD_W and 0 <= ty < WORLD_H:
                        river_mask[ty][tx] = True

    # Spring Pool on plateau: circular pool at (262, 228)
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            if dx*dx + dy*dy <= 7.0:
                river_mask[228 + dy][262 + dx] = True

    # Delta Sandbar Island at (191, 70)
    delta_islet = set()
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            if dx*dx + dy*dy <= 3.5:
                delta_islet.add((191 + dx, 70 + dy))

    for y in range(WORLD_H):
        for x in range(WORLD_W):
            if (x, y) in delta_islet:
                world[y][x] = BEACH_SAND
            elif river_mask[y][x]:
                if world[y][x] not in (OCEAN_DEEP, OCEAN_SHALLOW):
                    world[y][x] = RIVER_WATER

    # Mud banks at Central Ford (174, 155)
    for fx, fy in [(172, 155), (173, 155), (175, 155), (176, 155)]:
        if world[fy][fx] == GRASS_BASE:
            world[fy][fx] = DIRT_PATH

    # 4. Starting Camp Area & Exploration Paths
    print("Carving Reserved Starting Camp Area & Radiating Paths...")
    camp_cx, camp_cy = 135, 120
    for dy in range(-8, 9):
        for dx in range(-8, 9):
            d2 = dx*dx + dy*dy
            tx, ty = camp_cx + dx, camp_cy + dy
            if 0 <= tx < WORLD_W and 0 <= ty < WORLD_H and world[ty][tx] in (GRASS_BASE, BEACH_SAND):
                if d2 <= 20.0:
                    world[ty][tx] = DIRT_PATH
                elif d2 <= 55.0:
                    if (dx + dy) % 3 == 0 or (dx*dy) % 5 == 0:
                        world[ty][tx] = DIRT_PATH
                    else:
                        world[ty][tx] = GRASS_BASE

    def carve_path(pts, width=1):
        for i in range(len(pts) - 1):
            p1 = pts[i]
            p2 = pts[i + 1]
            dist = int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) * 1.5) + 1
            for s in range(dist + 1):
                t = s / float(dist)
                px = int(round(p1[0] + (p2[0] - p1[0]) * t))
                py = int(round(p1[1] + (p2[1] - p1[1]) * t))
                for wdy in range(-width, width + 1):
                    for wdx in range(-width, width + 1):
                        if wdx*wdx + wdy*wdy <= width*width:
                            tx, ty = px + wdx, py + wdy
                            if 0 <= tx < WORLD_W and 0 <= ty < WORLD_H:
                                if world[ty][tx] in (GRASS_BASE, CLIFF_TOP):
                                    world[ty][tx] = DIRT_PATH

    # 4 Cardinal Exploration Paths from Starting Camp:
    carve_path([(135, 112), (134, 102), (136, 92), (135, 86)], width=1) # South to Beach
    carve_path([(127, 120), (114, 122), (102, 124), (90, 125)], width=1) # West to Bay
    carve_path([(143, 120), (154, 128), (164, 142), (172, 155)], width=1) # East to Ford
    carve_path([(135, 128), (138, 145), (144, 165), (148, 190)], width=1) # North to Jungle

    # Continuing Trails:
    carve_path([(176, 155), (192, 162), (214, 172), (240, 188)], width=1) # Ford to Cliff Steps
    carve_path([(144, 165), (134, 188), (122, 210), (110, 230)], width=1) # To Escape Cove
    carve_path([(148, 190), (160, 215), (175, 238), (185, 255)], width=1) # Deep Jungle Path

    # 5. Ecological Clearings & Special Landmark Areas:
    # A. Northwest Escape Cove clearing at (108, 236)
    for dy in range(-7, 8):
        for dx in range(-7, 8):
            if dx*dx + dy*dy <= 36.0:
                tx, ty = 108 + dx, 236 + dy
                if world[ty][tx] == GRASS_BASE:
                    world[ty][tx] = DIRT_PATH

    # B. Northern Jungle secluded glade at (175, 242)
    for dy in range(-6, 7):
        for dx in range(-6, 7):
            if dx*dx + dy*dy <= 25.0:
                tx, ty = 175 + dx, 242 + dy
                if world[ty][tx] == GRASS_BASE:
                    world[ty][tx] = DIRT_PATH

    # C. Eastern Plateau spring sanctuary at (266, 222)
    for dy in range(-6, 7):
        for dx in range(-6, 7):
            if dx*dx + dy*dy <= 28.0:
                tx, ty = 266 + dx, 222 + dy
                if world[ty][tx] == CLIFF_TOP:
                    world[ty][tx] = DIRT_PATH

    # D. River Bend Grove at (196, 126)
    for dy in range(-5, 6):
        for dx in range(-5, 6):
            if dx*dx + dy*dy <= 18.0:
                tx, ty = 196 + dx, 126 + dy
                if world[ty][tx] == GRASS_BASE:
                    world[ty][tx] = DIRT_PATH

    print("Base island classification completed successfully!")
    return world, land_mask, cliff_map


# ---------------------------------------------------------
# AUTOTILE & SPRITE RENDERING ENGINE
# ---------------------------------------------------------
class TileRenderer:
    def __init__(self):
        self.cache = {}

    def get_tile(self, rel_path):
        if rel_path not in self.cache:
            full_path = os.path.join(TERRAIN_DIR, rel_path)
            if os.path.exists(full_path):
                self.cache[rel_path] = Image.open(full_path).convert("RGBA")
            else:
                self.cache[rel_path] = None
        return self.cache[rel_path]

    def solve_wang(self, world, x, y, neighbor_type):
        """
        Solves 8-neighbor Wang/marching bitmask for terrain transition.
        """
        def is_type(tx, ty):
            if 0 <= tx < WORLD_W and 0 <= ty < WORLD_H:
                return world[ty][tx] == neighbor_type
            return False

        n = is_type(x, y + 1)
        s = is_type(x, y - 1)
        w = is_type(x - 1, y)
        e = is_type(x + 1, y)
        nw = is_type(x - 1, y + 1)
        ne = is_type(x + 1, y + 1)
        sw = is_type(x - 1, y - 1)
        se = is_type(x + 1, y - 1)

        # Inner corners (convex corner inside)
        if s and w and not sw: return "inner_bl"
        if s and e and not se: return "inner_br"
        if n and w and not nw: return "inner_tl"
        if n and e and not ne: return "inner_tr"

        # Straight edges
        if s and not n: return "edge_s_01" if (x + y) % 2 == 0 else "edge_s_02"
        if n and not s: return "edge_n_01" if (x + y) % 2 == 0 else "edge_n_02"
        if e and not w: return "edge_e"
        if w and not e: return "edge_w"

        # Outer corners (concave corner)
        if nw and not n and not w: return "outer_br"
        if ne and not n and not e: return "outer_bl"
        if sw and not s and not w: return "outer_tr"
        if se and not s and not e: return "outer_tl"

        return None


def render_full_island(world, cliff_map, out_png="scratch/island_final_render.png", crop_boxes=None):
    print("Rendering high-fidelity tilemap with authentic sprites and transitions...")
    renderer = TileRenderer()

    # Pre-fetch base tiles
    t_deep = renderer.get_tile("Water/Sea/sea_deep_base_01.png")
    t_shallow = renderer.get_tile("Water/Sea/sea_shallow_base_01.png")
    t_sand01 = renderer.get_tile("Sand/sand_base_01.png")
    t_sand02 = renderer.get_tile("Sand/sand_base_02.png")
    t_grass01 = renderer.get_tile("Grass/grass_base_01.png")
    t_grass02 = renderer.get_tile("Grass/grass_base_02.png")
    t_dirt01 = renderer.get_tile("Dirt/mud_base_01.png")
    t_dirt02 = renderer.get_tile("Dirt/mud_base_02.png")
    t_river = renderer.get_tile("Water/River/river_water_base_01.png")

    # Cliffs
    t_cliff_face_bot = renderer.get_tile("Cliffs/cliff_face_bot_01.png")
    t_cliff_face_top = renderer.get_tile("Cliffs/cliff_face_top_01.png")
    t_cliff_side_w_top = renderer.get_tile("Cliffs/cliff_side_w_top.png")
    t_cliff_side_w_bot = renderer.get_tile("Cliffs/cliff_side_w_bot.png")
    t_cliff_side_e_top = renderer.get_tile("Cliffs/cliff_side_e_top.png")
    t_cliff_side_e_bot = renderer.get_tile("Cliffs/cliff_side_e_bot.png")
    t_cliff_steps_top = renderer.get_tile("Cliffs/cliff_mud_steps_top.png")
    t_cliff_steps_bot = renderer.get_tile("Cliffs/cliff_mud_steps_bot.png")
    t_cliff_ramp_top = renderer.get_tile("Cliffs/cliff_ramp_mid_top.png")
    t_cliff_ramp_bot = renderer.get_tile("Cliffs/cliff_ramp_mid_bot.png")

    canvas = Image.new("RGBA", (WORLD_W * TILE_SIZE, WORLD_H * TILE_SIZE), (18, 52, 88, 255))

    for y in range(WORLD_H):
        for x in range(WORLD_W):
            # Unity coordinates: y=0 is bottom, Pillow y=0 is top
            px = x * TILE_SIZE
            py = (WORLD_H - 1 - y) * TILE_SIZE
            c = world[y][x]

            # 1. Base Layer
            if c == OCEAN_DEEP:
                canvas.paste(t_deep, (px, py))
            elif c == OCEAN_SHALLOW:
                canvas.paste(t_shallow, (px, py))
            elif c == BEACH_SAND:
                sand_t = t_sand01 if (x * 7 + y * 13) % 2 == 0 else t_sand02
                canvas.paste(sand_t, (px, py))
                # Transition to Shallow Water
                sw_code = renderer.solve_wang(world, x, y, OCEAN_SHALLOW)
                if sw_code:
                    trans_tile = renderer.get_tile(f"Transitions/Sand_Water/sand_water_{sw_code}.png")
                    if trans_tile:
                        canvas.paste(trans_tile, (px, py), trans_tile)
            elif c in (GRASS_BASE, CLIFF_TOP):
                grass_t = t_grass01 if (x * 11 + y * 17) % 2 == 0 else t_grass02
                canvas.paste(grass_t, (px, py))
                # Transition to Sand
                gs_code = renderer.solve_wang(world, x, y, BEACH_SAND)
                if gs_code:
                    trans_tile = renderer.get_tile(f"Transitions/Grass_Sand/grass_sand_{gs_code}.png")
                    if trans_tile:
                        canvas.paste(trans_tile, (px, py), trans_tile)
            elif c == DIRT_PATH:
                dirt_t = t_dirt01 if (x * 5 + y * 9) % 2 == 0 else t_dirt02
                # Underneath is grass
                canvas.paste(t_grass01, (px, py))
                canvas.paste(dirt_t, (px, py))
                # Transition to Grass
                gd_code = renderer.solve_wang(world, x, y, GRASS_BASE)
                if gd_code:
                    trans_tile = renderer.get_tile(f"Transitions/Grass_Dirt/grass_dirt_{gd_code}.png")
                    if trans_tile:
                        canvas.paste(trans_tile, (px, py), trans_tile)
            elif c == RIVER_WATER:
                canvas.paste(t_river, (px, py))
                # Riverbank transition to Grass
                gr_code = renderer.solve_wang(world, x, y, GRASS_BASE)
                if gr_code:
                    trans_tile = renderer.get_tile(f"Transitions/Grass_RiverWater/grass_riverwater_{gr_code}.png")
                    if trans_tile:
                        canvas.paste(trans_tile, (px, py), trans_tile)
            elif c == CLIFF_WALL:
                # Underneath is ground
                canvas.paste(t_grass01, (px, py))
                cm = cliff_map[y][x]
                if cm == "cliff_face_bot":
                    canvas.paste(t_cliff_face_bot, (px, py), t_cliff_face_bot)
                elif cm == "cliff_face_top":
                    canvas.paste(t_cliff_face_top, (px, py), t_cliff_face_top)
                elif cm == "cliff_side_w_top":
                    canvas.paste(t_cliff_side_w_top, (px, py), t_cliff_side_w_top)
                elif cm == "cliff_side_w_bot":
                    canvas.paste(t_cliff_side_w_bot, (px, py), t_cliff_side_w_bot)
                elif cm == "cliff_side_e_top":
                    canvas.paste(t_cliff_side_e_top, (px, py), t_cliff_side_e_top)
                elif cm == "cliff_side_e_bot":
                    canvas.paste(t_cliff_side_e_bot, (px, py), t_cliff_side_e_bot)
                else:
                    canvas.paste(t_cliff_face_bot, (px, py), t_cliff_face_bot)

            # Extra Cliff Overlay (Steps & Ramps)
            if cliff_map[y][x] == "cliff_mud_steps":
                if y % 2 == 0:
                    canvas.paste(t_cliff_steps_bot, (px, py), t_cliff_steps_bot)
                else:
                    canvas.paste(t_cliff_steps_top, (px, py), t_cliff_steps_top)
            elif cliff_map[y][x] == "cliff_ramp":
                if y % 2 == 0:
                    canvas.paste(t_cliff_ramp_bot, (px, py), t_cliff_ramp_bot)
                else:
                    canvas.paste(t_cliff_ramp_top, (px, py), t_cliff_ramp_top)

    # Save full downscaled overview (350x350 and 700x700)
    overview_small = canvas.resize((350, 350), Image.BILINEAR)
    overview_small.save("scratch/island_overview_tiles.png")
    overview_2x = canvas.resize((700, 700), Image.NEAREST)
    overview_2x.save("scratch/island_overview_tiles_2x.png")
    print("Saved overview tilemap images!")

    # Render regional crops for deep quality inspection:
    if crop_boxes:
        for name, (bx1, by1, bx2, by2) in crop_boxes.items():
            # Convert world coords (y=0 at bottom) to image coords (y=0 at top)
            ix1 = bx1 * TILE_SIZE
            ix2 = bx2 * TILE_SIZE
            iy1 = (WORLD_H - by2) * TILE_SIZE
            iy2 = (WORLD_H - by1) * TILE_SIZE
            cropped = canvas.crop((ix1, iy1, ix2, iy2))
            crop_path = f"scratch/crop_{name}.png"
            cropped.save(crop_path)
            print(f"Saved regional crop: {crop_path} ({cropped.size})")

    return canvas


if __name__ == "__main__":
    world, land_mask, cliff_map = generate_base_island()
    
    crops = {
        "starting_camp": (105, 90, 165, 150),
        "river_crossing": (145, 125, 205, 185),
        "cliff_plateau": (220, 175, 285, 240),
        "escape_cove": (75, 205, 140, 270),
        "estuary_delta": (160, 50, 225, 115)
    }

    render_full_island(world, cliff_map, crop_boxes=crops)
    print("All renders completed successfully!")
