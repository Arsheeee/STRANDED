using System;
using UnityEngine;
using UnityEngine.InputSystem;

/// <summary>
/// Authoritative Survival Stat System for STRANDED (Batch 6).
/// Manages player Health, Hunger, Thirst, and Energy.
/// Governs gradual metabolic depletion, grace-period damage intervals, resting recovery,
/// food/drink consumption, starvation/dehydration consequences, and death/respawn state.
/// </summary>
public class SurvivalStats : MonoBehaviour
{
    private static SurvivalStats instance;
    public static SurvivalStats Instance => instance;

    [Header("Health Settings")]
    [Tooltip("Maximum player health capacity.")]
    [SerializeField] private float maxHealth = 100f;
    [SerializeField] private float currentHealth = 100f;
    [Tooltip("Health percentage threshold that triggers critical warning.")]
    [SerializeField] private float healthCriticalThreshold = 25f;

    [Header("Hunger Settings")]
    [Tooltip("Maximum player hunger capacity.")]
    [SerializeField] private float maxHunger = 100f;
    [SerializeField] private float currentHunger = 100f;
    [Tooltip("Hunger points depleted per second (default: ~1 pt / 60s).")]
    [SerializeField] private float hungerDepletionRate = 0.01667f;
    [Tooltip("Hunger threshold that triggers getting hungry warning.")]
    [SerializeField] private float hungerWarningThreshold = 20f;
    [Tooltip("Grace period in seconds after hunger hits 0 before starvation damage begins.")]
    [SerializeField] private float starvationGracePeriod = 20f;
    [Tooltip("Health damage inflicted per interval during starvation.")]
    [SerializeField] private float starvationDamage = 4f;
    [Tooltip("Interval in seconds between starvation damage ticks.")]
    [SerializeField] private float starvationDamageInterval = 5f;

    [Header("Thirst Settings")]
    [Tooltip("Maximum player thirst capacity.")]
    [SerializeField] private float maxThirst = 100f;
    [SerializeField] private float currentThirst = 100f;
    [Tooltip("Thirst points depleted per second (default: ~1 pt / 45s).")]
    [SerializeField] private float thirstDepletionRate = 0.0222f;
    [Tooltip("Thirst threshold that triggers thirsty warning.")]
    [SerializeField] private float thirstWarningThreshold = 20f;
    [Tooltip("Grace period in seconds after thirst hits 0 before dehydration damage begins.")]
    [SerializeField] private float dehydrationGracePeriod = 15f;
    [Tooltip("Health damage inflicted per interval during dehydration.")]
    [SerializeField] private float dehydrationDamage = 5f;
    [Tooltip("Interval in seconds between dehydration damage ticks.")]
    [SerializeField] private float dehydrationDamageInterval = 5f;

    [Header("Energy & Stamina Settings")]
    [Tooltip("Maximum player energy capacity.")]
    [SerializeField] private float maxEnergy = 100f;
    [SerializeField] private float currentEnergy = 100f;
    [Tooltip("Energy threshold that triggers exhaustion warning.")]
    [SerializeField] private float energyWarningThreshold = 20f;
    [Tooltip("Energy consumed per tool harvest action.")]
    [SerializeField] private float toolEnergyCost = 8f;
    [Tooltip("Energy points recovered per second while resting.")]
    [SerializeField] private float restingEnergyRate = 15f;

    [Header("State")]
    [SerializeField] private bool isDead = false;
    [SerializeField] private bool isResting = false;
    [SerializeField] private string deathCause = "";

    // Internal Timers
    private float zeroHungerTimer = 0f;
    private float starvationDamageTimer = 0f;
    private float zeroThirstTimer = 0f;
    private float dehydrationDamageTimer = 0f;

    // Warning Cooldowns to prevent spam
    private float lastHungerWarningTime = -100f;
    private float lastThirstWarningTime = -100f;
    private float lastEnergyWarningTime = -100f;
    private float lastHealthWarningTime = -100f;
    private const float WARNING_COOLDOWN = 35f;

    private Vector3 initialSpawnPosition;
    private PlayerMovement playerMovement;
    private Inventory inventory;

    // Events
    public event Action<float, float> OnHealthChanged;
    public event Action<float, float> OnHungerChanged;
    public event Action<float, float> OnThirstChanged;
    public event Action<float, float> OnEnergyChanged;
    public event Action<bool> OnRestingStateChanged;
    public event Action<string> OnPlayerDied;
    public event Action OnPlayerRespawned;

