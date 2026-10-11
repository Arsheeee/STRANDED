using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.Tilemaps;

/// <summary>
/// Handles player interaction with environmental ResourceNodes and water sources in STRANDED.
/// Detects the closest interactable resource or water within range, displays contextual HUD prompts,
/// and processes harvest/drink interaction on pressing 'E'.
/// Also enforces energy costs and maintains dynamic Y-depth sorting for the player character.
/// </summary>
public class PlayerInteraction : MonoBehaviour
{
    public enum NearbyWaterType
    {
        None,
        Freshwater,
        Seawater
    }

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
    private FishingSpot currentTargetSpot;
    private FishingSpot activeFishingSpot;
    private BoatConstructionSite currentTargetBoatSite;
    private NearbyWaterType nearbyWater = NearbyWaterType.None;
    private float lastInteractionTime = -99f;
    private readonly Collider2D[] queryResults = new Collider2D[16];

    private Inventory inventory;
    private SurvivalStats survivalStats;
    private Tilemap riverTilemap;
    private Tilemap shallowOceanTilemap;
    private Tilemap deepOceanTilemap;

    public Inventory Inventory => inventory;
    public SurvivalStats Survival => survivalStats;
    public FishingSpot ActiveFishingSpot => activeFishingSpot;
    public FishingSpot CurrentTargetSpot => currentTargetSpot;
    public BoatConstructionSite CurrentTargetBoatSite => currentTargetBoatSite;

    public void SetActiveFishingSpot(FishingSpot spot)
    {
        activeFishingSpot = spot;
    }

    public void ClearActiveFishingSpot(FishingSpot spot)
    {
        if (activeFishingSpot == spot)
        {
            activeFishingSpot = null;
        }
    }

    public void ClearFishing()
    {
        activeFishingSpot = null;
    }

    void Start()
    {
        playerRenderer = GetComponent<SpriteRenderer>();

        // Setup E key interaction action with New Input System
        interactAction = new InputAction("Interact", binding: "<Keyboard>/e");
        interactAction.AddBinding("<Gamepad>/buttonSouth"); // Gamepad 'A' / Cross
        interactAction.Enable();

        // Ensure Inventory, Crafting, and Survival components exist on player
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
        survivalStats = GetComponent<SurvivalStats>();
        if (survivalStats == null)
        {
            survivalStats = gameObject.AddComponent<SurvivalStats>();
        }
        if (GetComponent<SurvivalHUD>() == null)
        {
            gameObject.AddComponent<SurvivalHUD>();
        }
        if (GetComponent<ObjectiveUI>() == null)
        {
            gameObject.AddComponent<ObjectiveUI>();
        }

        // Ensure TemporaryResourceHUD is present in the scene for notifications
        if (TemporaryResourceHUD.Instance == null)
        {
            GameObject hudObj = new GameObject("TemporaryResourceHUD");
            hudObj.AddComponent<TemporaryResourceHUD>();
        }

        LocateWaterTilemaps();
        FishingSpot.EnsureDefaultFishingSpotsExist();
        ResourceNode.EnsureDefaultVineNodesExist();
        BoatConstructionSite.EnsureDefaultSiteExists();
        ObjectiveManager.EnsureExists();
        EscapeEndingController.EnsureExists();
        SaveManager.EnsureExists();
    }

    private void LocateWaterTilemaps()
    {
        if (riverTilemap == null)
        {
            var riverObj = GameObject.Find("Tilemap_River");
            if (riverObj != null) riverTilemap = riverObj.GetComponent<Tilemap>();
        }
        if (shallowOceanTilemap == null)
        {
            var shallowObj = GameObject.Find("Tilemap_ShallowWater");
            if (shallowObj != null) shallowOceanTilemap = shallowObj.GetComponent<Tilemap>();
        }
        if (deepOceanTilemap == null)
        {
            var deepObj = GameObject.Find("Tilemap_DeepOcean");
            if (deepObj != null) deepOceanTilemap = deepObj.GetComponent<Tilemap>();
        }
    }

    void OnDestroy()
    {
        interactAction?.Disable();
    }

