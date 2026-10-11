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

        // Initialize sprite if available
        if (availableSprite != null && spriteRenderer.sprite == null)
        {
            spriteRenderer.sprite = availableSprite;
        }

        // Apply 2D Y-depth sorting so objects naturally layer based on ground position
        UpdateSortingOrder();
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
    /// Harvests the resource from this node.
    /// Returns the yielded amount (or 0 if unavailable).
    /// </summary>
    public int Interact(PlayerInteraction player)
    {
        if (!CanInteract())
        {
            return 0;
        }

        int collected = yieldAmount;

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

#if UNITY_EDITOR
    private void OnDrawGizmosSelected()
    {
        // Visualize interaction range in editor
        Gizmos.color = Color.green;
        Gizmos.DrawWireSphere(transform.position, interactionRange);
    }
#endif
}