    // Public Properties
    public float CurrentHealth => currentHealth;
    public float MaxHealth => maxHealth;
    public float CurrentHunger => currentHunger;
    public float MaxHunger => maxHunger;
    public float CurrentThirst => currentThirst;
    public float MaxThirst => maxThirst;
    public float CurrentEnergy => currentEnergy;
    public float MaxEnergy => maxEnergy;
    public bool IsDead => isDead;
    public bool IsResting => isResting;
    public string DeathCause => deathCause;
    public float ToolEnergyCost => toolEnergyCost;

    void Awake()
    {
        if (instance != null && instance != this)
        {
            Destroy(this);
            return;
        }
        instance = this;

        playerMovement = GetComponent<PlayerMovement>();
        inventory = GetComponent<Inventory>();
        initialSpawnPosition = transform.position;

        currentHealth = maxHealth;
        currentHunger = maxHunger;
        currentThirst = maxThirst;
        currentEnergy = maxEnergy;
    }

    void Start()
    {
        if (playerMovement == null) playerMovement = FindAnyObjectByType<PlayerMovement>();
        if (inventory == null) inventory = FindAnyObjectByType<Inventory>();

        NotifyAllChanged();
    }

    void Update()
    {
        if (isDead) return;

        // Check if gameplay is paused by menu windows (InventoryUI, CraftingUI, BoatConstructionUI) or ending sequence
        if (InventoryUI.IsOpen || CraftingUI.IsOpen || BoatConstructionUI.IsOpen || (EscapeEndingController.Instance != null && EscapeEndingController.Instance.IsEndingActive))
        {
            // Halt metabolic depletion and resting while player organizes inventory, crafts, or views ending
            return;
        }

        // Handle Resting Input & Logic
        HandleRestingInput();

        if (isResting)
        {
            // While resting, regenerate energy and do not deplete hunger/thirst aggressively
            RestoreEnergy(restingEnergyRate * Time.deltaTime);

            if (currentEnergy >= maxEnergy)
            {
                StopResting("Energy fully restored!");
            }
        }
        else
        {
            // 1. Natural Metabolic Depletion
            ConsumeHunger(hungerDepletionRate * Time.deltaTime);
            ConsumeThirst(thirstDepletionRate * Time.deltaTime);
        }

        // 2. Starvation Grace Period & Damage Tick
        if (currentHunger <= 0f)
        {
            zeroHungerTimer += Time.deltaTime;
            if (zeroHungerTimer >= starvationGracePeriod)
            {
                starvationDamageTimer += Time.deltaTime;
                if (starvationDamageTimer >= starvationDamageInterval)
                {
                    starvationDamageTimer = 0f;
                    TakeDamage(starvationDamage, "Starvation");
                    TemporaryResourceHUD.Instance?.ShowNotification("Starving! Taking damage from hunger.", new Color(1.0f, 0.35f, 0.35f));
                }
            }
        }
        else
        {
            zeroHungerTimer = 0f;
            starvationDamageTimer = 0f;
        }

        // 3. Dehydration Grace Period & Damage Tick
        if (currentThirst <= 0f)
        {
            zeroThirstTimer += Time.deltaTime;
            if (zeroThirstTimer >= dehydrationGracePeriod)
            {
                dehydrationDamageTimer += Time.deltaTime;
                if (dehydrationDamageTimer >= dehydrationDamageInterval)
                {
                    dehydrationDamageTimer = 0f;
                    TakeDamage(dehydrationDamage, "Dehydration");
                    TemporaryResourceHUD.Instance?.ShowNotification("Dehydrated! Taking damage from thirst.", new Color(1.0f, 0.40f, 0.35f));
                }
            }
        }
        else
        {
            zeroThirstTimer = 0f;
            dehydrationDamageTimer = 0f;
        }

        // 4. Threshold Warnings (Controlled intervals to avoid spam)
        CheckSurvivalWarnings();
    }