    void Update()
    {
        // 0. If dead, suppress all interaction
        if (survivalStats != null && survivalStats.IsDead)
        {
            if (activeFishingSpot != null)
            {
                activeFishingSpot.CancelFishing(string.Empty);
            }
            if (currentTargetBoatSite != null || currentTargetNode != null || currentTargetSpot != null || nearbyWater != NearbyWaterType.None)
            {
                currentTargetBoatSite = null;
                currentTargetNode = null;
                currentTargetSpot = null;
                nearbyWater = NearbyWaterType.None;
                TemporaryResourceHUD.Instance?.SetInteractionPrompt("");
            }
            return;
        }

        // 0.5. If Escape Ending is active, suppress all interaction
        if (EscapeEndingController.Instance != null && EscapeEndingController.Instance.IsEndingActive)
        {
            if (activeFishingSpot != null)
            {
                activeFishingSpot.CancelFishing(string.Empty);
            }
            if (currentTargetBoatSite != null || currentTargetNode != null || currentTargetSpot != null || nearbyWater != NearbyWaterType.None)
            {
                currentTargetBoatSite = null;
                currentTargetNode = null;
                currentTargetSpot = null;
                nearbyWater = NearbyWaterType.None;
                TemporaryResourceHUD.Instance?.SetInteractionPrompt("");
            }
            return;
        }

        // 1. If Inventory, Crafting, or Boat Construction window is open, suppress world interaction to prevent accidental harvesting
        if (InventoryUI.IsOpen || CraftingUI.IsOpen || BoatConstructionUI.IsOpen)
        {
            if (activeFishingSpot != null)
            {
                activeFishingSpot.CancelFishing("Fishing cancelled.");
            }
            if (currentTargetBoatSite != null || currentTargetNode != null || currentTargetSpot != null || nearbyWater != NearbyWaterType.None)
            {
                currentTargetBoatSite = null;
                currentTargetNode = null;
                currentTargetSpot = null;
                nearbyWater = NearbyWaterType.None;
                TemporaryResourceHUD.Instance?.SetInteractionPrompt("");
            }
            return;
        }

        // Check discovery proximity for boat construction site
        BoatConstructionSite.Instance?.CheckDiscovery(transform.position);

        // Quick Consume key (F key): Consumes food from currently selected hotbar slot
        if (Keyboard.current != null && Keyboard.current.fKey.wasPressedThisFrame)
        {
            HandleQuickConsume();
        }

        // Check for interaction input ('E')
        bool wasInteracted = (interactAction != null && interactAction.WasPressedThisFrame());
        if (!wasInteracted && Keyboard.current != null && Keyboard.current.eKey.wasPressedThisFrame)
        {
            wasInteracted = true;
        }

        // If actively fishing, direct input directly to the fishing spot
        if (activeFishingSpot != null)
        {
            if (wasInteracted)
            {
                activeFishingSpot.OnInteractPressed(this);
            }

            // Update prompt for active fishing state
            if (TemporaryResourceHUD.Instance != null)
            {
                if (activeFishingSpot.CurrentState == FishingSpot.FishingState.WaitingForBite)
                {
                    TemporaryResourceHUD.Instance.SetInteractionPrompt("[E] Waiting for bite... (Move to cancel)");
                }
                else if (activeFishingSpot.CurrentState == FishingSpot.FishingState.BiteAlert)
                {
                    TemporaryResourceHUD.Instance.SetInteractionPrompt($"[E] REEL IN! ({activeFishingSpot.RemainingReactionTime:F1}s)");
                }
                else
                {
                    TemporaryResourceHUD.Instance.SetInteractionPrompt("");
                }
            }
            return;
        }

        // 2. Efficient local query for closest available ResourceNode, FishingSpot, Boat Site, or Water
        UpdateNearbyInteractable();

        if (wasInteracted)
        {
            if (currentTargetBoatSite != null)
            {
                if (currentTargetBoatSite.IsComplete)
                {
                    currentTargetBoatSite.TryLaunch(this, out _);
                }
                else
                {
                    currentTargetBoatSite.Interact(this);
                }
            }
            else if (currentTargetSpot != null)
            {
                if (currentTool == ToolType.FishingRod)
                {
                    currentTargetSpot.StartFishing(this);
                }
                else
                {
                    TemporaryResourceHUD.ShowRequirementFeedback("Requires Fishing Rod to fish.");
                }
            }
            else if (currentTargetNode != null && currentTargetNode.CanInteract())
            {
                HarvestCurrentTarget();
            }
            else if (nearbyWater != NearbyWaterType.None)
            {
                InteractWithWater();
            }
        }
    }

