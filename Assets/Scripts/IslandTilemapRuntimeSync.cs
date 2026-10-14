using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Tilemaps;

#if UNITY_EDITOR
using UnityEditor;
#endif

public class IslandTilemapRuntimeSync : MonoBehaviour
{
    private static readonly (int x, int y, string piece)[] SandRiverContacts = new (int, int, string)[]
    {
        (188, 74, "outer_bl"),
        (188, 75, "edge_e"),
        (187, 76, "outer_bl"),
        (188, 76, "inner_bl"),
        (187, 77, "edge_e"),
        (186, 78, "outer_bl"),
        (187, 78, "inner_bl"),
        (193, 78, "edge_w"),
        (185, 79, "outer_bl"),
        (186, 79, "inner_bl"),
        (193, 79, "edge_w"),
        (185, 80, "edge_e"),
        (192, 80, "inner_tr"),
        (193, 80, "outer_tr"),
        (184, 81, "outer_bl"),
        (185, 81, "inner_bl"),
        (191, 81, "inner_tr"),
        (192, 81, "outer_tr"),
        (184, 82, "edge_e"),
        (191, 82, "edge_w"),
        (183, 83, "outer_bl"),
        (184, 83, "inner_bl"),
        (190, 83, "inner_tr"),
        (191, 83, "outer_tr"),
        (190, 84, "edge_w"),
        (189, 85, "inner_tr"),
        (190, 85, "outer_tr"),
        (189, 86, "edge_w"),
        (189, 87, "edge_w"),
        (189, 88, "edge_w"),
        (189, 89, "inner_br"),
        (190, 89, "outer_br"),
        (190, 90, "edge_w"),
        (190, 91, "inner_br"),
        (191, 91, "outer_br"),
        (191, 92, "inner_br"),
        (192, 92, "outer_br"),
        (192, 93, "inner_br"),
        (193, 93, "outer_br"),
        (193, 94, "inner_br"),
        (194, 94, "outer_br"),
        (195, 95, "outer_br")
    };

    private static bool _syncedThisSession = false;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    public static void SyncOnSceneLoad()
    {
        if (_syncedThisSession) return;
        ApplySandRiverTransitions();
    }

    private void Awake()
    {
        if (_syncedThisSession) return;
        ApplySandRiverTransitions();
    }

    public static void ApplySandRiverTransitions()
    {
        if (_syncedThisSession) return;
        _syncedThisSession = true;
        ResourceNode.EnsureDefaultForageNodesExist();
        GameObject gridObj = GameObject.Find("Grid");
        if (gridObj == null) return;

        Transform transT = gridObj.transform.Find("Tilemap_Transitions");
        if (transT == null) return;

        Tilemap tmTransitions = transT.GetComponent<Tilemap>();
        if (tmTransitions == null) return;

#if UNITY_EDITOR
        Dictionary<string, TileBase> tileCache = new Dictionary<string, TileBase>();
        int appliedCount = 0;

        foreach (var (x, y, piece) in SandRiverContacts)
        {
            Vector3Int pos = new Vector3Int(x, y, 0);
            if (!tileCache.TryGetValue(piece, out TileBase tile))
            {
                string assetPath = $"Assets/Art/Terrain/Tiles/Transitions_Sand_RiverWater_sand_riverwater_{piece}.asset";
                tile = AssetDatabase.LoadAssetAtPath<TileBase>(assetPath);
                if (tile == null)
                {
                    // Fallback to sprite directly
                    string pngPath = $"Assets/Art/Terrain/Transitions/Sand_RiverWater/sand_riverwater_{piece}.png";
                    Sprite spr = AssetDatabase.LoadAssetAtPath<Sprite>(pngPath);
                    if (spr != null)
                    {
                        Tile t = ScriptableObject.CreateInstance<Tile>();
                        t.sprite = spr;
                        t.colliderType = Tile.ColliderType.None;
                        tile = t;
                    }
                }
                tileCache[piece] = tile;
            }

            if (tile != null)
            {
                tmTransitions.SetTile(pos, tile);
                appliedCount++;
            }
        }

        if (appliedCount > 0 && !_syncedThisSession)
        {
            _syncedThisSession = true;
            Debug.Log($"[STRANDED] IslandTilemapRuntimeSync applied {appliedCount} Sand-to-River transition tiles to Tilemap_Transitions.");
        }
#endif
    }
}
