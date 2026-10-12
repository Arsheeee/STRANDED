using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

/// <summary>
/// Reusable fishing spot component for STRANDED (Batch 7).
/// Manages fishing location interactions, animated water ripple / bobber visuals,
/// bite timers, reaction window reels, reward payouts, and safety cancellations.
/// </summary>
public class FishingSpot : MonoBehaviour
{
    public enum FishingState
    {
        Idle,
        WaitingForBite,
        BiteAlert,
        Cooldown
    }

    public static readonly List<FishingSpot> AllSpots = new List<FishingSpot>();

    [Header("Spot Identity")]
    [Tooltip("Friendly display name for this fishing location.")]
    [SerializeField] private string spotName = "Fishing Spot";

    [Tooltip("Maximum distance from player to spot to interact.")]
    [SerializeField] private float interactionRadius = 2.2f;

    [Header("Fishing Timing Settings")]
    [Tooltip("Minimum wait duration before a fish bites (seconds).")]
    [SerializeField] private float minWaitTime = 2.0f;

    [Tooltip("Maximum wait duration before a fish bites (seconds).")]
    [SerializeField] private float maxWaitTime = 4.5f;

    [Tooltip("Time window in seconds during which the player must press E to reel in.")]
    [SerializeField] private float reactionWindow = 1.6f;

    [Tooltip("Probability of successfully catching a fish on timely reaction (0.0 to 1.0).")]
    [Range(0.5f, 1.0f)]
    [SerializeField] private float catchSuccessChance = 0.95f;

    [Tooltip("Brief cooldown duration after fishing before the spot can be used again.")]
    [SerializeField] private float cooldownDuration = 1.2f;

    [Header("Visual Components")]
    [SerializeField] private SpriteRenderer rippleRenderer;
    [SerializeField] private SpriteRenderer bobberRenderer;
    [SerializeField] private SpriteRenderer alertRenderer;

    // Runtime State
    private FishingState currentState = FishingState.Idle;
    private float stateTimer = 0f;
    private float cooldownTimer = 0f;
    private bool rewardGivenThisAttempt = false;
    private PlayerInteraction activePlayer;
    private Vector3 initialBobberLocalPos;
    private Vector3 initialAlertLocalPos;

    // Public Accessors
    public string SpotName => spotName;
    public float InteractionRadius => interactionRadius;
    public FishingState CurrentState => currentState;
    public float RemainingReactionTime => currentState == FishingState.BiteAlert ? Mathf.Max(0f, stateTimer) : 0f;
    public bool IsBusy => currentState != FishingState.Idle;
    public PlayerInteraction ActivePlayer => activePlayer;

    void OnEnable()
    {
        if (!AllSpots.Contains(this))
        {
            AllSpots.Add(this);
        }
    }

    void OnDisable()
    {
        AllSpots.Remove(this);
        if (activePlayer != null)
        {
            CancelFishing(string.Empty);
        }
    }

    void Awake()
    {
        EnsureVisualComponents();
    }

    void Start()
    {
        SetVisualsState(FishingState.Idle);
    }

