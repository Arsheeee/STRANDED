import os
import json
import base64

PROJECT_ROOT = r'd:\Unity\Projects\STRANDED'
BRAIN_DIR = r'C:\Users\PAVILION\.gemini\antigravity-ide\brain\84db0e2d-58d2-466d-be05-dbff8f133035'
CLIFFS_DIR = os.path.join(PROJECT_ROOT, 'Assets', 'Art', 'Terrain', 'Cliffs')

def to_b64(path):
    if not os.path.exists(path):
        return ""
    with open(path, 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8')

print("Compiling Cliff preview assets...")

# Gather cliff sprites
cliff_files = [f for f in os.listdir(CLIFFS_DIR) if f.endswith('.png')]
CLIFF_ASSETS = {f[:-4]: to_b64(os.path.join(CLIFFS_DIR, f)) for f in cliff_files}

# Base terrain
CLIFF_ASSETS['grass_01'] = to_b64(os.path.join(PROJECT_ROOT, 'Assets', 'Art', 'Terrain', 'Grass', 'grass_base_01.png'))
CLIFF_ASSETS['dirt_01']  = to_b64(os.path.join(PROJECT_ROOT, 'Assets', 'Art', 'Terrain', 'Dirt', 'mud_base_01.png'))

# Player
player_im_path = os.path.join(PROJECT_ROOT, 'Assets', 'player', 'player_base.png')
from PIL import Image
p_im = Image.open(player_im_path)
p_crop = p_im.crop((0, 0, 32, 32))
import io
buf = io.BytesIO()
p_crop.save(buf, format='PNG')
CLIFF_ASSETS['player'] = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode('utf-8')

html_content = f'''<!DOCTYPE html>
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
      max-width: 1300px;
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
      grid-template-columns: 1fr 320px;
      gap: 20px;
      align-items: start;
    }}

    .viewport-card {{
      background: var(--bg-card);
      border: 1px solid var(--bg-card-border);
      border-radius: var(--radius-md);
      overflow: hidden;
      box-shadow: 0 16px 36px rgba(0, 0, 0, 0.4);
    }}

    .viewport-toolbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 18px;
      background: rgba(10, 18, 30, 0.6);
      border-bottom: 1px solid var(--bg-card-border);
      font-size: 13px;
    }}

    .canvas-container {{
      width: 100%;
      height: 520px;
      background: #060b13;
      display: flex;
      justify-content: center;
      align-items: center;
      overflow: hidden;
      position: relative;
    }}

    #cliffCanvas {{
      image-rendering: pixelated;
      image-rendering: crisp-edges;
      transform: scale(2.5);
    }}

    /* Controls HUD */
    .hud {{
      position: absolute;
      bottom: 12px;
      left: 12px;
      background: rgba(10, 18, 30, 0.85);
      border: 1px solid rgba(45, 85, 125, 0.5);
      padding: 6px 12px;
      border-radius: var(--radius-sm);
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--text-muted);
      pointer-events: none;
    }}
    .hud span {{ color: var(--accent-cyan); font-weight: 600; }}

    /* Sidebar */
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
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="header-title">
        <h1>STRANDED - Hill & Cliff Elevation Tileset</h1>
        <p>Volumetric 2-tile high earthen rock cliffs, arched mine/cave entrance, and walkable elevation path cuts inspired by Stardew Valley.</p>
      </div>
      <div class="badge-bar">
        <div class="badge"><span>⛰️</span> 2-Tile High (32px) Cliffs</div>
        <div class="badge"><span>🕳️</span> Mine / Cave Entrance</div>
        <div class="badge"><span>🚶</span> Walkable Ramp Cut</div>
      </div>
    </header>

    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('scene')">Interactive Elevation Scene</button>
      <button class="tab-btn" onclick="switchTab('gallery')">Tile Library & Gallery</button>
    </div>

    <!-- TAB 1: SCENE -->
    <div id="tab-scene" class="tab-content active">
      <div class="workspace">
        <div class="viewport-card">
          <div class="viewport-toolbar">
            <span style="font-weight: 600; color: var(--accent-cliff);">Live Elevation Simulation</span>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--accent-cyan);" id="playerPos">X: 8 | Y: 6 (Level 0)</div>
          </div>
          <div class="canvas-container">
            <canvas id="cliffCanvas" width="384" height="224"></canvas>
            <div class="hud">
              Explore: <span>[W, A, S, D]</span> or <span>[Arrow Keys]</span> | Walk up path to reach <span>Plateau Level 1</span>!
            </div>
          </div>
        </div>

        <div class="sidebar">
          <div class="card">
            <div class="card-title">Elevation Features</div>
            <div style="font-size: 13px; color: var(--text-muted); line-height: 1.6;">
              <p style="margin-bottom: 8px;"><strong style="color: var(--accent-grass);">Level 1 (Plateau):</strong> Upper grass meadow above the cliff.</p>
              <p style="margin-bottom: 8px;"><strong style="color: var(--accent-cliff);">Cliff Wall:</strong> 32px volumetric rock wall with zero horizontal seams.</p>
              <p style="margin-bottom: 8px;"><strong style="color: var(--accent-dirt);">Canyon Path:</strong> Cut between two rock shoulders allowing player traversal.</p>
              <p><strong style="color: #fff;">Mine Cave:</strong> Arched cavern opening into the hillside.</p>
            </div>
          </div>

          <div class="card">
            <div class="card-title">Display Settings</div>
            <div class="toggle-row">
              <span>Grid Overlay</span>
              <input type="checkbox" id="toggleGrid" onchange="draw()">
            </div>
            <div class="toggle-row">
              <span>Show Player</span>
              <input type="checkbox" id="togglePlayer" checked onchange="draw()">
            </div>
            <div class="toggle-row">
              <span>Zoom Scale</span>
              <select id="scaleSelect" onchange="updateScale()" style="background: rgba(10, 18, 30, 0.8); border: 1px solid var(--bg-card-border); color: #fff; padding: 4px 8px; border-radius: 4px;">
                <option value="2">2×</option>
                <option value="2.5" selected>2.5×</option>
                <option value="3">3×</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: GALLERY -->
    <div id="tab-gallery" class="tab-content">
      <div class="grid-gallery" id="galleryGrid"></div>
    </div>
  </div>

  <script>
    const ASSETS = {json.dumps(CLIFF_ASSETS)};
    const imgCache = {{}};
    function getImg(src) {{
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

    // Map definition (24 cols x 14 rows)
    const SW = 24, SH = 14;
    const canvas = document.getElementById('cliffCanvas');
    const ctx = canvas.getContext('2d');

    // Player position
    const player = {{
      x: 8.5 * 16,
      y: 6.5 * 16,
      speed: 1.8
    }};

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

    // Collision & Elevation logic
    function canWalk(px, py) {{
      const tx = Math.floor(px / 16);
      const ty = Math.floor(py / 16);
      if (tx < 0 || tx >= SW || ty < 0 || ty >= SH) return false;

      // Cliff wall rows 4 & 5
      if (ty === 4 || ty === 5) {{
        // Path is at x=15..17 (can walk through ramp!)
        if (tx >= 15 && tx <= 17) return true;
        // Cave entrance is at x=8..9 (can walk in!)
        if (tx >= 8 && tx <= 9 && ty === 5) return true;
        // Solid cliff elsewhere
        return false;
      }}

      // Vertical canyon walls along path (ty 0..3)
      if (ty < 4) {{
        if (tx === 14 || tx === 18) return false;
      }}

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
      const level = (ty < 4) ? "Level 1 (Plateau)" : "Level 0 (Lowland)";
      document.getElementById('playerPos').innerText = `X: ${{tx}} | Y: ${{ty}} (${{level}})`;
    }}

    function draw() {{
      ctx.imageSmoothingEnabled = false;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const grassImg = getImg(ASSETS.grass_01);
      const dirtImg  = getImg(ASSETS.dirt_01);

      // 1. Base Ground
      for (let y = 0; y < SH; y++) {{
        for (let x = 0; x < SW; x++) {{
          if (x >= 15 && x <= 17) {{
            ctx.drawImage(dirtImg, x * 16, y * 16);
          }} else {{
            ctx.drawImage(grassImg, x * 16, y * 16);
          }}
        }}
      }}

      // 2. Canyon vertical walls (rows 0..3)
      for (let y = 0; y < 4; y++) {{
        ctx.drawImage(getImg(ASSETS.cliff_side_w), 14 * 16, y * 16);
        ctx.drawImage(getImg(ASSETS.cliff_side_e), 18 * 16, y * 16);
      }}

      // 3. Cliff Wall (rows 4 and 5)
      for (let x = 0; x < 8; x++) {{
        const t = (x % 2 === 0) ? ASSETS.cliff_face_top_01 : ASSETS.cliff_face_top_02;
        const b = (x % 2 === 0) ? ASSETS.cliff_face_bot_01 : ASSETS.cliff_face_bot_02;
        ctx.drawImage(getImg(t), x * 16, 4 * 16);
        ctx.drawImage(getImg(b), x * 16, 5 * 16);
      }}

      // Cave (x=8..9)
      ctx.drawImage(getImg(ASSETS.cliff_cave_tl), 8 * 16, 4 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_cave_tr), 9 * 16, 4 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_cave_bl), 8 * 16, 5 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_cave_br), 9 * 16, 5 * 16);

      // Cliff between cave and ramp (x=10..13)
      for (let x = 10; x <= 13; x++) {{
        const t = (x % 2 === 0) ? ASSETS.cliff_face_top_02 : ASSETS.cliff_face_top_01;
        const b = (x % 2 === 0) ? ASSETS.cliff_face_bot_02 : ASSETS.cliff_face_bot_01;
        ctx.drawImage(getImg(t), x * 16, 4 * 16);
        ctx.drawImage(getImg(b), x * 16, 5 * 16);
      }}

      // Ramp Shoulders (x=14 & x=18)
      ctx.drawImage(getImg(ASSETS.cliff_ramp_left_top), 14 * 16, 4 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_ramp_left_bot), 14 * 16, 5 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_ramp_right_top), 18 * 16, 4 * 16);
      ctx.drawImage(getImg(ASSETS.cliff_ramp_right_bot), 18 * 16, 5 * 16);

      // Right cliff section (x=19..23)
      for (let x = 19; x < SW; x++) {{
        const t = (x % 2 === 0) ? ASSETS.cliff_face_top_01 : ASSETS.cliff_face_top_02;
        const b = (x % 2 === 0) ? ASSETS.cliff_face_bot_01 : ASSETS.cliff_face_bot_02;
        ctx.drawImage(getImg(t), x * 16, 4 * 16);
        ctx.drawImage(getImg(b), x * 16, 5 * 16);
      }}

      // 4. Player
      if (document.getElementById('togglePlayer').checked) {{
        const pImg = getImg(ASSETS.player);
        if (pImg) {{
          ctx.fillStyle = 'rgba(20, 40, 50, 0.35)';
          ctx.beginPath();
          ctx.ellipse(player.x + 8, player.y + 24, 7, 3, 0, 0, Math.PI * 2);
          ctx.fill();
          ctx.drawImage(pImg, player.x - 8, player.y - 4, 32, 32);
        }}
      }}

      // 5. Grid
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

    // Populate Gallery
    const galleryItems = [
      {{ title: "Cliff Face Top 01", file: "cliff_face_top_01.png", key: "cliff_face_top_01" }},
      {{ title: "Cliff Face Top 02", file: "cliff_face_top_02.png", key: "cliff_face_top_02" }},
      {{ title: "Cliff Face Bot 01", file: "cliff_face_bot_01.png", key: "cliff_face_bot_01" }},
      {{ title: "Cliff Face Bot 02", file: "cliff_face_bot_02.png", key: "cliff_face_bot_02" }},
      {{ title: "Cliff Side West", file: "cliff_side_w.png", key: "cliff_side_w" }},
      {{ title: "Cliff Side East", file: "cliff_side_e.png", key: "cliff_side_e" }},
      {{ title: "Cave Arch Top-Left", file: "cliff_cave_tl.png", key: "cliff_cave_tl" }},
      {{ title: "Cave Arch Top-Right", file: "cliff_cave_tr.png", key: "cliff_cave_tr" }},
      {{ title: "Cave Base Bottom-Left", file: "cliff_cave_bl.png", key: "cliff_cave_bl" }},
      {{ title: "Cave Base Bottom-Right", file: "cliff_cave_br.png", key: "cliff_cave_br" }},
      {{ title: "Ramp Shoulder Left Top", file: "cliff_ramp_left_top.png", key: "cliff_ramp_left_top" }},
      {{ title: "Ramp Shoulder Right Top", file: "cliff_ramp_right_top.png", key: "cliff_ramp_right_top" }},
      {{ title: "Ramp Shoulder Left Bot", file: "cliff_ramp_left_bot.png", key: "cliff_ramp_left_bot" }},
      {{ title: "Ramp Shoulder Right Bot", file: "cliff_ramp_right_bot.png", key: "cliff_ramp_right_bot" }},
      {{ title: "Corner Outer Top-Left", file: "cliff_outer_tl_top.png", key: "cliff_outer_tl_top" }},
      {{ title: "Corner Outer Top-Right", file: "cliff_outer_tr_top.png", key: "cliff_outer_tr_top" }}
    ];

    const gGrid = document.getElementById('galleryGrid');
    galleryItems.forEach(item => {{
      const card = document.createElement('div');
      card.className = 'tile-card';
      card.innerHTML = `
        <div class="tile-preview">
          <img src="${{ASSETS[item.key]}}" alt="${{item.title}}">
        </div>
        <div class="tile-name">${{item.title}}</div>
        <div class="tile-file">${{item.file}}</div>
      `;
      gGrid.appendChild(card);
    }});

    setTimeout(() => {{
      requestAnimationFrame(loop);
    }}, 100);
  </script>
</body>
</html>
'''

target_html = os.path.join(PROJECT_ROOT, 'cliff_preview.html')
with open(target_html, 'w', encoding='utf-8') as f:
    f.write(html_content)
print("Saved:", target_html)

brain_html = os.path.join(BRAIN_DIR, 'cliff_preview.html')
with open(brain_html, 'w', encoding='utf-8') as f:
    f.write(html_content)
print("Saved:", brain_html)
