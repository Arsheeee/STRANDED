using UnityEngine;
using UnityEngine.InputSystem;

/// <summary>
/// Handles player interaction with environmental ResourceNodes in STRANDED.
/// Detects the closest interactable resource within range, displays contextual HUD prompts,
/// and processes harvest interaction on pressing 'E'.
/// Also maintains dynamic Y-depth sorting for the player character.
/// </summary>
public class PlayerInteraction : MonoBehaviour
{
    [Header("Interaction Settings")]
    [Tooltip("Maximum search radius to query for nearby interactable nodes.")]
    [SerializeField] private float maxDetectionRadius = 2.0f;

    [Tooltip("Layer mask containing interactable resource nodes (default to Everything if unset).")]
    [SerializeField] private LayerMask interactableLayers = ~0;

    [Tooltip("Cooldown in seconds between interactions to prevent accidental repeated harvesting.")]
    [SerializeField] private float interactionCooldown = 0.25f;

    [Header("Tool Equipment")]
    [Tooltip("Currently equipped primitive tool.")]
    [SerializeField] private ToolType currentTool = ToolType.None;

    public ToolType CurrentTool => currentTool;
    public ToolType GetCurrentTool() => currentTool;

    /// <summary>
    /// Event triggered whenever a tool action is performed on a resource.
    /// Connects to future tool animations or sound hooks.
    /// </summary>
    public event System.Action<ToolType> OnToolUsed;

    private InputAction interactAction;
    private SpriteRenderer playerRenderer;
    private ResourceNode currentTargetNode;
    private float lastInteractionTime = -99f;
    private readonly Collider2D[] queryResults = new Collider2D[16];

    private Inventory inventory;
    public Inventory Inventory => inventory;

    void Start()
    {
        playerRenderer = GetComponent<SpriteRenderer>();

        // Setup E key interaction action with New Input System
        interactAction = new InputAction("Interact", binding: "<Keyboard>/e");
        interactAction.AddBinding("<Gamepad>/buttonSouth"); // Gamepad 'A' / Cross
        interactAction.Enable();

        // Ensure Inventory and UI components exist on player
        inventory = GetComponent<Inventory>();
        if (inventory == null)
        {
            inventory = gameObject.AddComponent<Inventory>();
        }
        if (GetComponent<HotbarUI>() == null)
        {
            gameObject.AddComponent<HotbarUI>();
        }
        if (GetComponent<InventoryUI>() == null)
        {
            gameObject.AddComponent<InventoryUI>();
        }
        if (GetComponent<CraftingManager>() == null)
        {
            gameObject.AddComponent<CraftingManager>();
        }
        if (GetComponent<CraftingUI>() == null)
        {
            gameObject.AddComponent<CraftingUI>();
        }

        // Ensure TemporaryResourceHUD is present in the scene for notifications
        if (TemporaryResourceHUD.Instance == null)
        {
            GameObject hudObj = new GameObject("TemporaryResourceHUD");
            hudObj.AddComponent<TemporaryResourceHUD>();
        }
    }

    void OnDestroy()
    {
        interactAction?.Disable();
    }

    void Update()
    {
        // 1. If Inventory or Crafting window is open, suppress world interaction to prevent accidental harvesting
        if (InventoryUI.IsOpen || CraftingUI.IsOpen)
        {
            if (currentTargetNode != null)
            {
                currentTargetNode = null;
                TemporaryResourceHUD.Instance?.SetInteractionPrompt("");
            }
            return;
        }

        // 2. Efficient local query for closest available ResourceNode
        UpdateNearbyInteractable();

        // 3. Check for interaction input ('E')
        bool wasInteracted = (interactAction != null && interactAction.WasPressedThisFrame());
        if (!wasInteracted && Keyboard.current != null && Keyboard.current.eKey.wasPressedThisFrame)
        {
            wasInteracted = true;
        }

        if (wasInteracted && currentTargetNode != null && currentTargetNode.CanInteract())
        {
            HarvestCurrentTarget();
        }
    }

    /// <summary>
    /// Equips the specified tool and updates feedback.
    /// </summary>
    public void EquipTool(ToolType tool)
    {
        currentTool = tool;
        string toolName = tool.ToDisplayName();
        Debug.Log($"[STRANDED Tool] Equipped: {toolName}");

        if (tool == ToolType.None)
        {
            TemporaryResourceHUD.ShowEquipmentNotification("Unequipped Tool (Hands Free)");
        }
        else
        {
            TemporaryResourceHUD.ShowEquipmentNotification($"Equipped: {toolName}");
        }

        UpdateNearbyInteractable();
    }

