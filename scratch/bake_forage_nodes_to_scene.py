import os
import re

SCENE_PATH = 'Assets/Scenes/MainScene.unity'

# Forage Sprite GUIDs
GUIDS = {
    'item_poison_mushroom': '6c409275580b4ed799659b960d6b0560',
    'item_mushroom': 'e8f3f1e48da448d09b43b53e68cb9baf',
    'item_morel': 'eedc095bb0f3482a95e49102d9bc95ea',
    'item_chanterelle': '98d695ef16d2482289ba0804470efb86',
    'item_purple_mushroom': '0d4d60b731174b4c9ca9d8618ed15dfe',
    'item_poison_berry': 'c3016ddd26eb47c4918c46a8005b3a6d',
    'item_berry': 'f525cffbd43849df8ced1d41dfb7262c',
    'item_blackberry': '836ee97658b844d1baa9ad6514572587'
}

RESOURCE_NODE_SCRIPT_GUID = '4e241ba3b2d4c9a4f96d542a8c885867'

GROUPS = [
    {
        'type': 'poison_mushroom',
        'display': 'Crimson Toadstool (Toxic)',
        'custom_id': 'poison_mushroom',
        'guid': GUIDS['item_poison_mushroom'],
        'yield': 1,
        'positions': [
            (138.5, 126.5), # Camp North
            (144.5, 122.5), # Camp East
            (152.5, 115.5), # Forest path
            (162.5, 128.5), # Grove
            (172.5, 105.5), # Near river
            (182.5, 95.5),  # River sand border
            (125.5, 115.5), # West woods
            (148.5, 138.5), # North pine
            (165.5, 145.5), # Highlands
            (195.5, 110.5)  # East riverbank
        ]
    },
    {
        'type': 'mushroom',
        'display': 'Island Morel',
        'custom_id': 'mushroom',
        'guid': GUIDS['item_mushroom'],
        'yield': 1,
        'positions': [
            (133.5, 126.5), # Camp
            (140.5, 116.5), # South camp
            (149.5, 125.5), # Mid woods
            (158.5, 112.5), # Forest trail
            (168.5, 120.5), # Central grove
            (178.5, 98.5),  # Near river
            (190.5, 88.5)   # River sand crossing
        ]
    },
    {
        'type': 'chanterelle',
        'display': 'Golden Chanterelle',
        'custom_id': 'chanterelle',
        'guid': GUIDS['item_chanterelle'],
        'yield': 1,
        'positions': [
            (136.5, 114.5), # South camp
            (147.5, 130.5), # North forest
            (155.5, 122.5), # Oak clearing
            (165.5, 115.5), # Forest grove
            (175.5, 102.5), # River trail
            (184.5, 92.5)   # Riverbank
        ]
    },
    {
        'type': 'purple_mushroom',
        'display': 'Purple Cave Mushroom',
        'custom_id': 'purple_mushroom',
        'guid': GUIDS['item_purple_mushroom'],
        'yield': 1,
        'positions': [
            (128.5, 128.5), # Shaded cliff base
            (142.5, 135.5), # North ridge
            (158.5, 132.5), # Highland cliff
            (170.5, 126.5), # Deep shade
            (181.5, 112.5)  # River bend
        ]
    },
    {
        'type': 'poison_berry',
        'display': 'Nightshade Berries (Toxic)',
        'custom_id': 'poison_berries',
        'guid': GUIDS['item_poison_berry'],
        'yield': 2,
        'positions': [
            (137.5, 128.5), # North of camp
            (145.5, 115.5), # South-east of camp
            (153.5, 128.5), # Forest thicket
            (163.5, 108.5), # Jungle edge
            (174.5, 118.5), # River woodland
            (183.5, 96.5),  # Near river transition
            (190.5, 102.5)  # East bank
        ]
    },
    {
        'type': 'berry',
        'display': 'Wild Berries',
        'custom_id': 'berries',
        'guid': GUIDS['item_berry'],
        'yield': 2,
        'positions': [
            (134.5, 118.5), # Beside camp
            (139.5, 121.5), # East of camp
            (148.5, 118.5), # Trail towards river
            (156.5, 118.5), # Sunny glade
            (167.5, 110.5), # Lowland meadow
            (176.5, 106.5), # River glade
            (190.5, 86.5)   # River sand crossing
        ]
    },
    {
        'type': 'blackberry',
        'display': 'Wild Blackberry',
        'custom_id': 'blackberry',
        'guid': GUIDS['item_blackberry'],
        'yield': 2,
        'positions': [
            (131.5, 123.5), # West of camp
            (142.5, 126.5), # North-east of camp
            (150.5, 134.5), # Pine forest
            (160.5, 122.5), # Bramble patch
            (171.5, 114.5), # River clearing
            (191.5, 90.5)   # Riverbank
        ]
    }
]