    private void HandleQuickConsume()
    {
        if (inventory == null || survivalStats == null) return;
        var hotbar = GetComponent<HotbarUI>();
        int activeSlot = hotbar != null ? hotbar.SelectedSlotIndex : 0;
        var slot = inventory.GetSlot(activeSlot);

        if (slot != null && !slot.IsEmpty && slot.Item != null && slot.Item.IsConsumable)
        {
            survivalStats.TryConsumeItem(slot.Item, activeSlot);
        }
        else
        {
            for (int i = 0; i < 12; i++)
            {
                var s = inventory.GetSlot(i);
                if (s != null && !s.IsEmpty && s.Item != null && s.Item.IsConsumable)
                {
                    survivalStats.TryConsumeItem(s.Item, i);
                    return;
                }
            }
            TemporaryResourceHUD.Instance?.ShowNotification("No edible food in hotbar to consume.", Color.gray);
        }
    }

    /// <summary>
    /// Equips the specified tool and updates feedback.
    /// </summary>
    public void EquipTool(ToolType tool)
    {
        if (activeFishingSpot != null && tool != ToolType.FishingRod)
        {
            activeFishingSpot.CancelFishing("Unequipped Fishing Rod.");
        }

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
    /// Searches nearby colliders and prioritizes the closest available ResourceNode or FishingSpot within range.
    /// </summary>
    private void UpdateNearbyInteractable()
    {
        Vector2 playerPos = transform.position;
        int hitCount = Physics2D.OverlapCircleNonAlloc(playerPos, maxDetectionRadius, queryResults, interactableLayers);

        ResourceNode bestNode = null;
        float bestNodeDistSq = float.MaxValue;

        for (int i = 0; i < hitCount; i++)
        {
            Collider2D col = queryResults[i];
            if (col == null) continue;

            ResourceNode node = col.GetComponent<ResourceNode>();
            if (node == null)
            {
                node = col.GetComponentInParent<ResourceNode>();
            }

            // Only skip trigger colliders if they do not belong to a ResourceNode
            if (node == null && col.isTrigger) continue;

            if (node != null && node.CanInteract())
            {
                // Measure distance from player to node
                float distSq = ((Vector2)node.transform.position - playerPos).sqrMagnitude;
                float range = node.InteractionRange;

                // Must be within the node's specific interaction range
                if (distSq <= range * range && distSq < bestNodeDistSq)
                {
                    bestNodeDistSq = distSq;
                    bestNode = node;
                }
            }
        }

        // Query for closest valid FishingSpot within interaction radius
        FishingSpot bestSpot = null;
        float bestSpotDistSq = float.MaxValue;
        for (int i = 0; i < FishingSpot.AllSpots.Count; i++)
        {
            var spot = FishingSpot.AllSpots[i];
            if (spot == null || !spot.gameObject.activeInHierarchy) continue;

            float distSq = ((Vector2)spot.transform.position - playerPos).sqrMagnitude;
            float range = spot.InteractionRadius;

            if (distSq <= range * range && distSq < bestSpotDistSq)
            {
                bestSpotDistSq = distSq;
                bestSpot = spot;
            }
        }

        // Query for Boat Construction Site
        BoatConstructionSite bestBoatSite = null;
        var siteInstance = BoatConstructionSite.Instance;
        if (siteInstance != null && siteInstance.gameObject.activeInHierarchy)
        {
            float distSq = ((Vector2)siteInstance.transform.position - playerPos).sqrMagnitude;
            float range = siteInstance.InteractionRadius;
            if (distSq <= range * range)
            {
                bestBoatSite = siteInstance;
            }
        }

        currentTargetNode = bestNode;
        currentTargetSpot = bestSpot;
        currentTargetBoatSite = bestBoatSite;

        // Prioritize fishing spot if Fishing Rod is equipped, or if no node is near, or if spot is closer
        bool prioritizeFishing = (bestSpot != null) && (bestNode == null || currentTool == ToolType.FishingRod || bestSpotDistSq < bestNodeDistSq);

        // Update HUD prompt with contextual tool, boat site, or water information
        if (TemporaryResourceHUD.Instance != null)
        {
            if (currentTargetBoatSite != null)
            {
                nearbyWater = NearbyWaterType.None;
                currentTargetSpot = null;
                currentTargetNode = null;
                if (currentTargetBoatSite.IsComplete)
                {
                    TemporaryResourceHUD.Instance.SetInteractionPrompt("[E] Launch Escape Boat (Set Sail)");
                }
                else
                {
                    var req = currentTargetBoatSite.GetCurrentRequirement();
                    string nextReqStr = req != null ? $" — Needs {req.DisplayName}" : "";
                    TemporaryResourceHUD.Instance.SetInteractionPrompt($"[E] {currentTargetBoatSite.SiteDisplayName} (Stage {currentTargetBoatSite.CurrentStageIndex}/{currentTargetBoatSite.TotalStages}{nextReqStr})");
                }
            }
            else if (prioritizeFishing && currentTargetSpot != null)
            {
                nearbyWater = NearbyWaterType.None;
                currentTargetNode = null; // Suppress node prompt while focused on fishing spot
                if (currentTool == ToolType.FishingRod)
                {
                    TemporaryResourceHUD.Instance.SetInteractionPrompt($"[E] Fish at {currentTargetSpot.SpotName}");
                }
                else
                {
                    TemporaryResourceHUD.Instance.SetInteractionPrompt($"[E] {currentTargetSpot.SpotName} (Requires Fishing Rod)");
                }
            }
            else if (currentTargetNode != null)
            {
                currentTargetSpot = null;
                nearbyWater = NearbyWaterType.None;
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
                currentTargetSpot = null;
                nearbyWater = CheckNearbyWater(playerPos);
                if (nearbyWater == NearbyWaterType.Freshwater)
                {
                    TemporaryResourceHUD.Instance.SetInteractionPrompt("[E] Drink Freshwater");
                }
                else if (nearbyWater == NearbyWaterType.Seawater)
                {
                    TemporaryResourceHUD.Instance.SetInteractionPrompt("[E] Ocean Water");
                }
                else
                {
                    TemporaryResourceHUD.Instance.SetInteractionPrompt("");
                }
            }
        }
    }

    private NearbyWaterType CheckNearbyWater(Vector2 playerPos)
    {
        LocateWaterTilemaps();

        int px = Mathf.RoundToInt(playerPos.x);
        int py = Mathf.RoundToInt(playerPos.y);

        // Check river first (Freshwater has priority)
        if (riverTilemap != null)
        {
            for (int dx = -1; dx <= 1; dx++)
            {
                for (int dy = -1; dy <= 1; dy++)
                {
                    Vector3Int pos = new Vector3Int(px + dx, py + dy, 0);
                    if (riverTilemap.HasTile(pos))
                    {
                        return NearbyWaterType.Freshwater;
                    }
                }
            }
        }

        // Check shallow or deep ocean (Seawater)
        for (int dx = -1; dx <= 1; dx++)
        {
            for (int dy = -1; dy <= 1; dy++)
            {
                Vector3Int pos = new Vector3Int(px + dx, py + dy, 0);
                if (shallowOceanTilemap != null && shallowOceanTilemap.HasTile(pos))
                {
                    return NearbyWaterType.Seawater;
                }
                if (deepOceanTilemap != null && deepOceanTilemap.HasTile(pos))
                {
                    return NearbyWaterType.Seawater;
                }
            }
        }

        return NearbyWaterType.None;
    }

    private void InteractWithWater()
    {
        if (Time.time - lastInteractionTime < interactionCooldown) return;
        lastInteractionTime = Time.time;

        if (nearbyWater == NearbyWaterType.Freshwater)
        {
            if (survivalStats != null)
            {
                if (survivalStats.CurrentThirst >= survivalStats.MaxThirst)
                {
                    TemporaryResourceHUD.Instance?.ShowNotification("Thirst is already quenched.", Color.white);
                }
                else
                {
                    survivalStats.RestoreThirst(25f);
                    TemporaryResourceHUD.Instance?.ShowNotification("Drank fresh river water (+25 Thirst)", new Color(0.35f, 0.85f, 1.0f));
                }
            }
        }
        else if (nearbyWater == NearbyWaterType.Seawater)
        {
            TemporaryResourceHUD.Instance?.ShowNotification("Salt water is unsafe to drink.", new Color(1.0f, 0.40f, 0.35f));
        }
    }

    /// <summary>
    /// Triggers harvest on the current target node and records collected yield.
    /// Checks energy cost when using tools to enforce stamina management.
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

        // Energy Check: Tool harvesting consumes energy
        if (currentTargetNode.RequiresTool && survivalStats != null)
        {
            if (survivalStats.CurrentEnergy < survivalStats.ToolEnergyCost)
            {
                TemporaryResourceHUD.ShowRequirementFeedback("Too exhausted to perform this action.");
                return;
            }
        }

        lastInteractionTime = Time.time;

        ResourceNode nodeToHarvest = currentTargetNode;
        int yielded = nodeToHarvest.Interact(this);

        // Deduct energy only if harvest was successfully performed with a tool
        if (yielded > 0 && currentTargetNode != null && currentTargetNode.RequiresTool && survivalStats != null)
        {
            survivalStats.ConsumeEnergy(survivalStats.ToolEnergyCost);
        }

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
