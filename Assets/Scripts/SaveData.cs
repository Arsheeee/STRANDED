using System;
using System.Collections.Generic;

/// <summary>
/// Serializable data container representing a single inventory slot for STRANDED save/load.
/// </summary>
[Serializable]
public class InventorySaveSlot
{
    public int slotIndex;
    public string itemId = "";
    public int quantity;
}

/// <summary>
/// Versioned serializable root data model for STRANDED (Batch 11).
/// Encapsulates player position, all 36 inventory slots, survival statistics,
/// storyline objective progression, and boat construction stage into JSON.
/// Compatible with Unity's JsonUtility.
/// </summary>
[Serializable]
public class SaveData
{
    public int version = 1;
    public string timestamp = "";

    // 1. Player Position
    public float playerX;
    public float playerY;
    public float playerZ;

    // 2. Inventory (36 slots)
    public List<InventorySaveSlot> inventorySlots = new List<InventorySaveSlot>();

    // 3. Survival Statistics
    public float health = 100f;
    public float hunger = 100f;
    public float thirst = 100f;
    public float energy = 100f;

    // 4. Objective Progression
    public int currentObjective = 0;
    public bool hasDiscoveredCove = false;
    public bool hasEscaped = false;

    // 5. Boat Construction Progress
    public int boatStageIndex = 0;
    public int boatState = 0;
    public bool boatDiscovered = false;
    public List<string> installedComponentIds = new List<string>();
}
