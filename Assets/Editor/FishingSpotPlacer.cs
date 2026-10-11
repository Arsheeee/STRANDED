using System;
using System.IO;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;

/// <summary>
/// Editor utility for placing designated riverbank and coastal FishingSpots across STRANDED.
/// Ensures valid ground placement near water, subtle ripple visual indicators,
/// and clean scene hierarchy integration.
/// </summary>
public class FishingSpotPlacer : EditorWindow
{
    private const string SCENE_PATH = "Assets/Scenes/MainScene.unity";

    private struct SpotDefinition
    {
        public string name;
        public Vector2 position;
        public SpotDefinition(string name, Vector2 pos)
        {
            this.name = name;
            this.position = pos;
        }
    }

    private static readonly List<SpotDefinition> DesignatedSpots = new List<SpotDefinition>()
    {
        // 4 Designated Riverbank Locations
        new SpotDefinition("West Riverbank Fishing Spot", new Vector2(175.5f, 137.5f)),
        new SpotDefinition("Central Riverbend Fishing Spot", new Vector2(195.5f, 124.5f)),
        new SpotDefinition("South Estuary Fishing Spot", new Vector2(189.5f, 75.5f)),
        new SpotDefinition("North River Rapids Fishing Spot", new Vector2(212.5f, 207.5f)),

        // 4 Designated Coastal Shoreline Locations
        new SpotDefinition("South Beach Fishing Spot", new Vector2(116.5f, 85.5f)),
        new SpotDefinition("West Shoreline Fishing Spot", new Vector2(82.5f, 110.5f)),
        new SpotDefinition("East Shoreline Fishing Spot", new Vector2(278.5f, 121.5f)),
        new SpotDefinition("South Ocean Reef Fishing Spot", new Vector2(172.5f, 62.5f)),
    };

    [MenuItem("Tools/STRANDED/Place Fishing Spots in MainScene")]
    public static void PlaceFishingSpots()
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
        GameObject spotsRoot = GameObject.Find("FishingSpots");

        if (spotsRoot != null)
        {
            Undo.DestroyObjectImmediate(spotsRoot);
        }

        spotsRoot = new GameObject("FishingSpots");
        Undo.RegisterCreatedObjectUndo(spotsRoot, "Create FishingSpots Root");

        if (envRoot != null)
        {
            spotsRoot.transform.SetParent(envRoot.transform, false);
        }

        Sprite rippleSprite = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Items/fishing_ripple.png");
        Sprite bobberSprite = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Items/fishing_bobber.png");
        Sprite alertSprite = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Items/fishing_alert.png");

        foreach (var def in DesignatedSpots)
        {
            GameObject spotGo = new GameObject(def.name.Replace(" ", "_"));
            Undo.RegisterCreatedObjectUndo(spotGo, "Create " + def.name);
            spotGo.transform.position = new Vector3(def.position.x, def.position.y, 0f);
            spotGo.transform.SetParent(spotsRoot.transform, true);

            FishingSpot spot = spotGo.AddComponent<FishingSpot>();
            spot.SetIdentity(def.name, 2.2f);

            // Child 1: Ripple
            GameObject rippleObj = new GameObject("Visual_Ripple");
            rippleObj.transform.SetParent(spotGo.transform, false);
            SpriteRenderer srRipple = rippleObj.AddComponent<SpriteRenderer>();
            srRipple.sprite = rippleSprite;
            srRipple.sortingOrder = 16;

            // Child 2: Bobber
            GameObject bobberObj = new GameObject("Visual_Bobber");
            bobberObj.transform.SetParent(spotGo.transform, false);
            SpriteRenderer srBobber = bobberObj.AddComponent<SpriteRenderer>();
            srBobber.sprite = bobberSprite;
            srBobber.sortingOrder = 25;
            srBobber.enabled = false;

            // Child 3: Alert
            GameObject alertObj = new GameObject("Visual_Alert");
            alertObj.transform.SetParent(spotGo.transform, false);
            alertObj.transform.localPosition = new Vector3(0f, 0.45f, 0f);
            SpriteRenderer srAlert = alertObj.AddComponent<SpriteRenderer>();
            srAlert.sprite = alertSprite;
            srAlert.sortingOrder = 30;
            srAlert.enabled = false;

            spot.EnsureVisualComponents();
        }

        EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
        EditorSceneManager.SaveOpenScenes();

        Debug.Log($"[STRANDED Fishing] Successfully placed {DesignatedSpots.Count} FishingSpots in MainScene!");
    }
}
