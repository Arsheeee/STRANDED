import os
import json
import math
import random
from collections import deque
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

            n_macro = noise_macro.fbm(x * 0.018, y * 0.018, octaves=3) * 25.0
            n_det = noise_detail.fbm(x * 0.048, y * 0.048, octaves=3) * 11.0
            n_mic = noise_micro.sample(x * 0.12, y * 0.12) * 3.5

            perturbed_dist = dist - (n_macro + n_det + n_mic)

            if perturbed_dist < target_r:
                land_mask[y][x] = True

    # Cellular smoothing pass (3 passes)
    for _ in range(3):
        new_land = [row[:] for row in land_mask]
        for y in range(1, WORLD_H - 1):
            for x in range(1, WORLD_W - 1):
                cnt = sum(land_mask[ny][nx] for ny in range(y - 1, y + 2) for nx in range(x - 1, x + 2))
                if land_mask[y][x] and cnt < 4:
                    new_land[y][x] = False
                elif not land_mask[y][x] and cnt >= 6:
                    new_land[y][x] = True
        land_mask = new_land

    # Connected Component Filtering: remove any tiny disconnected islands < 30 tiles
    visited = [[False for _ in range(WORLD_W)] for _ in range(WORLD_H)]
    components = []

    for y in range(WORLD_H):
        for x in range(WORLD_W):
            if land_mask[y][x] and not visited[y][x]:
                comp = []
                q = deque([(x, y)])
                visited[y][x] = True
                while q:
                    cx_cur, cy_cur = q.popleft()
                    comp.append((cx_cur, cy_cur))
                    for ny in range(cy_cur - 1, cy_cur + 2):
                        for nx in range(cx_cur - 1, cx_cur + 2):
                            if 0 <= nx < WORLD_W and 0 <= ny < WORLD_H:
                                if land_mask[ny][nx] and not visited[ny][nx]:
                                    visited[ny][nx] = True
                                    q.append((nx, ny))
                components.append(comp)

    if components:
        components.sort(key=len, reverse=True)
        for comp in components[1:]:
            if len(comp) < 30:
                for (cx_pt, cy_pt) in comp:
                    land_mask[cy_pt][cx_pt] = False

    return land_mask


