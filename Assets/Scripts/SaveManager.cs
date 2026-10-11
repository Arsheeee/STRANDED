using System;
using System.IO;
using UnityEngine;
using UnityEngine.InputSystem;

/// <summary>
/// Authoritative Save & Load Manager for STRANDED (Batch 11).
/// Coordinates JSON-based serialization and restoration of player transform,
/// 36-slot inventory, survival vitals, objective progress, and boat slipway construction.
/// Stores save data under Application.persistentDataPath/stranded_save.json.
/// Includes F5 Quick Save and F9 Quick Load shortcuts with input-focus guards.
/// </summary>
public class SaveManager : MonoBehaviour
{
    private static SaveManager instance;
    public static SaveManager Instance => instance;

    public const int CURRENT_SAVE_VERSION = 1;
    public const string SAVE_FILE_NAME = "stranded_save.json";

    public static string SaveFilePath => Path.Combine(Application.persistentDataPath, SAVE_FILE_NAME);

    // Public Events
    public event Action<SaveData> OnGameSaved;
    public event Action<SaveData> OnGameLoaded;

    void Awake()
    {
        if (instance != null && instance != this)
        {
            Destroy(gameObject);
            return;
        }
        instance = this;
    }

    void OnDestroy()
    {
        if (instance == this) instance = null;
    }

    void Update()
    {
        HandleKeyboardShortcuts();
    }

    /// <summary>
    /// Processes F5 (Quick Save) and F9 (Quick Load) hotkeys.
    /// Safely suppresses triggers if player is focused in a text input field
    /// or if the victory ending departure sequence is active.
    /// </summary>
    private void HandleKeyboardShortcuts()
    {
        // 1. Guard against victory sequence or cutscenes
        if (EscapeEndingController.Instance != null && EscapeEndingController.Instance.IsEndingActive)
        {
            return;
        }

        // 2. Guard against active text field / keyboard input focus
        if (GUIUtility.keyboardControl != 0)
        {
            return;
        }

        bool f5Pressed = false;
        bool f9Pressed = false;

        if (Keyboard.current != null)
        {
            if (Keyboard.current.f5Key.wasPressedThisFrame) f5Pressed = true;
            if (Keyboard.current.f9Key.wasPressedThisFrame) f9Pressed = true;
        }

#if ENABLE_LEGACY_INPUT_MANAGER
        if (!f5Pressed && Input.GetKeyDown(KeyCode.F5)) f5Pressed = true;
        if (!f9Pressed && Input.GetKeyDown(KeyCode.F9)) f9Pressed = true;
#endif

        if (f5Pressed)
        {
            SaveGame(out _);
        }
        else if (f9Pressed)
        {
            if (SaveExists())
            {
                LoadGame(out _);
            }
            else
            {
                TemporaryResourceHUD.Instance?.ShowNotification("No save file to load (Press F5 to save).", new Color(1.0f, 0.7f, 0.2f));
            }
        }
    }

    /// <summary>
    /// Returns true if a valid save file currently exists on disk.
    /// </summary>
    public bool SaveExists()
    {
        try
        {
            return File.Exists(SaveFilePath);
        }
        catch
        {
            return false;
        }
    }

    /// <summary>
    /// Retrieves a formatted timestamp string of the latest save file for UI display.
    /// </summary>
    public string GetSaveTimestampDisplay()
    {
        if (!SaveExists()) return "No Save File Found";

        try
        {
            DateTime lastWrite = File.GetLastWriteTime(SaveFilePath);
            return $"Last Saved: {lastWrite:yyyy-MM-dd HH:mm}";
        }
        catch
        {
            return "Save File Present";
        }
    }

