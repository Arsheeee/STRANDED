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
    print("Generating base island geometry (350x350) - Iteration 4 (Crafted Precision)...")
    land_mask = generate_island_mask(seed=2026)
    
    print("Calculating coastal distance fields...")
    dist_to_land = compute_dist_to_land(land_mask)
    dist_to_water = compute_dist_to_water(land_mask)

    world = [[OCEAN_DEEP for _ in range(WORLD_W)] for _ in range(WORLD_H)]
    # Stores cliff sprite names for exact placement
    cliff_sprites = {} 

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
                # Broad white sand beaches in bays
                if (80 < x < 140 and 200 < y < 265) or (140 < x < 220 and 60 < y < 115):
                    beach_w += 5.0
                # Narrow beach on rocky eastern/northern bluffs
                if (x > 260 and 150 < y < 245) or (y > 270 and 165 < x < 225):
                    beach_w = max(2.5, beach_w - 2.5)

                if dist_to_water[y][x] <= beach_w:
                    world[y][x] = BEACH_SAND
                else:
                    world[y][x] = GRASS_BASE

    # 2. Handcrafted Eastern Cliff Plateau (Authentic Stardew Architecture)
    # The plateau is positioned at X: 234..276, Y: 188..234
    print("Assembling Handcrafted Eastern Cliff Plateau...")
    
    # We build the plateau with orthogonal walls and true 2-tile cliff faces:
    # South wall: runs from X=234 to X=276 at Y=188 (bot) and Y=189 (top)
    # Mud steps: placed at X=244..245, cutting through Y=188..189
    # West wall: runs from Y=190 to Y=230 at X=234
    # East wall: runs from Y=190 to Y=230 at X=276
    
    # Mark the plateau top (Y >= 190, X: 235..275)
    for y in range(190, 235):
        for x in range(235, 276):
            if world[y][x] in (GRASS_BASE, BEACH_SAND):
                world[y][x] = CLIFF_TOP

    # A. South Cliff Face (cols 235..275 at row Y=188 bot, Y=189 top)
    for x in range(235, 276):
        # Leave gap at X=244..245 for Carved Mud Steps!
        if x in (244, 245):
            continue
        world[188][x] = CLIFF_WALL
        world[189][x] = CLIFF_WALL
        alt = "01" if x % 2 == 0 else "02"
        cliff_sprites[(x, 188)] = f"cliff_face_bot_{alt}.png"
        cliff_sprites[(x, 189)] = f"cliff_face_top_{alt}.png"

    # B. Southwest Outer Corner at X=234, rows 188 & 189
    world[188][234] = CLIFF_WALL
    world[189][234] = CLIFF_WALL
    cliff_sprites[(234, 188)] = "cliff_corner_sw_bot.png"
    cliff_sprites[(234, 189)] = "cliff_corner_sw_top.png"

    # C. Southeast Outer Corner at X=276, rows 188 & 189
    world[188][276] = CLIFF_WALL
    world[189][276] = CLIFF_WALL
    cliff_sprites[(276, 188)] = "cliff_corner_se_bot.png"
    cliff_sprites[(276, 189)] = "cliff_corner_se_top.png"

    # D. Carved Mud Steps at X=244..245, rows 188 & 189
    # Left step (244) & Right step (245)
    world[188][244] = DIRT_PATH
    world[189][244] = DIRT_PATH
    cliff_sprites[(244, 188)] = "cliff_mud_steps_01_bot.png"
    cliff_sprites[(244, 189)] = "cliff_mud_steps_01_top.png"

    world[188][245] = DIRT_PATH
    world[189][245] = DIRT_PATH
    cliff_sprites[(245, 188)] = "cliff_mud_steps_02_bot.png"
    cliff_sprites[(245, 189)] = "cliff_mud_steps_02_top.png"

    # Step approach mud apron (1 tile south and 1 tile north)
    for sx in (244, 245):
        world[187][sx] = DIRT_PATH
        world[190][sx] = DIRT_PATH

    # E. West Vertical Cliff Wall (column 234, rows 190..232)
    # Leaves canyon gap at rows 211..217 for river gorge exit!
    for y in range(190, 232):
        if 211 <= y <= 217:
            continue # Canyon gap for river!
        world[y][234] = CLIFF_WALL
        if y == 190:
            cliff_sprites[(234, y)] = "cliff_side_w_bot.png"
        elif y == 231:
            cliff_sprites[(234, y)] = "cliff_side_w_top.png"
        else:
            cliff_sprites[(234, y)] = "cliff_side_w.png"

    # Canyon shoulders at river gap (rows 210 and 218)
    cliff_sprites[(234, 210)] = "cliff_ramp_left_top.png"
    cliff_sprites[(234, 218)] = "cliff_ramp_left_bot.png"

    # F. East Vertical Cliff Wall (column 276, rows 190..232)
    for y in range(190, 232):
        world[y][276] = CLIFF_WALL
        if y == 190:
            cliff_sprites[(276, y)] = "cliff_side_e_bot.png"
        elif y == 231:
            cliff_sprites[(276, y)] = "cliff_side_e_top.png"
        else:
            cliff_sprites[(276, y)] = "cliff_side_e.png"

    # G. North Cliff Rims (corners turning into plateau)
    cliff_sprites[(234, 232)] = "cliff_outer_tl_top.png"
    cliff_sprites[(276, 232)] = "cliff_outer_tr_top.png"

    # 3. Winding Natural River System
    print("Simulating River System (Source to Estuary Delta)...")
    waypoints = [
        (260, 226), # Highland spring pool on plateau
        (248, 220), # Highland river reach
        (234, 214), # Gorge exit through cliff canyon gap
        (214, 206), # Upper forest loop (curves west)
        (196, 194), # Meander around northern jungle spur
        (185, 172), # Upper valley reach
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
        r_rad = 1.25 + 0.95 * progress
        # Narrow crossing at Ford
        d_to_ford = math.hypot(rx - ford_center[0], ry - ford_center[1])
        if d_to_ford < 6.0:
            r_rad = 0.95

        irx, iry = int(round(rx)), int(round(ry))
        rad_ceil = int(math.ceil(r_rad))
        for dy in range(-rad_ceil, rad_ceil + 1):
            for dx in range(-rad_ceil, rad_ceil + 1):
                if dx*dx + dy*dy <= r_rad * r_rad:
                    tx, ty = irx + dx, iry + dy
                    if 0 <= tx < WORLD_W and 0 <= ty < WORLD_H:
                        river_mask[ty][tx] = True

    # Spring Pool on plateau: circular pool at (260, 226)
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            if dx*dx + dy*dy <= 7.0:
                river_mask[226 + dy][260 + dx] = True

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
    for fx in range(171, 178):
        for fy in range(153, 158):
            if world[fy][fx] == GRASS_BASE:
                world[fy][fx] = DIRT_PATH

    # 4. Starting Camp Area & Exploration Paths
    print("Carving Handcrafted Starting Camp & Natural 3-Tile Exploration Trails...")
    camp_cx, camp_cy = 135, 120
    
    # Smooth, organic circular camp clearing (solid radius ~6.5 tiles)
    for dy in range(-7, 8):
        for dx in range(-7, 8):
            d2 = dx*dx + dy*dy
            tx, ty = camp_cx + dx, camp_cy + dy
            if 0 <= tx < WORLD_W and 0 <= ty < WORLD_H:
                if world[ty][tx] in (GRASS_BASE, BEACH_SAND):
                    if d2 <= 38.0:
                        world[ty][tx] = DIRT_PATH

    # Natural 3-tile wide solid trail rasterizer
    def carve_smooth_trail(pts, radius=1.65):
        for i in range(len(pts) - 1):
            p1 = pts[i]
            p2 = pts[i + 1]
            dist = int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) * 2.5) + 1
            for s in range(dist + 1):
                t = s / float(dist)
                px = p1[0] + (p2[0] - p1[0]) * t
                py = p1[1] + (p2[1] - p1[1]) * t
                ipx, ipy = int(round(px)), int(round(py))
                rad_ceil = int(math.ceil(radius))
                for dy in range(-rad_ceil, rad_ceil + 1):
                    for dx in range(-rad_ceil, rad_ceil + 1):
                        if dx*dx + dy*dy <= radius * radius:
                            tx, ty = ipx + dx, ipy + dy
                            if 0 <= tx < WORLD_W and 0 <= ty < WORLD_H:
                                if world[ty][tx] in (GRASS_BASE, CLIFF_TOP):
                                    world[ty][tx] = DIRT_PATH

    # 4 Cardinal Exploration Paths from Starting Camp:
    # 1. South Trail (Camp -> South Beach)
    carve_smooth_trail([(135, 114), (135, 104), (136, 94), (135, 86)], radius=1.65)
    # 2. West Trail (Camp -> West Coastal Bay)
    carve_smooth_trail([(128, 120), (116, 121), (104, 123), (90, 124)], radius=1.65)
    # 3. East Trail (Camp -> Central River Crossing)
    carve_smooth_trail([(142, 120), (153, 128), (163, 142), (172, 155)], radius=1.65)
    # 4. North Trail (Camp -> Northern Jungle)
    carve_smooth_trail([(135, 127), (138, 145), (144, 165), (148, 190)], radius=1.65)

    # Connecting Routes:
    # Ford to Plateau Mud Steps:
    carve_smooth_trail([(176, 155), (194, 162), (218, 172), (244, 186)], radius=1.65)
    # North Jungle to Escape Cove:
    carve_smooth_trail([(144, 165), (134, 188), (122, 210), (110, 230)], radius=1.65)
    # Deep Jungle Trail:
    carve_smooth_trail([(148, 190), (160, 215), (175, 238), (185, 255)], radius=1.65)

    # 5. Ecological Landmark Clearings:
    # A. Northwest Escape Cove clearing at (108, 236)
    for dy in range(-7, 8):
        for dx in range(-7, 8):
            if dx*dx + dy*dy <= 32.0:
                tx, ty = 108 + dx, 236 + dy
                if world[ty][tx] == GRASS_BASE:
                    world[ty][tx] = DIRT_PATH

    # B. Northern Jungle secluded glade at (175, 242)
    for dy in range(-6, 7):
        for dx in range(-6, 7):
            if dx*dx + dy*dy <= 24.0:
                tx, ty = 175 + dx, 242 + dy
                if world[ty][tx] == GRASS_BASE:
                    world[ty][tx] = DIRT_PATH

    # C. Eastern Plateau spring sanctuary at (266, 222)
    for dy in range(-6, 7):
        for dx in range(-6, 7):
            if dx*dx + dy*dy <= 26.0:
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

    print("Base island generation finished!")
    return world, land_mask, cliff_sprites


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
        Notice: In Unity/world space, +y is North, -y is South, -x is West, +x is East.
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