    /// <summary>
    /// Configures or dynamically creates child SpriteRenderers for ripple, bobber, and alert.
    /// </summary>
    public void EnsureVisualComponents()
    {
        // 1. Water Ripple Visual
        if (rippleRenderer == null)
        {
            Transform tRipple = transform.Find("Visual_Ripple");
            if (tRipple == null)
            {
                GameObject obj = new GameObject("Visual_Ripple");
                obj.transform.SetParent(transform, false);
                tRipple = obj.transform;
            }
            rippleRenderer = tRipple.GetComponent<SpriteRenderer>();
            if (rippleRenderer == null) rippleRenderer = tRipple.gameObject.AddComponent<SpriteRenderer>();

            Sprite rippleSprite = LoadSpriteAsset("fishing_ripple.png");
            if (rippleSprite != null) rippleRenderer.sprite = rippleSprite;
            rippleRenderer.sortingOrder = 16; // Just above water tilemaps
        }

        // 2. Bobber Float Visual
        if (bobberRenderer == null)
        {
            Transform tBobber = transform.Find("Visual_Bobber");
            if (tBobber == null)
            {
                GameObject obj = new GameObject("Visual_Bobber");
                obj.transform.SetParent(transform, false);
                tBobber = obj.transform;
            }
            bobberRenderer = tBobber.GetComponent<SpriteRenderer>();
            if (bobberRenderer == null) bobberRenderer = tBobber.gameObject.AddComponent<SpriteRenderer>();

            Sprite bobberSprite = LoadSpriteAsset("fishing_bobber.png");
            if (bobberSprite != null) bobberRenderer.sprite = bobberSprite;
            bobberRenderer.sortingOrder = 25; // Above ripple
        }

        // 3. Alert '!' Visual
        if (alertRenderer == null)
        {
            Transform tAlert = transform.Find("Visual_Alert");
            if (tAlert == null)
            {
                GameObject obj = new GameObject("Visual_Alert");
                obj.transform.SetParent(transform, false);
                tAlert = obj.transform;
            }
            alertRenderer = tAlert.GetComponent<SpriteRenderer>();
            if (alertRenderer == null) alertRenderer = tAlert.gameObject.AddComponent<SpriteRenderer>();

            Sprite alertSprite = LoadSpriteAsset("fishing_alert.png");
            if (alertSprite != null) alertRenderer.sprite = alertSprite;
            alertRenderer.sortingOrder = 30; // Above bobber
            alertRenderer.transform.localPosition = new Vector3(0f, 0.45f, 0f);
        }

        if (bobberRenderer != null) initialBobberLocalPos = bobberRenderer.transform.localPosition;
        if (alertRenderer != null) initialAlertLocalPos = alertRenderer.transform.localPosition;
    }

