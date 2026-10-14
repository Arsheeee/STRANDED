using System;
using System.Collections;
using UnityEngine;

/// <summary>
/// Authoritative controller for the Crashed Helicopter Base Camp and Shelter in STRANDED.
/// Represents the crash site, serves as the central starting landmark, provides resting shelter,
/// manages the visible cabin interior and sleeping survivor visual, and orchestrates the
/// opening new-game survival introduction and surrounding foraging nodes.
/// </summary>
public class HelicopterShelter : MonoBehaviour
{
    private static HelicopterShelter instance;
    public static HelicopterShelter Instance => instance;

    [Header("Configuration")]
    [SerializeField] private string shelterDisplayName = "Crashed Helicopter";
    [SerializeField] private float interactionRadius = 3.0f;

    [Header("Visuals")]
    private SpriteRenderer spriteRenderer;
    private BoxCollider2D fuselageCollider;
    private GameObject sleepingVisual;

    // Resting positions
    private readonly Vector3 insideCabinPos = new Vector3(134.4f, 122.7f, 0f);
    private readonly Vector3 outsideExitPos = new Vector3(134.5f, 121.2f, 0f);
    private SpriteRenderer cachedPlayerSr;

    // Events
    public event Action OnShelterUsed;

    public string DisplayName => shelterDisplayName;
    public float InteractionRadius => interactionRadius;
    public GameObject HelicopterObject => gameObject;
    public GameObject CampfireObject => GameObject.Find("Campfire_Primitive");
    public GameObject SleepingVisual => sleepingVisual;

    void Awake()
    {
        if (instance != null && instance != this)
        {
            Destroy(gameObject);
            return;
        }
        instance = this;

        if (spriteRenderer == null) spriteRenderer = GetComponent<SpriteRenderer>();
        if (fuselageCollider == null) fuselageCollider = GetComponent<BoxCollider2D>();
    }

    void Start()
    {
        UpdateSortingOrder();
        EnsureSleepingVisual();
        EnsureForagingNodes();

        var survival = SurvivalStats.Instance ?? FindAnyObjectByType<SurvivalStats>();
        if (survival != null)
        {
            survival.OnRestingStateChanged += HandleRestingStateChanged;
        }

        StartCoroutine(OpeningIntroductionRoutine());
    }

    void OnDestroy()
    {
        var survival = SurvivalStats.Instance ?? FindAnyObjectByType<SurvivalStats>();
        if (survival != null)
        {
            survival.OnRestingStateChanged -= HandleRestingStateChanged;
        }

        if (cachedPlayerSr != null)
        {
            cachedPlayerSr.enabled = true;
        }

        if (instance == this) instance = null;
    }

    public void UpdateSortingOrder()
    {
        if (spriteRenderer == null) spriteRenderer = GetComponent<SpriteRenderer>();
        if (spriteRenderer != null)
        {
            spriteRenderer.sortingOrder = ResourceNode.BASE_SORTING_ORDER + Mathf.RoundToInt(-transform.position.y * 10f);
        }
    }

    public void EnsureSleepingVisual()
    {
        if (sleepingVisual != null) return;

        var existing = transform.Find("SleepingSurvivorVisual");
        if (existing != null)
        {
            sleepingVisual = existing.gameObject;
        }
        else
        {
            sleepingVisual = new GameObject("SleepingSurvivorVisual");
            sleepingVisual.transform.SetParent(transform, false);
            // Positioned inside the open corrugated cabin cot
            sleepingVisual.transform.localPosition = new Vector3(-0.05f, -0.05f, 0f);

            var sr = sleepingVisual.AddComponent<SpriteRenderer>();
            var sleepSprite = LoadSprite("Assets/Art/Environment/Camp/survivor_sleeping.png");
            if (sleepSprite != null) sr.sprite = sleepSprite;

            int parentOrder = spriteRenderer != null ? spriteRenderer.sortingOrder : ResourceNode.BASE_SORTING_ORDER;
            sr.sortingOrder = parentOrder + 1;
        }

        // Starts inactive
        sleepingVisual.SetActive(false);
    }

    public void HandleRestingStateChanged(bool isResting)
    {
        if (sleepingVisual == null) EnsureSleepingVisual();

        var playerObj = GameObject.FindWithTag("Player") ?? FindAnyObjectByType<PlayerInteraction>()?.gameObject;
        if (playerObj != null && cachedPlayerSr == null)
        {
            cachedPlayerSr = playerObj.GetComponentInChildren<SpriteRenderer>();
        }

        if (isResting)
        {
            // Player is resting inside the wreckage:
            // Display the sleeping survivor visual in the open cabin and hide standing sprite
            if (sleepingVisual != null)
            {
                sleepingVisual.SetActive(true);
            }
            if (cachedPlayerSr != null)
            {
                cachedPlayerSr.enabled = false;
            }
            if (playerObj != null)
            {
                playerObj.transform.position = insideCabinPos;
            }
        }
        else
        {
            // Player woke up:
            // Hide sleeping visual, restore standing sprite, and emerge at the cabin door
            if (sleepingVisual != null)
            {
                sleepingVisual.SetActive(false);
            }
            if (cachedPlayerSr != null)
            {
                cachedPlayerSr.enabled = true;
            }
            if (playerObj != null)
            {
                playerObj.transform.position = outsideExitPos;
            }
        }
    }