    /// <summary>
    /// Saves current game state to JSON on disk under Application.persistentDataPath.
    /// Serializes player position, inventory slots, survival stats, objectives, and boat stages.
    /// </summary>
    public bool SaveGame(out string message)
    {
        // Guard: Prevent saving during terminal departure / victory sequence
        if (EscapeEndingController.Instance != null && EscapeEndingController.Instance.IsEndingActive)
        {
            message = "Cannot save during departure / victory sequence.";
            TemporaryResourceHUD.Instance?.ShowNotification(message, new Color(1.0f, 0.4f, 0.4f));
            Debug.LogWarning($"[STRANDED Save] {message}");
            return false;
        }

        var survival = SurvivalStats.Instance ?? FindAnyObjectByType<SurvivalStats>();
        if (survival != null && survival.IsDead)
        {
            message = "Cannot save while player is deceased.";
            TemporaryResourceHUD.Instance?.ShowNotification(message, new Color(1.0f, 0.4f, 0.4f));
            return false;
        }

        var player = FindAnyObjectByType<PlayerInteraction>()?.transform ?? GameObject.FindWithTag("Player")?.transform;
        var inventory = FindAnyObjectByType<Inventory>();
        var objManager = ObjectiveManager.Instance ?? FindAnyObjectByType<ObjectiveManager>();
        var boatSite = BoatConstructionSite.Instance ?? BoatConstructionSite.EnsureDefaultSiteExists();

        if (player == null || inventory == null || survival == null)
        {
            message = "Failed to save: Core gameplay components missing.";
            TemporaryResourceHUD.Instance?.ShowNotification(message, new Color(1.0f, 0.35f, 0.35f));
            Debug.LogError($"[STRANDED Save] {message}");
            return false;
        }

        // Construct serializable SaveData
        SaveData data = new SaveData
        {
            version = CURRENT_SAVE_VERSION,
            timestamp = DateTime.UtcNow.ToString("o"),
            playerX = player.position.x,
            playerY = player.position.y,
            playerZ = player.position.z,
            health = survival.CurrentHealth,
            hunger = survival.CurrentHunger,
            thirst = survival.CurrentThirst,
            energy = survival.CurrentEnergy
        };

        // Populate inventory slots
        if (inventory.Slots != null)
        {
            for (int i = 0; i < inventory.TotalSlots && i < inventory.Slots.Length; i++)
            {
                var slot = inventory.Slots[i];
                if (slot != null && !slot.IsEmpty && slot.Item != null && !string.IsNullOrEmpty(slot.Item.ItemId))
                {
                    data.inventorySlots.Add(new InventorySaveSlot
                    {
                        slotIndex = i,
                        itemId = slot.Item.ItemId,
                        quantity = slot.Quantity
                    });
                }
            }
        }

        // Populate objective progression
        if (objManager != null)
        {
            data.currentObjective = (int)objManager.CurrentObjective;
            data.hasDiscoveredCove = objManager.HasDiscoveredCove;
            data.hasEscaped = objManager.HasEscaped;
        }

        // Populate boat construction progress
        if (boatSite != null)
        {
            data.boatStageIndex = boatSite.CurrentStageIndex;
            data.boatState = (int)boatSite.CurrentState;
            data.boatDiscovered = boatSite.IsDiscovered;
            data.installedComponentIds = boatSite.GetInstalledComponentIds();
        }

        // Serialize to JSON and write atomically
        try
        {
            string json = JsonUtility.ToJson(data, true);
            string tempPath = SaveFilePath + ".tmp";

            string dir = Path.GetDirectoryName(SaveFilePath);
            if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
            {
                Directory.CreateDirectory(dir);
            }

            File.WriteAllText(tempPath, json);
            if (File.Exists(SaveFilePath))
            {
                File.Delete(SaveFilePath);
            }
            File.Move(tempPath, SaveFilePath);

            message = "Game Saved Successfully!";
            TemporaryResourceHUD.Instance?.ShowNotification(message, new Color(0.35f, 1.0f, 0.55f));
            Debug.Log($"[STRANDED Save] Game saved successfully to: {SaveFilePath}");

            OnGameSaved?.Invoke(data);
            return true;
        }
        catch (Exception ex)
        {
            message = $"Save write error: {ex.Message}";
            TemporaryResourceHUD.Instance?.ShowNotification("Failed to write save file!", new Color(1.0f, 0.35f, 0.35f));
            Debug.LogError($"[STRANDED Save] Exception writing save file: {ex}");
            return false;
        }
    }

