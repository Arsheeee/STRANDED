using System.Collections;
using UnityEngine;

/// <summary>
/// Data-driven categorization for environmental resource nodes in STRANDED.
/// </summary>
public enum ResourceCategory
{
    Generic,
    Rock,
    Bush,
    Log,
    Tree,
    Palm
}

/// <summary>
/// Data-driven physical sizing for environmental resource nodes in STRANDED.
/// Controls strict tool tier permissions (e.g. Stone Knife restricted to Very Small nodes).
/// </summary>
public enum ResourceSize
{
    None,
    VerySmall,
    Small,
    Medium,
    Large
}

/// <summary>
/// Reusable interactive resource node for STRANDED.
/// Handles resource yields, harvest interaction, depletion states,
/// visual feedback, and optional regrowth hooks.
/// </summary>
[RequireComponent(typeof(SpriteRenderer))]
[RequireComponent(typeof(Collider2D))]
public class ResourceNode : MonoBehaviour
{
    [Header("Resource Configuration")]
    [Tooltip("The primitive resource type yielded by this node.")]
    [SerializeField] private ResourceType resourceType = ResourceType.Wood;

    [Tooltip("Friendly display name shown in interaction prompts (e.g. 'Coconut Palm', 'Berry Bush').")]
    [SerializeField] private string nodeDisplayName = "";

    [Tooltip("Number of resource items yielded per harvest.")]
    [SerializeField] private int yieldAmount = 1;

    [Tooltip("Interaction distance from the player to this node.")]
    [SerializeField] private float interactionRange = 1.6f;

    [Header("Resource Classification & Sizing")]
    [Tooltip("Data-driven category of the resource node.")]
    [SerializeField] private ResourceCategory nodeCategory = ResourceCategory.Generic;

    [Tooltip("Data-driven size category of the resource node.")]
    [SerializeField] private ResourceSize nodeSize = ResourceSize.None;

    [Header("Tool Requirement")]
    [Tooltip("Primitive tool required to harvest this node. ToolType.None means harvestable by hand.")]
    [SerializeField] private ToolType requiredTool = ToolType.None;

    [Header("State & Depletion")]
    [Tooltip("Whether this node is currently harvestable.")]
    [SerializeField] private bool isHarvestable = true;

    [Tooltip("Whether the node transitions to a depleted state upon being harvested.")]
    [SerializeField] private bool depleteOnHarvest = true;

    [Tooltip("Sprite used when the node is available for harvest.")]
    [SerializeField] private Sprite availableSprite;

    [Tooltip("Sprite used when the node is depleted (e.g. tree stump, empty berry bush).")]
    [SerializeField] private Sprite depletedSprite;

    [Tooltip("If true, the GameObject is disabled/destroyed after depletion (e.g. small fiber plants or loose rocks).")]
    [SerializeField] private bool destroyOnDeplete = false;

    [Header("Future Regrowth (Optional)")]
    [Tooltip("Regrowth duration in seconds (0 = does not regrow automatically).")]
    [SerializeField] private float regrowthDuration = 0f;

    private SpriteRenderer spriteRenderer;
    private Collider2D nodeCollider;
    private bool isDepleted = false;
    private Vector3 initialScale;
    private Coroutine feedbackCoroutine;

    // Public Properties
    public ResourceType Type => resourceType;
    public ResourceCategory Category => nodeCategory;
    public ResourceSize Size => nodeSize;
    public ToolType RequiredTool => requiredTool;
    public bool RequiresTool => requiredTool != ToolType.None;
    public int YieldAmount => yieldAmount;
    public float InteractionRange => interactionRange;
    public bool IsAvailable => isHarvestable && !isDepleted;
    public bool IsDepleted => isDepleted;
    public float RegrowthDuration => regrowthDuration;
    public string DisplayName => string.IsNullOrEmpty(nodeDisplayName) ? resourceType.ToString() : nodeDisplayName;