def generate_base_island():
    print("Generating handcrafted tropical survival island geometry (350x350)...")
    land_mask = generate_island_mask(seed=2026)
    
    print("Calculating coastal distance fields...")
    dist_to_land = compute_dist_to_land(land_mask)
    dist_to_water = compute_dist_to_water(land_mask)

    world = [[OCEAN_DEEP for _ in range(WORLD_W)] for _ in range(WORLD_H)]
    cliff_sprites = {}

    noise_shelf = ValueNoise2D(seed=3033)
    noise_beach = ValueNoise2D(seed=4044)

    # 1. Water & Beach Classification
    for y in range(WORLD_H):
        for x in range(WORLD_W):
            if not land_mask[y][x]:
                ns = noise_shelf.sample(x * 0.03, y * 0.03) * 2.5
                shelf_w = 6.0 + ns
                if (160 < x < 230 and 50 < y < 110) or (80 < x < 140 and 200 < y < 265):
                    shelf_w += 4.5

                if dist_to_land[y][x] <= shelf_w:
                    world[y][x] = OCEAN_SHALLOW
                else:
                    world[y][x] = OCEAN_DEEP
            else:
                nb = noise_beach.sample(x * 0.035, y * 0.035) * 2.5
                beach_w = 4.5 + nb
                # Wide expansive southern beach and southwest bay
                if (130 < x < 210 and 55 < y < 110) or (80 < x < 135 and 195 < y < 265):
                    beach_w += 5.5
                # Narrow rocky cliff beaches on eastern shores
                if (x > 260 and 150 < y < 245) or (y > 270 and 165 < x < 225):
                    beach_w = max(2.5, beach_w - 2.5)

                if dist_to_water[y][x] <= beach_w:
                    world[y][x] = BEACH_SAND
                else:
                    # Mud/Earth is the primary underlying soil and base ground across the island!
                    world[y][x] = DIRT_PATH

    # 2. Handcrafted Eastern Cliff Plateau (Warm Earth/Mud Rock)
    print("Sculpting Handcrafted Eastern Cliff Plateau with Mud Steps & River Canyon Gap...")
    
    # Plateau Top (elevated walkable tableland)
    for y in range(190, 236):
        for x in range(234, 278):
            if world[y][x] in (DIRT_PATH, BEACH_SAND):
                world[y][x] = CLIFF_TOP

    # South Cliff Face (cols 235..276 at rows 188 & 189)
    for x in range(235, 277):
        if x in (244, 245): # Mud Steps Gap
            continue
        world[188][x] = CLIFF_WALL
        world[189][x] = CLIFF_WALL
        alt = "01" if x % 2 == 0 else "02"
        cliff_sprites[(x, 188)] = f"cliff_face_bot_{alt}.png"
        cliff_sprites[(x, 189)] = f"cliff_face_top_{alt}.png"

    # Southwest Corner (X=234, rows 188 & 189)
    world[188][234] = CLIFF_WALL
    world[189][234] = CLIFF_WALL
    cliff_sprites[(234, 188)] = "cliff_corner_sw_bot.png"
    cliff_sprites[(234, 189)] = "cliff_corner_sw_top.png"

    # Southeast Corner (X=277, rows 188 & 189)
    world[188][277] = CLIFF_WALL
    world[189][277] = CLIFF_WALL
    cliff_sprites[(277, 188)] = "cliff_corner_se_bot.png"
    cliff_sprites[(277, 189)] = "cliff_corner_se_top.png"

    # Flanking Shoulders for Mud Steps (X=243 Left Shoulder, X=246 Right Shoulder)
    cliff_sprites[(243, 188)] = "cliff_ramp_left_bot.png"
    cliff_sprites[(243, 189)] = "cliff_ramp_left_top.png"
    cliff_sprites[(246, 188)] = "cliff_ramp_right_bot.png"
    cliff_sprites[(246, 189)] = "cliff_ramp_right_top.png"

    # Carved Mud Steps at X=244..245 (cutting cleanly through rows 188 & 189)
    world[188][244] = DIRT_PATH
    world[189][244] = DIRT_PATH
    cliff_sprites[(244, 188)] = "cliff_mud_steps_01_bot.png"
    cliff_sprites[(244, 189)] = "cliff_mud_steps_01_top.png"

    world[188][245] = DIRT_PATH
    world[189][245] = DIRT_PATH
    cliff_sprites[(245, 188)] = "cliff_mud_steps_02_bot.png"
    cliff_sprites[(245, 189)] = "cliff_mud_steps_02_top.png"

    # Mud Steps Apron (Approach ramp from South rows 185..187 and Exit on Plateau rows 190..192)
    for sx in range(242, 248):
        for sy in range(185, 188):
            if world[sy][sx] in (GRASS_BASE, DIRT_PATH):
                world[sy][sx] = DIRT_PATH
        for sy in range(190, 193):
            if world[sy][sx] in (CLIFF_TOP, GRASS_BASE):
                world[sy][sx] = DIRT_PATH

    # Southern Cliff Base Scree / Mud Apron (rows 185..187 along cliff base)
    noise_cliff_base = ValueNoise2D(seed=7788)
    for cx in range(232, 279):
        apron_depth = int(round(2.0 + noise_cliff_base.sample(cx * 0.16, 188 * 0.16) * 1.5))
        for ay in range(188 - apron_depth, 188):
            if world[ay][cx] in (GRASS_BASE, DIRT_PATH):
                world[ay][cx] = DIRT_PATH

    # West Vertical Wall (col 234, rows 190..232)
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

    # Canyon shoulders at river gap
    cliff_sprites[(234, 210)] = "cliff_ramp_left_top.png"
    cliff_sprites[(234, 218)] = "cliff_ramp_left_bot.png"

    # East Vertical Wall (col 277, rows 190..232)
    for y in range(190, 232):
        world[y][277] = CLIFF_WALL
        if y == 190:
            cliff_sprites[(277, y)] = "cliff_side_e_bot.png"
        elif y == 231:
            cliff_sprites[(277, y)] = "cliff_side_e_top.png"
        else:
            cliff_sprites[(277, y)] = "cliff_side_e.png"

    # North Rims
    cliff_sprites[(234, 232)] = "cliff_outer_tl_top.png"
    cliff_sprites[(277, 232)] = "cliff_outer_tr_top.png"

    # 3. Winding Natural River System
    print("Sculpting River System with Natural Alluvial Mud Banks...")
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
        d_to_ford = math.hypot(rx - ford_center[0], ry - ford_center[1])
        if d_to_ford < 6.0:
            r_rad = 0.95 # Narrower and shallower at central crossing

        irx, iry = int(round(rx)), int(round(ry))
        rad_ceil = int(math.ceil(r_rad))
        for dy in range(-rad_ceil, rad_ceil + 1):
            for dx in range(-rad_ceil, rad_ceil + 1):
                if dx*dx + dy*dy <= r_rad * r_rad:
                    tx, ty = irx + dx, iry + dy
                    if 0 <= tx < WORLD_W and 0 <= ty < WORLD_H:
                        river_mask[ty][tx] = True

    # Spring Pool on plateau at (260, 226)
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

    # Apply River Water to Map
    for y in range(WORLD_H):
        for x in range(WORLD_W):
            if (x, y) in delta_islet:
                world[y][x] = BEACH_SAND
            elif river_mask[y][x]:
                if world[y][x] not in (OCEAN_DEEP, OCEAN_SHALLOW):
                    world[y][x] = RIVER_WATER

    # Continuous Organic Muddy Riverbanks (1.5 to 3.5 tiles wide)
    noise_riverbank = ValueNoise2D(seed=8899)
    for y in range(WORLD_H):
        for x in range(WORLD_W):
            if river_mask[y][x] or world[y][x] in (OCEAN_DEEP, OCEAN_SHALLOW, BEACH_SAND, CLIFF_WALL):
                continue
            close_to_river = False
            for dy in range(-4, 5):
                for dx in range(-4, 5):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < WORLD_W and 0 <= ny < WORLD_H and river_mask[ny][nx]:
                        d = math.hypot(dx, dy)
                        bank_w = 2.0 + 1.2 * noise_riverbank.sample(x * 0.12, y * 0.12)
                        if math.hypot(x - 174, y - 155) < 9.0:
                            bank_w += 2.0
                        if math.hypot(x - 196, y - 126) < 8.0:
                            bank_w += 1.8

                        if d <= bank_w:
                            close_to_river = True
                            break
                if close_to_river:
                    break
            if close_to_river and world[y][x] != RIVER_WATER:
                world[y][x] = DIRT_PATH

    # 4. Handcrafted Starting Camp & Radial Paths
    print("Sculpting Multi-Zone Starting Camp & Camp Basin...")
    camp_subzones = [
        (135, 120, 6.8), # Hearth
        (128, 121, 4.8), # Crafting
        (134, 127, 4.4), # Sleeping
        (141, 118, 4.2), # Storage
    ]
    noise_camp = ValueNoise2D(seed=5511)
    for (zx, zy, zrad) in camp_subzones:
        rad_ceil = int(math.ceil(zrad + 1))
        for dy in range(-rad_ceil, rad_ceil + 1):
            for dx in range(-rad_ceil, rad_ceil + 1):
                tx, ty = zx + dx, zy + dy
                if 0 <= tx < WORLD_W and 0 <= ty < WORLD_H:
                    d = math.hypot(dx, dy)
                    wobble = noise_camp.sample(tx * 0.25, ty * 0.25) * 1.2
                    if d <= zrad + wobble and world[ty][tx] not in (OCEAN_DEEP, OCEAN_SHALLOW, RIVER_WATER, CLIFF_WALL):
                        world[ty][tx] = DIRT_PATH

    # Helper: Natural Organic Grassland Region Sculptor
    # Grass sits ON the mud!
    def add_organic_grassland(cx, cy, rx, ry, seed_val=100, allow_cliff=False):
        noise_gl = ValueNoise2D(seed=seed_val)
        max_r = max(rx, ry) + 4
        for dy in range(-int(max_r), int(max_r) + 1):
            for dx in range(-int(max_r), int(max_r) + 1):
                tx, ty = cx + dx, cy + dy
                if 0 <= tx < WORLD_W and 0 <= ty < WORLD_H:
                    # Do not overwrite water, sand beaches, cliff walls, or the river
                    if world[ty][tx] == DIRT_PATH or (allow_cliff and world[ty][tx] == CLIFF_TOP):
                        # Elliptical normalized distance
                        norm_d = ((dx / float(rx)) ** 2) + ((dy / float(ry)) ** 2)
                        wobble = noise_gl.sample(tx * 0.18, ty * 0.18) * 0.35
                        if norm_d <= 1.0 + wobble:
                            world[ty][tx] = GRASS_BASE

    # Helper: Natural Winding Exploration Trail Rasterizer
    def carve_smooth_trail(pts, radius=1.65, seed_val=999):
        noise_tr = ValueNoise2D(seed=seed_val)
        for i in range(len(pts) - 1):
            p1 = pts[i]
            p2 = pts[i + 1]
            dist = int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) * 2.8) + 1
            for s in range(dist + 1):
                t = s / float(dist)
                px = p1[0] + (p2[0] - p1[0]) * t
                py = p1[1] + (p2[1] - p1[1]) * t
                ipx, ipy = int(round(px)), int(round(py))
                rad_ceil = int(math.ceil(radius + 1))
                for dy in range(-rad_ceil, rad_ceil + 1):
                    for dx in range(-rad_ceil, rad_ceil + 1):
                        d = math.hypot(dx, dy)
                        tx, ty = ipx + dx, ipy + dy
                        if 0 <= tx < WORLD_W and 0 <= ty < WORLD_H:
                            wobble = noise_tr.sample(tx * 0.3, ty * 0.3) * 0.35
                            if d <= radius + wobble:
                                if world[ty][tx] in (GRASS_BASE, CLIFF_TOP):
                                    world[ty][tx] = DIRT_PATH

    # 5. Sculpt Handcrafted Grassland Regions on Top of the Mud
    print("Sculpting Handcrafted Grassland Regions (Grass sitting on Mud)...")

    # Region 1: Broad Central Sunlit Meadow (Multi-lobed natural expanse)
    central_meadow = [
        (156, 150, 15.0, 12.0, 301),
        (165, 142, 13.0, 10.0, 302),
        (148, 160, 12.0, 13.0, 303),
        (166, 162, 11.0, 9.5, 304),
        (172, 170, 9.0, 8.0, 305),
        (152, 134, 11.0, 9.5, 306),
    ]
    for (cx, cy, rx, ry, s) in central_meadow:
        add_organic_grassland(cx, cy, rx, ry, s)

    # Region 2: Western Coastal Savanna & Terraced Hill Meadow
    west_grassland = [
        (96, 155, 13.0, 16.0, 311),
        (106, 172, 12.0, 14.0, 312),
        (92, 136, 11.0, 12.0, 313),
        (110, 148, 10.0, 10.0, 314),
        (102, 188, 9.0, 10.0, 315),
    ]
    for (cx, cy, rx, ry, s) in west_grassland:
        add_organic_grassland(cx, cy, rx, ry, s)

    # Region 3: Starting Camp Dappled Meadows (Soft grass islands around camp)
    camp_meadows = [
        (122, 108, 9.5, 8.0, 321),
        (116, 102, 8.0, 7.0, 322),
        (146, 134, 9.0, 7.5, 323),
        (152, 138, 8.0, 7.0, 324),
        (132, 96, 8.5, 7.0, 325),
        (144, 94, 7.5, 6.0, 326),
        (124, 132, 7.5, 6.5, 327),
    ]
    for (cx, cy, rx, ry, s) in camp_meadows:
        add_organic_grassland(cx, cy, rx, ry, s)

    # Region 4: Northern Upland Prairie
    north_prairie = [
        (168, 240, 16.0, 12.5, 331),
        (154, 248, 13.0, 11.0, 332),
        (178, 232, 12.0, 10.0, 333),
        (160, 224, 11.0, 9.0, 334),
        (185, 245, 9.5, 8.0, 335),
    ]
    for (cx, cy, rx, ry, s) in north_prairie:
        add_organic_grassland(cx, cy, rx, ry, s)

    # Region 5: Highland Plateau Meadow (elevated grassland surrounding spring)
    highland_meadow = [
        (258, 212, 13.0, 12.0, 341),
        (268, 204, 10.5, 9.5, 342),
        (250, 224, 9.5, 8.5, 343),
        (264, 226, 8.5, 8.0, 344),
    ]
    for (cx, cy, rx, ry, s) in highland_meadow:
        add_organic_grassland(cx, cy, rx, ry, s, allow_cliff=True)

    # Region 6: Northwest Smuggler's Meadow
    nw_meadow = [
        (115, 230, 12.0, 11.0, 351),
        (122, 240, 10.0, 9.0, 352),
        (106, 220, 10.0, 9.0, 353),
    ]
    for (cx, cy, rx, ry, s) in nw_meadow:
        add_organic_grassland(cx, cy, rx, ry, s)

    # Region 7: Southern Maritime Grassland (Maritime bluffs behind beach)
    south_maritime = [
        (154, 90, 12.0, 7.5, 361),
        (168, 94, 11.0, 7.0, 362),
        (138, 88, 10.0, 7.0, 363),
    ]
    for (cx, cy, rx, ry, s) in south_maritime:
        add_organic_grassland(cx, cy, rx, ry, s)

    # Region 8: River Bluff Scenic Overlooks
    river_bluffs = [
        (166, 172, 8.5, 7.5, 371),
        (162, 160, 7.5, 6.5, 372),
        (188, 118, 9.0, 8.0, 373),
        (182, 110, 8.0, 7.0, 374),
        (204, 130, 9.5, 8.5, 375),
    ]
    for (cx, cy, rx, ry, s) in river_bluffs:
        add_organic_grassland(cx, cy, rx, ry, s)

    # Region 9: 90+ Scattered Natural Grass Knolls & Sunlit Understory Tufts
    print("Scattering 90+ sunlit grass knolls & tufts across tropical forest floor...")
    rng_gl = random.Random(707)
    for _ in range(95):
        px = rng_gl.randint(65, 285)
        py = rng_gl.randint(65, 285)
        if world[py][px] == DIRT_PATH and dist_to_water[py][px] > 3.0:
            prx = rng_gl.uniform(2.8, 5.5)
            pry = rng_gl.uniform(2.4, 4.8)
            ps = rng_gl.randint(1000, 9999)
            add_organic_grassland(px, py, prx, pry, ps)

    # 6. Carve Primary Cardinal Exploration Trails Through Grassland
    print("Carving natural winding exploration trails through terrain...")
    # South Trail (Camp -> South Beach)
    carve_smooth_trail([(135, 114), (135, 104), (136, 94), (135, 84)], radius=1.65, seed_val=101)
    # West Trail (Camp -> West Coastal Bay)
    carve_smooth_trail([(128, 120), (116, 121), (104, 123), (90, 124)], radius=1.65, seed_val=102)
    # East Trail (Camp -> Central River Crossing)
    carve_smooth_trail([(142, 120), (153, 128), (163, 142), (172, 155)], radius=1.65, seed_val=103)
    # North Trail (Camp -> Northern Rainforest)
    carve_smooth_trail([(135, 127), (138, 145), (144, 165), (148, 190)], radius=1.65, seed_val=104)

    # Connecting Routes:
    # Ford to Plateau Mud Steps:
    carve_smooth_trail([(176, 155), (194, 162), (218, 172), (244, 186)], radius=1.65, seed_val=105)
    # North Rainforest to Escape Cove:
    carve_smooth_trail([(144, 165), (134, 188), (122, 210), (110, 230)], radius=1.65, seed_val=106)
    # Deep Rainforest Trail:
    carve_smooth_trail([(148, 190), (160, 215), (175, 238), (185, 255)], radius=1.65, seed_val=107)
    # Western Coastal Trail:
    carve_smooth_trail([(90, 124), (88, 145), (92, 168), (96, 195)], radius=1.55, seed_val=108)
    # River Bend to South Beach Trail:
    carve_smooth_trail([(196, 126), (188, 108), (176, 92), (158, 85)], radius=1.55, seed_val=109)

    print("Handcrafted base island generation completed successfully!")
    return world, land_mask, cliff_sprites


