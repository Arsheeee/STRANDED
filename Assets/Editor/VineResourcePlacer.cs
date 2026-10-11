using System.IO;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;

/// <summary>
/// Editor utility for placing natural Vine gathering nodes across STRANDED.
/// Adds Vine nodes non-destructively to MainScene without modifying terrain or existing resource nodes.
/// </summary>
public class VineResourcePlacer : EditorWindow
{
    private const string SCENE_PATH = "Assets/Scenes/MainScene.unity";

    private static readonly Vector2[] DesignatedVinePositions = new Vector2[]
    {
        // Camp & Starting Forest Clearing
        new Vector2(141.5f, 124.5f),
        new Vector2(146.5f, 118.5f),
        new Vector2(132.5f, 127.5f),
        new Vector2(154.5f, 134.5f),

        // South-Central Jungle
        new Vector2(165.5f, 112.5f),
        new Vector2(178.5f, 108.5f),
        new Vector2(188.5f, 132.5f),

        // North & East Forests
        new Vector2(202.5f, 232.5f),
        new Vector2(215.5f, 222.5f),
        new Vector2(230.5f, 178.5f)
    };

    [MenuItem("Tools/STRANDED/Place Vine Resources in MainScene")]
    public static void PlaceVineResources()
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
        GameObject vinesRoot = GameObject.Find("VineBushes");

        if (vinesRoot != null)
        {
            Undo.DestroyObjectImmediate(vinesRoot);
        }

        vinesRoot = new GameObject("VineBushes");
        Undo.RegisterCreatedObjectUndo(vinesRoot, "Create VineBushes Root");

        if (envRoot != null)
        {
            vinesRoot.transform.SetParent(envRoot.transform, false);
        }

        Sprite bushSprite = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Plants/plant_vine_bush.png");
        Sprite depletedSprite = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Plants/plant_vine_depleted.png");

        for (int i = 0; i < DesignatedVinePositions.Length; i++)
        {
            Vector2 pos = DesignatedVinePositions[i];
            GameObject nodeGo = new GameObject($"Vine_Cluster_{i + 1}");
            Undo.RegisterCreatedObjectUndo(nodeGo, $"Create Vine_Cluster_{i + 1}");

            nodeGo.transform.position = new Vector3(pos.x, pos.y, 0f);
            nodeGo.transform.SetParent(vinesRoot.transform, true);

            SpriteRenderer sr = nodeGo.AddComponent<SpriteRenderer>();
            sr.sprite = bushSprite;

            CircleCollider2D col = nodeGo.AddComponent<CircleCollider2D>();
            col.isTrigger = false;
            col.radius = 0.4f;
            col.offset = new Vector2(0f, 0.2f);

            ResourceNode node = nodeGo.AddComponent<ResourceNode>();
            // Configure serialized fields via SerializedObject for editor persistence
            SerializedObject so = new SerializedObject(node);
            so.FindProperty("resourceType").enumValueIndex = (int)ResourceType.Vines;
            so.FindProperty("nodeDisplayName").stringValue = "Jungle Vine Cluster";
            so.FindProperty("requiredTool").enumValueIndex = (int)ToolType.StoneKnife;
            so.FindProperty("yieldAmount").intValue = 2;
            so.FindProperty("interactionRange").floatValue = 1.6f;
            so.FindProperty("isHarvestable").boolValue = true;
            so.FindProperty("depleteOnHarvest").boolValue = true;
            so.FindProperty("destroyOnDeplete").boolValue = false;
            so.FindProperty("availableSprite").objectReferenceValue = bushSprite;
            so.FindProperty("depletedSprite").objectReferenceValue = depletedSprite;
            so.ApplyModifiedPropertiesWithoutUndo();

            node.UpdateSortingOrder();
        }

        EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
        Debug.Log($"[STRANDED World] Successfully placed {DesignatedVinePositions.Length} Vine ResourceNodes into MainScene.");
    }
}
