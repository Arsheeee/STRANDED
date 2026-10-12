using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

/// <summary>
/// Authoritative controller for the Escape Boat construction site at the northeastern cove in STRANDED.
/// Tracks modular component requirements, sequential stage validation, visual sprite progression,
/// atomic component installation from inventory, and objective progression triggers.
/// </summary>
[RequireComponent(typeof(SpriteRenderer))]
[RequireComponent(typeof(Collider2D))]
public class BoatConstructionSite : MonoBehaviour
{
    private static BoatConstructionSite instance;
    public static BoatConstructionSite Instance => instance;

    [Header("Site Identity")]
    [Tooltip("Friendly display name of the construction site.")]
    [SerializeField] private string siteDisplayName = "Escape Boat Slipway";

    [Tooltip("Interaction distance from the player to the boat site.")]
    [SerializeField] private float interactionRadius = 3.2f;

    [Tooltip("Discovery proximity trigger distance.")]
    [SerializeField] private float discoveryRadius = 7.0f;

    [Header("Construction State")]
    [SerializeField] private BoatConstructionState currentState = BoatConstructionState.NotStarted;
    [SerializeField] private int currentStageIndex = 0;
    [SerializeField] private bool isDiscovered = false;

    [Header("Component Requirements")]
    [SerializeField] private List<BoatComponentRequirement> requirements = new List<BoatComponentRequirement>();

    [Header("Visual Stage Sprites")]
    [SerializeField] private Sprite[] stageSprites;

    private SpriteRenderer spriteRenderer;
    private Collider2D siteCollider;
    private Vector3 initialScale;
    private Coroutine bounceRoutine;

    // Public Events
    public event Action<bool> OnDiscoveryChanged;
    public event Action<BoatComponentRequirement, int, int> OnComponentInstalled;
    public event Action OnConstructionCompleted;
    public event Action OnStateChanged;

    // Properties
    public string SiteDisplayName => siteDisplayName;
    public float InteractionRadius => interactionRadius;
    public float DiscoveryRadius => discoveryRadius;
    public BoatConstructionState CurrentState => currentState;
    public int CurrentStageIndex => currentStageIndex;
    public int TotalStages => requirements != null ? requirements.Count : 5;
    public bool IsDiscovered => isDiscovered;
    public bool IsComplete => currentState == BoatConstructionState.Completed;
    public float ProgressNormalized => TotalStages > 0 ? (float)currentStageIndex / TotalStages : 0f;
    public IReadOnlyList<BoatComponentRequirement> Requirements => requirements;

    void Awake()
    {
        if (instance != null && instance != this)
        {
            Destroy(gameObject);
            return;
        }
        instance = this;

        spriteRenderer = GetComponent<SpriteRenderer>();
        siteCollider = GetComponent<Collider2D>();
        initialScale = transform.localScale;

        InitializeRequirements();
        LoadStageSprites();
        UpdateVisuals();
        UpdateSortingOrder();
    }

    void OnDestroy()
    {
        if (instance == this) instance = null;
    }

    /// <summary>
    /// Initializes default 5-stage boat requirements if not already configured in inspector.
    /// </summary>
    public void InitializeRequirements()
    {
        if (requirements == null || requirements.Count == 0)
        {
            requirements = new List<BoatComponentRequirement>
            {
                new BoatComponentRequirement("reinforced_hull", "Reinforced Hull", 1, 0,
                    "Carved buoyant wooden outrigger hull forming the ship's foundation."),
                new BoatComponentRequirement("structural_frame", "Structural Frame", 1, 1,
                    "Rigid timber keel stringers and internal rib supports."),
                new BoatComponentRequirement("rope_binding_kit", "Rope Binding Kit", 1, 2,
                    "Prepared nautical lashings and loops securing all timber framing joints."),
                new BoatComponentRequirement("paddle", "Paddle", 1, 3,
                    "Hand-carved balanced wooden canoe paddle stowed aboard."),
                new BoatComponentRequirement("wind_assembly", "Wind-Catching Assembly", 1, 4,
                    "Rigged spar yardarm and durable woven triangular canvas sail.")
            };
        }
    }