# ---------------------------------------------------------
# AUTOTILE & SPRITE RENDERING ENGINE
# ---------------------------------------------------------
class TileRenderer:
    def __init__(self, terrain_dir):
        self.terrain_dir = terrain_dir
        self.tile_cache = {}

    def get_tile(self, rel_path):
        if rel_path in self.tile_cache:
            return self.tile_cache[rel_path]

        full_path = os.path.join(self.terrain_dir, rel_path)
        if not os.path.exists(full_path):
            return None

        img = Image.open(full_path).convert("RGBA")
        self.tile_cache[rel_path] = img
        return img

    def solve_wang(self, grid, x, y, match_type, is_river=False):
        h = len(grid)
        w = len(grid[0])

        def is_type(tx, ty):
            if 0 <= tx < w and 0 <= ty < h:
                return grid[ty][tx] == match_type
            return False

        n = is_type(x, y + 1)
        s = is_type(x, y - 1)
        wt = is_type(x - 1, y)
        e = is_type(x + 1, y)
        nw = is_type(x - 1, y + 1)
        ne = is_type(x + 1, y + 1)
        sw = is_type(x - 1, y - 1)
        se = is_type(x + 1, y - 1)

        # 1. Convex corners (neighbor on TWO adjacent cardinal sides)
        if s and e: return "inner_tl"
        if s and wt: return "inner_tr"
        if n and e: return "inner_bl"
        if n and wt: return "inner_br"

        # 2. Straight edges (neighbor on ONE cardinal side)
        if is_river:
            if s: return "edge_s_01" if (x + y) % 2 == 0 else "edge_s_02"
            if n: return "edge_n_01" if (x + y) % 2 == 0 else "edge_n_02"
            if e: return "edge_e"
            if wt: return "edge_w"
        else:
            if s: return "edge_n_01" if (x + y) % 2 == 0 else "edge_n_02"
            if n: return "edge_s_01" if (x + y) % 2 == 0 else "edge_s_02"
            if e: return "edge_w"
            if wt: return "edge_e"

        # 3. Concave corners (neighbor ONLY on one diagonal corner)
        if sw and not s and not wt: return "outer_tr"
        if se and not s and not e: return "outer_tl"
        if nw and not n and not wt: return "outer_br"
        if ne and not n and not e: return "outer_bl"

        return None


