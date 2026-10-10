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
            r_mod = 1.0 + 0.19 * math.cos(angle - 0.12)
            
            # 2. Southwestern Camp & Savanna Lobe (-x, -y, angle ~ -2.25)
            diff_sw = angle - (-2.25)
            while diff_sw > math.pi: diff_sw -= 2*math.pi
            while diff_sw < -math.pi: diff_sw += 2*math.pi
            r_mod += 0.18 * math.exp(-(diff_sw ** 2) / 0.65)

            # 3. Northwestern Hook Peninsula (+y, -x, angle ~ 2.25)
            diff_nw = angle - 2.25
            while diff_nw > math.pi: diff_nw -= 2*math.pi
            while diff_nw < -math.pi: diff_nw += 2*math.pi
            r_mod += 0.28 * math.exp(-(diff_nw ** 2) / 0.40)

            # 4. Northern Headland (+y, angle ~ 1.25)
            diff_n = angle - 1.25
            while diff_n > math.pi: diff_n -= 2*math.pi
            while diff_n < -math.pi: diff_n += 2*math.pi
            r_mod += 0.14 * math.exp(-(diff_n ** 2) / 0.35)

            # 5. Southern Crescent Lagoon Bay (-y, angle ~ -1.20)
            diff_s = angle - (-1.20)
            while diff_s > math.pi: diff_s -= 2*math.pi
            while diff_s < -math.pi: diff_s += 2*math.pi
            r_mod -= 0.24 * math.exp(-(diff_s ** 2) / 0.35)

            # 6. Northwestern Escape Cove Bay (angle ~ 1.75)
            diff_nwb = angle - 1.75
            while diff_nwb > math.pi: diff_nwb -= 2*math.pi
            while diff_nwb < -math.pi: diff_nwb += 2*math.pi
            r_mod -= 0.28 * math.exp(-(diff_nwb ** 2) / 0.22)

            # 7. Western Mid-Coast Bay indentation (angle ~ 2.9)
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

            # Multi-octave natural perturbation
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
    print("Generating base island geometry (350x350) - Iteration 2...")
    land_mask = generate_island_mask(seed=2026)
    
    print("Calculating coastal distance fields...")
    dist_to_land = compute_dist_to_land(land_mask)
    dist_to_water = compute_dist_to_water(land_mask)

    world = [[OCEAN_DEEP for _ in range(WORLD_W)] for _ in range(WORLD_H)]
    noise_shelf = ValueNoise2D(seed=3033)
    noise_beach = ValueNoise2D(seed=4044)
    noise_biome = ValueNoise2D(seed=6066)

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

    # 2. Elevated Cliff Plateau (Eastern Highlands: ~X: 232..282, Y: 185..238)
    print("Sculpting Handcrafted Eastern Cliff Plateau...")
    cliff_mask = [[False for _ in range(WORLD_W)] for _ in range(WORLD_H)]
    noise_cliff = ValueNoise2D(seed=5055)

    # Define an organic asymmetric plateau shape
    for y in range(186, 238):
        for x in range(232, 282):
            if world[y][x] == GRASS_BASE:
                edge_noise = noise_cliff.fbm(x * 0.05, y * 0.05, octaves=2) * 5.0
                dx = (x - 256.0) / 22.0
                dy = (y - 212.0) / 23.0
                if (dx*dx + dy*dy) + edge_noise * 0.08 < 0.82:
                    cliff_mask[y][x] = True

    # Plateau Top Ground
    for y in range(WORLD_H):
        for x in range(WORLD_W):
            if cliff_mask[y][x]:
                world[y][x] = CLIFF_TOP

    # South cliff wall is 2 tiles high:
    # row y is cliff_face_bot, row y+1 is cliff_face_top
    for y in range(1, WORLD_H - 2):
        for x in range(1, WORLD_W - 1):
            if not cliff_mask[y][x] and cliff_mask[y+1][x]:
                world[y][x] = CLIFF_WALL
            elif cliff_mask[y][x]:
                # Flank edges: West, East, North
                if not cliff_mask[y][x-1] or not cliff_mask[y][x+1] or not cliff_mask[y-1][x]:
                    world[y][x] = CLIFF_WALL

    # Walkable Access Routes into Plateau:
    # 1. Southwestern Mud Steps at (X: 238..239, Y: 184..188)
    for sx in [238, 239]:
        for sy in [184, 185, 186, 187, 188]:
            world[sy][sx] = DIRT_PATH
            cliff_mask[sy][sx] = False

    # 2. Northwestern Cliff Ramp at (X: 233..235, Y: 228..230)
    for rx in [233, 234, 235]:
        for ry in [228, 229, 230]:
            world[ry][rx] = DIRT_PATH
            cliff_mask[ry][rx] = False

    # 3. Winding Natural River System with Realistic Meanders & Estuary Delta
    print("Simulating Winding River with Natural Meanders & Estuary Delta...")
    waypoints = [
        (258, 222), # Spring pool on highland plateau
        (247, 218), # Highland waterfall cascade
        (234, 208), # Rocky gorge exit into lowlands
        (215, 206), # Upper forest loop (curves west)
        (196, 192), # Meander around northern jungle spur
        (186, 172), # Upper valley reach
        (172, 155), # Central Ford / Shallow River Crossing
        (176, 138), # Curves southeast past central clearing
        (195, 126), # Broad eastern meander bend
        (198, 108), # Curves back southwest
        (188, 88),  # Approach to coastal plain
        (192, 76),  # Delta entrance
        (193, 64),  # Ocean mouth
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
    ford_center = (172, 155)

    for idx, (rx, ry) in enumerate(river_path):
        progress = idx / float(len(river_path))
        # Variable width: narrow near source (1.2 rad = 2 tiles wide), widens to 2.2 rad (4 tiles)
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

    # Spring Pool on plateau: circular pool at (258, 222)
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            if dx*dx + dy*dy <= 7.0:
                river_mask[222 + dy][258 + dx] = True

    # Estuary Delta Sandbar Island at (191, 72)
    # The river fans out and wraps around a small sandy islet before entering the ocean
    delta_islet = set()
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            if dx*dx + dy*dy <= 3.5:
                delta_islet.add((191 + dx, 72 + dy))

    for y in range(WORLD_H):
        for x in range(WORLD_W):
            if (x, y) in delta_islet:
                world[y][x] = BEACH_SAND
            elif river_mask[y][x]:
                if world[y][x] not in (OCEAN_DEEP, OCEAN_SHALLOW):
                    world[y][x] = RIVER_WATER

    # Mud banks at Central Ford (172, 155)
    for fx, fy in [(170, 155), (171, 155), (173, 155), (174, 155)]:
        if world[fy][fx] == GRASS_BASE:
            world[fy][fx] = DIRT_PATH

    # 4. Starting Camp Area & Radiating Exploration Trails
    print("Carving Reserved Starting Camp Area & Exploration Paths...")
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
    # 1. South Trail (Camp -> South Beach):
    carve_path([(135, 112), (134, 102), (136, 92), (135, 86)], width=1)
    # 2. West Trail (Camp -> West Coastal Bay):
    carve_path([(127, 120), (114, 122), (102, 124), (90, 125)], width=1)
    # 3. East Trail (Camp -> Central Ford / River Crossing):
    carve_path([(143, 120), (154, 128), (164, 142), (170, 155)], width=1)
    # 4. North Trail (Camp -> Northern Jungle):
    carve_path([(135, 128), (138, 145), (144, 165), (148, 190)], width=1)

    # Trail Continuing from Ford up to Eastern Plateau:
    carve_path([(174, 155), (192, 162), (212, 172), (236, 185)], width=1)
    # Trail branching toward Northwest Escape Cove:
    carve_path([(144, 165), (134, 188), (122, 210), (110, 230)], width=1)
    # Northern Jungle Interior Trail:
    carve_path([(148, 190), (160, 215), (175, 238), (185, 255)], width=1)

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

    # C. Eastern Plateau spring sanctuary at (266, 218)
    for dy in range(-6, 7):
        for dx in range(-6, 7):
            if dx*dx + dy*dy <= 28.0:
                tx, ty = 266 + dx, 218 + dy
                if world[ty][tx] == CLIFF_TOP:
                    world[ty][tx] = DIRT_PATH

    # D. River Bend Grove at (195, 130)
    for dy in range(-5, 6):
        for dx in range(-5, 6):
            if dx*dx + dy*dy <= 18.0:
                tx, ty = 195 + dx, 130 + dy
                if world[ty][tx] == GRASS_BASE:
                    world[ty][tx] = DIRT_PATH

    # 6. Natural Dirt Patches / Forest Clearings scattered in interior
    for y in range(WORLD_H):
        for x in range(WORLD_W):
            if world[y][x] == GRASS_BASE:
                # Organic noise patches for dirt clearings in the jungle
                nv = noise_biome.sample(x * 0.08, y * 0.08)
                if nv > 0.45 and dist_to_water[y][x] > 18.0:
                    world[y][x] = DIRT_PATH

    print("Iteration 2 generation finished!")
    return world, land_mask


def render_color_preview(world, filename="scratch/island_overview.png"):
    palette = {
        OCEAN_DEEP: (18, 52, 88),      # Deep ocean blue
        OCEAN_SHALLOW: (38, 115, 165), # Turquoise shallow
        BEACH_SAND: (244, 226, 152),   # Warm tropical sand
        GRASS_BASE: (72, 148, 38),     # Lush grass
        DIRT_PATH: (170, 115, 48),     # Earthen trail
        RIVER_WATER: (48, 122, 173),   # Freshwater river
        CLIFF_WALL: (95, 68, 54),      # Cliff rock face
        CLIFF_TOP: (65, 138, 35),      # Highland grass
    }

    img = Image.new("RGB", (WORLD_W, WORLD_H))
    pixels = img.load()
    for y in range(WORLD_H):
        for x in range(WORLD_W):
            py = WORLD_H - 1 - y # Flip Y for standard map orientation
            pixels[x, py] = palette.get(world[y][x], (0, 0, 0))

    img.save(filename)
    print(f"Saved overview preview to: {filename}")
    
    img_4x = img.resize((WORLD_W * 4, WORLD_H * 4), Image.NEAREST)
    img_4x_path = filename.replace(".png", "_4x.png")
    img_4x.save(img_4x_path)
    print(f"Saved 4x overview to: {img_4x_path}")
    return img


if __name__ == "__main__":
    world, land_mask = generate_base_island()
    render_color_preview(world)
    print("Done!")