    /// <summary>
    /// Loads the 6 stage pixel-art sprites from Assets/Art/Environment/Boat/
    /// </summary>
    private void LoadStageSprites()
    {
        if (stageSprites != null && stageSprites.Length >= 6 && stageSprites[0] != null) return;

        stageSprites = new Sprite[6];
        string[] fileNames = new string[]
        {
            "boat_stage_0_slipway.png",
            "boat_stage_1_hull.png",
            "boat_stage_2_frame.png",
            "boat_stage_3_bindings.png",
            "boat_stage_4_paddle.png",
            "boat_stage_5_completed.png"
        };

        for (int i = 0; i < fileNames.Length; i++)
        {
            stageSprites[i] = LoadSpriteAsset($"Assets/Art/Environment/Boat/{fileNames[i]}");
        }
    }

    private Sprite LoadSpriteAsset(string path)
    {
#if UNITY_EDITOR
        Sprite s = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(path);
        if (s != null) return s;
#endif
        if (File.Exists(path))
        {
            try
            {
                byte[] bytes = File.ReadAllBytes(path);
                Texture2D tex = new Texture2D(32, 32, TextureFormat.RGBA32, false);
                tex.filterMode = FilterMode.Point;
                if (tex.LoadImage(bytes))
                {
                    return Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height), new Vector2(0.5f, 0.5f), 16f);
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[BoatConstructionSite] Failed to load sprite {path}: {ex.Message}");
            }
        }
        return null;
    }

    /// <summary>
    /// Updates the sprite renderer to reflect current construction progression.
    /// </summary>
    public void UpdateVisuals()
    {
        if (spriteRenderer == null) spriteRenderer = GetComponent<SpriteRenderer>();
        if (stageSprites == null || stageSprites.Length == 0) LoadStageSprites();

        int spriteIndex = Mathf.Clamp(currentStageIndex, 0, stageSprites.Length - 1);
        if (stageSprites != null && spriteIndex < stageSprites.Length && stageSprites[spriteIndex] != null)
        {
            spriteRenderer.sprite = stageSprites[spriteIndex];
        }
    }

    public void UpdateSortingOrder()
    {
        if (spriteRenderer == null) spriteRenderer = GetComponent<SpriteRenderer>();
        if (spriteRenderer != null)
        {
            spriteRenderer.sortingOrder = ResourceNode.BASE_SORTING_ORDER + Mathf.RoundToInt(-transform.position.y * 10f);
        }
    }

    /// <summary>
    /// Checks player proximity to trigger discovery when the escape cove is first approached.
    /// </summary>
    public void CheckDiscovery(Vector2 playerPosition)
    {
        if (isDiscovered) return;

        float distSq = ((Vector2)transform.position - playerPosition).sqrMagnitude;
        if (distSq <= discoveryRadius * discoveryRadius)
        {
            MarkDiscovered();
        }
    }

    public void MarkDiscovered()
    {
        if (isDiscovered) return;
        isDiscovered = true;

        TemporaryResourceHUD.Instance?.ShowNotification("Discovered Northeastern Escape Cove!", new Color(0.95f, 0.85f, 0.45f));
        Debug.Log("[STRANDED Boat] Player discovered the Escape Cove boat slipway!");

        OnDiscoveryChanged?.Invoke(true);
        OnStateChanged?.Invoke();
    }

    /// <summary>
    /// Gets the requirement definition for a specific stage index (0..4).
    /// </summary>
    public BoatComponentRequirement GetRequirement(int stage)
    {
        if (stage < 0 || stage >= requirements.Count) return null;
        return requirements[stage];
    }

    /// <summary>
    /// Gets the requirement currently needed to advance to the next construction stage.
    /// Returns null if construction is complete.
    /// </summary>
    public BoatComponentRequirement GetCurrentRequirement()
    {
        if (IsComplete || currentStageIndex >= requirements.Count) return null;
        return requirements[currentStageIndex];
    }

    /// <summary>
    /// Validates whether the next component can be installed from player's inventory.
    /// </summary>
    public bool CanInstallNext(Inventory inventory, out string failReason)
    {
        failReason = string.Empty;

        if (IsComplete)
        {
            failReason = "Boat construction is already complete.";
            return false;
        }

        if (inventory == null)
        {
            failReason = "No inventory available.";
            return false;
        }

        var req = GetCurrentRequirement();
        if (req == null)
        {
            failReason = "No further requirements.";
            return false;
        }

        ItemData item = ItemDatabase.GetItemById(req.ComponentItemId);
        if (item == null)
        {
            failReason = $"Component item '{req.ComponentItemId}' not found in database.";
            return false;
        }

        int count = inventory.GetItemCount(item);
        if (count < req.RequiredQuantity)
        {
            failReason = $"Missing {req.DisplayName} ({count}/{req.RequiredQuantity}).";
            return false;
        }

        return true;
    }

    /// <summary>
    /// Executes atomic component installation:
    /// Validates -> consumes inventory item -> advances stage -> updates visuals -> triggers notifications.
    /// Returns true on success; zero items consumed on failure.
    /// </summary>
    public bool InstallNext(Inventory inventory, out string message)
    {
        if (!CanInstallNext(inventory, out string failReason))
        {
            message = failReason;
            TemporaryResourceHUD.Instance?.ShowNotification(failReason, new Color(1.0f, 0.35f, 0.35f));
            AudioManager.Instance?.PlayCraftFail();
            return false;
        }

        var req = GetCurrentRequirement();
        ItemData item = ItemDatabase.GetItemById(req.ComponentItemId);

        // Deduct component from inventory
        inventory.RemoveItem(item, req.RequiredQuantity);

        // Advance stage
        currentStageIndex++;
        currentState = (BoatConstructionState)Mathf.Clamp(currentStageIndex, 0, (int)BoatConstructionState.Completed);

        // Update visuals & tactile bounce
        UpdateVisuals();
        TriggerBounceEffect();

        if (IsComplete)
        {
            message = "Escape Boat Completed! The vessel is seaworthy and ready for voyage.";
            TemporaryResourceHUD.Instance?.ShowNotification(message, new Color(0.35f, 1.0f, 0.55f));
            AudioManager.Instance?.PlayVictory();
            Debug.Log("[STRANDED Boat] Escape boat construction fully completed!");

            OnConstructionCompleted?.Invoke();
        }
        else
        {
            message = $"Installed {req.DisplayName}! Stage {currentStageIndex}/{TotalStages} complete.";
            TemporaryResourceHUD.Instance?.ShowNotification(message, new Color(0.40f, 0.90f, 1.0f));
            AudioManager.Instance?.PlayBoatBuild();
            Debug.Log($"[STRANDED Boat] {message}");
        }

        OnComponentInstalled?.Invoke(req, currentStageIndex, TotalStages);
        OnStateChanged?.Invoke();
        return true;
    }

    private void TriggerBounceEffect()
    {
        if (gameObject.activeInHierarchy)
        {
            if (bounceRoutine != null) StopCoroutine(bounceRoutine);
            bounceRoutine = StartCoroutine(BounceRoutine());
        }
    }

    private IEnumerator BounceRoutine()
    {
        Vector3 punch = initialScale * 1.10f;
        float elapsed = 0f;
        float duration = 0.08f;
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            transform.localScale = Vector3.Lerp(initialScale, punch, elapsed / duration);
            yield return null;
        }
        elapsed = 0f;
        duration = 0.12f;
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            transform.localScale = Vector3.Lerp(punch, initialScale, elapsed / duration);
            yield return null;
        }
        transform.localScale = initialScale;
    }

    /// <summary>
    /// Interacts with the construction site, opening the Boat Construction UI.
    /// </summary>
    public void Interact(PlayerInteraction player)
    {
        if (!isDiscovered) MarkDiscovered();

        var ui = FindAnyObjectByType<BoatConstructionUI>();
        if (ui == null && player != null)
        {
            ui = player.gameObject.AddComponent<BoatConstructionUI>();
        }

        if (ui != null)
        {
            ui.OpenUI(this);
        }
    }

    /// <summary>
    /// Attempts to launch the completed escape boat.
    /// Validates all 5 stages are complete before initiating the departure sequence.
    /// Displays a clear notification and logs warning if construction is incomplete.
    /// </summary>
    public bool TryLaunch(PlayerInteraction player, out string failReason)
    {
        if (!IsComplete)
        {
            var req = GetCurrentRequirement();
            string missingPart = req != null ? req.DisplayName : "required components";
            failReason = $"Boat construction is incomplete! Stage {currentStageIndex}/{TotalStages} complete. Needs {missingPart}.";
            TemporaryResourceHUD.Instance?.ShowNotification("Cannot launch: Boat construction is incomplete!", new Color(1.0f, 0.35f, 0.35f));
            AudioManager.Instance?.PlayCraftFail();
            Debug.LogWarning($"[STRANDED Boat] Launch rejected: {failReason}");
            return false;
        }

        failReason = string.Empty;
        var ending = EscapeEndingController.EnsureExists();
        return ending.TriggerLaunchSequence(this, player);
    }

    /// <summary>
    /// Public helper to launch the boat, triggering validation and departure sequence.
    /// </summary>
    public bool LaunchBoat(PlayerInteraction player = null)
    {
        return TryLaunch(player, out _);
    }

    /// <summary>
    /// Restores boat construction stage, state, and discovery status.
    /// </summary>
    public void RestoreConstructionProgress(int stageIndex, bool discovered)
    {
        InitializeRequirements();
        currentStageIndex = Mathf.Clamp(stageIndex, 0, TotalStages);
        currentState = (BoatConstructionState)Mathf.Clamp(currentStageIndex, 0, (int)BoatConstructionState.Completed);
        isDiscovered = discovered;
        UpdateVisuals();
        UpdateSortingOrder();
        OnStateChanged?.Invoke();
    }

    /// <summary>
    /// Returns the item IDs of all components installed so far.
    /// </summary>
    public List<string> GetInstalledComponentIds()
    {
        var installed = new List<string>();
        if (requirements != null)
        {
            for (int i = 0; i < currentStageIndex && i < requirements.Count; i++)
            {
                if (requirements[i] != null && !string.IsNullOrEmpty(requirements[i].ComponentItemId))
                {
                    installed.Add(requirements[i].ComponentItemId);
                }
            }
        }
        return installed;
    }