    /// <summary>
    /// Unequips current tool (sets to ToolType.None).
    /// </summary>
    public void UnequipTool()
    {
        EquipTool(ToolType.None);
    }

    /// <summary>
    /// Returns true if the currently equipped tool matches the specified tool.
    /// </summary>
    public bool CheckCurrentTool(ToolType tool)
    {
        return currentTool == tool;
    }

    /// <summary>
    /// Checks whether the currently equipped tool can interact with the given ResourceNode.
    /// </summary>
    public bool CanInteractWith(ResourceNode node)
    {
        return node != null && node.CanInteract() && node.CanHarvestWith(currentTool);
    }

    /// <summary>
    /// Triggers tool action event for animation/audio hooks.
    /// </summary>
    public void TriggerToolAction(ToolType tool)
    {
        OnToolUsed?.Invoke(tool);
        Debug.Log($"[STRANDED Action Hook] Tool action performed with {tool.ToDisplayName()}");
    }

    void LateUpdate()
    {
        // 3. Dynamic Y-depth sorting for Player:
        // Position at feet determines whether player renders behind or in front of trees/rocks.
        if (playerRenderer != null)
        {
            // +1 ensures that when player stands on the exact same Y line as an object base,
            // player's feet layer cleanly in front.
            playerRenderer.sortingOrder = ResourceNode.BASE_SORTING_ORDER + Mathf.RoundToInt(-transform.position.y * 10f) + 1;
        }
    }

    /// <summary>
    /// Searches nearby colliders and prioritizes the closest available ResourceNode within its range.
    /// </summary>
    private void UpdateNearbyInteractable()
    {
        Vector2 playerPos = transform.position;
        int hitCount = Physics2D.OverlapCircleNonAlloc(playerPos, maxDetectionRadius, queryResults, interactableLayers);

        ResourceNode bestNode = null;
        float bestDistanceSq = float.MaxValue;

        for (int i = 0; i < hitCount; i++)
        {
            Collider2D col = queryResults[i];
            if (col == null || col.isTrigger) continue;

            ResourceNode node = col.GetComponent<ResourceNode>();
            if (node == null)
            {
                node = col.GetComponentInParent<ResourceNode>();
            }

            if (node != null && node.CanInteract())
            {
                // Measure distance from player to node
                float distSq = ((Vector2)node.transform.position - playerPos).sqrMagnitude;
                float range = node.InteractionRange;

                // Must be within the node's specific interaction range
                if (distSq <= range * range && distSq < bestDistanceSq)
                {
                    bestDistanceSq = distSq;
                    bestNode = node;
                }
            }
        }

        currentTargetNode = bestNode;

        // Update HUD prompt with contextual tool information
        if (TemporaryResourceHUD.Instance != null)
        {
            if (currentTargetNode != null)
            {
                if (!currentTargetNode.RequiresTool)
                {
                    TemporaryResourceHUD.Instance.SetInteractionPrompt($"[E] Gather {currentTargetNode.DisplayName}");
                }
                else if (currentTargetNode.CanHarvestWith(currentTool))
                {
                    TemporaryResourceHUD.Instance.SetInteractionPrompt($"[E] Harvest {currentTargetNode.DisplayName} [{currentTool.ToDisplayName()}]");
                }
                else
                {
                    TemporaryResourceHUD.Instance.SetInteractionPrompt($"[E] {currentTargetNode.DisplayName} (Requires {currentTargetNode.RequiredTool.ToDisplayName()})");
                }
            }
            else
            {
                TemporaryResourceHUD.Instance.SetInteractionPrompt("");
            }
        }
    }

    /// <summary>
    /// Triggers harvest on the current target node and records collected yield.
    /// Uses interaction cooldown to prevent accidental repeated harvesting.
    /// </summary>
    private void HarvestCurrentTarget()
    {
        if (currentTargetNode == null) return;

        // Interaction cooldown check
        if (Time.time - lastInteractionTime < interactionCooldown)
        {
            return;
        }
        lastInteractionTime = Time.time;

        ResourceNode nodeToHarvest = currentTargetNode;
        int yielded = nodeToHarvest.Interact(this);

        // Re-evaluate target after state change
        UpdateNearbyInteractable();
    }

#if UNITY_EDITOR
    private void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(transform.position, maxDetectionRadius);
    }
#endif
}
