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

    private InputAction interactAction;
    private SpriteRenderer playerRenderer;
    private ResourceNode currentTargetNode;
    private readonly Collider2D[] queryResults = new Collider2D[16];

    void Start()
    {
        playerRenderer = GetComponent<SpriteRenderer>();

        // Setup E key interaction action with New Input System
        interactAction = new InputAction("Interact", binding: "<Keyboard>/e");
        interactAction.AddBinding("<Gamepad>/buttonSouth"); // Gamepad 'A' / Cross
        interactAction.Enable();

        // Ensure TemporaryResourceHUD is present in the scene
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
        // 1. Efficient local query for closest available ResourceNode
        UpdateNearbyInteractable();

        // 2. Check for interaction input ('E')
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

        // Update HUD prompt
        if (TemporaryResourceHUD.Instance != null)
        {
            if (currentTargetNode != null)
            {
                TemporaryResourceHUD.Instance.SetInteractionPrompt($"[E] Gather {currentTargetNode.DisplayName}");
            }
            else
            {
                TemporaryResourceHUD.Instance.SetInteractionPrompt("");
            }
        }
    }

    /// <summary>
    /// Triggers harvest on the current target node and records collected yield.
    /// </summary>
    private void HarvestCurrentTarget()
    {
        if (currentTargetNode == null) return;

        ResourceNode nodeToHarvest = currentTargetNode;
        int yielded = nodeToHarvest.Interact(this);

        if (yielded > 0)
        {
            TemporaryResourceHUD.RecordCollection(nodeToHarvest.Type, yielded, nodeToHarvest.DisplayName);
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