def main():
    print("Reading MainScene.unity...")
    with open(SCENE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    if "m_Name: Forage" in content:
        print("Forage already exists in MainScene.unity!")
        return

    # Find highest 32-bit fileID
    file_ids = set(int(m) for m in re.findall(r'--- !u!\d+ &(\d+)', content))
    normal_ids = [x for x in file_ids if x < 2100000000]
    max_normal = max(normal_ids) if normal_ids else 1000000
    print(f"Max normal 32-bit fileID: {max_normal}")

    def get_next_id(start_val):
        curr = start_val
        while curr in file_ids or curr >= 2147483640:
            curr += 1
        file_ids.add(curr)
        return curr

    curr_alloc = max_normal + 100
    env_transform_id = 1592220667

    forage_go_id = get_next_id(curr_alloc); curr_alloc = forage_go_id + 1
    forage_tr_id = get_next_id(curr_alloc); curr_alloc = forage_tr_id + 1

    child_tr_ids = []
    yaml_blocks = []

    # Forage root GameObject and Transform
    forage_go_yaml = f"""--- !u!1 &{forage_go_id}
GameObject:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  serializedVersion: 6
  m_Component:
  - component: {{fileID: {forage_tr_id}}}
  m_Layer: 0
  m_Name: Forage
  m_TagString: Untagged
  m_Icon: {{fileID: 0}}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: 1
--- !u!4 &{forage_tr_id}
Transform:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {forage_go_id}}}
  serializedVersion: 2
  m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
  m_LocalPosition: {{x: 0, y: 0, z: 0}}
  m_LocalScale: {{x: 1, y: 1, z: 1}}
  m_ConstrainProportionsScale: 0
  m_Children: []
  m_Father: {{fileID: {env_transform_id}}}
  m_LocalEulerAnglesHint: {{x: 0, y: 0, z: 0}}"""
    yaml_blocks.append(forage_go_yaml)

    # Process all forage nodes
    node_count = 0
    for group in GROUPS:
        type_name = group['type']
        for i, pos in enumerate(group['positions']):
            node_count += 1
            node_name = f"Forage_{type_name.replace('_', ' ').title().replace(' ', '')}_{i + 1}"
            
            go_id = get_next_id(curr_alloc); curr_alloc = go_id + 1
            tr_id = get_next_id(curr_alloc); curr_alloc = tr_id + 1
            sr_id = get_next_id(curr_alloc); curr_alloc = sr_id + 1
            cc_id = get_next_id(curr_alloc); curr_alloc = cc_id + 1
            mn_id = get_next_id(curr_alloc); curr_alloc = mn_id + 1
            
            child_tr_ids.append(tr_id)
            sorting_order = 5000 + round(-pos[1] * 10)
            
            node_yaml = f"""--- !u!1 &{go_id}
GameObject:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  serializedVersion: 6
  m_Component:
  - component: {{fileID: {tr_id}}}
  - component: {{fileID: {sr_id}}}
  - component: {{fileID: {cc_id}}}
  - component: {{fileID: {mn_id}}}
  m_Layer: 0
  m_Name: {node_name}
  m_TagString: Untagged
  m_Icon: {{fileID: 0}}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: 1
--- !u!4 &{tr_id}
Transform:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go_id}}}
  serializedVersion: 2
  m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
  m_LocalPosition: {{x: {pos[0]}, y: {pos[1]}, z: 0}}
  m_LocalScale: {{x: 1, y: 1, z: 1}}
  m_ConstrainProportionsScale: 0
  m_Children: []
  m_Father: {{fileID: {forage_tr_id}}}
  m_LocalEulerAnglesHint: {{x: 0, y: 0, z: 0}}
--- !u!212 &{sr_id}
SpriteRenderer:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go_id}}}
  m_Enabled: 1
  m_CastShadows: 0
  m_ReceiveShadows: 0
  m_DynamicOccludee: 1
  m_StaticShadowCaster: 0
  m_MotionVectors: 1
  m_LightProbeUsage: 1
  m_ReflectionProbeUsage: 1
  m_RayTracingMode: 0
  m_RayTraceProcedural: 0
  m_RayTracingAccelStructBuildFlagsOverride: 0
  m_RayTracingAccelStructBuildFlags: 1
  m_SmallMeshCulling: 1
  m_RenderingLayerMask: 1
  m_RendererPriority: 0
  m_Materials:
  - {{fileID: 10754, guid: 0000000000000000f000000000000000, type: 0}}
  m_StaticBatchInfo:
    firstSubMesh: 0
    subMeshCount: 0
  m_StaticBatchRoot: {{fileID: 0}}
  m_ProbeAnchor: {{fileID: 0}}
  m_LightProbeVolumeOverride: {{fileID: 0}}
  m_ScaleInLightmap: 1
  m_ReceiveGI: 1
  m_PreserveUVs: 0
  m_IgnoreNormalsForChartDetection: 0
  m_ImportantGI: 0
  m_StitchLightmapSeams: 1
  m_SelectedEditorRenderState: 0
  m_MinimumChartSize: 4
  m_AutoUVMaxDistance: 0.5
  m_AutoUVMaxAngle: 89
  m_LightmapParameters: {{fileID: 0}}
  m_SortingLayerID: 0
  m_SortingLayer: 0
  m_SortingOrder: {sorting_order}
  m_Sprite: {{fileID: 21300000, guid: {group['guid']}, type: 3}}
  m_Color: {{r: 1, g: 1, b: 1, a: 1}}
  m_FlipX: 0
  m_FlipY: 0
  m_DrawMode: 0
  m_Size: {{x: 1, y: 1}}
  m_AdaptiveModeThreshold: 0.5
  m_SpriteTileMode: 0
  m_WasSpriteAssigned: 1
  m_MaskInteraction: 0
  m_SpriteSortPoint: 0
--- !u!58 &{cc_id}
CircleCollider2D:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go_id}}}
  m_Enabled: 1
  serializedVersion: 3
  m_Density: 1
  m_Material: {{fileID: 0}}
  m_IncludeLayers:
    serializedVersion: 2
    m_Bits: 0
  m_ExcludeLayers:
    serializedVersion: 2
    m_Bits: 0
  m_LayerOverridePriority: 0
  m_ForceSendLayers:
    serializedVersion: 2
    m_Bits: 4294967295
  m_ForceReceiveLayers:
    serializedVersion: 2
    m_Bits: 4294967295
  m_ContactCaptureLayers:
    serializedVersion: 2
    m_Bits: 4294967295
  m_CallbackLayers:
    serializedVersion: 2
    m_Bits: 4294967295
  m_IsTrigger: 0
  m_UsedByEffector: 0
  m_CompositeOperation: 0
  m_CompositeOrder: 0
  m_Offset: {{x: 0, y: 0.1}}
  m_Radius: 0.22
--- !u!114 &{mn_id}
MonoBehaviour:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go_id}}}
  m_Enabled: 1
  m_EditorHideFlags: 0
  m_Script: {{fileID: 11500000, guid: {RESOURCE_NODE_SCRIPT_GUID}, type: 3}}
  m_Name: 
  m_EditorClassIdentifier: Assembly-CSharp::ResourceNode
  resourceType: 4
  nodeDisplayName: {group['display']}
  yieldAmount: {group['yield']}
  customItemId: {group['custom_id']}
  interactionRange: 1.4
  nodeCategory: 2
  nodeSize: 1
  requiredTool: 0
  isHarvestable: 1
  depleteOnHarvest: 1
  availableSprite: {{fileID: 21300000, guid: {group['guid']}, type: 3}}
  depletedSprite: {{fileID: 0}}
  destroyOnDeplete: 1
  regrowthDuration: 45"""
            yaml_blocks.append(node_yaml)

    # Now update Forage root Transform m_Children to list all child transforms
    children_yaml_lines = "\n".join([f"  - {{fileID: {tid}}}" for tid in child_tr_ids])
    yaml_blocks[0] = yaml_blocks[0].replace("  m_Children: []", f"  m_Children:\n{children_yaml_lines}")

    # Now update Environment_Resources (Transform &1592220667) m_Children to include forage_tr_id
    target_sub = "  m_Children:\n  - {fileID: 445644086}\n  - {fileID: 2097839440}"
    repl_sub = f"  m_Children:\n  - {{fileID: 445644086}}\n  - {{fileID: 2097839440}}\n  - {{fileID: {forage_tr_id}}}"
    if target_sub not in content:
        print("ERROR: Target Environment_Resources m_Children block not found!")
        return

    content_with_child = content.replace(target_sub, repl_sub, 1)

    # Insert all new yaml blocks right before SceneRoots
    roots_marker = "--- !u!1660057539 &9223372036854775807"
    if roots_marker not in content_with_child:
        print("ERROR: SceneRoots marker not found!")
        return

    all_new_yaml = "\n".join(yaml_blocks) + "\n"
    final_content = content_with_child.replace(roots_marker, all_new_yaml + roots_marker, 1)

    print(f"Writing {node_count} Forage nodes + 1 Forage root to {SCENE_PATH}...")
    with open(SCENE_PATH, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print(f"SUCCESS: Baked {node_count} forage nodes into {SCENE_PATH}!")

if __name__ == '__main__':
    main()
