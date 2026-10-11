using System.IO;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;

/// <summary>
/// Editor utility for placing the designated Escape Boat Construction Site in MainScene.
/// Positions the slipway at the northeastern escape cove (276.5, 265.5) on firm sand beach at the water's edge.
/// Non-destructive: preserves existing terrain, resources, and player coordinates.
/// </summary>
public class BoatSitePlacer : EditorWindow
{
    private const string SCENE_PATH = "Assets/Scenes/MainScene.unity";
    public static readonly Vector3 DESIGNATED_POSITION = new Vector3(276.5f, 265.5f, 0f);

    [MenuItem("Tools/STRANDED/Place Boat Construction Site in MainScene")]
    public static void PlaceBoatConstructionSite()
    {
        if (File.Exists(SCENE_PATH))
        {
            var activeScene = EditorSceneManager.GetActiveScene();
            if (activeScene.path != SCENE_PATH)
            {
                EditorSceneManager.OpenScene(SCENE_PATH);
            }
        }

        GameObject envRoot = GameObject.Find("Environment_Resources");
        GameObject siteGo = GameObject.Find("Boat_Construction_Site");

        if (siteGo != null)
        {
            Undo.DestroyObjectImmediate(siteGo);
            Debug.Log("[STRANDED Boat Placer] Removed previous Boat_Construction_Site for fresh placement.");
        }

        siteGo = new GameObject("Boat_Construction_Site");
        Undo.RegisterCreatedObjectUndo(siteGo, "Place Boat Construction Site");

        siteGo.transform.position = DESIGNATED_POSITION;
        if (envRoot != null)
        {
            siteGo.transform.SetParent(envRoot.transform);
        }

        // Trigger Collider
        BoxCollider2D boxCol = siteGo.AddComponent<BoxCollider2D>();
        boxCol.isTrigger = true;
        boxCol.size = new Vector2(2.5f, 2.0f);

        // Sprite Renderer
        SpriteRenderer sr = siteGo.AddComponent<SpriteRenderer>();
        string spritePath = "Assets/Art/Environment/Boat/boat_stage_0_slipway.png";
        Sprite initialSprite = AssetDatabase.LoadAssetAtPath<Sprite>(spritePath);
        if (initialSprite != null)
        {
            sr.sprite = initialSprite;
        }
        sr.sortingOrder = ResourceNode.BASE_SORTING_ORDER + Mathf.RoundToInt(-DESIGNATED_POSITION.y * 10f);

        // BoatConstructionSite component
        BoatConstructionSite site = siteGo.AddComponent<BoatConstructionSite>();
        site.InitializeRequirements();
        site.UpdateVisuals();
        site.UpdateSortingOrder();

        // Mark scene dirty and save
        var scene = EditorSceneManager.GetActiveScene();
        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene);

        Debug.Log($"[STRANDED Boat Placer] Successfully placed Boat_Construction_Site at {DESIGNATED_POSITION} in {SCENE_PATH}!");
    }
}
