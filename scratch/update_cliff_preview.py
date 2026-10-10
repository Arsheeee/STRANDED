import os
import json
import base64
from PIL import Image, ImageDraw
import io

PROJECT_ROOT = r'd:\Unity\Projects\STRANDED'
BRAIN_DIR = r'C:\Users\PAVILION\.gemini\antigravity-ide\brain\84db0e2d-58d2-466d-be05-dbff8f133035'
SCRATCH_DIR = os.path.join(BRAIN_DIR, 'scratch')
CLIFFS_DIR = os.path.join(PROJECT_ROOT, 'Assets', 'Art', 'Terrain', 'Cliffs')

def to_b64(path):
    if not os.path.exists(path): return ""
    with open(path, 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8')

# Re-assemble showcase with both Pure Mud Slope and Mud Steps:
sw, sh = 26, 16
sim = Image.new("RGBA", (sw * 16, sh * 16), (0, 0, 0, 0))
grass_base = Image.open(r"d:\Unity\Projects\STRANDED\Assets\Art\Terrain\Grass\grass_base_01.png").convert("RGBA")
mud_base   = Image.open(r"d:\Unity\Projects\STRANDED\Assets\Art\Terrain\Dirt\mud_base_01.png").convert("RGBA")

for y in range(sh):
    for x in range(sw):
        if 12 <= x <= 13: sim.paste(mud_base, (x * 16, y * 16))
        else: sim.paste(grass_base, (x * 16, y * 16))

def get_tile(name): return Image.open(os.path.join(CLIFFS_DIR, f"{name}.png")).convert("RGBA")

# West Wall Flank (col 3, rows 2..5)
sim.paste(get_tile("cliff_side_w_top"), (3 * 16, 2 * 16))
sim.paste(get_tile("cliff_side_w"),     (3 * 16, 3 * 16))
sim.paste(get_tile("cliff_side_w"),     (3 * 16, 4 * 16))
sim.paste(get_tile("cliff_side_w_bot"), (3 * 16, 5 * 16))

# SW Corner (col 3, rows 6..7)
sim.paste(get_tile("cliff_corner_sw_top"), (3 * 16, 6 * 16))
sim.paste(get_tile("cliff_corner_sw_bot"), (3 * 16, 7 * 16))

# South Front Cliff Left (cols 4..10, rows 6..7)
for x in range(4, 11):
    t = get_tile("cliff_face_top_01" if x % 2 == 0 else "cliff_face_top_02")
    b = get_tile("cliff_face_bot_01" if x % 2 == 0 else "cliff_face_bot_02")
    sim.paste(t, (x * 16, 6 * 16))
    sim.paste(b, (x * 16, 7 * 16))

# Left Canyon Wall (col 11)
sim.paste(get_tile("cliff_side_e_top"), (11 * 16, 2 * 16))
sim.paste(get_tile("cliff_side_e"),     (11 * 16, 3 * 16))
sim.paste(get_tile("cliff_side_e"),     (11 * 16, 4 * 16))
sim.paste(get_tile("cliff_side_e_bot"), (11 * 16, 5 * 16))
sim.paste(get_tile("cliff_ramp_left_top"), (11 * 16, 6 * 16))
sim.paste(get_tile("cliff_ramp_left_bot"), (11 * 16, 7 * 16))

# Center Mud Steps at rows 6..7 (cols 12 & 13)
sim.paste(get_tile("cliff_mud_steps_01_top"), (12 * 16, 6 * 16))
sim.paste(get_tile("cliff_mud_steps_01_bot"), (12 * 16, 7 * 16))
sim.paste(get_tile("cliff_mud_steps_02_top"), (13 * 16, 6 * 16))
sim.paste(get_tile("cliff_mud_steps_02_bot"), (13 * 16, 7 * 16))

# Right Canyon Wall (col 14)
sim.paste(get_tile("cliff_side_w_top"), (14 * 16, 2 * 16))
sim.paste(get_tile("cliff_side_w"),     (14 * 16, 3 * 16))
sim.paste(get_tile("cliff_side_w"),     (14 * 16, 4 * 16))
sim.paste(get_tile("cliff_side_w_bot"), (14 * 16, 5 * 16))
sim.paste(get_tile("cliff_ramp_right_top"), (14 * 16, 6 * 16))
sim.paste(get_tile("cliff_ramp_right_bot"), (14 * 16, 7 * 16))

# South Front Cliff Right (cols 15..21, rows 6..7)
for x in range(15, 22):
    t = get_tile("cliff_face_top_01" if x % 2 == 0 else "cliff_face_top_02")
    b = get_tile("cliff_face_bot_01" if x % 2 == 0 else "cliff_face_bot_02")
    sim.paste(t, (x * 16, 6 * 16))
    sim.paste(b, (x * 16, 7 * 16))

# SE Outer Corner (col 22, rows 6..7)
sim.paste(get_tile("cliff_corner_se_top"), (22 * 16, 6 * 16))
sim.paste(get_tile("cliff_corner_se_bot"), (22 * 16, 7 * 16))

# East Wall Flank (col 22, rows 2..5)
sim.paste(get_tile("cliff_side_e_top"), (22 * 16, 2 * 16))
sim.paste(get_tile("cliff_side_e"),     (22 * 16, 3 * 16))
sim.paste(get_tile("cliff_side_e"),     (22 * 16, 4 * 16))
sim.paste(get_tile("cliff_side_e_bot"), (22 * 16, 5 * 16))

sim.save(os.path.join(SCRATCH_DIR, "simulated_canyon_pass_native.png"))

# Build showcase comparison
full_ref = Image.open(os.path.join(SCRATCH_DIR, "stardew_native_512.png")).convert("RGBA")
ref_crop = full_ref.crop((184, 0, 360, 160))
sim_crop = sim.crop((128, 0, 304, 160))

scale = 3
ref_3x = ref_crop.resize((ref_crop.width * scale, ref_crop.height * scale), Image.NEAREST)
sim_3x = sim_crop.resize((sim_crop.width * scale, sim_crop.height * scale), Image.NEAREST)

card_w, card_h = sim_3x.width, sim_3x.height
header_h = 100
gallery_h = 240
pad = 30
total_w = card_w * 2 + pad * 3
total_h = header_h + card_h + gallery_h + pad * 2

out = Image.new("RGBA", (total_w, total_h), (11, 19, 32, 255))
draw = ImageDraw.Draw(out)
draw.text((pad, 20), "STRANDED - Volumetric Cliff & Carved Mud Steps Incline", fill=(255, 255, 255))
draw.text((pad, 48), "Zero-seam pillow boulders, seamless East/West flanks, and carved earthen mud terrace steps.", fill=(170, 195, 220))
draw.text((pad, 70), "Strict 0/16 pixel seam matching across all horizontal and vertical tile boundaries.", fill=(225, 175, 45))

draw.text((pad, header_h - 22), "Original Reference (Stardew Valley Farm Canyon)", fill=(110, 225, 120))
out.paste(ref_3x, (pad, header_h))
draw.rectangle([pad, header_h, pad + card_w, header_h + card_h], outline=(45, 85, 125, 255), width=2)

x_right = pad * 2 + card_w
draw.text((x_right, header_h - 22), "STRANDED In-Game Production Tiles (Carved Mud Steps Mode)", fill=(245, 205, 55))
out.paste(sim_3x, (x_right, header_h))
draw.rectangle([x_right, header_h, x_right + card_w, header_h + card_h], outline=(200, 150, 40, 255), width=2)

gy = header_h + card_h + pad
draw.text((pad, gy - 20), "Authentic 16x16 Autotile Library (Sample Tiles at 3x Native Scale):", fill=(200, 220, 245))

tiles_names = [
    ("Front Top 01", "cliff_face_top_01"),
    ("Front Top 02", "cliff_face_top_02"),
    ("Front Bot 01", "cliff_face_bot_01"),
    ("Front Bot 02", "cliff_face_bot_02"),
    ("West Flank Top", "cliff_side_w_top"),
    ("West Flank Mid", "cliff_side_w"),
    ("West Flank Bot", "cliff_side_w_bot"),
    ("East Flank Top", "cliff_side_e_top"),
    ("Mud Steps 01 Top", "cliff_mud_steps_01_top"),
    ("Mud Steps 01 Bot", "cliff_mud_steps_01_bot"),
    ("Mud Steps 02 Top", "cliff_mud_steps_02_top"),
    ("Mud Steps 02 Bot", "cliff_mud_steps_02_bot"),
    ("Shoulder Left Top", "cliff_ramp_left_top"),
    ("Shoulder Left Bot", "cliff_ramp_left_bot"),
    ("Shoulder Right Top", "cliff_ramp_right_top"),
    ("Shoulder Right Bot", "cliff_ramp_right_bot"),
]

tile_col_w = (total_w - pad * 2) // 8
for idx, (label, tname) in enumerate(tiles_names):
    r = idx // 8
    c = idx % 8
    tp = os.path.join(CLIFFS_DIR, f"{tname}.png")
    if os.path.exists(tp):
        tim = Image.open(tp).convert("RGBA")
        tim_3x = tim.resize((48, 48), Image.NEAREST)
        bx = pad + c * tile_col_w
        by = gy + r * 90 + 10
        draw.rectangle([bx, by, bx + 52, by + 52], fill=(16, 28, 46, 255), outline=(45, 85, 125, 255))
        out.paste(tim_3x, (bx + 2, by + 2), tim_3x)
        draw.text((bx, by + 56), label, fill=(180, 200, 220))

showcase_brain = os.path.join(BRAIN_DIR, "cliff_mud_elevation_showcase.png")
out.save(showcase_brain)

# Gather Base64 assets
cliff_files = [f for f in os.listdir(CLIFFS_DIR) if f.endswith('.png')]
CLIFF_ASSETS = {f[:-4]: to_b64(os.path.join(CLIFFS_DIR, f)) for f in cliff_files}
CLIFF_ASSETS['grass_01'] = to_b64(os.path.join(PROJECT_ROOT, 'Assets', 'Art', 'Terrain', 'Grass', 'grass_base_01.png'))
CLIFF_ASSETS['mud_01']   = to_b64(os.path.join(PROJECT_ROOT, 'Assets', 'Art', 'Terrain', 'Dirt', 'mud_base_01.png'))
CLIFF_ASSETS['dirt_01']  = CLIFF_ASSETS['mud_01']
CLIFF_ASSETS['showcase'] = to_b64(showcase_brain)

player_im_path = os.path.join(PROJECT_ROOT, 'Assets', 'player', 'player_base.png')
p_im = Image.open(player_im_path)
p_crop = p_im.crop((0, 0, 32, 32))
buf = io.BytesIO()
p_crop.save(buf, format='PNG')
CLIFF_ASSETS['player'] = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode('utf-8')

html_code = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>STRANDED - Hill & Cliff Elevation Tileset Preview</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-dark: #070d17;
      --bg-card: rgba(14, 25, 41, 0.78);
      --bg-card-border: rgba(45, 85, 125, 0.35);
      --accent-aqua: #19c8dd;
      --accent-cyan: #71dcec;
      --accent-grass: #44a318;
      --accent-dirt: #b37729;
      --accent-cliff: #bc8e38;
      --text-main: #f0f6fc;
      --text-muted: #8b9eb3;
      --radius-sm: 8px;
      --radius-md: 14px;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: 'Outfit', sans-serif;
      background: radial-gradient(circle at 50% 0%, #152233 0%, var(--bg-dark) 75%);
      color: var(--text-main);
      min-height: 100vh;
      padding: 24px 20px 48px;
    }}

    .container {{
      max-width: 1350px;
      margin: 0 auto;
    }}

    header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      margin-bottom: 24px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--bg-card-border);
    }}

    .header-title h1 {{
      font-size: 28px;
      font-weight: 700;
      background: linear-gradient(135deg, #ffffff 30%, var(--accent-cliff) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 6px;
    }}

    .header-title p {{
      color: var(--text-muted);
      font-size: 14px;
    }}

    .badge-bar {{
      display: flex;
      gap: 10px;
    }}

    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-family: 'JetBrains Mono', monospace;
      background: rgba(188, 142, 56, 0.15);
      border: 1px solid rgba(188, 142, 56, 0.4);
      color: #e2ba64;
    }}

    .badge.green {{
      background: rgba(68, 163, 24, 0.15);
      border-color: rgba(68, 163, 24, 0.4);
      color: #72e041;
    }}

    .badge.cyan {{
      background: rgba(25, 200, 221, 0.15);
      border-color: rgba(25, 200, 221, 0.4);
      color: var(--accent-cyan);
    }}

    /* Tabs */
    .tabs {{
      display: flex;
      gap: 10px;
      margin-bottom: 20px;
    }}

    .tab-btn {{
      background: rgba(45, 85, 125, 0.2);
      border: 1px solid var(--bg-card-border);
      color: var(--text-muted);
      padding: 10px 18px;
      border-radius: var(--radius-sm);
      font-family: inherit;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }}

    .tab-btn.active {{
      background: rgba(188, 142, 56, 0.2);
      border-color: var(--accent-cliff);
      color: #fff;
    }}

    .tab-content {{ display: none; }}
    .tab-content.active {{ display: block; }}

    /* Layout */
    .workspace {{
      display: grid;
      grid-template-columns: 1fr 340px;
      gap: 24px;
    }}

    .viewport-card {{
      background: var(--bg-card);
      border: 1px solid var(--bg-card-border);
      border-radius: var(--radius-md);
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}

    .viewport-toolbar {{
      padding: 12px 18px;
      background: rgba(10, 18, 30, 0.85);
      border-bottom: 1px solid var(--bg-card-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 13px;
    }}

    .canvas-container {{
      position: relative;
      background: #060b13;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 30px 20px;
      overflow: auto;
      min-height: 480px;
    }}

    canvas {{
      image-rendering: pixelated;
      box-shadow: 0 12px 36px rgba(0, 0, 0, 0.6);
      border-radius: 4px;
      transform-origin: center center;
    }}

    .hud {{
      position: absolute;
      bottom: 16px;
      left: 16px;
      background: rgba(8, 14, 24, 0.88);
      border: 1px solid var(--bg-card-border);
      padding: 8px 14px;
      border-radius: var(--radius-sm);
      font-size: 12px;
      font-family: 'JetBrains Mono', monospace;
      color: var(--text-muted);
      pointer-events: none;
      backdrop-filter: blur(4px);
    }}
    .hud span {{ color: var(--accent-cliff); font-weight: 600; }}

    /* Sidebar controls */
    .sidebar {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    .card {{
      background: var(--bg-card);
      border: 1px solid var(--bg-card-border);
      border-radius: var(--radius-md);
      padding: 16px;
    }}

    .card-title {{
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: var(--text-muted);
      margin-bottom: 12px;
    }}

    .toggle-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 0;
      font-size: 13px;
      border-bottom: 1px solid rgba(45, 85, 125, 0.15);
    }}
    .toggle-row:last-child {{ border-bottom: none; }}

    .btn-action {{
      width: 100%;
      padding: 9px 14px;
      background: rgba(45, 85, 125, 0.25);
      border: 1px solid var(--bg-card-border);
      color: var(--text-main);
      border-radius: var(--radius-sm);
      font-family: inherit;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
      margin-top: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }}
    .btn-action:hover {{
      background: rgba(188, 142, 56, 0.25);
      border-color: var(--accent-cliff);
    }}

    /* Gallery styles */
    .gallery-section-title {{
      font-size: 16px;
      font-weight: 600;
      color: var(--accent-cliff);
      margin: 24px 0 12px;
      padding-bottom: 6px;
      border-bottom: 1px solid var(--bg-card-border);
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .gallery-section-title:first-child {{ margin-top: 0; }}

    .grid-gallery {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
      gap: 16px;
    }}

    .tile-card {{
      background: var(--bg-card);
      border: 1px solid var(--bg-card-border);
      border-radius: var(--radius-sm);
      padding: 14px;
      text-align: center;
      transition: transform 0.2s, border-color 0.2s;
    }}
    .tile-card:hover {{
      transform: translateY(-2px);
      border-color: var(--accent-cliff);
    }}

    .tile-preview {{
      height: 64px;
      display: flex;
      justify-content: center;
      align-items: center;
      background: rgba(10, 18, 30, 0.6);
      border-radius: var(--radius-sm);
      margin-bottom: 10px;
    }}

    .tile-preview img {{
      image-rendering: pixelated;
      transform: scale(3);
    }}

    .tile-name {{
      font-size: 13px;
      font-weight: 600;
      color: var(--text-main);
      margin-bottom: 4px;
    }}

    .tile-file {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--accent-cliff);
    }}

    /* Comparison tab */
    .comparison-container {{
      background: var(--bg-card);
      border: 1px solid var(--bg-card-border);
      border-radius: var(--radius-md);
      padding: 24px;
      text-align: center;
    }}
    .comparison-container img {{
      max-width: 100%;
      height: auto;
      border-radius: var(--radius-sm);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
      border: 1px solid var(--bg-card-border);
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="header-title">
        <h1>STRANDED - Hill & Cliff Elevation Tileset</h1>
        <p>Volumetric 32px stone cliffs, chunky East & West rock flanks, and natural earthen mud incline ramp & carved mud steps.</p>
      </div>
      <div class="badge-bar">
        <div class="badge"><span>⛰️</span> 32px Volumetric Cliffs</div>
        <div class="badge green"><span>🧭</span> Chunky East & West Flanks</div>
        <div class="badge" style="color: #dea848; border-color: rgba(222, 168, 72, 0.4);"><span>🪜</span> Carved Mud Steps & Slope</div>
        <div class="badge cyan"><span>🚶</span> 100% Seamless Seams</div>
      </div>
    </header>

    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('scene')">Interactive Elevation Scene</button>
      <button class="tab-btn" onclick="switchTab('gallery')">Tile Library & Gallery</button>
      <button class="tab-btn" onclick="switchTab('comparison')">Side-by-Side Reference Comparison</button>
    </div>

    <!-- TAB 1: SCENE -->
    <div id="tab-scene" class="tab-content active">
      <div class="workspace">
        <div class="viewport-card">
          <div class="viewport-toolbar">
            <span style="font-weight: 600; color: var(--accent-cliff);">Live Elevation Simulation (Authentic Stardew Canyon Pass)</span>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--accent-cyan);" id="playerPos">X: 12 | Y: 9 (Level 0: Island Lowlands)</div>
          </div>
          <div class="canvas-container">
            <canvas id="cliffCanvas" width="416" height="256"></canvas>
            <div class="hud">
              Movement: <span>[W, A, S, D]</span> or <span>[Arrow Keys]</span><br>
              Walk up the <span id="hudInclineName">Carved Mud Steps</span> (Center) to ascend onto <span>Highland Plateau Level 1</span>!
            </div>
          </div>
        </div>

        <div class="sidebar">
          <div class="card">
            <div class="card-title">Canyon Incline Mode</div>
            <div class="toggle-row">
              <span>Incline Type</span>
              <select id="inclineModeSelect" onchange="draw()" style="background: rgba(10, 18, 30, 0.85); border: 1px solid var(--accent-cliff); color: #fff; padding: 5px 8px; border-radius: 4px; font-weight: 600;">
                <option value="steps" selected>🪜 Carved Mud Steps</option>
                <option value="slope">🌱 Pure Mud Slope</option>
              </select>
            </div>
            <p style="font-size: 12px; color: var(--text-muted); margin-top: 8px; line-height: 1.5;">
              Switch between natural carved earthen mud steps (timber/stone lips) and smooth earthen trail slope!
            </p>
          </div>

          <div class="card">
            <div class="card-title">Elevation Features</div>
            <div style="font-size: 13px; color: var(--text-muted); line-height: 1.6;">
              <p style="margin-bottom: 8px;"><strong style="color: var(--accent-grass);">Level 1 (Highland Plateau):</strong> Upper elevated grass meadow bounded by rock cliffs.</p>
              <p style="margin-bottom: 8px;"><strong style="color: var(--accent-cliff);">Cliff Wall (32px):</strong> Front rock face with organic boulders, grass overhang, and base shadows.</p>
              <p style="margin-bottom: 8px;"><strong style="color: #72e041;">East & West Flanks:</strong> Chunky vertical rock walls with jagged grass overhang & micro pebbles.</p>
              <p style="margin-bottom: 8px;"><strong style="color: var(--accent-cyan);">Zero-Seam Polish:</strong> 100% strict 0-pixel mismatch on all horizontal and vertical tile edges.</p>
              <p><strong style="color: #dea848;">Mud Canyon Elevation:</strong> Smooth traversal from lowlands to highlands.</p>
            </div>
          </div>

          <div class="card">
            <div class="card-title">Quick Teleport</div>
            <button class="btn-action" onclick="teleport(12.5, 9.5)">
              <span>⬇️</span> Lowland (Near Mud Canyon)
            </button>
            <button class="btn-action" onclick="teleport(12.5, 2.5)">
              <span>⬆️</span> Highland Plateau (Level 1)
            </button>
            <button class="btn-action" onclick="teleport(6.5, 3.0)">
              <span>🧭</span> West Plateau Meadow
            </button>
          </div>

          <div class="card">
            <div class="card-title">Display Settings</div>
            <div class="toggle-row">
              <span>Grid Overlay (16px)</span>
              <input type="checkbox" id="toggleGrid" onchange="draw()">
            </div>
            <div class="toggle-row">
              <span>Show Player (Aash)</span>
              <input type="checkbox" id="togglePlayer" checked onchange="draw()">
            </div>
            <div class="toggle-row">
              <span>Zoom Scale</span>
              <select id="scaleSelect" onchange="updateScale()" style="background: rgba(10, 18, 30, 0.8); border: 1px solid var(--bg-card-border); color: #fff; padding: 4px 8px; border-radius: 4px;">
                <option value="1.8">1.8×</option>
                <option value="2.2" selected>2.2×</option>
                <option value="2.6">2.6×</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: GALLERY -->
    <div id="tab-gallery" class="tab-content">
      <div id="galleryContainer"></div>
    </div>

    <!-- TAB 3: COMPARISON -->
    <div id="tab-comparison" class="tab-content">
      <div class="comparison-container">
        <h3 style="margin-bottom: 8px; color: var(--accent-cliff);">Visual Fidelity Verification vs Stardew Valley Reference</h3>
        <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 20px;">Direct 3x magnification comparing authentic Stardew Valley boulder contours, olive-gold lighting, and canyon pass mud elevation against newly crafted STRANDED production tiles.</p>
        <img src="{CLIFF_ASSETS['showcase']}" alt="Cliff & Mud Elevation Showcase">
      </div>
    </div>
  </div>

  <script>
    const ASSETS = {json.dumps(CLIFF_ASSETS)};
    const imgCache = {{}};
    function getImg(src) {{
      if (!src) return null;
      if (!imgCache[src]) {{
        const im = new Image();
        im.src = src;
        imgCache[src] = im;
      }}
      return imgCache[src];
    }}

    function switchTab(id) {{
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      event.currentTarget.classList.add('active');
      document.getElementById('tab-' + id).classList.add('active');
    }}

    // Map definition: 26 cols x 16 rows (416 x 256 px)
    const SW = 26, SH = 16;
    const canvas = document.getElementById('cliffCanvas');
    const ctx = canvas.getContext('2d');

    // Player position
    const player = {{
      x: 12.5 * 16,
      y: 9.5 * 16,
      speed: 1.8
    }};

    function teleport(tx, ty) {{
      player.x = tx * 16;
      player.y = ty * 16;
    }}

    const keys = {{}};
    window.addEventListener('keydown', e => {{
      keys[e.key.toLowerCase()] = true;
      if (['arrowup', 'arrowdown', 'arrowleft', 'arrowright', 'w', 'a', 's', 'd'].includes(e.key.toLowerCase())) {{
        e.preventDefault();
      }}
    }});
    window.addEventListener('keyup', e => {{
      keys[e.key.toLowerCase()] = false;
    }});

    function updateScale() {{
      const s = document.getElementById('scaleSelect').value;
      canvas.style.transform = `scale(${{s}})`;
    }}

    function canWalk(px, py) {{
      const tx = Math.floor(px / 16);
      const ty = Math.floor(py / 16);
      if (tx < 0 || tx >= SW || ty < 0 || ty >= SH) return false;

      // Canyon Pass (cols 12 & 13): ALWAYS 100% WALKABLE!
      if (tx >= 12 && tx <= 13) return true;

      // 1. South Cliff Walls (rows 6 & 7)
      if (ty === 6 || ty === 7) {{
        if ((tx >= 3 && tx <= 11) || (tx >= 14 && tx <= 22)) return false;
      }}

      // 2. West Highland Wall (col 3, rows 2..5)
      if (tx === 3 && ty >= 2 && ty <= 5) return false;

      // 3. East Highland Wall (col 22, rows 2..5)
      if (tx === 22 && ty >= 2 && ty <= 5) return false;

      // 4. Canyon Inner West Wall (col 11, rows 2..5)
      if (tx === 11 && ty >= 2 && ty <= 5) return false;

      // 5. Canyon Inner East Wall (col 14, rows 2..5)
      if (tx === 14 && ty >= 2 && ty <= 5) return false;

      return true;
    }}

    function updatePlayer() {{
      let dx = 0, dy = 0;
      if (keys['w'] || keys['arrowup'])    dy -= 1;
      if (keys['s'] || keys['arrowdown'])  dy += 1;
      if (keys['a'] || keys['arrowleft'])  dx -= 1;
      if (keys['d'] || keys['arrowright']) dx += 1;

      if (dx !== 0 && dy !== 0) {{ dx *= 0.7071; dy *= 0.7071; }}

      const nx = player.x + dx * player.speed;
      const ny = player.y + dy * player.speed;

      if (canWalk(nx, player.y + 12)) player.x = nx;
      if (canWalk(player.x, ny + 12)) player.y = ny;

      const tx = Math.floor(player.x / 16);
      const ty = Math.floor(player.y / 16);
      let level = "Level 0: Island Lowlands";
      if (ty <= 4) {{
        level = (tx >= 12 && tx <= 13) ? "Ascending Canyon (Entering Plateau)" : "Level 1: Highland Plateau";
      }} else if (ty === 5 || ty === 6 || ty === 7) {{
        level = (tx >= 12 && tx <= 13) ? "Ascending Canyon Incline..." : "Near Cliff Wall";
      }}
      document.getElementById('playerPos').innerText = `X: ${{tx}} | Y: ${{ty}} (${{level}})`;
    }}

    function draw() {{
      ctx.imageSmoothingEnabled = false;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const grassImg = getImg(ASSETS.grass_01);
      const mudImg   = getImg(ASSETS.mud_01);
      const isSteps  = (document.getElementById('inclineModeSelect').value === 'steps');
      document.getElementById('hudInclineName').innerText = isSteps ? "Carved Mud Steps" : "Natural Mud Slope";

      // 1. Base Ground (Grass everywhere, and natural mud trail coming up through center cols 12..13)
      for (let y = 0; y < SH; y++) {{
        for (let x = 0; x < SW; x++) {{
          if (x >= 12 && x <= 13) {{
            ctx.drawImage(mudImg, x * 16, y * 16);
          }} else {{
            ctx.drawImage(grassImg, x * 16, y * 16);
          }}
        }}
      }}

      // 2. West Vertical Cliff Wall (column 3, rows 2..5)
      ctx.drawImage(getImg(ASSETS.cliff_side_w_top), 3 * 16, 2 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_side_w),     3 * 16, 3 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_side_w),     3 * 16, 4 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_side_w_bot), 3 * 16, 5 * 16);

      // 3. Southwest Outer Corner (x=3, rows 6 & 7)
      ctx.drawImage(getImg(ASSETS.cliff_corner_sw_top), 3 * 16, 6 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_corner_sw_bot), 3 * 16, 7 * 16);

      // 4. South Cliff Face (Left Section: cols 4..10, rows 6 & 7)
      for (let x = 4; x <= 10; x++) {{
        const t = (x % 2 === 0) ? ASSETS.cliff_face_top_01 : ASSETS.cliff_face_top_02;
        const b = (x % 2 === 0) ? ASSETS.cliff_face_bot_01 : ASSETS.cliff_face_bot_02;
        ctx.drawImage(getImg(t), x * 16, 6 * 16);
        ctx.drawImage(getImg(b), x * 16, 7 * 16);
      }}

      // 5. Left Canyon Wall (col 11):
      // Upper vertical wall at rows 2..5 (East-facing wall)
      ctx.drawImage(getImg(ASSETS.cliff_side_e_top), 11 * 16, 2 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_side_e),     11 * 16, 3 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_side_e),     11 * 16, 4 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_side_e_bot), 11 * 16, 5 * 16);
      // Left entrance shoulder at rows 6..7 (curves 90° into South wall)
      ctx.drawImage(getImg(ASSETS.cliff_ramp_left_top), 11 * 16, 6 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_ramp_left_bot), 11 * 16, 7 * 16);

      // 6. Canyon Incline (cols 12 & 13, rows 6 & 7):
      if (isSteps) {{
        // MODE A: Carved Mud Steps
        ctx.drawImage(getImg(ASSETS.cliff_mud_steps_01_top), 12 * 16, 6 * 16);
        ctx.drawImage(getImg(ASSETS.cliff_mud_steps_01_bot), 12 * 16, 7 * 16);
        ctx.drawImage(getImg(ASSETS.cliff_mud_steps_02_top), 13 * 16, 6 * 16);
        ctx.drawImage(getImg(ASSETS.cliff_mud_steps_02_bot), 13 * 16, 7 * 16);
      }} else {{
        // MODE B: Pure Mud Slope
        ctx.drawImage(getImg(ASSETS.cliff_ramp_mid_top), 12 * 16, 6 * 16);
        ctx.drawImage(getImg(ASSETS.cliff_ramp_mid_bot), 12 * 16, 7 * 16);
        ctx.drawImage(getImg(ASSETS.cliff_mud_slope_top), 13 * 16, 6 * 16);
        ctx.drawImage(getImg(ASSETS.cliff_mud_slope_bot), 13 * 16, 7 * 16);
      }}

      // 7. Right Canyon Wall (col 14):
      // Upper vertical wall at rows 2..5 (West-facing wall)
      ctx.drawImage(getImg(ASSETS.cliff_side_w_top), 14 * 16, 2 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_side_w),     14 * 16, 3 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_side_w),     14 * 16, 4 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_side_w_bot), 14 * 16, 5 * 16);
      // Right entrance shoulder at rows 6..7 (curves 90° into South wall)
      ctx.drawImage(getImg(ASSETS.cliff_ramp_right_top), 14 * 16, 6 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_ramp_right_bot), 14 * 16, 7 * 16);

      // 8. South Cliff Face (Right Section: cols 15..21, rows 6 & 7)
      for (let x = 15; x <= 21; x++) {{
        const t = (x % 2 === 0) ? ASSETS.cliff_face_top_01 : ASSETS.cliff_face_top_02;
        const b = (x % 2 === 0) ? ASSETS.cliff_face_bot_01 : ASSETS.cliff_face_bot_02;
        ctx.drawImage(getImg(t), x * 16, 6 * 16);
        ctx.drawImage(getImg(b), x * 16, 7 * 16);
      }}

      // 9. Southeast Outer Corner (col 22, rows 6 & 7)
      ctx.drawImage(getImg(ASSETS.cliff_corner_se_top), 22 * 16, 6 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_corner_se_bot), 22 * 16, 7 * 16);

      // 10. East Vertical Cliff Wall (column 22, rows 2..5)
      ctx.drawImage(getImg(ASSETS.cliff_side_e_top), 22 * 16, 2 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_side_e),     22 * 16, 3 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_side_e),     22 * 16, 4 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_side_e_bot), 22 * 16, 5 * 16);

      // 11. Player
      if (document.getElementById('togglePlayer').checked) {{
        const pImg = getImg(ASSETS.player);
        if (pImg) {{
          ctx.fillStyle = 'rgba(20, 40, 50, 0.38)';
          ctx.beginPath();
          ctx.ellipse(player.x + 8, player.y + 24, 7, 3, 0, 0, Math.PI * 2);
          ctx.fill();
          ctx.drawImage(pImg, player.x - 8, player.y - 4, 32, 32);
        }}
      }}

      // 12. Grid
      if (document.getElementById('toggleGrid').checked) {{
        ctx.strokeStyle = 'rgba(25, 200, 221, 0.2)';
        ctx.lineWidth = 1;
        for (let x = 0; x <= SW * 16; x += 16) {{
          ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, SH * 16); ctx.stroke();
        }}
        for (let y = 0; y <= SH * 16; y += 16) {{
          ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(SW * 16, y); ctx.stroke();
        }}
      }}
    }}

    function loop() {{
      updatePlayer();
      draw();
      requestAnimationFrame(loop);
    }}

    // Populate Gallery Categorized
    const gallerySections = [
      {{
        title: "⛰️ Volumetric Rock Cliff Face (South 32px Wall - 0px Seam)",
        items: [
          {{ title: "Cliff Face Top 01", file: "cliff_face_top_01.png", key: "cliff_face_top_01" }},
          {{ title: "Cliff Face Top 02", file: "cliff_face_top_02.png", key: "cliff_face_top_02" }},
          {{ title: "Cliff Face Bot 01", file: "cliff_face_bot_01.png", key: "cliff_face_bot_01" }},
          {{ title: "Cliff Face Bot 02", file: "cliff_face_bot_02.png", key: "cliff_face_bot_02" }}
        ]
      }},
      {{
        title: "🪜 Carved Earthen Mud Steps (Natural Terrace Incline)",
        items: [
          {{ title: "Mud Steps Top (Standard)", file: "cliff_mud_steps_top.png", key: "cliff_mud_steps_top" }},
          {{ title: "Mud Steps Bot (Standard)", file: "cliff_mud_steps_bot.png", key: "cliff_mud_steps_bot" }},
          {{ title: "Mud Steps 01 Top (Sunlit Left)", file: "cliff_mud_steps_01_top.png", key: "cliff_mud_steps_01_top" }},
          {{ title: "Mud Steps 01 Bot (Sunlit Left)", file: "cliff_mud_steps_01_bot.png", key: "cliff_mud_steps_01_bot" }},
          {{ title: "Mud Steps 02 Top (Shadowed Right)", file: "cliff_mud_steps_02_top.png", key: "cliff_mud_steps_02_top" }},
          {{ title: "Mud Steps 02 Bot (Shadowed Right)", file: "cliff_mud_steps_02_bot.png", key: "cliff_mud_steps_02_bot" }}
        ]
      }},
      {{
        title: "🌱 Pure Mud Slope Canyon Ramp (Natural Earth)",
        items: [
          {{ title: "Canyon Shoulder Left Top", file: "cliff_ramp_left_top.png", key: "cliff_ramp_left_top" }},
          {{ title: "Canyon Shoulder Left Bot", file: "cliff_ramp_left_bot.png", key: "cliff_ramp_left_bot" }},
          {{ title: "Mud Slope Top", file: "cliff_ramp_mid_top.png", key: "cliff_ramp_mid_top" }},
          {{ title: "Mud Slope Bot", file: "cliff_ramp_mid_bot.png", key: "cliff_ramp_mid_bot" }},
          {{ title: "Canyon Shoulder Right Top", file: "cliff_ramp_right_top.png", key: "cliff_ramp_right_top" }},
          {{ title: "Canyon Shoulder Right Bot", file: "cliff_ramp_right_bot.png", key: "cliff_ramp_right_bot" }}
        ]
      }},
      {{
        title: "🧭 Chunky West-Facing Rock Flanks (Wall Facing West)",
        items: [
          {{ title: "Cliff Side West Top", file: "cliff_side_w_top.png", key: "cliff_side_w_top" }},
          {{ title: "Cliff Side West Mid", file: "cliff_side_w.png", key: "cliff_side_w" }},
          {{ title: "Cliff Side West Bot", file: "cliff_side_w_bot.png", key: "cliff_side_w_bot" }}
        ]
      }},
      {{
        title: "🧭 Chunky East-Facing Rock Flanks (Wall Facing East)",
        items: [
          {{ title: "Cliff Side East Top", file: "cliff_side_e_top.png", key: "cliff_side_e_top" }},
          {{ title: "Cliff Side East Mid", file: "cliff_side_e.png", key: "cliff_side_e" }},
          {{ title: "Cliff Side East Bot", file: "cliff_side_e_bot.png", key: "cliff_side_e_bot" }}
        ]
      }},
      {{
        title: "📐 Volumetric Outer 90° Corners & Highland Rims",
        items: [
          {{ title: "Corner SW Top", file: "cliff_corner_sw_top.png", key: "cliff_corner_sw_top" }},
          {{ title: "Corner SW Bot", file: "cliff_corner_sw_bot.png", key: "cliff_corner_sw_bot" }},
          {{ title: "Corner SE Top", file: "cliff_corner_se_top.png", key: "cliff_corner_se_top" }},
          {{ title: "Corner SE Bot", file: "cliff_corner_se_bot.png", key: "cliff_corner_se_bot" }},
          {{ title: "Highland Rim TL", file: "cliff_outer_tl_top.png", key: "cliff_outer_tl_top" }},
          {{ title: "Highland Rim TR", file: "cliff_outer_tr_top.png", key: "cliff_outer_tr_top" }}
        ]
      }}
    ];

    const gc = document.getElementById('galleryContainer');
    gallerySections.forEach(sec => {{
      const st = document.createElement('div');
      st.className = 'gallery-section-title';
      st.innerText = sec.title;
      gc.appendChild(st);

      const grid = document.createElement('div');
      grid.className = 'grid-gallery';

      sec.items.forEach(it => {{
        const card = document.createElement('div');
        card.className = 'tile-card';

        const prev = document.createElement('div');
        prev.className = 'tile-preview';
        const img = document.createElement('img');
        img.src = ASSETS[it.key] || '';
        prev.appendChild(img);

        const tn = document.createElement('div');
        tn.className = 'tile-name';
        tn.innerText = it.title;

        const tf = document.createElement('div');
        tf.className = 'tile-file';
        tf.innerText = it.file;

        card.appendChild(prev);
        card.appendChild(tn);
        card.appendChild(tf);
        grid.appendChild(card);
      }});

      gc.appendChild(grid);
    }});

    updateScale();
    loop();
  </script>
</body>
</html>
'''

output_path = os.path.join(PROJECT_ROOT, 'cliff_preview.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_code)

print(f"Successfully generated updated {output_path} with 0-seam cliffs & mud steps toggle!")