    /// <summary>
    /// Restores game state from JSON on disk.
    /// Restores player position, 36 inventory slots, survival stats, objectives, and boat construction.
    /// Preserves current game state if the file is missing, corrupted, or incompatible.
    /// </summary>
    public bool LoadGame(out string message)
    {
        if (!SaveExists())
        {
            message = "No save file found.";
            TemporaryResourceHUD.Instance?.ShowNotification(message, new Color(1.0f, 0.65f, 0.2f));
            Debug.LogWarning($"[STRANDED Save] {message}");
            return false;
        }

        if (EscapeEndingController.Instance != null && EscapeEndingController.Instance.IsEndingActive)
        {
            message = "Cannot load game during victory ending.";
            TemporaryResourceHUD.Instance?.ShowNotification(message, new Color(1.0f, 0.4f, 0.4f));
            return false;
        }

        string json;
        try
        {
            json = File.ReadAllText(SaveFilePath);
        }
        catch (Exception ex)
        {
            message = $"Failed to read save file: {ex.Message}";
            TemporaryResourceHUD.Instance?.ShowNotification("Error reading save file! Current state preserved.", new Color(1.0f, 0.35f, 0.35f));
            Debug.LogError($"[STRANDED Save] {message}");
            return false;
        }

        SaveData data;
        try
        {
            data = JsonUtility.FromJson<SaveData>(json);
        }
        catch (Exception ex)
        {
            message = $"Save file corrupted: {ex.Message}";
            TemporaryResourceHUD.Instance?.ShowNotification("Save file corrupted! Current state preserved.", new Color(1.0f, 0.35f, 0.35f));
            Debug.LogError($"[STRANDED Save] {message}");
            return false;
        }

        if (data == null || data.version <= 0 || data.version > CURRENT_SAVE_VERSION)
        {
            message = "Incompatible or invalid save data format.";
            TemporaryResourceHUD.Instance?.ShowNotification("Incompatible save version! Current state preserved.", new Color(1.0f, 0.35f, 0.35f));
            Debug.LogWarning($"[STRANDED Save] {message}");
            return false;
        }

        // Initialize lookup catalog
        ItemDatabase.EnsureInitialized();

        var player = FindAnyObjectByType<PlayerInteraction>()?.transform ?? GameObject.FindWithTag("Player")?.transform;
        var inventory = FindAnyObjectByType<Inventory>();
        var survival = SurvivalStats.Instance ?? FindAnyObjectByType<SurvivalStats>();
        var objManager = ObjectiveManager.Instance ?? FindAnyObjectByType<ObjectiveManager>();
        var boatSite = BoatConstructionSite.Instance ?? BoatConstructionSite.EnsureDefaultSiteExists();

        // 1. Restore Player Position & Snap Exploration Camera
        if (player != null)
        {
            player.position = new Vector3(data.playerX, data.playerY, data.playerZ);
            var rb = player.GetComponent<Rigidbody2D>();
            if (rb != null)
            {
                rb.position = new Vector2(data.playerX, data.playerY);
                rb.linearVelocity = Vector2.zero;
            }

            var cam = FindAnyObjectByType<ExplorationCamera>();
            if (cam != null)
            {
                cam.SetTarget(player);
                Vector3 clamped = cam.CalculateClampedPosition(player.position);
                clamped.z = cam.transform.position.z;
                cam.transform.position = clamped;
            }
        }

        // 2. Restore Inventory (clear first to prevent duplicates; safely ignore unknown item IDs)
        if (inventory != null)
        {
            inventory.Clear();
            if (data.inventorySlots != null)
            {
                foreach (var slotData in data.inventorySlots)
                {
                    if (slotData == null || string.IsNullOrEmpty(slotData.itemId)) continue;
                    ItemData item = ItemDatabase.GetItemById(slotData.itemId);
                    if (item == null)
                    {
                        Debug.LogWarning($"[STRANDED Save] Unknown item ID '{slotData.itemId}' skipped safely during load.");
                        continue;
                    }

                    if (slotData.slotIndex >= 0 && slotData.slotIndex < inventory.TotalSlots)
                    {
                        inventory.SetSlot(slotData.slotIndex, item, slotData.quantity);
                    }
                    else
                    {
                        inventory.AddItem(item, slotData.quantity);
                    }
                }
            }
        }

        // 3. Restore Survival Vitals
        if (survival != null)
        {
            survival.RestoreStats(data.health, data.hunger, data.thirst, data.energy);
        }

        // 4. Restore Objective Progression
        if (objManager != null)
        {
            IslandObjective savedObj = (IslandObjective)Mathf.Clamp(data.currentObjective, 0, (int)IslandObjective.PrepareToEscape);
            objManager.RestoreObjectiveState(savedObj, data.hasDiscoveredCove, data.hasEscaped);
        }

        // 5. Restore Boat Slipway Construction Progress
        if (boatSite != null)
        {
            boatSite.RestoreConstructionProgress(data.boatStageIndex, data.boatDiscovered);
        }

        // 6. Refresh contextual HUD prompts
        TemporaryResourceHUD.Instance?.SetInteractionPrompt("");

        message = "Game Loaded Successfully!";
        TemporaryResourceHUD.Instance?.ShowNotification(message, new Color(0.40f, 0.90f, 1.0f));
        Debug.Log("[STRANDED Save] Game state loaded successfully.");

        OnGameLoaded?.Invoke(data);
        return true;
    }

    /// <summary>
    /// Deletes the current save file from disk.
    /// </summary>
    public bool DeleteSave()
    {
        try
        {
            if (File.Exists(SaveFilePath))
            {
                File.Delete(SaveFilePath);
                Debug.Log("[STRANDED Save] Save file deleted.");
                return true;
            }
        }
        catch (Exception ex)
        {
            Debug.LogError($"[STRANDED Save] Failed to delete save file: {ex.Message}");
        }
        return false;
    }

    /// <summary>
    /// Ensures a singleton instance of SaveManager exists in the scene.
    /// </summary>
    public static SaveManager EnsureExists()
    {
        if (instance != null) return instance;

        var existing = FindAnyObjectByType<SaveManager>();
        if (existing != null)
        {
            instance = existing;
            return existing;
        }

        GameObject go = new GameObject("SaveManager");
        instance = go.AddComponent<SaveManager>();
        Debug.Log("[STRANDED Save] Initialized SaveManager singleton in scene.");
        return instance;
    }
}
