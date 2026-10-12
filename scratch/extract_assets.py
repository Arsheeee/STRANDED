import os
import uuid
from PIL import Image

META_TEMPLATE = """fileFormatVersion: 2
guid: {GUID}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {}
  serializedVersion: 13
  mipmaps:
    mipMapMode: 0
    enableMipMap: 0
    sRGBTexture: 1
    linearTexture: 0
    fadeOut: 0
    borderMipMap: 0
    mipMapsPreserveCoverage: 0
    alphaTestReferenceValue: 0.5
    mipMapFadeDistanceStart: 1
    mipMapFadeDistanceEnd: 3
  bumpmap:
    convertToNormalMap: 0
    externalNormalMap: 0
    heightScale: 0.25
    normalMapFilter: 0
    flipGreenChannel: 0
  isReadable: 0
  streamingMipmaps: 0
  streamingMipmapsPriority: 0
  vTOnly: 0
  ignoreMipmapLimit: 0
  grayScaleToAlpha: 0
  generateCubemap: 6
  cubemapConvolution: 0
  seamlessCubemap: 0
  textureFormat: 1
  maxTextureSize: 2048
  textureSettings:
    serializedVersion: 2
    filterMode: 0
    aniso: 1
    mipBias: 0
    wrapU: 1
    wrapV: 1
    wrapW: 1
  nPOTScale: 0
  lightmap: 0
  compressionQuality: 50
  spriteMode: 1
  spriteExtrude: 1
  spriteMeshType: 1
  alignment: 7
  spritePivot: {x: 0.5, y: 0}
  spritePixelsToUnits: {PPU}
  spriteBorder: {x: 0, y: 0, z: 0, w: 0}
  spriteGenerateFallbackPhysicsShape: 1
  alphaUsage: 1
  alphaIsTransparency: 1
  spriteTessellationDetail: -1
  textureType: 8
  textureShape: 1
  singleChannelComponent: 0
  flipbookRows: 1
  flipbookColumns: 1
  maxTextureSizeSet: 0
  compressionQualitySet: 0
  textureFormatSet: 0
  ignorePngGamma: 0
  applyGammaDecoding: 0
  swizzle: 50462976
  cookieLightType: 0
  platformSettings:
  - serializedVersion: 4
    buildTarget: DefaultTexturePlatform
    maxTextureSize: 2048
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 0
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  - serializedVersion: 4
    buildTarget: Standalone
    maxTextureSize: 2048
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 0
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  - serializedVersion: 4
    buildTarget: WebGL
    maxTextureSize: 2048
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 0
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
"""

trees_src = Image.open('D:/myAssets/PC _ Computer - Stardew Valley - Environment - Trees.png')
bushes_src = Image.open('D:/myAssets/PC _ Computer - Stardew Valley - Environment - Bushes.png')
grass_src = Image.open('D:/myAssets/PC _ Computer - Stardew Valley - Environment - Grass.png')

def save_sprite(img, out_path, ppu=16):
    img.save(out_path)
    meta_path = out_path + '.meta'
    guid = None
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('guid: '):
                    guid = line.strip().split(' ')[1]
                    break
    if not guid:
        guid = uuid.uuid4().hex
    meta_content = META_TEMPLATE.replace('{GUID}', guid).replace('{PPU}', str(ppu))
    with open(meta_path, 'w', encoding='utf-8') as f:
        f.write(meta_content)
    print(f'Saved {out_path} (PPU={ppu}, size={img.size})')

# 1. Trees (Mature & Stumps)
save_sprite(trees_src.crop((0, 0, 48, 84)), 'Assets/Art/Environment/Trees/tree_tropical_mature.png')
save_sprite(trees_src.crop((0, 96, 48, 144)), 'Assets/Art/Environment/Trees/tree_tropical_stump.png')

save_sprite(trees_src.crop((146, 0, 194, 84)), 'Assets/Art/Environment/Trees/tree_pine_mature.png')
save_sprite(trees_src.crop((146, 96, 194, 144)), 'Assets/Art/Environment/Trees/tree_pine_stump.png')

save_sprite(trees_src.crop((96, 0, 144, 84)), 'Assets/Art/Environment/Trees/tree_maple_mature.png')
save_sprite(trees_src.crop((96, 96, 144, 144)), 'Assets/Art/Environment/Trees/tree_maple_stump.png')

save_sprite(trees_src.crop((292, 0, 340, 84)), 'Assets/Art/Environment/Trees/tree_birch_mature.png')
save_sprite(trees_src.crop((292, 96, 340, 144)), 'Assets/Art/Environment/Trees/tree_birch_stump.png')

save_sprite(trees_src.crop((432, 0, 480, 84)), 'Assets/Art/Environment/Trees/tree_sakura_mature.png')
save_sprite(trees_src.crop((432, 96, 480, 144)), 'Assets/Art/Environment/Trees/tree_sakura_stump.png')

save_sprite(trees_src.crop((388, 0, 436, 84)), 'Assets/Art/Environment/Trees/tree_mahogany_mature.png')
save_sprite(trees_src.crop((388, 96, 436, 144)), 'Assets/Art/Environment/Trees/tree_mahogany_stump.png')

save_sprite(trees_src.crop((144, 480, 192, 564)), 'Assets/Art/Environment/Trees/tree_spruce_mature.png')
save_sprite(trees_src.crop((144, 576, 192, 624)), 'Assets/Art/Environment/Trees/tree_spruce_stump.png')

# 2. Bushes
save_sprite(bushes_src.crop((0, 8, 32, 40)), 'Assets/Art/Environment/Plants/bush_shrub_small.png', ppu=16)
save_sprite(bushes_src.crop((64, 8, 128, 48)), 'Assets/Art/Environment/Plants/bush_foliage_medium.png', ppu=16)
save_sprite(bushes_src.crop((0, 178, 48, 222)), 'Assets/Art/Environment/Plants/bush_flowering_pink.png', ppu=16)
save_sprite(bushes_src.crop((48, 178, 96, 222)), 'Assets/Art/Environment/Plants/bush_flowering_white.png', ppu=16)
save_sprite(bushes_src.crop((0, 293, 32, 319)), 'Assets/Art/Environment/Plants/bush_autumn_golden.png', ppu=16)

# 3. Grass
save_sprite(grass_src.crop((0, 0, 15, 20)), 'Assets/Art/Environment/Plants/plant_grass_wild.png', ppu=16)

print('SUCCESS: All assets extracted and configured!')
