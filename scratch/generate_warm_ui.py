import os
from PIL import Image, ImageDraw

def generate_warm_pixel_ui():
    os.makedirs("Assets/Art/UI", exist_ok=True)

    # -------------------------------------------------------------
    # 1. ui_slot_background.png (64x64)
    # The beloved warm parchment & wood palette from previous stable version:
    # Well: (222, 184, 126), Shadow: (186, 134, 76), Highlight: (244, 216, 160)
    # Inner Bevel: (138, 86, 42), Outer Border: (85, 48, 22)
    # Combined with crisp, finished pixel bevels and corner styling!
    # -------------------------------------------------------------
    w, h = 64, 64
    slot = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(slot)

    # Outer border (85, 48, 22) - 2px dark wood border
    draw.rectangle([0, 0, 63, 63], fill=(85, 48, 22, 255), outline=(60, 30, 10, 255), width=1)
    
    # Outer carved wood frame (138, 86, 42)
    draw.rectangle([2, 2, 61, 61], fill=(138, 86, 42, 255), outline=(180, 115, 55, 255), width=1)

    # Inner recessed well rim shadow (85, 48, 22)
    draw.rectangle([4, 4, 59, 59], outline=(85, 48, 22, 255), width=1)

    # Warm Parchment Well Center (222, 184, 126)
    draw.rectangle([5, 5, 58, 58], fill=(222, 184, 126, 255))

    # Inner Shadow on Top and Left edges (186, 134, 76)
    draw.line([(5, 5), (57, 5)], fill=(186, 134, 76, 255), width=2)
    draw.line([(5, 5), (5, 57)], fill=(186, 134, 76, 255), width=2)

    # Inner Highlight on Bottom and Right edges (244, 216, 160)
    draw.line([(6, 58), (58, 58)], fill=(244, 216, 160, 255), width=1)
    draw.line([(58, 6), (58, 58)], fill=(244, 216, 160, 255), width=1)

    # Pixel corner accents
    draw.point((4, 4), fill=(60, 30, 10, 255))
    draw.point((59, 4), fill=(60, 30, 10, 255))
    draw.point((4, 59), fill=(60, 30, 10, 255))
    draw.point((59, 59), fill=(60, 30, 10, 255))

    slot.save("Assets/Art/UI/ui_slot_background.png")
    print("Saved Assets/Art/UI/ui_slot_background.png")

    # -------------------------------------------------------------
    # 2. ui_slot_selected.png (64x64)
    # The beloved Stardew Valley crimson selector box:
    # Crimson: (208, 44, 30), Highlight: (245, 95, 75), Dark: (100, 18, 12)
    # With crisp corner brackets and clean transparent center!
    # -------------------------------------------------------------
    sel = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(sel)

    # Outer dark shadow line (100, 18, 12)
    sdraw.rectangle([0, 0, 63, 63], outline=(100, 18, 12, 255), width=1)

    # Vibrant Crimson Frame (208, 44, 30) - 3px wide border
    sdraw.rectangle([1, 1, 62, 62], outline=(208, 44, 30, 255), width=2)
    sdraw.rectangle([3, 3, 60, 60], outline=(100, 18, 12, 255), width=1)

    # Highlight Corner Brackets (245, 95, 75)
    c_len = 10
    corners = [(1, 1), (62, 1), (1, 62), (62, 62)]
    for x0, y0 in corners:
        dx = -1 if x0 > 1 else 1
        dy = -1 if y0 > 1 else 1
        sdraw.line([(x0, y0), (x0 + dx * c_len, y0)], fill=(245, 95, 75, 255), width=2)
        sdraw.line([(x0, y0), (x0, y0 + dy * c_len)], fill=(245, 95, 75, 255), width=2)
        sdraw.point((x0 + dx, y0 + dy), fill=(255, 175, 155, 255))

    sel.save("Assets/Art/UI/ui_slot_selected.png")
    print("Saved Assets/Art/UI/ui_slot_selected.png")

    # -------------------------------------------------------------
    # 3. ui_inventory_panel.png (480x320)
    # Warm wood borders with parchment body from before:
    # Parchment: (235, 200, 155), Wood mid: (100, 55, 22), Wood dark: (60, 30, 10),
    # Bevel: (180, 115, 55), with crisp rivets and polished finishing.
    # -------------------------------------------------------------
    pw, ph = 480, 320
    panel = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(panel)

    c_dark_rim = (60, 30, 10, 255)
    c_wood_mid = (100, 55, 22, 255)
    c_wood_light = (180, 115, 55, 255)
    c_parchment = (235, 200, 155, 255)
    c_parchment_shadow = (222, 184, 126, 255)

    # Outer 4px dark border
    pdraw.rectangle([0, 0, pw - 1, ph - 1], fill=c_wood_mid, outline=c_dark_rim, width=3)
    
    # Outer wood bevel frame
    pdraw.rectangle([4, 4, pw - 5, ph - 5], fill=c_wood_mid, outline=c_wood_light, width=2)

    # Subtle horizontal plank seams in outer border
    for py in range(8, 20):
        if py % 4 == 0:
            pdraw.line([(8, py), (pw - 9, py)], fill=c_wood_light)
            pdraw.line([(8, ph - 1 - py), (pw - 9, ph - 1 - py)], fill=c_dark_rim)

    # Inner carved frame border
    pdraw.rectangle([14, 14, pw - 15, ph - 15], outline=c_dark_rim, width=2)
    pdraw.rectangle([16, 16, pw - 17, ph - 17], outline=c_wood_light, width=1)

    # Warm Parchment Field
    pdraw.rectangle([18, 18, pw - 19, ph - 19], fill=c_parchment, outline=c_wood_light, width=1)

    # Subtle horizontal parchment texture
    for py in range(24, ph - 24, 6):
        pdraw.line([(22, py), (pw - 23, py)], fill=c_parchment_shadow)

    # Corner Rivets / Brass Fasteners
    for cx, cy in [(8, 8), (pw - 14, 8), (8, ph - 14), (pw - 14, ph - 14)]:
        pdraw.rectangle([cx, cy, cx + 5, cy + 5], fill=(220, 175, 75, 255), outline=c_dark_rim, width=1)
        pdraw.point((cx + 1, cy + 1), fill=(255, 235, 150, 255))

    panel.save("Assets/Art/UI/ui_inventory_panel.png")
    print("Saved Assets/Art/UI/ui_inventory_panel.png")

    # -------------------------------------------------------------
    # 4. ui_menu_panel.png (400x360) for Escape / Restart Menu
    # Matching rustic wooden plaque with warm parchment interior
    # -------------------------------------------------------------
    mw, mh = 400, 360
    menu = Image.new("RGBA", (mw, mh), (0, 0, 0, 0))
    mdraw = ImageDraw.Draw(menu)

    # Outer dark edge & wood frame
    mdraw.rectangle([0, 0, mw - 1, mh - 1], fill=c_wood_mid, outline=c_dark_rim, width=3)
    mdraw.rectangle([4, 4, mw - 5, mh - 5], fill=c_wood_mid, outline=c_wood_light, width=2)

    # Inner carved border
    mdraw.rectangle([12, 12, mw - 13, mh - 13], outline=c_dark_rim, width=2)
    mdraw.rectangle([14, 14, mw - 15, mh - 15], outline=c_wood_light, width=1)

    # Warm Parchment Center
    mdraw.rectangle([16, 16, mw - 17, mh - 17], fill=c_parchment, outline=c_wood_light, width=1)

    for my in range(22, mh - 22, 6):
        mdraw.line([(20, my), (mw - 21, my)], fill=c_parchment_shadow)

    # Corner Rivets
    for cx, cy in [(8, 8), (mw - 14, 8), (8, mh - 14), (mw - 14, mh - 14)]:
        mdraw.rectangle([cx, cy, cx + 5, cy + 5], fill=(220, 175, 75, 255), outline=c_dark_rim, width=1)
        mdraw.point((cx + 1, cy + 1), fill=(255, 235, 150, 255))

    menu.save("Assets/Art/UI/ui_menu_panel.png")
    print("Saved Assets/Art/UI/ui_menu_panel.png")

if __name__ == "__main__":
    generate_warm_pixel_ui()