    private IEnumerator OpeningIntroductionRoutine()
    {
        // Wait briefly for frame 1 initialization and camera positioning
        yield return new WaitForSeconds(0.6f);

        if (!SaveManager.IsLoadedSession)
        {
            TemporaryResourceHUD.Instance?.ShowNotification(
                "You survived the crash, but you're stranded on an unfamiliar island.",
                new Color(1.0f, 0.88f, 0.45f)
            );

            yield return new WaitForSeconds(3.8f);

            if (!SaveManager.IsLoadedSession)
            {
                TemporaryResourceHUD.Instance?.ShowNotification(
                    "Explore the island and gather resources to survive.",
                    new Color(0.40f, 0.90f, 1.0f)
                );
            }
        }
    }

    public string GetInteractionPrompt(PlayerInteraction player)
    {
        if (player != null && player.Survival != null && player.Survival.IsResting)
        {
            return "[E] Stand Up (Stop Resting)";
        }
        return "[E] Crashed Helicopter (Shelter)";
    }

    public void Interact(PlayerInteraction player)
    {
        if (player == null) return;
        var survival = player.Survival;

        if (survival != null)
        {
            if (survival.IsDead) return;

            if (survival.IsResting)
            {
                survival.StopResting("Emerged from the helicopter cabin.");
                HandleRestingStateChanged(false);
                return;
            }

            if (survival.CurrentEnergy < 95f)
            {
                survival.StartResting();
                HandleRestingStateChanged(true);
                TemporaryResourceHUD.Instance?.ShowNotification(
                    "Resting inside the helicopter cabin. Safe from the island elements.",
                    new Color(0.45f, 1.0f, 0.60f)
                );
                AudioManager.Instance?.PlayItemCollect();
                OnShelterUsed?.Invoke();
            }
            else
            {
                TemporaryResourceHUD.Instance?.ShowNotification(
                    "The wreckage is badly damaged, but provides sturdy shelter from the elements.",
                    new Color(0.90f, 0.95f, 1.0f)
                );
                AudioManager.Instance?.PlayItemCollect();
            }
        }
        else
        {
            TemporaryResourceHUD.Instance?.ShowNotification(
                "The wreckage is badly damaged, but provides sturdy shelter from the elements.",
                new Color(0.90f, 0.95f, 1.0f)
            );
        }
    }

    /// <summary>
    /// Guarantees that the Crashed Helicopter and primitive base camp objects exist in the scene.
    /// Non-destructively spawns them under Environment_BaseCamp if not already present.
    /// </summary>
    public static HelicopterShelter EnsureExists()
    {
        if (instance != null) return instance;

        var existing = FindAnyObjectByType<HelicopterShelter>();
        if (existing != null)
        {
            instance = existing;
            existing.EnsureSleepingVisual();
            existing.EnsureForagingNodes();
            return existing;
        }

        // Create or locate base camp parent
        GameObject campRoot = GameObject.Find("Environment_BaseCamp");
        if (campRoot == null)
        {
            campRoot = new GameObject("Environment_BaseCamp");
        }

        // 1. Spawn Crashed Helicopter Landmark
        GameObject heliGo = GameObject.Find("Crashed_Helicopter");
        if (heliGo == null)
        {
            heliGo = new GameObject("Crashed_Helicopter");
            heliGo.transform.SetParent(campRoot.transform, false);
            heliGo.transform.position = new Vector3(134.5f, 122.8f, 0f);

            var sr = heliGo.AddComponent<SpriteRenderer>();
            var heliSprite = LoadSprite("Assets/Art/Environment/Camp/helicopter_wreckage.png");
            if (heliSprite != null) sr.sprite = heliSprite;

            var col = heliGo.AddComponent<BoxCollider2D>();
            col.size = new Vector2(3.6f, 1.4f);
            col.offset = new Vector2(0f, -0.2f);
        }
        else
        {
            // Update existing sprite & collider if refreshed
            var sr = heliGo.GetComponent<SpriteRenderer>();
            if (sr != null)
            {
                var heliSprite = LoadSprite("Assets/Art/Environment/Camp/helicopter_wreckage.png");
                if (heliSprite != null) sr.sprite = heliSprite;
            }
            var col = heliGo.GetComponent<BoxCollider2D>();
            if (col != null)
            {
                col.size = new Vector2(3.6f, 1.4f);
                col.offset = new Vector2(0f, -0.2f);
            }
        }

        var shelter = heliGo.GetComponent<HelicopterShelter>();
        if (shelter == null)
        {
            shelter = heliGo.AddComponent<HelicopterShelter>();
        }
        shelter.UpdateSortingOrder();
        shelter.EnsureSleepingVisual();

        // 2. Spawn Primitive Campfire
        GameObject fireGo = GameObject.Find("Campfire_Primitive");
        if (fireGo == null)
        {
            fireGo = new GameObject("Campfire_Primitive");
            fireGo.transform.SetParent(campRoot.transform, false);
            fireGo.transform.position = new Vector3(137.5f, 120.8f, 0f);

            var fireSr = fireGo.AddComponent<SpriteRenderer>();
            var fireSprite = LoadSprite("Assets/Art/Environment/Camp/campfire_primitive.png");
            if (fireSprite != null) fireSr.sprite = fireSprite;

            var fireCol = fireGo.AddComponent<CircleCollider2D>();
            fireCol.radius = 0.35f;

            if (fireSr != null)
            {
                fireSr.sortingOrder = ResourceNode.BASE_SORTING_ORDER + Mathf.RoundToInt(-120.8f * 10f);
            }
        }

        // 3. Spawn Surrounding Foraging Nodes
        shelter.EnsureForagingNodes();

        Debug.Log("[STRANDED Base Camp] Initialized Crashed Helicopter shelter and base camp at (134.5, 122.8).");
        return shelter;
    }

