from PIL import Image

def extract_pine_and_stump():
    trees = Image.open('D:/myAssets/PC _ Computer - Stardew Valley - Environment - Trees.png')

    # 1. Mature Pine Tree (48x89 inside sheet at x: 0..48, y: 320..416)
    raw_tree = trees.crop((0, 320, 48, 416))
    t_bbox = raw_tree.getbbox() # (0, 5, 48, 94)
    tree_trimmed = raw_tree.crop(t_bbox) # 48x89
    tw, th = tree_trimmed.size
    print(f'Mature Pine Tree: {tw}x{th}')

    # Save to 48x96 canvas, bottom-aligned so trunk root is at the bottom
    c_tree = Image.new('RGBA', (48, 96), (0, 0, 0, 0))
    c_tree.paste(tree_trimmed, (0, 96 - th))
    c_tree.save('Assets/Art/Environment/Trees/tree_fir_mature.png')
    print('Saved Assets/Art/Environment/Trees/tree_fir_mature.png')

    # 2. Clean Stump with top tree rings and roots
    # In pine_bottom (x: 0..150, y: 380..560 of Trees.png):
    # In Trees.png, the stump is located at x: 30..50, y: 395..420 or y: 416..440
    # Let's crop from y: 390..450, x: 20..60 and find the stump bounding box
    region = trees.crop((24, 380, 56, 430))
    # Let's search for the stump in the pine column (x: 0..60, y: 380..440)
    # In scratch/pine_bottom.png, the clean stump was in the lower part
    # Let's locate the stump accurately
    # In scratch/pine_candidate.png (y=300 in Trees.png):
    # The clean stump was around x: 32, y: 92 in pine_candidate.png => y = 392 in Trees.png
    stump_crop = trees.crop((28, 390, 52, 420))
    s_bbox = stump_crop.getbbox()
    stump_trimmed = stump_crop.crop(s_bbox)
    sw, sh = stump_trimmed.size
    print(f'Stump: {sw}x{sh}')

    c_stump = Image.new('RGBA', (sw + 4, sh + 4), (0, 0, 0, 0))
    c_stump.paste(stump_trimmed, (2, 4))
    c_stump.save('Assets/Art/Environment/Trees/tree_fir_stump.png')
    print('Saved Assets/Art/Environment/Trees/tree_fir_stump.png')

if __name__ == '__main__':
    extract_pine_and_stump()
