from PIL import Image

def extract_forage():
    sheet = Image.open('D:/myAssets/PC _ Computer - Stardew Valley - Environment - Forage.png')

    items = {
        'item_poison_mushroom.png': (5, 6), # Red Mushroom (Poisonous)
        'item_mushroom.png': (0, 6),        # Common Brown Mushroom (Edible)
        'item_chanterelle.png': (4, 6),     # Chanterelle (Edible)
        'item_purple_mushroom.png': (7, 6), # Purple Cave Mushroom (Edible)
        'item_poison_berry.png': (7, 4),    # Holly with Red Berries (Poisonous)
        'item_berry.png': (4, 2),           # Salmonberry (Edible)
        'item_blackberry.png': (2, 2),      # Blackberry (Edible)
    }

    for fname, (col, row) in items.items():
        x = col * 16
        y = row * 16
        tile = sheet.crop((x, y, x + 16, y + 16))
        
        # Save to 16x16 or trim and center
        bbox = tile.getbbox()
        if bbox:
            trimmed = tile.crop(bbox)
            canvas = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
            # Center horizontally, bottom-aligned
            px = (16 - trimmed.width) // 2
            py = 16 - trimmed.height
            canvas.paste(trimmed, (px, py))
            out_path = f'Assets/Art/Environment/Items/{fname}'
            canvas.save(out_path)
            print(f'Saved {out_path} ({trimmed.size})')
        else:
            print(f'Warning: Empty tile at ({col}, {row})')

if __name__ == '__main__':
    extract_forage()