    private void HandleRestingInput()
    {
        bool restKeyPressed = false;
        if (Keyboard.current != null && Keyboard.current.rKey.wasPressedThisFrame)
        {
            restKeyPressed = true;
        }

#if ENABLE_LEGACY_INPUT_MANAGER
        if (!restKeyPressed && Input.GetKeyDown(KeyCode.R))
        {
            restKeyPressed = true;
        }
#endif

        if (restKeyPressed)
        {
            ToggleResting();
        }

        // If player is resting and attempts to move, automatically cancel rest
        if (isResting)
        {
            bool moved = false;
            if (Keyboard.current != null)
            {
                if (Keyboard.current.wKey.isPressed || Keyboard.current.sKey.isPressed ||
                    Keyboard.current.aKey.isPressed || Keyboard.current.dKey.isPressed ||
                    Keyboard.current.upArrowKey.isPressed || Keyboard.current.downArrowKey.isPressed ||
                    Keyboard.current.leftArrowKey.isPressed || Keyboard.current.rightArrowKey.isPressed)
                {
                    moved = true;
                }
            }

            if (moved)
            {
                StopResting("Rest interrupted by movement.");
            }
        }
    }

    public void ToggleResting()
    {
        if (isResting)
        {
            StopResting("Finished resting.");
        }
        else
        {
            StartResting();
        }
    }

    public void StartResting()
    {
        if (isDead) return;
        if (currentEnergy >= maxEnergy)
        {
            TemporaryResourceHUD.Instance?.ShowNotification("Energy is already full.", new Color(0.9f, 0.9f, 0.9f));
            return;
        }

        isResting = true;
        if (playerMovement != null)
        {
            playerMovement.SetMovementEnabled(false);
        }

        TemporaryResourceHUD.Instance?.ShowNotification("Resting... Recovering energy [R to stop]", new Color(1.0f, 0.88f, 0.4f));
        OnRestingStateChanged?.Invoke(true);
    }

    public void StopResting(string feedbackMessage = "")
    {
        if (!isResting) return;
        isResting = false;

        if (playerMovement != null && !isDead)
        {
            playerMovement.SetMovementEnabled(true);
        }

        if (!string.IsNullOrEmpty(feedbackMessage))
        {
            TemporaryResourceHUD.Instance?.ShowNotification(feedbackMessage, new Color(0.85f, 0.95f, 0.85f));
        }

        OnRestingStateChanged?.Invoke(false);
    }

    private void CheckSurvivalWarnings()
    {
        float now = Time.time;

        // Health Warning
        if (currentHealth <= healthCriticalThreshold && (now - lastHealthWarningTime > WARNING_COOLDOWN))
        {
            lastHealthWarningTime = now;
            TemporaryResourceHUD.Instance?.ShowNotification("Health is critical!", new Color(1.0f, 0.25f, 0.25f));
        }

        // Hunger Warning
        if (currentHunger <= hungerWarningThreshold && currentHunger > 0f && (now - lastHungerWarningTime > WARNING_COOLDOWN))
        {
            lastHungerWarningTime = now;
            TemporaryResourceHUD.Instance?.ShowNotification("You're getting hungry.", new Color(1.0f, 0.65f, 0.25f));
        }

        // Thirst Warning
        if (currentThirst <= thirstWarningThreshold && currentThirst > 0f && (now - lastThirstWarningTime > WARNING_COOLDOWN))
        {
            lastThirstWarningTime = now;
            TemporaryResourceHUD.Instance?.ShowNotification("You're thirsty.", new Color(0.35f, 0.80f, 1.0f));
        }

        // Energy Warning
        if (currentEnergy <= energyWarningThreshold && currentEnergy > 0f && (now - lastEnergyWarningTime > WARNING_COOLDOWN))
        {
            lastEnergyWarningTime = now;
            TemporaryResourceHUD.Instance?.ShowNotification("You're exhausted.", new Color(1.0f, 0.85f, 0.35f));
        }
    }

    // =========================================================================
    // STAT MODIFICATION METHODS
    // =========================================================================

    public void TakeDamage(float amount, string reason = "")
    {
        if (isDead || amount <= 0f) return;

        currentHealth = Mathf.Clamp(currentHealth - amount, 0f, maxHealth);
        OnHealthChanged?.Invoke(currentHealth, maxHealth);

        // If resting, damage cancels rest immediately
        if (isResting)
        {
            StopResting("Rest interrupted by damage!");
        }

        if (currentHealth <= 0f)
        {
            Die(string.IsNullOrEmpty(reason) ? "Physical trauma" : reason);
        }
    }