    private Sprite LoadSpriteAsset(string fileName)
    {
        string relativePath = $"Assets/Art/Environment/Items/{fileName}";
#if UNITY_EDITOR
        Sprite s = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(relativePath);
        if (s != null) return s;
#endif
        if (File.Exists(relativePath))
        {
            try
            {
                byte[] bytes = File.ReadAllBytes(relativePath);
                Texture2D tex = new Texture2D(16, 16, TextureFormat.RGBA32, false);
                tex.filterMode = FilterMode.Point;
                if (tex.LoadImage(bytes))
                {
                    return Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height), new Vector2(0.5f, 0.5f), 16f);
                }
            }
            catch (Exception) { }
        }
        return null;
    }

    void Update()
    {
        // 1. Ambient ripple animation
        if (rippleRenderer != null)
        {
            float pulse = 1.0f + 0.12f * Mathf.Sin(Time.time * 2.2f);
            rippleRenderer.transform.localScale = new Vector3(pulse, pulse * 0.85f, 1f);
        }

        // 2. State Machine Handling
        switch (currentState)
        {
            case FishingState.Idle:
                // Nothing pending
                break;

            case FishingState.WaitingForBite:
                UpdateWaitingForBite();
                break;

            case FishingState.BiteAlert:
                UpdateBiteAlert();
                break;

            case FishingState.Cooldown:
                cooldownTimer -= Time.deltaTime;
                if (cooldownTimer <= 0f)
                {
                    currentState = FishingState.Idle;
                    SetVisualsState(FishingState.Idle);
                }
                break;
        }
    }

    private void UpdateWaitingForBite()
    {
        // Safety cancel checks
        if (activePlayer == null || !IsPlayerWithinRange(activePlayer))
        {
            CancelFishing("Moved away from fishing spot.");
            return;
        }

        if (InventoryUI.IsOpen || CraftingUI.IsOpen)
        {
            CancelFishing("Fishing cancelled.");
            return;
        }

        if (activePlayer.CurrentTool != ToolType.FishingRod)
        {
            CancelFishing("Unequipped Fishing Rod.");
            return;
        }

        // Bobber floats gently
        if (bobberRenderer != null)
        {
            float bob = Mathf.Sin(Time.time * 3.5f) * 0.04f;
            bobberRenderer.transform.localPosition = initialBobberLocalPos + new Vector3(0f, bob, 0f);
        }

        stateTimer -= Time.deltaTime;
        if (stateTimer <= 0f)
        {
            // Transition to Bite!
            TriggerBiteAlert();
        }
    }

    private void UpdateBiteAlert()
    {
        // Safety cancel checks
        if (activePlayer == null || !IsPlayerWithinRange(activePlayer))
        {
            CancelFishing("Moved away from fishing spot.");
            return;
        }

        if (InventoryUI.IsOpen || CraftingUI.IsOpen)
        {
            CancelFishing("Fishing cancelled.");
            return;
        }

        // Bobber tugs vigorously down into the water
        if (bobberRenderer != null)
        {
            float violentBob = -0.08f + Mathf.Sin(Time.time * 18f) * 0.08f;
            bobberRenderer.transform.localPosition = initialBobberLocalPos + new Vector3(0f, violentBob, 0f);
        }

        // Alert bounces excitedly
        if (alertRenderer != null)
        {
            float bounce = 1.0f + 0.25f * Mathf.Abs(Mathf.Sin(Time.time * 12f));
            alertRenderer.transform.localScale = new Vector3(bounce, bounce, 1f);
        }

        stateTimer -= Time.deltaTime;
        if (stateTimer <= 0f)
        {
            // Reaction window expired without player reeling in!
            FailCatch("The fish got away!");
        }
    }

    private void TriggerBiteAlert()
    {
        currentState = FishingState.BiteAlert;
        stateTimer = reactionWindow;

        SetVisualsState(FishingState.BiteAlert);

        TemporaryResourceHUD.Instance?.ShowNotification("! FISH ON THE LINE! Press [E] to Reel In!", new Color(1.0f, 0.85f, 0.2f));
        AudioManager.Instance?.PlayFishBite();
        Debug.Log($"[STRANDED Fishing] Fish biting at '{spotName}'! Reaction window: {reactionWindow:F1}s");
    }

    /// <summary>
    /// Checks whether player can initiate fishing at this spot.
    /// </summary>
    public bool CanStartFishing(PlayerInteraction player, out string reason)
    {
        reason = string.Empty;

        if (player == null)
        {
            reason = "No player available.";
            return false;
        }

        if (player.Survival != null && player.Survival.IsDead)
        {
            reason = "Cannot fish while dead.";
            return false;
        }

        if (currentState != FishingState.Idle)
        {
            reason = "Fishing spot is currently busy.";
            return false;
        }

        if (!IsPlayerWithinRange(player))
        {
            reason = "Too far from fishing spot.";
            return false;
        }

        if (player.CurrentTool != ToolType.FishingRod)
        {
            reason = "Requires Fishing Rod to fish.";
            return false;
        }

        if (player.Survival != null && player.Survival.CurrentEnergy < player.Survival.ToolEnergyCost)
        {
            reason = "Too exhausted to fish.";
            return false;
        }

        return true;
    }

    /// <summary>
    /// Begins a fishing session for the player.
    /// </summary>
    public bool StartFishing(PlayerInteraction player)
    {
        if (!CanStartFishing(player, out string reason))
        {
            if (!string.IsNullOrEmpty(reason))
            {
                TemporaryResourceHUD.ShowRequirementFeedback(reason);
            }
            return false;
        }

        activePlayer = player;
        player.SetActiveFishingSpot(this);
        rewardGivenThisAttempt = false;

        currentState = FishingState.WaitingForBite;
        stateTimer = UnityEngine.Random.Range(minWaitTime, maxWaitTime);

        SetVisualsState(FishingState.WaitingForBite);

        TemporaryResourceHUD.Instance?.ShowNotification("Cast line... waiting for a bite.", new Color(0.4f, 0.85f, 1.0f));
        Debug.Log($"[STRANDED Fishing] Started fishing at '{spotName}'. Bite in {stateTimer:F2}s");
        return true;
    }

    /// <summary>
    /// Handles 'E' press from the player while fishing is active.
    /// </summary>
    public void OnInteractPressed(PlayerInteraction player)
    {
        if (player != activePlayer) return;

        if (currentState == FishingState.WaitingForBite)
        {
            // Reeled in too early before the fish bit
            CancelFishing("Reeled in too early! The fish wasn't biting yet.");
        }
        else if (currentState == FishingState.BiteAlert)
        {
            // Reaction during valid bite window
            AttemptReelIn();
        }
    }

    private void AttemptReelIn()
    {
        if (rewardGivenThisAttempt) return; // Guard against multi-reward spam

        // Success probability check
        bool catchSuccess = (UnityEngine.Random.value <= catchSuccessChance);

        if (!catchSuccess)
        {
            FailCatch("The hook slipped! The fish got away.");
            return;
        }

        // Resolve Raw Fish reward
        ItemData fishItem = ItemDatabase.GetResourceItem(ResourceType.Fish);
        if (fishItem == null) fishItem = ItemDatabase.GetItemById("fish");

        if (fishItem == null)
        {
            Debug.LogError("[STRANDED Fishing] Raw Fish ItemData not found in ItemDatabase!");
            FailCatch("Failed to resolve fish item.");
            return;
        }

        Inventory inv = activePlayer.Inventory;
        if (inv == null || !inv.CanAddItem(fishItem, 1))
        {
            // Inventory full safeguard
            TemporaryResourceHUD.Instance?.ShowNotification("Inventory full! Cannot carry fish.", new Color(1.0f, 0.40f, 0.35f));
            FinishAttempt(false);
            return;
        }

        // Successfully add Raw Fish
        rewardGivenThisAttempt = true;
        inv.AddItem(fishItem, 1);

        // Deduct energy if survival system active
        if (activePlayer.Survival != null)
        {
            activePlayer.Survival.ConsumeEnergy(activePlayer.Survival.ToolEnergyCost);
        }

        activePlayer.TriggerToolAction(ToolType.FishingRod);

        TemporaryResourceHUD.Instance?.ShowNotification("Caught Raw Fish!", new Color(0.35f, 0.95f, 0.45f));
        AudioManager.Instance?.PlayFishCatch();
        AudioManager.Instance?.PlayItemCollect();
        Debug.Log($"[STRANDED Fishing] Player successfully caught Raw Fish at '{spotName}'!");

        FinishAttempt(true);
    }

    private void FailCatch(string message)
    {
        TemporaryResourceHUD.Instance?.ShowNotification(message, new Color(0.9f, 0.55f, 0.45f));
        AudioManager.Instance?.PlayCraftFail();
        FinishAttempt(false);
    }

    private void FinishAttempt(bool success)
    {
        currentState = FishingState.Cooldown;
        cooldownTimer = cooldownDuration;

        SetVisualsState(FishingState.Cooldown);

        if (activePlayer != null)
        {
            activePlayer.ClearActiveFishingSpot(this);
            activePlayer = null;
        }
    }

    /// <summary>
    /// Cancels current fishing attempt (e.g. by moving away or closing menus).
    /// </summary>
    public void CancelFishing(string message)
    {
        if (currentState == FishingState.WaitingForBite || currentState == FishingState.BiteAlert)
        {
            if (!string.IsNullOrEmpty(message))
            {
                TemporaryResourceHUD.Instance?.ShowNotification(message, new Color(0.75f, 0.75f, 0.75f));
            }

            currentState = FishingState.Idle;
            SetVisualsState(FishingState.Idle);

            if (activePlayer != null)
            {
                activePlayer.ClearActiveFishingSpot(this);
                activePlayer = null;
            }

            rewardGivenThisAttempt = false;
        }
    }

    private void SetVisualsState(FishingState state)
    {
        if (bobberRenderer != null)
        {
            bobberRenderer.enabled = (state == FishingState.WaitingForBite || state == FishingState.BiteAlert);
            if (bobberRenderer.enabled)
            {
                bobberRenderer.transform.localPosition = initialBobberLocalPos;
            }
        }

        if (alertRenderer != null)
        {
            alertRenderer.enabled = (state == FishingState.BiteAlert);
            if (alertRenderer.enabled)
            {
                alertRenderer.transform.localPosition = initialAlertLocalPos;
                alertRenderer.transform.localScale = Vector3.one;
            }
        }
    }

    public bool IsPlayerWithinRange(PlayerInteraction player)
    {
        if (player == null) return false;
        float distSq = ((Vector2)player.transform.position - (Vector2)transform.position).sqrMagnitude;
        return distSq <= interactionRadius * interactionRadius;
    }

    /// <summary>
    /// Configure timing parameters programmatically for automated testing or tuning.
    /// </summary>
    public void SetParameters(float minWait, float maxWait, float window, float successRate)
    {
        minWaitTime = minWait;
        maxWaitTime = maxWait;
        reactionWindow = window;
        catchSuccessChance = successRate;
    }

    /// <summary>
    /// Set spot name and radius programmatically.
    /// </summary>
    public void SetIdentity(string name, float radius)
    {
        spotName = name;
        interactionRadius = radius;
    }

    /// <summary>
    /// Ensures designated river and coastal fishing spots exist in the scene.
    /// </summary>
    public static void EnsureDefaultFishingSpotsExist()
    {
        if (AllSpots.Count > 0) return;

        GameObject root = GameObject.Find("FishingSpots");
        if (root == null)
        {
            GameObject env = GameObject.Find("Environment_Resources");
            root = new GameObject("FishingSpots");
            if (env != null) root.transform.SetParent(env.transform);
        }

        // 4 Designated Riverbank Spots
        CreateSpot(root, "West Riverbank Fishing Spot", new Vector2(175.5f, 137.5f));
        CreateSpot(root, "Central Riverbend Fishing Spot", new Vector2(195.5f, 124.5f));
        CreateSpot(root, "South Estuary Fishing Spot", new Vector2(189.5f, 75.5f));
        CreateSpot(root, "North River Rapids Fishing Spot", new Vector2(212.5f, 207.5f));

        // 4 Designated Coastal Shoreline Spots
        CreateSpot(root, "South Beach Fishing Spot", new Vector2(116.5f, 85.5f));
        CreateSpot(root, "West Shoreline Fishing Spot", new Vector2(82.5f, 110.5f));
        CreateSpot(root, "East Shoreline Fishing Spot", new Vector2(278.5f, 121.5f));
        CreateSpot(root, "South Ocean Reef Fishing Spot", new Vector2(172.5f, 62.5f));

        Debug.Log($"[STRANDED Fishing] Initialized {AllSpots.Count} default fishing spots.");
    }

    public static FishingSpot CreateSpot(GameObject parent, string name, Vector2 pos)
    {
        GameObject go = new GameObject(name.Replace(" ", "_"));
        go.transform.position = new Vector3(pos.x, pos.y, 0f);
        if (parent != null) go.transform.SetParent(parent.transform);

        FishingSpot spot = go.AddComponent<FishingSpot>();
        spot.spotName = name;
        spot.interactionRadius = 2.2f;
        spot.EnsureVisualComponents();
        return spot;
    }

#if UNITY_EDITOR
    private void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.cyan;
        Gizmos.DrawWireSphere(transform.position, interactionRadius);
    }
#endif
}