    void Awake()
    {
        spriteRenderer = GetComponent<SpriteRenderer>();
        nodeCollider = GetComponent<Collider2D>();
        initialScale = transform.localScale;

        // Ensure default tool requirement matches resource type if unassigned
        if (requiredTool == ToolType.None)
        {
            requiredTool = GetDefaultToolRequirement(resourceType);
        }

        // Auto-infer category and size if left as defaults
        AutoInferCategoryAndSize();

        // Initialize sprite if available
        if (availableSprite != null && spriteRenderer.sprite == null)
        {
            spriteRenderer.sprite = availableSprite;
        }

        // Apply 2D Y-depth sorting so objects naturally layer based on ground position
        UpdateSortingOrder();
    }

    /// <summary>
    /// Explicitly configure the resource category and size classification.
    /// </summary>
    public void SetCategoryAndSize(ResourceCategory category, ResourceSize size)
    {
        nodeCategory = category;
        nodeSize = size;
    }

    /// <summary>
    /// Automatically infers node category and size from object name and properties if not explicitly set.
    /// Ensures 100% backward compatibility with pre-existing scene objects.
    /// </summary>
    public void AutoInferCategoryAndSize()
    {
        if (nodeCategory != ResourceCategory.Generic && nodeSize != ResourceSize.None)
        {
            return;
        }

        string n = gameObject != null ? gameObject.name.ToLowerInvariant() : "";
        string d = nodeDisplayName != null ? nodeDisplayName.ToLowerInvariant() : "";

        // Tree Classification
        if (n.Contains("tree") || d.Contains("tree") || (resourceType == ResourceType.Wood && (n.Contains("oak") || n.Contains("pine") || n.Contains("birch") || n.Contains("spruce") || n.Contains("fir") || n.Contains("cedar") || n.Contains("maple") || n.Contains("mahogany"))))
        {
            nodeCategory = ResourceCategory.Tree;
            nodeSize = ResourceSize.Large;
            return;
        }

        // Palm Classification
        if (n.Contains("palm") || d.Contains("palm") || resourceType == ResourceType.Coconut)
        {
            nodeCategory = ResourceCategory.Palm;
            nodeSize = ResourceSize.Large;
            return;
        }

        // Rock Classification
        if (resourceType == ResourceType.Stone || n.Contains("rock") || n.Contains("boulder") || n.Contains("slate") || n.Contains("pebble") || d.Contains("stone") || d.Contains("rock"))
        {
            nodeCategory = ResourceCategory.Rock;
            if (n.Contains("boulder") || d.Contains("large") || d.Contains("boulder"))
            {
                nodeSize = ResourceSize.Large;
            }
            else if (n.Contains("slate") || d.Contains("medium") || d.Contains("slate"))
            {
                nodeSize = ResourceSize.Medium;
            }
            else if (n.Contains("pebble") || d.Contains("pebble") || d.Contains("small") || d.Contains("loose") || n.Contains("small"))
            {
                nodeSize = ResourceSize.VerySmall;
            }
            else
            {
                nodeSize = ResourceSize.Medium;
            }
            return;
        }

        // Log / Driftwood Classification
        if (resourceType == ResourceType.Wood && (n.Contains("driftwood") || n.Contains("log") || d.Contains("log") || d.Contains("branch")))
        {
            nodeCategory = ResourceCategory.Log;
            if (n.Contains("small") || d.Contains("small") || d.Contains("branch"))
            {
                nodeSize = ResourceSize.VerySmall;
            }
            else if (n.Contains("large") || d.Contains("large"))
            {
                nodeSize = ResourceSize.Large;
            }
            else
            {
                nodeSize = ResourceSize.Medium;
            }
            return;
        }

        // Bush / Plant / Fiber Classification
        if (resourceType == ResourceType.Fiber || resourceType == ResourceType.Vines || resourceType == ResourceType.Berries || n.Contains("bush") || n.Contains("fern") || n.Contains("plant") || n.Contains("shrub") || n.Contains("tuft") || n.Contains("grass"))
        {
            nodeCategory = ResourceCategory.Bush;
            if (resourceType == ResourceType.Vines)
            {
                nodeSize = ResourceSize.Medium;
            }
            else if (resourceType == ResourceType.Berries)
            {
                nodeSize = ResourceSize.Medium;
            }
            else if (n.Contains("foliage") || d.Contains("foliage") || d.Contains("medium"))
            {
                nodeSize = ResourceSize.Medium;
            }
            else if (n.Contains("large") || d.Contains("large"))
            {
                nodeSize = ResourceSize.Large;
            }
            else
            {
                nodeSize = ResourceSize.VerySmall;
            }
            return;
        }
    }