def export_map_json(world, cliff_sprites, out_path):
    print(f"Exporting map data to {out_path}...")
    serializable_cliffs = {f"{k[0]},{k[1]}": v for k, v in cliff_sprites.items()}
    data = {
        "title": "STRANDED Handcrafted Island",
        "width": WORLD_W,
        "height": WORLD_H,
        "tileSize": TILE_SIZE,
        "playerSpawn": {"x": 135, "y": 120},
        "tiles": world,
        "cliffSprites": serializable_cliffs
    }
    with open(out_path, "w") as f:
        json.dump(data, f)
    print("Map JSON export complete!")


def render_full_island(world, cliff_sprites, crop_boxes=None):
    print("Rendering high-resolution full island preview canvas...")
    renderer = TileRenderer(TERRAIN_DIR)

    canvas_w = WORLD_W * TILE_SIZE
    canvas_h = WORLD_H * TILE_SIZE
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (8, 20, 36, 255))

    t_deep01 = renderer.get_tile("Water/Sea/sea_deep_base_01.png")
    t_deep02 = renderer.get_tile("Water/Sea/sea_deep_base_02.png")
    t_deep_pebbles = renderer.get_tile("Water/Sea/sea_deep_pebbles_f0.png")

    t_shallow01 = renderer.get_tile("Water/Sea/sea_shallow_base_01.png")
    t_shallow02 = renderer.get_tile("Water/Sea/sea_shallow_base_02.png")
    t_shallow_pebbles = renderer.get_tile("Water/Sea/sea_shallow_pebbles_f0.png")
    t_shallow_starfish = renderer.get_tile("Water/Sea/sea_shallow_starfish_f0.png")

    t_sand01 = renderer.get_tile("Sand/sand_base_01.png")
    t_sand02 = renderer.get_tile("Sand/sand_base_02.png")
    t_sand_slate = renderer.get_tile("Sand/sand_pebble_slate.png")
    t_sand_seashell = renderer.get_tile("Sand/sand_seashell.png")
    t_sand_starfish = renderer.get_tile("Sand/sand_starfish.png")

    t_grass01 = renderer.get_tile("Grass/grass_base_01.png")
    t_grass02 = renderer.get_tile("Grass/grass_base_02.png")
    t_grass_tuft = renderer.get_tile("Grass/grass_tuft_lush.png")
    t_grass_flower_blue = renderer.get_tile("Grass/grass_wildflower_blue.png")
    t_grass_flower_pink = renderer.get_tile("Grass/grass_wildflower_pink.png")

    t_dirt01 = renderer.get_tile("Dirt/mud_base_01.png")
    t_dirt02 = renderer.get_tile("Dirt/mud_base_02.png")
    t_mud_pebbles = renderer.get_tile("Dirt/mud_pebbles.png")
    t_mud_crater = renderer.get_tile("Dirt/mud_crater.png")
    t_mud_tuft = renderer.get_tile("Dirt/mud_tuft.png")

    t_river01 = renderer.get_tile("Water/River/river_water_base_01.png")
    t_river_lilypad = renderer.get_tile("Water/River/river_lilypad_lotus_f0.png")
    t_river_reeds = renderer.get_tile("Water/River/river_reeds_f0.png")
    t_river_pebbles = renderer.get_tile("Water/River/river_pebbles_f0.png")

    def get_tile_hash(x, y, seed=1337):
        h = (x * 0x1f1f1f1f) ^ (y * 0x5b5b5b5b) ^ seed
        h = ((h >> 16) ^ h) * 0x45d9f3b & 0xffffffff
        h = ((h >> 16) ^ h) * 0x45d9f3b & 0xffffffff
        h = (h >> 16) ^ h
        return h & 0x7fffffff

    # Pass 1: Base ground layer
    for y in range(WORLD_H):
        for x in range(WORLD_W):
            px = x * TILE_SIZE
            py = (WORLD_H - 1 - y) * TILE_SIZE
            c = world[y][x]

            if c == OCEAN_DEEP:
                val = get_tile_hash(x, y, 808) % 1000
                if val < 5:
                    deep_t = t_deep_pebbles
                else:
                    deep_t = t_deep01 if (get_tile_hash(x, y, 850) % 2 == 0) else t_deep02
                canvas.paste(deep_t, (px, py))
            elif c == OCEAN_SHALLOW:
                val = get_tile_hash(x, y, 707) % 1000
                if val < 10:
                    shallow_t = t_shallow_starfish
                elif val < 22:
                    shallow_t = t_shallow_pebbles
                else:
                    shallow_t = t_shallow01 if (get_tile_hash(x, y, 750) % 2 == 0) else t_shallow02
                canvas.paste(shallow_t, (px, py))
            elif c == BEACH_SAND:
                val = get_tile_hash(x, y, 404) % 1000
                if val < 12:
                    sand_t = t_sand_seashell
                elif val < 18:
                    sand_t = t_sand_starfish
                elif val < 28:
                    sand_t = t_sand_slate
                else:
                    sand_t = t_sand01 if (get_tile_hash(x, y, 450) % 2 == 0) else t_sand02
                canvas.paste(sand_t, (px, py))

                # Transition to Shallow Water
                sw_code = renderer.solve_wang(world, x, y, OCEAN_SHALLOW)
                if sw_code:
                    trans_tile = renderer.get_tile(f"Transitions/Sand_Water/sand_water_{sw_code}.png")
                    if trans_tile:
                        canvas.paste(trans_tile, (px, py), trans_tile)
            elif c in (GRASS_BASE, CLIFF_TOP, CLIFF_WALL):
                val = get_tile_hash(x, y, 101) % 1000
                if val < 8:
                    grass_t = t_grass_flower_blue
                elif val < 16:
                    grass_t = t_grass_flower_pink
                elif val < 36:
                    grass_t = t_grass_tuft
                else:
                    grass_t = t_grass01 if (get_tile_hash(x, y, 150) % 2 == 0) else t_grass02
                canvas.paste(grass_t, (px, py))

                # Transition to River Water
                gr_code = renderer.solve_wang(world, x, y, RIVER_WATER, is_river=True)
                if gr_code:
                    trans_tile = renderer.get_tile(f"Transitions/Grass_RiverWater/grass_riverwater_{gr_code}.png")
                    if trans_tile:
                        canvas.paste(trans_tile, (px, py), trans_tile)
                else:
                    # Transition to Sand
                    gs_code = renderer.solve_wang(world, x, y, BEACH_SAND)
                    if gs_code:
                        trans_tile = renderer.get_tile(f"Transitions/Grass_Sand/grass_sand_{gs_code}.png")
                        if trans_tile:
                            canvas.paste(trans_tile, (px, py), trans_tile)
                    else:
                        # Transition to Mud / Dirt
                        gd_code = renderer.solve_wang(world, x, y, DIRT_PATH)
                        if gd_code:
                            trans_tile = renderer.get_tile(f"Transitions/Grass_Dirt/grass_dirt_{gd_code}.png")
                            if trans_tile:
                                canvas.paste(trans_tile, (px, py), trans_tile)
            elif c == DIRT_PATH:
                val = get_tile_hash(x, y, 303) % 1000
                if val < 18:
                    dirt_t = t_mud_pebbles
                elif val < 32:
                    dirt_t = t_mud_tuft
                elif val < 42:
                    dirt_t = t_mud_crater
                else:
                    dirt_t = t_dirt01 if (get_tile_hash(x, y, 350) % 2 == 0) else t_dirt02
                canvas.paste(dirt_t, (px, py))

                # Transition to River
                dr_code = renderer.solve_wang(world, x, y, RIVER_WATER, is_river=True)
                if dr_code:
                    trans_tile = renderer.get_tile(f"Transitions/Dirt_RiverWater/dirt_riverwater_{dr_code}.png")
                    if trans_tile:
                        canvas.paste(trans_tile, (px, py), trans_tile)
                else:
                    # Transition to Sand
                    ds_code = renderer.solve_wang(world, x, y, BEACH_SAND)
                    if ds_code:
                        trans_tile = renderer.get_tile(f"Transitions/Dirt_Sand/dirt_sand_{ds_code}.png")
                        if trans_tile:
                            canvas.paste(trans_tile, (px, py), trans_tile)
            elif c == RIVER_WATER:
                val = get_tile_hash(x, y, 505) % 1000
                if val < 15:
                    river_t = t_river_lilypad
                elif val < 28:
                    river_t = t_river_reeds
                elif val < 42:
                    river_t = t_river_pebbles
                else:
                    river_t = t_river01
                canvas.paste(river_t, (px, py))

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
    export_map_json(world, cliff_sprites, "Assets/Art/Terrain/island_world_350.json")
    print("All tasks completed successfully!")