def render_full_island(world, cliff_sprites, crop_boxes=None):
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

    canvas = Image.new("RGBA", (WORLD_W * TILE_SIZE, WORLD_H * TILE_SIZE), (18, 52, 88, 255))

    # Pass 1: Base ground layer
    for y in range(WORLD_H):
        for x in range(WORLD_W):
            px = x * TILE_SIZE
            py = (WORLD_H - 1 - y) * TILE_SIZE # Pillow Y=0 is top
            c = world[y][x]

            if c == OCEAN_DEEP:
                canvas.paste(t_deep, (px, py))
            elif c == OCEAN_SHALLOW:
                canvas.paste(t_shallow, (px, py))
            elif c == BEACH_SAND:
                sand_t = t_sand01 if (x * 7 + y * 13) % 2 == 0 else t_sand02
                canvas.paste(sand_t, (px, py))
                # Transition to Shallow Water (placed on Sand tile)
                sw_code = renderer.solve_wang(world, x, y, OCEAN_SHALLOW)
                if sw_code:
                    trans_tile = renderer.get_tile(f"Transitions/Sand_Water/sand_water_{sw_code}.png")
                    if trans_tile:
                        canvas.paste(trans_tile, (px, py), trans_tile)
            elif c in (GRASS_BASE, CLIFF_TOP, CLIFF_WALL):
                grass_t = t_grass01 if (x * 11 + y * 17) % 2 == 0 else t_grass02
                canvas.paste(grass_t, (px, py))
                # Transition to Sand (placed on Grass tile)
                gs_code = renderer.solve_wang(world, x, y, BEACH_SAND)
                if gs_code:
                    trans_tile = renderer.get_tile(f"Transitions/Grass_Sand/grass_sand_{gs_code}.png")
                    if trans_tile:
                        canvas.paste(trans_tile, (px, py), trans_tile)
                # Transition to River Water (placed on Grass bank tile)
                gr_code = renderer.solve_wang(world, x, y, RIVER_WATER)
                if gr_code:
                    trans_tile = renderer.get_tile(f"Transitions/Grass_RiverWater/grass_riverwater_{gr_code}.png")
                    if trans_tile:
                        canvas.paste(trans_tile, (px, py), trans_tile)
            elif c == DIRT_PATH:
                dirt_t = t_dirt01 if (x * 5 + y * 9) % 2 == 0 else t_dirt02
                canvas.paste(t_grass01, (px, py))
                canvas.paste(dirt_t, (px, py))
                # Transition to Grass (placed on Dirt tile)
                gd_code = renderer.solve_wang(world, x, y, GRASS_BASE)
                if gd_code:
                    trans_tile = renderer.get_tile(f"Transitions/Grass_Dirt/grass_dirt_{gd_code}.png")
                    if trans_tile:
                        canvas.paste(trans_tile, (px, py), trans_tile)
            elif c == RIVER_WATER:
                canvas.paste(t_river, (px, py))

    # Pass 2: Cliff Sprites
    for (cx, cy), sname in cliff_sprites.items():
        px = cx * TILE_SIZE
        py = (WORLD_H - 1 - cy) * TILE_SIZE
        tile_img = renderer.get_tile(f"Cliffs/{sname}")
        if tile_img:
            canvas.paste(tile_img, (px, py), tile_img)

    # Save overview tilemap images
    overview_small = canvas.resize((350, 350), Image.BILINEAR)
    overview_small.save("scratch/island_overview_tiles.png")
    overview_2x = canvas.resize((700, 700), Image.NEAREST)
    overview_2x.save("scratch/island_overview_tiles_2x.png")
    print("Saved overview tilemap images!")

    # Render regional crops for deep quality inspection
    if crop_boxes:
        for name, (bx1, by1, bx2, by2) in crop_boxes.items():
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
    world, land_mask, cliff_sprites = generate_base_island()
    
    crops = {
        "starting_camp": (105, 90, 165, 150),
        "river_crossing": (145, 125, 205, 185),
        "cliff_plateau": (220, 175, 285, 240),
        "escape_cove": (75, 205, 140, 270),
        "estuary_delta": (160, 50, 225, 115)
    }

    render_full_island(world, cliff_sprites, crop_boxes=crops)
    print("All renders completed successfully!")