#if UNITY_EDITOR || DEVELOPMENT_BUILD
    /// <summary>
    /// Developer test helper to instantly assemble all boat components for verification.
    /// </summary>
    public void DeveloperCompleteBoat()
    {
        currentStageIndex = TotalStages;
        currentState = BoatConstructionState.Completed;
        UpdateVisuals();
        Debug.Log("[STRANDED Boat] Developer shortcut: Boat completed to Stage 5/5!");
    }
#endif


    /// <summary>
    /// Static helper ensuring the designated Escape Cove boat construction site exists in the world.
    /// Defaults to coordinate (276.5, 265.5, 0) on the northeastern sandy shoreline.
    /// </summary>
    public static BoatConstructionSite EnsureDefaultSiteExists()
    {
        if (instance != null) return instance;

        var existing = FindAnyObjectByType<BoatConstructionSite>();
        if (existing != null)
        {
            instance = existing;
            return existing;
        }

        GameObject envRoot = GameObject.Find("Environment_Resources");
        GameObject siteGo = new GameObject("Boat_Construction_Site");
        siteGo.transform.position = new Vector3(276.5f, 265.5f, 0f);
        if (envRoot != null) siteGo.transform.SetParent(envRoot.transform);

        BoxCollider2D boxCol = siteGo.AddComponent<BoxCollider2D>();
        boxCol.isTrigger = true;
        boxCol.size = new Vector2(2.5f, 2.0f);

        SpriteRenderer sr = siteGo.AddComponent<SpriteRenderer>();

        BoatConstructionSite site = siteGo.AddComponent<BoatConstructionSite>();
        site.UpdateVisuals();
        site.UpdateSortingOrder();

        Debug.Log("[STRANDED Boat] Created default Boat Construction Site at Northeastern Cove (276.5, 265.5).");
        return site;
    }

#if UNITY_EDITOR
    private void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(transform.position, interactionRadius);
        Gizmos.color = new Color(0.2f, 0.8f, 1f, 0.4f);
        Gizmos.DrawWireSphere(transform.position, discoveryRadius);
    }
#endif
}
