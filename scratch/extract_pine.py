from PIL import Image

def extract_authentic_pine_tree():
    trees_sheet = Image.open('D:/myAssets/PC _ Computer - Stardew Valley - Environment - Trees.png')

    # 1. Mature Pine Tree (emerald pine tree from screenshot)
    # Location in sheet: x: 0..48, y: 320..416
    raw_tree = trees_sheet.crop((0, 320, 48, 416))
    bbox = raw_tree.getbbox()
    trimmed_tree = raw_tree.crop(bbox) # 48x89
    tw, th = trimmed_tree.size
    print(f'Trimmed Pine Tree size: {tw}x{th}')

    # Place on 48x96 canvas, bottom-aligned so trunk touches bottom (y=95)
    canvas_tree = Image.new('RGBA', (48, 96), (0, 0, 0, 0))
    canvas_tree.paste(trimmed_tree, (0, 96 - th))
    canvas_tree.save('Assets/Art/Environment/Trees/tree_fir_mature.png')
    print('Saved Assets/Art/Environment/Trees/tree_fir_mature.png (48x96)')

    # 2. Matching Clean Pine Stump
    # In pine section, stump is at x: 32..48, y: 440..460
    raw_stump = trees_sheet.crop((32, 440, 48, 460))
    s_bbox = raw_stump.getbbox()
    trimmed_stump = raw_stump.crop(s_bbox) # 16x19
    sw, sh = trimmed_stump.size
    print(f'Trimmed Pine Stump size: {sw}x{sh}')

    # Place on 16x24 canvas, bottom-aligned
    canvas_stump = Image.new('RGBA', (16, 24), (0, 0, 0, 0))
    canvas_stump.paste(trimmed_stump, (0, 24 - sh))
    canvas_stump.save('Assets/Art/Environment/Trees/tree_fir_stump.png')
    print('Saved Assets/Art/Environment/Trees/tree_fir_stump.png (16x24)')

if __name__ == '__main__':
    extract_authentic_pine_tree()
