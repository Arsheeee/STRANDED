import os
import sys
from PIL import Image, ImageDraw, ImageFont

def render_hud_overlay(img, equipped_tool_name, prompt_text=None, toast_text=None, is_warning=False, wood=2, stone=0, fiber=0, berries=0, coconut=0):
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # 1. Top-Left Resource & Tool HUD Box (380x90 at x=15, y=15)
    box_x0, box_y0, box_x1, box_y1 = 15, 15, 395, 105
    draw.rectangle([box_x0, box_y0, box_x1, box_y1], fill=(15, 20, 25, 225), outline=(90, 115, 135, 255), width=2)
    
    # Text in HUD Box
    # Title
    draw.text((box_x0 + 12, box_y0 + 8), "STRANDED - Resource Tracker [TEMPORARY]", fill=(255, 215, 0, 255))
    # Tool
    tool_color = (0, 255, 255, 255) if equipped_tool_name != "None" else (180, 180, 180, 255)
    draw.text((box_x0 + 12, box_y0 + 26), f"Equipped: [{equipped_tool_name}]", fill=tool_color)
    draw.text((box_x0 + 180, box_y0 + 26), "Keys: 1:Knife, 2:Axe, 3:Pick, 4:Rod, 0:Hands", fill=(170, 170, 170, 255))
    # Counts
    counts_str = f"Wood: {wood}   Stone: {stone}   Fiber: {fiber}   Berries: {berries}   Coconut: {coconut}"
    draw.text((box_x0 + 12, box_y0 + 44), counts_str, fill=(230, 230, 230, 255))
    draw.text((box_x0 + 12, box_y0 + 64), "Tool System Active | Primitive Stone Tier", fill=(130, 170, 130, 255))
    
    # 2. Contextual Prompt (Bottom-Center: 520x40 at x=220, y=475)
    if prompt_text:
        px0, py0, px1, py1 = 220, 475, 740, 515
        draw.rectangle([px0, py0, px1, py1], fill=(10, 15, 20, 235), outline=(0, 255, 200, 255) if not is_warning else (255, 120, 100, 255), width=2)
        prompt_color = (255, 255, 255, 255) if not is_warning else (255, 180, 170, 255)
        draw.text((px0 + 20, py0 + 12), prompt_text, fill=prompt_color)
        
    # 3. Toast Notification (Center-Top: 360x36 at x=300, y=125)
    if toast_text:
        tx0, ty0, tx1, ty1 = 300, 125, 660, 161
        bg_col = (180, 40, 40, 240) if is_warning else (20, 120, 60, 240)
        border_col = (255, 90, 80, 255) if is_warning else (50, 255, 140, 255)
        draw.rectangle([tx0, ty0, tx1, ty1], fill=bg_col, outline=border_col, width=2)
        draw.text((tx0 + 24, ty0 + 10), toast_text, fill=(255, 255, 255, 255))

def generate_previews():
    base_grove = Image.open('scratch/updated_forest_grove.png').convert('RGBA')
    base_plateau = Image.open('scratch/updated_mountain_plateau.png').convert('RGBA')
    
    tree_mature = Image.open('Assets/Art/Environment/Trees/tree_tropical_mature.png').convert('RGBA')
    tree_stump = Image.open('Assets/Art/Environment/Trees/tree_tropical_stump.png').convert('RGBA')
    
    ppu = 540.0 / 13.0
    scale = ppu / 16.0
    
    # Scenario 1: Equipped Stone Knife attempting Tree -> WRONG TOOL FEEDBACK
    view1 = base_grove.copy()
    render_hud_overlay(
        view1,
        equipped_tool_name="Stone Knife",
        prompt_text="[E] Tropical Tree (Requires Stone Axe)",
        toast_text="Requires Stone Axe",
        is_warning=True,
        wood=0, stone=0, fiber=0, berries=0, coconut=0
    )
    view1.save('scratch/batch3_wrong_tool_rejection.png')
    print("Saved scratch/batch3_wrong_tool_rejection.png")
    
    # Scenario 2: Equipped Stone Axe approaching Tree -> CORRECT TOOL PROMPT
    view2 = base_grove.copy()
    render_hud_overlay(
        view2,
        equipped_tool_name="Stone Axe",
        prompt_text="[E] Harvest Tropical Tree [Stone Axe]",
        toast_text="Equipped: Stone Axe",
        is_warning=False,
        wood=0, stone=0, fiber=0, berries=0, coconut=0
    )
    view2.save('scratch/batch3_correct_tool_equipped.png')
    print("Saved scratch/batch3_correct_tool_equipped.png")
    
    # Scenario 3: Tree Harvested -> Becomes Stump, Yields Wood +2
    view3 = base_grove.copy()
    # Draw stump over mature tree position (x=107.5, y=172.5, cam=(105, 175))
    cam_x, cam_y = 105.0, 175.0
    wx, wy = 107.5, 172.5
    screen_x = 480.0 + (wx - cam_x) * ppu
    screen_y = 270.0 - (wy - cam_y) * ppu
    stump_w = int(tree_stump.width * scale)
    stump_h = int(tree_stump.height * scale)
    scaled_stump = tree_stump.resize((stump_w, stump_h), Image.Resampling.NEAREST)
    paste_x = int(screen_x - (stump_w / 2.0))
    paste_y = int(screen_y - stump_h)
    view3.paste(scaled_stump, (paste_x, paste_y), scaled_stump)
    
    render_hud_overlay(
        view3,
        equipped_tool_name="Stone Axe",
        prompt_text=None,
        toast_text="Collected: Wood +2",
        is_warning=False,
        wood=2, stone=0, fiber=0, berries=0, coconut=0
    )
    view3.save('scratch/batch3_harvest_success_stump.png')
    print("Saved scratch/batch3_harvest_success_stump.png")
    
    # Scenario 4: Mountain Plateau - Stone Pickaxe Equipped on Large Boulder
    view4 = base_plateau.copy()
    render_hud_overlay(
        view4,
        equipped_tool_name="Stone Pickaxe",
        prompt_text="[E] Harvest Large Boulder [Stone Pickaxe]",
        toast_text="Collected: Stone +2",
        is_warning=False,
        wood=2, stone=2, fiber=0, berries=0, coconut=0
    )
    view4.save('scratch/batch3_pickaxe_boulder_success.png')
    print("Saved scratch/batch3_pickaxe_boulder_success.png")

if __name__ == '__main__':
    generate_previews()