    /// <summary>
    /// Spawns edible berries, poisonous nightshade berries, and mushroom clusters around the camp.
    /// </summary>
    public void EnsureForagingNodes()
    {
        GameObject campRoot = GameObject.Find("Environment_BaseCamp");
        if (campRoot == null) campRoot = new GameObject("Environment_BaseCamp");

        // 1. Sweet Berry Bush at (132.0, 118.5)
        SpawnForagingNode(campRoot.transform, "Foraging_BerryBush",
            new Vector3(132.0f, 118.5f, 0f), "Assets/Art/Environment/Nodes/node_berry_bush.png",
            "Sweet Berry Bush", "berries", ResourceType.Berries, 2);

        // 2. Poisonous Nightshade Berry Bush at (139.5, 122.5)
        SpawnForagingNode(campRoot.transform, "Foraging_NightshadeBush",
            new Vector3(139.5f, 122.5f, 0f), "Assets/Art/Environment/Nodes/node_poison_berry_bush.png",
            "Poisonous Nightshade Bush", "poison_berries", ResourceType.Berries, 2);

        // 3. Edible Morel Mushroom Cluster at (138.0f, 117.2f)
        SpawnForagingNode(campRoot.transform, "Foraging_MorelCluster",
            new Vector3(138.0f, 117.2f, 0f), "Assets/Art/Environment/Nodes/node_mushroom_cluster.png",
            "Island Morel Cluster", "mushroom", ResourceType.Wood, 1);

        // 4. Poisonous Crimson Toadstools at (131.0f, 123.0f)
        SpawnForagingNode(campRoot.transform, "Foraging_CrimsonToadstools",
            new Vector3(131.0f, 123.0f, 0f), "Assets/Art/Environment/Nodes/node_poison_mushroom_cluster.png",
            "Crimson Toadstool Patch", "poison_mushroom", ResourceType.Wood, 1);
    }

    private void SpawnForagingNode(Transform parent, string nodeName, Vector3 worldPos, string spritePath,
        string displayName, string customItemId, ResourceType resType, int yield)
    {
        if (GameObject.Find(nodeName) != null) return;

        GameObject go = new GameObject(nodeName);
        go.transform.SetParent(parent, false);
        go.transform.position = worldPos;

        var sr = go.AddComponent<SpriteRenderer>();
        var sp = LoadSprite(spritePath);
        if (sp != null) sr.sprite = sp;

        var col = go.AddComponent<CircleCollider2D>();
        col.radius = 0.45f;
        col.isTrigger = false;

        var node = go.AddComponent<ResourceNode>();
        node.CustomItemId = customItemId;
        node.UpdateSortingOrder();

        // Use reflection to configure fields cleanly
        var t = typeof(ResourceNode);
        SetField(t, node, "resourceType", resType);
        SetField(t, node, "nodeDisplayName", displayName);
        SetField(t, node, "requiredTool", ToolType.None); // Harvestable by hand
        SetField(t, node, "nodeCategory", ResourceCategory.Bush);
        SetField(t, node, "nodeSize", ResourceSize.VerySmall);
        SetField(t, node, "yieldAmount", yield);
        SetField(t, node, "depleteOnHarvest", true);
        SetField(t, node, "regrowthDuration", 45f);
        SetField(t, node, "interactionRange", 1.8f);
    }

    private static void SetField(Type t, object target, string fieldName, object value)
    {
        var f = t.GetField(fieldName, System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
        if (f != null) f.SetValue(target, value);
    }

    private static Sprite LoadSprite(string path)
    {
#if UNITY_EDITOR
        var sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(path);
        if (sp != null) return sp;
#endif
        var allSprites = Resources.FindObjectsOfTypeAll<Sprite>();
        string fname = System.IO.Path.GetFileNameWithoutExtension(path);
        for (int i = 0; i < allSprites.Length; i++)
        {
            if (allSprites[i] != null && allSprites[i].name == fname)
            {
                return allSprites[i];
            }
        }
        return null;
    }
}
