using System;
using UnityEngine;

/// <summary>
/// Objective progression states for the escape storyline in STRANDED.
/// </summary>
public enum IslandObjective
{
    ExploreIsland = 0,         // Objective 1: Discover the northeastern escape cove
    PrepareConstruction = 1,   // Objective 2: Craft required boat components via hierarchical crafting
    BuildTheBoat = 2,          // Objective 3: Install components sequentially at the slipway
    CompleteConstruction = 3,  // Objective 4: All 5 components installed; vessel structurally complete
    PrepareToEscape = 4        // Objective 5: Inspect completed seaworthy vessel; ready for future launch
}

/// <summary>
/// Authoritative objective controller for STRANDED (Batch 9).
/// Tracks player progression from island exploration to boat manufacturing, assembly, and readiness.
/// Coordinates events between BoatConstructionSite, Inventory, and UI notifications without duplicates.
/// </summary>
public class ObjectiveManager : MonoBehaviour
{
    private static ObjectiveManager instance;
    public static ObjectiveManager Instance => instance;

    [Header("Current Progression")]
    [SerializeField] private IslandObjective currentObjective = IslandObjective.ExploreIsland;
    [SerializeField] private bool hasDiscoveredCove = false;
    [SerializeField] private bool hasEscaped = false;

    // Events
    public event Action<IslandObjective> OnObjectiveChanged;
    public event Action<string> OnProgressUpdated;

    public IslandObjective CurrentObjective => currentObjective;
    public bool HasDiscoveredCove => hasDiscoveredCove;
    public bool HasEscaped => hasEscaped;
    public bool IsComplete => currentObjective == IslandObjective.PrepareToEscape || hasEscaped;

    public void MarkEscaped()
    {
        hasEscaped = true;
        OnProgressUpdated?.Invoke("The escape boat has set sail! You conquered the island.");
        Debug.Log("[STRANDED Objective] Narrative completed: Player has escaped the island!");
    }

    /// <summary>
    /// Restores objective progression state.
    /// </summary>
    public void RestoreObjectiveState(IslandObjective objective, bool discoveredCove, bool escaped)
    {
        hasDiscoveredCove = discoveredCove;
        hasEscaped = escaped;
        currentObjective = objective;
        OnObjectiveChanged?.Invoke(currentObjective);
        OnProgressUpdated?.Invoke(Description);
    }

    public string Title
    {
        get
        {
            if (hasEscaped) return "Escape the Island (Completed)";
            switch (currentObjective)
            {
                case IslandObjective.ExploreIsland:
                    return "Explore the Island";
                case IslandObjective.PrepareConstruction:
                    return "Prepare for Construction";
                case IslandObjective.BuildTheBoat:
                    return "Build the Escape Boat";
                case IslandObjective.CompleteConstruction:
                    return "Boat Construction Complete";
                case IslandObjective.PrepareToEscape:
                    return "Prepare to Escape";
                default:
                    return "Survive the Island";
            }
        }
    }

    public string Description
    {
        get
        {
            switch (currentObjective)
            {
                case IslandObjective.ExploreIsland:
                    return "Search the northeastern shoreline for an escape cove.";

                case IslandObjective.PrepareConstruction:
                    return "Manufacture boat components using hierarchical crafting.";

                case IslandObjective.BuildTheBoat:
                    var site = BoatConstructionSite.Instance;
                    if (site != null)
                    {
                        var req = site.GetCurrentRequirement();
                        if (req != null)
                        {
                            return $"Install {req.DisplayName} at the slipway ({site.CurrentStageIndex}/{site.TotalStages}).";
                        }
                    }
                    return "Assemble components at the northeastern slipway.";

                case IslandObjective.CompleteConstruction:
                    return "All 5 boat components have been successfully assembled.";

                case IslandObjective.PrepareToEscape:
                    return "The escape boat is seaworthy! Inspect the vessel and prepare for departure.";

                default:
                    return "Survive and find a way off the island.";
            }
        }
    }

    public string ProgressText
    {
        get
        {
            var site = BoatConstructionSite.Instance;
            if (site != null)
            {
                return $"{site.CurrentStageIndex} / {site.TotalStages} Stages";
            }
            return "0 / 5 Stages";
        }
    }

    public float ProgressNormalized
    {
        get
        {
            var site = BoatConstructionSite.Instance;
            if (site != null)
            {
                return site.ProgressNormalized;
            }
            return 0f;
        }
    }

    void Awake()
    {
        if (instance != null && instance != this)
        {
            Destroy(gameObject);
            return;
        }
        instance = this;
    }

    void Start()
    {
        SubscribeToSiteEvents();
        EvaluateObjectiveState();
    }