    public void RestoreHealth(float amount)
    {
        if (isDead || amount <= 0f) return;
        currentHealth = Mathf.Clamp(currentHealth + amount, 0f, maxHealth);
        OnHealthChanged?.Invoke(currentHealth, maxHealth);
    }

    public void ConsumeHunger(float amount)
    {
        if (isDead || amount <= 0f) return;
        currentHunger = Mathf.Clamp(currentHunger - amount, 0f, maxHunger);
        OnHungerChanged?.Invoke(currentHunger, maxHunger);
    }

    public void RestoreHunger(float amount)
    {
        if (isDead || amount <= 0f) return;
        currentHunger = Mathf.Clamp(currentHunger + amount, 0f, maxHunger);
        zeroHungerTimer = 0f;
        starvationDamageTimer = 0f;
        OnHungerChanged?.Invoke(currentHunger, maxHunger);
    }

    public void ConsumeThirst(float amount)
    {
        if (isDead || amount <= 0f) return;
        currentThirst = Mathf.Clamp(currentThirst - amount, 0f, maxThirst);
        OnThirstChanged?.Invoke(currentThirst, maxThirst);
    }

    public void RestoreThirst(float amount)
    {
        if (isDead || amount <= 0f) return;
        currentThirst = Mathf.Clamp(currentThirst + amount, 0f, maxThirst);
        zeroThirstTimer = 0f;
        dehydrationDamageTimer = 0f;
        OnThirstChanged?.Invoke(currentThirst, maxThirst);
    }

    public void ConsumeEnergy(float amount)
    {
        if (isDead || amount <= 0f) return;
        currentEnergy = Mathf.Clamp(currentEnergy - amount, 0f, maxEnergy);
        OnEnergyChanged?.Invoke(currentEnergy, maxEnergy);
    }

    public void RestoreEnergy(float amount)
    {
        if (isDead || amount <= 0f) return;
        currentEnergy = Mathf.Clamp(currentEnergy + amount, 0f, maxEnergy);
        OnEnergyChanged?.Invoke(currentEnergy, maxEnergy);
    }

    // =========================================================================
    // FOOD & DRINK CONSUMPTION
    // =========================================================================

    /// <summary>
    /// Attempts to consume an item from inventory to restore survival stats.
    /// Returns true if consumed and removed from inventory; false if rejected.
    /// Does not waste food if player stats are already completely full.
    /// </summary>
    public bool TryConsumeItem(ItemData item, int slotIndex = -1)
    {
        if (isDead)
        {
            TemporaryResourceHUD.Instance?.ShowNotification("Cannot consume items while dead.", Color.red);
            return false;
        }

        if (item == null || !item.IsConsumable)
        {
            TemporaryResourceHUD.Instance?.ShowNotification("This item is not edible.", Color.gray);
            return false;
        }

        if (inventory == null) inventory = FindAnyObjectByType<Inventory>();
        if (inventory == null) return false;

        // Verify item is present in inventory
        if (slotIndex >= 0)
        {
            var slot = inventory.GetSlot(slotIndex);
            if (slot == null || slot.IsEmpty || slot.Item.ItemId != item.ItemId)
            {
                return false;
            }
        }
        else
        {
            if (inventory.GetItemCount(item) <= 0)
            {
                return false;
            }
        }

        // Sensible safeguard: Check if stats are already full to prevent accidental waste
        bool needsHunger = (item.HungerRestored > 0f && currentHunger < maxHunger);
        bool needsThirst = (item.ThirstRestored > 0f && currentThirst < maxThirst);
        bool needsHealth = (item.HealthRestored > 0f && currentHealth < maxHealth);
        bool needsEnergy = (item.EnergyRestored > 0f && currentEnergy < maxEnergy);

        if (!needsHunger && !needsThirst && !needsHealth && !needsEnergy)
        {
            TemporaryResourceHUD.Instance?.ShowNotification("Your stomach is full; no need to eat right now.", new Color(0.9f, 0.9f, 0.9f));
            return false;
        }

        // Apply restorations
        if (item.HungerRestored != 0f)
        {
            if (item.HungerRestored > 0f) RestoreHunger(item.HungerRestored);
            else ConsumeHunger(-item.HungerRestored);
        }

        if (item.ThirstRestored != 0f)
        {
            if (item.ThirstRestored > 0f) RestoreThirst(item.ThirstRestored);
            else ConsumeThirst(-item.ThirstRestored);
        }

        if (item.HealthRestored != 0f)
        {
            if (item.HealthRestored > 0f) RestoreHealth(item.HealthRestored);
            else TakeDamage(-item.HealthRestored, "Bad Food");
        }

        if (item.EnergyRestored != 0f)
        {
            if (item.EnergyRestored > 0f) RestoreEnergy(item.EnergyRestored);
            else ConsumeEnergy(-item.EnergyRestored);
        }

        // Deduct item from inventory only after successful consumption
        bool removed = false;
        if (slotIndex >= 0)
        {
            removed = inventory.RemoveFromSlot(slotIndex, 1);
        }
        else
        {
            removed = inventory.RemoveItem(item, 1);
        }

        if (!removed)
        {
            return false;
        }

        // Build clear feedback string
        string feedback = $"Consumed {item.DisplayName}";
        if (item.HungerRestored > 0f && item.ThirstRestored > 0f)
        {
            feedback += $" (Hunger +{item.HungerRestored:F0}, Thirst +{item.ThirstRestored:F0})";
        }
        else if (item.HungerRestored > 0f)
        {
            feedback += $" (Hunger +{item.HungerRestored:F0})";
        }
        else if (item.ThirstRestored > 0f)
        {
            feedback += $" (Thirst +{item.ThirstRestored:F0})";
        }

        TemporaryResourceHUD.Instance?.ShowNotification(feedback, new Color(0.40f, 1.0f, 0.60f));
        return true;
    }

