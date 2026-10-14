using System;
using System.IO;
using UnityEngine;
using UnityEngine.Tilemaps;
using UnityEditor;
using UnityEditor.SceneManagement;

[InitializeOnLoad]
public static class IslandTilemapAutoBaker
{
    private static bool _bakeAttempted = false;

    static IslandTilemapAutoBaker()
    {
        EditorApplication.delayCall += CheckAndBake;
    }

    [MenuItem("Tools/STRANDED/Bake Sand-River Transitions to Scene")]
    public static void BakeTransitionsMenu()
    {
        DoBake(true);
    }

    [MenuItem("Tools/STRANDED/Bake Forage and Resources to Scene")]
    public static void BakeForageMenu()
    {
        BakeForageAndResources(true);
    }

    private static void CheckAndBake()
    {
        if (_bakeAttempted) return;
        _bakeAttempted = true;

        if (EditorApplication.isPlayingOrWillChangePlaymode) return;

        DoBake(false);
        BakeForageAndResources(false);
    }

    public static void BakeForageAndResources(bool force)
    {
        var scene = EditorSceneManager.GetActiveScene();
        if (scene.name != "MainScene" && !force) return;

        GameObject forageObj = GameObject.Find("Forage");
        if (forageObj != null && !force) return;

        Debug.Log("[STRANDED] AutoBaker: Baking Forage nodes and camp resources into scene...");
        ResourceNode.EnsureDefaultForageNodesExist();
        ResourceNode.EnsureStartingCampResourcesExist();
        ResourceNode.EnsureDefaultVineNodesExist();

        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene);
        AssetDatabase.SaveAssets();
        Debug.Log("[STRANDED] AutoBaker: Successfully baked Forage nodes into MainScene.unity!");
    }

    private static void DoBake(bool force)
    {
        var scene = EditorSceneManager.GetActiveScene();
        if (scene.name != "MainScene" && !force)
        {
            return;
        }

        GameObject gridObj = GameObject.Find("Grid");
        if (gridObj == null) return;

        Transform transT = gridObj.transform.Find("Tilemap_Transitions");
        if (transT == null) return;

        Tilemap tmTransitions = transT.GetComponent<Tilemap>();
        if (tmTransitions == null) return;

        // Check test coordinate (189, 86) which is an edge_w transition on the east bank of river mouth
        TileBase existingTile = tmTransitions.GetTile(new Vector3Int(189, 86, 0));
        if (existingTile != null && !force)
        {
            // Already has transition baked in!
            return;
        }

        Debug.Log("[STRANDED] AutoBaker: Missing Sand-to-River transition detected. Baking full island with sand-river transitions...");

        // Execute full island build
        IslandTilemapBuilder.BuildIslandAndCamera();
        ResourceNode.EnsureDefaultForageNodesExist();

        // Also ensure runtime sync script is attached to Grid or Tilemap_Transitions
        if (gridObj.GetComponent<IslandTilemapRuntimeSync>() == null)
        {
            gridObj.AddComponent<IslandTilemapRuntimeSync>();
        }

        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene);
        AssetDatabase.SaveAssets();

        Debug.Log("[STRANDED] AutoBaker: Successfully baked Sand-to-River transitions into MainScene.unity!");
    }
}