    void OnDestroy()
    {
        UnsubscribeFromSiteEvents();
        if (instance == this) instance = null;
    }

    private void SubscribeToSiteEvents()
    {
        var site = BoatConstructionSite.Instance;
        if (site != null)
        {
            site.OnDiscoveryChanged += HandleSiteDiscovered;
            site.OnComponentInstalled += HandleComponentInstalled;
            site.OnConstructionCompleted += HandleConstructionCompleted;
        }
    }

    private void UnsubscribeFromSiteEvents()
    {
        var site = BoatConstructionSite.Instance;
        if (site != null)
        {
            site.OnDiscoveryChanged -= HandleSiteDiscovered;
            site.OnComponentInstalled -= HandleComponentInstalled;
            site.OnConstructionCompleted -= HandleConstructionCompleted;
        }
    }

    /// <summary>
    /// Evaluates current state based on construction site status and player inventory.
    /// </summary>
    public void EvaluateObjectiveState()
    {
        var site = BoatConstructionSite.Instance;
        if (site == null) return;

        if (site.IsDiscovered)
        {
            hasDiscoveredCove = true;
        }

        if (site.IsComplete)
        {
            if (currentObjective != IslandObjective.CompleteConstruction && currentObjective != IslandObjective.PrepareToEscape)
            {
                SetObjective(IslandObjective.PrepareToEscape);
            }
            return;
        }

        if (site.CurrentStageIndex > 0)
        {
            if (currentObjective != IslandObjective.BuildTheBoat)
            {
                SetObjective(IslandObjective.BuildTheBoat);
            }
            return;
        }

        if (hasDiscoveredCove)
        {
            // If cove is discovered and not yet building, check player's inventory
            var inv = FindAnyObjectByType<Inventory>();
            bool hasFirstComponent = false;
            if (inv != null)
            {
                var req = site.GetCurrentRequirement();
                if (req != null)
                {
                    var item = ItemDatabase.GetItemById(req.ComponentItemId);
                    if (item != null && inv.GetItemCount(item) >= req.RequiredQuantity)
                    {
                        hasFirstComponent = true;
                    }
                }
            }

            if (hasFirstComponent)
            {
                if (currentObjective != IslandObjective.BuildTheBoat)
                {
                    SetObjective(IslandObjective.BuildTheBoat);
                }
            }
            else
            {
                if (currentObjective == IslandObjective.ExploreIsland)
                {
                    SetObjective(IslandObjective.PrepareConstruction);
                }
            }
        }
    }

    public void SetObjective(IslandObjective newObjective)
    {
        if (currentObjective == newObjective) return;

        currentObjective = newObjective;
        Debug.Log($"[STRANDED Objective] Objective updated to: {currentObjective} - '{Title}'");

        TemporaryResourceHUD.Instance?.ShowNotification($"New Objective: {Title}", new Color(1.0f, 0.85f, 0.40f));
        AudioManager.Instance?.PlayObjectiveUpdate();

        OnObjectiveChanged?.Invoke(currentObjective);
        OnProgressUpdated?.Invoke(Description);
    }

    private void HandleSiteDiscovered(bool discovered)
    {
        if (discovered && !hasDiscoveredCove)
        {
            hasDiscoveredCove = true;
            if (currentObjective == IslandObjective.ExploreIsland)
            {
                SetObjective(IslandObjective.PrepareConstruction);
            }
        }
    }

    private void HandleComponentInstalled(BoatComponentRequirement req, int currentStage, int totalStages)
    {
        if (currentObjective != IslandObjective.BuildTheBoat && !BoatConstructionSite.Instance.IsComplete)
        {
            SetObjective(IslandObjective.BuildTheBoat);
        }
        else
        {
            OnProgressUpdated?.Invoke(Description);
        }
    }

    private void HandleConstructionCompleted()
    {
        SetObjective(IslandObjective.CompleteConstruction);

        // Transition gracefully to PrepareToEscape
        StartCoroutine(TransitionToEscapeRoutine());
    }

    private System.Collections.IEnumerator TransitionToEscapeRoutine()
    {
        yield return new WaitForSeconds(3.0f);
        SetObjective(IslandObjective.PrepareToEscape);
    }

    /// <summary>
    /// Ensures the ObjectiveManager instance exists in the scene.
    /// </summary>
    public static ObjectiveManager EnsureExists()
    {
        if (instance != null) return instance;

        var existing = FindAnyObjectByType<ObjectiveManager>();
        if (existing != null)
        {
            instance = existing;
            return existing;
        }

        GameObject obj = new GameObject("ObjectiveManager");
        instance = obj.AddComponent<ObjectiveManager>();
        Debug.Log("[STRANDED Objective] Initialized ObjectiveManager singleton in scene.");
        return instance;
    }
}
