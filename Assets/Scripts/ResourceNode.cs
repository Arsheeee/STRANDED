using System.Collections;
using UnityEngine;

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
    public ToolType RequiredTool => requiredTool;
    public bool RequiresTool => requiredTool != ToolType.None;
    public int YieldAmount => yieldAmount;
    public float InteractionRange => interactionRange;
    public bool IsAvailable => isHarvestable && !isDepleted;
    public bool IsDepleted => isDepleted;
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

        // Initialize sprite if available
        if (availableSprite != null && spriteRenderer.sprite == null)
        {
            spriteRenderer.sprite = availableSprite;
        }

        // Apply 2D Y-depth sorting so objects naturally layer based on ground position
        UpdateSortingOrder();
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
            case ResourceType.Vines:
                return ToolType.StoneKnife;
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
    /// Returns true if no tool is required, or if the equipped tool matches.
    /// </summary>
    public bool CanHarvestWith(ToolType equippedTool)
    {
        if (requiredTool == ToolType.None)
        {
            return true;
        }
        // Improved Knife satisfies all Stone Knife cutting requirements
        if (requiredTool == ToolType.StoneKnife && equippedTool == ToolType.ImprovedKnife)
        {
            return true;
        }
        return equippedTool == requiredTool;
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
        if (!CanHarvestWith(equippedTool))
        {
            // Requirement not met: Reject harvest and display clear feedback
            string reqName = requiredTool.ToDisplayName();
            TemporaryResourceHUD.ShowRequirementFeedback($"Requires {reqName}");
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

        // Display inventory collection feedback
        string itemDisplayName = resItem != null ? resItem.DisplayName : DisplayName;
        TemporaryResourceHUD.RecordCollection(resourceType, collected, itemDisplayName);

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
                gameObject.SetActive(false);
            }

            // Regrowth hook for future systems
            if (regrowthDuration > 0f && gameObject.activeInHierarchy)
            {
                StartCoroutine(RegrowthRoutine(regrowthDuration));
            }
        }
        else
        {
            // Restored
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
            node.requiredTool = ToolType.StoneKnife;
            node.yieldAmount = 2;
            node.interactionRange = 1.6f;
            node.isHarvestable = true;
            node.depleteOnHarvest = true;
            node.destroyOnDeplete = false;
            node.availableSprite = bushSprite;
            node.depletedSprite = depletedSprite;

            node.UpdateSortingOrder();
        }

        Debug.Log($"[STRANDED World] Initialized {defaultPositions.Length} default Vine gathering nodes.");
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