    /// <summary>
    /// Gets the standard primitive tool requirement for a given resource type.
    /// </summary>
    public static ToolType GetDefaultToolRequirement(ResourceType type)
    {
        switch (type)
        {
            case ResourceType.Wood:
                return ToolType.StoneAxe;
            case ResourceType.Stone:
                return ToolType.StonePickaxe;
            case ResourceType.Fiber:
                return ToolType.StoneKnife;
            case ResourceType.Vines:
                return ToolType.StoneAxe;
            case ResourceType.Fish:
                return ToolType.FishingRod;
            case ResourceType.Berries:
            case ResourceType.Coconut:
            default:
                return ToolType.None;
        }
    }

    /// <summary>
    /// Explicitly configure the required tool for this node.
    /// </summary>
    public void SetRequiredTool(ToolType tool)
    {
        requiredTool = tool;
    }

    public const int BASE_SORTING_ORDER = 5000;

    /// <summary>
    /// Sets sorting order based on ground Y position.
    /// Higher Y sorts behind, lower Y sorts in front.
    /// Base offset of 5000 guarantees objects render above all terrain tilemaps (-20 to +20).
    /// </summary>
    public void UpdateSortingOrder()
    {
        if (spriteRenderer == null)
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
        }

        if (spriteRenderer != null)
        {
            // Scale by 10 to provide fine granularity between vertical pixel coordinates
            spriteRenderer.sortingOrder = BASE_SORTING_ORDER + Mathf.RoundToInt(-transform.position.y * 10f);
        }
    }

    /// <summary>
    /// Checks if the player can interact with this node.
    /// </summary>
    public bool CanInteract()
    {
        return gameObject.activeInHierarchy && isHarvestable && !isDepleted;
    }

    /// <summary>
    /// Checks whether the specified equipped tool satisfies this node's requirement.
    /// Returns true if harvestable, false otherwise.
    /// </summary>
    public bool CanHarvestWith(ToolType equippedTool)
    {
        return CanHarvestWith(equippedTool, out _);
    }

    /// <summary>
    /// Validates tool requirements with strict knife restriction enforcement and clear feedback.
    /// The Stone Knife is strictly permitted ONLY on:
    ///   1. Very Small Rock
    ///   2. Very Small Bush
    ///   3. Very Small Log
    /// Any other combination returns false with the clear rejection message:
    ///   "Your knife is too weak for this resource."
    /// </summary>
    public bool CanHarvestWith(ToolType equippedTool, out string failReason)
    {
        failReason = string.Empty;

        // If no tool is required (e.g. coconut palms, berry bushes), gatherable hands-free or with any tool
        if (requiredTool == ToolType.None)
        {
            return true;
        }

        // Strict Stone Knife harvesting rules:
        if (equippedTool == ToolType.StoneKnife)
        {
            bool isAllowed = (nodeCategory == ResourceCategory.Rock && nodeSize == ResourceSize.VerySmall)
                          || (nodeCategory == ResourceCategory.Bush && nodeSize == ResourceSize.VerySmall)
                          || (nodeCategory == ResourceCategory.Log && nodeSize == ResourceSize.VerySmall);

            if (isAllowed)
            {
                return true;
            }

            // Attempting to harvest medium/large rocks, medium/large bushes, normal/large logs, trees, or other nodes
            failReason = "Your knife is too weak for this resource.";
            return false;
        }

        // Hands free (None) attempted on tool-required node
        if (equippedTool == ToolType.None)
        {
            failReason = $"Requires {requiredTool.ToDisplayName()}";
            return false;
        }

        // Stone Axe harvesting: Fell trees, chop normal/large logs, cut dense foliage/vines, or very small logs
        if (equippedTool == ToolType.StoneAxe)
        {
            if (nodeCategory == ResourceCategory.Tree || nodeCategory == ResourceCategory.Log
                || nodeCategory == ResourceCategory.Bush || resourceType == ResourceType.Wood || resourceType == ResourceType.Vines)
            {
                return true;
            }
        }

        // Stone Pickaxe harvesting: Quarry small, medium, and large rocks/boulders
        if (equippedTool == ToolType.StonePickaxe)
        {
            if (nodeCategory == ResourceCategory.Rock || resourceType == ResourceType.Stone)
            {
                return true;
            }
        }

        // Improved Knife satisfies all Stone Knife cutting tasks, plus vines and bushes
        if (equippedTool == ToolType.ImprovedKnife)
        {
            if (requiredTool == ToolType.StoneKnife || requiredTool == ToolType.ImprovedKnife
                || nodeCategory == ResourceCategory.Bush || resourceType == ResourceType.Fiber || resourceType == ResourceType.Vines)
            {
                return true;
            }
        }

        // Exact tool match
        if (equippedTool == requiredTool)
        {
            return true;
        }

        // General failure with explicit requirement
        failReason = $"Requires {requiredTool.ToDisplayName()}";
        return false;
    }

    /// <summary>
    /// Harvests the resource from this node using the player's currently equipped tool.
    /// Returns yielded amount if successful, or 0 if requirement is not met or node is depleted.
    /// </summary>
    public int Interact(PlayerInteraction player)
    {
        ToolType equippedTool = player != null ? player.CurrentTool : ToolType.None;
        return Interact(equippedTool, player);
    }

    /// <summary>
    /// Attempts to harvest the node using a specific tool.
    /// Provides clear feedback if the tool is incorrect.
    /// </summary>
    public int Interact(ToolType equippedTool, PlayerInteraction player = null)
    {
        if (!CanInteract())
        {
            return 0;
        }

        // Validate tool requirement
        if (!CanHarvestWith(equippedTool, out string failReason))
        {
            // Requirement not met: Reject harvest, display clear feedback, and preserve state completely
            if (string.IsNullOrEmpty(failReason))
            {
                failReason = $"Requires {requiredTool.ToDisplayName()}";
            }
            TemporaryResourceHUD.ShowRequirementFeedback(failReason);
            AudioManager.Instance?.PlayCraftFail();
            return 0;
        }

        // Tool requirement satisfied: Check Inventory capacity if player has inventory
        ItemData resItem = ItemDatabase.GetResourceItem(resourceType);
        Inventory playerInv = player != null ? player.Inventory : null;

        if (playerInv != null && resItem != null)
        {
            if (!playerInv.CanAddItem(resItem, yieldAmount))
            {
                // Inventory is full: reject harvest atomically, preserve node state, show clear feedback
                TemporaryResourceHUD.ShowRequirementFeedback("Inventory Full");
                AudioManager.Instance?.PlayCraftFail();
                return 0;
            }
        }

        // Trigger player action hook for animations/audio
        if (player != null && equippedTool != ToolType.None)
        {
            player.TriggerToolAction(equippedTool);
        }

        int collected = yieldAmount;

        // Add to player's inventory
        if (playerInv != null && resItem != null)
        {
            playerInv.AddItem(resItem, collected);
        }

        // Display inventory collection feedback and trigger audio
        string itemDisplayName = resItem != null ? resItem.DisplayName : DisplayName;
        TemporaryResourceHUD.RecordCollection(resourceType, collected, itemDisplayName);
        AudioManager.Instance?.PlayResourceGather(resourceType);
        AudioManager.Instance?.PlayItemCollect();

        // Visual bounce feedback on interaction
        if (gameObject.activeInHierarchy)
        {
            if (feedbackCoroutine != null) StopCoroutine(feedbackCoroutine);
            feedbackCoroutine = StartCoroutine(InteractionBounceEffect());
        }

        // Update state
        if (depleteOnHarvest)
        {
            SetDepleted(true);
        }

        return collected;
    }

    /// <summary>
    /// Sets the node to available or depleted state.
    /// When regrowthDuration > 0, preserves GameObject activity to allow coroutine execution while disabling visuals/collision.
    /// </summary>
    public void SetDepleted(bool depleted)
    {
        isDepleted = depleted;

        if (isDepleted)
        {
            if (depletedSprite != null && spriteRenderer != null)
            {
                spriteRenderer.sprite = depletedSprite;
            }

            if (destroyOnDeplete)
            {
                if (nodeCollider != null) nodeCollider.enabled = false;
                if (spriteRenderer != null) spriteRenderer.enabled = false;

                // If regrowth is enabled, keep GameObject active so coroutine runs, but hide visual and disable collision
                if (regrowthDuration > 0f)
                {
                    StartCoroutine(RegrowthRoutine(regrowthDuration));
                }
                else
                {
                    gameObject.SetActive(false);
                }
            }
            else
            {
                // Regrowth hook for objects that remain in scene (e.g. tree stumps or harvested bushes)
                if (regrowthDuration > 0f && gameObject.activeInHierarchy)
                {
                    StartCoroutine(RegrowthRoutine(regrowthDuration));
                }
            }
        }
        else
        {
            // Restored to available state
            if (availableSprite != null && spriteRenderer != null)
            {
                spriteRenderer.sprite = availableSprite;
            }
            if (nodeCollider != null) nodeCollider.enabled = true;
            if (spriteRenderer != null) spriteRenderer.enabled = true;
            gameObject.SetActive(true);
        }
    }

    /// <summary>
    /// Restores the resource node to its available state.
    /// </summary>
    public void Regrow()
    {
        SetDepleted(false);
    }

    private IEnumerator RegrowthRoutine(float delay)
    {
        yield return new WaitForSeconds(delay);
        Regrow();
    }

    private IEnumerator InteractionBounceEffect()
    {
        // Gentle tactile punch scale for pixel art harvest feedback
        Vector3 targetPunch = initialScale * 1.12f;
        float elapsed = 0f;
        float duration = 0.08f;

        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            transform.localScale = Vector3.Lerp(initialScale, targetPunch, elapsed / duration);
            yield return null;
        }

        elapsed = 0f;
        duration = 0.10f;
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            transform.localScale = Vector3.Lerp(targetPunch, initialScale, elapsed / duration);
            yield return null;
        }

        transform.localScale = initialScale;
    }

    /// <summary>
    /// Ensures that default natural Vine gathering nodes exist in the island environment.
    /// Non-destructively spawns them under Environment_Resources/VineBushes if none are present in the scene.
    /// </summary>
    public static void EnsureDefaultVineNodesExist()
    {
        ResourceNode[] allNodes = FindObjectsByType<ResourceNode>();
        bool hasVines = false;
        for (int i = 0; i < allNodes.Length; i++)
        {
            if (allNodes[i] != null && allNodes[i].Type == ResourceType.Vines)
            {
                hasVines = true;
                // Ensure existing colliders are non-triggers so physical interaction is completely reliable
                Collider2D c = allNodes[i].GetComponent<Collider2D>();
                if (c != null && c.isTrigger)
                {
                    c.isTrigger = false;
                }
            }
        }
        if (hasVines) return;

        GameObject envRoot = GameObject.Find("Environment_Resources");
        GameObject vinesRoot = GameObject.Find("VineBushes");
        if (vinesRoot == null)
        {
            vinesRoot = new GameObject("VineBushes");
            if (envRoot != null) vinesRoot.transform.SetParent(envRoot.transform);
        }

        Vector2[] defaultPositions = new Vector2[]
        {
            new Vector2(141.5f, 124.5f),
            new Vector2(146.5f, 118.5f),
            new Vector2(132.5f, 127.5f),
            new Vector2(154.5f, 134.5f),
            new Vector2(165.5f, 112.5f),
            new Vector2(178.5f, 108.5f),
            new Vector2(188.5f, 132.5f),
            new Vector2(202.5f, 232.5f),
            new Vector2(215.5f, 222.5f),
            new Vector2(230.5f, 178.5f)
        };

        Sprite bushSprite = LoadSpriteAsset("Assets/Art/Environment/Plants/plant_vine_bush.png");
        Sprite depletedSprite = LoadSpriteAsset("Assets/Art/Environment/Plants/plant_vine_depleted.png");

        for (int i = 0; i < defaultPositions.Length; i++)
        {
            GameObject nodeGo = new GameObject($"Vine_Cluster_{i + 1}");
            nodeGo.transform.position = new Vector3(defaultPositions[i].x, defaultPositions[i].y, 0f);
            nodeGo.transform.SetParent(vinesRoot.transform, false);

            SpriteRenderer sr = nodeGo.AddComponent<SpriteRenderer>();
            sr.sprite = bushSprite;

            CircleCollider2D col = nodeGo.AddComponent<CircleCollider2D>();
            col.isTrigger = false;
            col.radius = 0.4f;
            col.offset = new Vector2(0f, 0.2f);

            ResourceNode node = nodeGo.AddComponent<ResourceNode>();
            node.resourceType = ResourceType.Vines;
            node.nodeDisplayName = "Jungle Vine Cluster";
            node.requiredTool = ToolType.StoneAxe;
            node.nodeCategory = ResourceCategory.Bush;
            node.nodeSize = ResourceSize.Medium;
            node.yieldAmount = 2;
            node.interactionRange = 1.6f;
            node.isHarvestable = true;
            node.depleteOnHarvest = true;
            node.destroyOnDeplete = false;
            node.regrowthDuration = 45f;
            node.availableSprite = bushSprite;
            node.depletedSprite = depletedSprite;

            node.UpdateSortingOrder();
        }

        Debug.Log($"[STRANDED World] Initialized {defaultPositions.Length} default Vine gathering nodes.");
    }

    /// <summary>
    /// Guarantees that essential knife-compatible starting resources exist around the helicopter crash shelter (135.5, 120.5):
    /// 8 Very Small Rocks (Pebbles yielding Stone), 8 Very Small Logs (Branches yielding Wood), and 8 Very Small Bushes (Shrubs yielding Fiber).
    /// All 24 starting nodes have regrowthDuration = 45f so the player can never permanently exhaust basic early resources.
    /// Non-destructively spawns them under Environment_Resources/StarterCamp if not already present.
    /// </summary>
    public static void EnsureStartingCampResourcesExist()
    {
        ResourceNode[] allNodes = FindObjectsByType<ResourceNode>();
        bool hasStarterCamp = false;
        for (int i = 0; i < allNodes.Length; i++)
        {
            if (allNodes[i] != null && allNodes[i].gameObject.name.StartsWith("Starter_"))
            {
                hasStarterCamp = true;
                break;
            }
        }
        if (hasStarterCamp) return;

        GameObject envRoot = GameObject.Find("Environment_Resources");
        if (envRoot == null)
        {
            envRoot = new GameObject("Environment_Resources");
        }

        GameObject starterRoot = GameObject.Find("StarterCamp");
        if (starterRoot == null)
        {
            starterRoot = new GameObject("StarterCamp");
            starterRoot.transform.SetParent(envRoot.transform, false);
        }

        // 8 Very Small Rocks (Pebbles yielding Stone, StoneKnife)
        Vector2[] rockPositions = new Vector2[]
        {
            new Vector2(132.5f, 122.5f),
            new Vector2(133.5f, 117.5f),
            new Vector2(137.5f, 117.5f),
            new Vector2(139.5f, 122.5f),
            new Vector2(138.5f, 124.5f),
            new Vector2(132.5f, 119.5f),
            new Vector2(136.5f, 125.5f),
            new Vector2(134.5f, 116.5f)
        };

        // 8 Very Small Logs (Driftwood branches yielding Wood, StoneKnife)
        Vector2[] logPositions = new Vector2[]
        {
            new Vector2(138.5f, 119.5f),
            new Vector2(132.5f, 124.5f),
            new Vector2(134.5f, 125.5f),
            new Vector2(139.5f, 118.5f),
            new Vector2(136.5f, 116.5f),
            new Vector2(131.5f, 121.5f),
            new Vector2(137.5f, 123.5f),
            new Vector2(133.5f, 123.5f)
        };

        // 8 Very Small Bushes (Wild shrubs yielding Fiber, StoneKnife)
        Vector2[] bushPositions = new Vector2[]
        {
            new Vector2(133.5f, 121.5f),
            new Vector2(137.5f, 121.5f),
            new Vector2(135.5f, 124.5f),
            new Vector2(135.5f, 117.5f),
            new Vector2(138.5f, 117.5f),
            new Vector2(131.5f, 118.5f),
            new Vector2(139.5f, 124.5f),
            new Vector2(132.5f, 116.5f)
        };

        Sprite spRockSmall = LoadSpriteAsset("Assets/Art/Environment/Rocks/rock_slate_small.png");
        Sprite spLogSmall = LoadSpriteAsset("Assets/Art/Environment/Trees/driftwood_small.png");
        Sprite spBushSmall = LoadSpriteAsset("Assets/Art/Environment/Plants/bush_shrub_small.png");

        for (int i = 0; i < rockPositions.Length; i++)
        {
            CreateStarterNode($"Starter_Rock_Pebble_{i + 1}", rockPositions[i], starterRoot.transform,
                ResourceType.Stone, "Small Pebble", ToolType.StoneKnife,
                ResourceCategory.Rock, ResourceSize.VerySmall, spRockSmall, 0.25f, 1.3f);
        }

        for (int i = 0; i < logPositions.Length; i++)
        {
            CreateStarterNode($"Starter_Log_Branch_{i + 1}", logPositions[i], starterRoot.transform,
                ResourceType.Wood, "Small Log", ToolType.StoneKnife,
                ResourceCategory.Log, ResourceSize.VerySmall, spLogSmall, 0.25f, 1.3f);
        }

        for (int i = 0; i < bushPositions.Length; i++)
        {
            CreateStarterNode($"Starter_Bush_Fiber_{i + 1}", bushPositions[i], starterRoot.transform,
                ResourceType.Fiber, "Small Bush", ToolType.StoneKnife,
                ResourceCategory.Bush, ResourceSize.VerySmall, spBushSmall, 0.25f, 1.3f);
        }

        Debug.Log("[STRANDED World] Initialized 24 guaranteed renewable starter nodes (8 Rocks, 8 Logs, 8 Bushes) around helicopter shelter.");
    }

    private static void CreateStarterNode(string name, Vector2 pos, Transform parent,
        ResourceType resType, string displayName, ToolType reqTool,
        ResourceCategory cat, ResourceSize sz, Sprite sprite, float colRadius, float range)
    {
        GameObject go = new GameObject(name);
        go.transform.position = new Vector3(pos.x, pos.y, 0f);
        go.transform.SetParent(parent, false);

        SpriteRenderer sr = go.AddComponent<SpriteRenderer>();
        sr.sprite = sprite;

        CircleCollider2D col = go.AddComponent<CircleCollider2D>();
        col.isTrigger = false;
        col.radius = colRadius;
        col.offset = new Vector2(0f, colRadius * 0.5f);

        ResourceNode node = go.AddComponent<ResourceNode>();
        node.resourceType = resType;
        node.nodeDisplayName = displayName;
        node.requiredTool = reqTool;
        node.nodeCategory = cat;
        node.nodeSize = sz;
        node.yieldAmount = 1;
        node.interactionRange = range;
        node.isHarvestable = true;
        node.depleteOnHarvest = true;
        node.destroyOnDeplete = true;
        node.regrowthDuration = 45f;
        node.availableSprite = sprite;

        node.UpdateSortingOrder();
    }

    private static Sprite LoadSpriteAsset(string path)
    {
#if UNITY_EDITOR
        Sprite s = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(path);
        if (s != null) return s;
#endif
        if (System.IO.File.Exists(path))
        {
            try
            {
                byte[] bytes = System.IO.File.ReadAllBytes(path);
                Texture2D tex = new Texture2D(16, 16, TextureFormat.RGBA32, false);
                tex.filterMode = FilterMode.Point;
                if (tex.LoadImage(bytes))
                {
                    return Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height), new Vector2(0.5f, 0.5f), 16f);
                }
            }
            catch (System.Exception) { }
        }
        return null;
    }

#if UNITY_EDITOR
    private void OnDrawGizmosSelected()
    {
        // Visualize interaction range in editor
        Gizmos.color = Color.green;
        Gizmos.DrawWireSphere(transform.position, interactionRange);
    }
#endif
}