    // =========================================================================
    // DEATH AND RESPAWN
    // =========================================================================

    public void Die(string reason)
    {
        if (isDead) return;

        isDead = true;
        isResting = false;
        deathCause = reason;

        if (playerMovement != null)
        {
            playerMovement.SetMovementEnabled(false);
        }

        Debug.LogWarning($"[STRANDED Survival] Player died! Cause: {reason}");
        TemporaryResourceHUD.Instance?.ShowNotification($"YOU DIED ({reason})", new Color(1.0f, 0.2f, 0.2f));

        OnPlayerDied?.Invoke(reason);
    }

    public void Respawn()
    {
        if (!isDead) return;

        isDead = false;
        isResting = false;
        deathCause = "";

        // Reset survival stats to full
        currentHealth = maxHealth;
        currentHunger = maxHunger;
        currentThirst = maxThirst;
        currentEnergy = maxEnergy;

        zeroHungerTimer = 0f;
        starvationDamageTimer = 0f;
        zeroThirstTimer = 0f;
        dehydrationDamageTimer = 0f;

        // Teleport player back to island camp
        transform.position = initialSpawnPosition;
        var rb = GetComponent<Rigidbody2D>();
        if (rb != null)
        {
            rb.position = initialSpawnPosition;
            rb.linearVelocity = Vector2.zero;
        }

        if (playerMovement != null)
        {
            playerMovement.SetMovementEnabled(true);
        }

        NotifyAllChanged();
        TemporaryResourceHUD.Instance?.ShowNotification("Respawned at Camp Sanctuary with full stats.", new Color(0.4f, 0.9f, 1.0f));

        OnPlayerRespawned?.Invoke();
    }

    /// <summary>
    /// Restores survival vitals safely within [0, Max] bounds and dispatches change events.
    /// </summary>
    public void RestoreStats(float health, float hunger, float thirst, float energy)
    {
        currentHealth = Mathf.Clamp(health, 0f, maxHealth);
        currentHunger = Mathf.Clamp(hunger, 0f, maxHunger);
        currentThirst = Mathf.Clamp(thirst, 0f, maxThirst);
        currentEnergy = Mathf.Clamp(energy, 0f, maxEnergy);
        isDead = currentHealth <= 0f;
        isResting = false;
        NotifyAllChanged();
    }

    private void NotifyAllChanged()
    {
        OnHealthChanged?.Invoke(currentHealth, maxHealth);
        OnHungerChanged?.Invoke(currentHunger, maxHunger);
        OnThirstChanged?.Invoke(currentThirst, maxThirst);
        OnEnergyChanged?.Invoke(currentEnergy, maxEnergy);
    }
}
