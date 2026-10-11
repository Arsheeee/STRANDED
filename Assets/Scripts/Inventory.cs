using System;
using UnityEngine;

/// <summary>
/// Slot-based player inventory system for STRANDED.
/// Manages a unified 36-slot array (Slots 0..11 represent Hotbar; Slots 12..35 represent Backpack).
/// Handles item storage, stacking limits, atomic capacity checks, and slot operations.
/// </summary>
public class Inventory : MonoBehaviour
{
    [Header("Inventory Capacity Configuration")]
    [Tooltip("Total number of inventory slots (default 36: 3 rows of 12).")]
    [SerializeField] private int totalSlots = 36;

    [Tooltip("Number of slots belonging to the active hotbar (default 12).")]
    [SerializeField] private int hotbarSlotsCount = 12;

    [Header("Starting Equipment")]
    [Tooltip("Whether to give starting primitive stone tools in hotbar for testing.")]
    [SerializeField] private bool grantStartingTools = true;

    [SerializeField] private InventorySlot[] slots;

    public int TotalSlots => totalSlots;
    public int HotbarSlotsCount => hotbarSlotsCount;
    public InventorySlot[] Slots => slots;

    /// <summary>
    /// Event dispatched whenever any inventory slot content or quantity changes.
    /// </summary>
    public event Action OnInventoryChanged;

    /// <summary>
    /// Event dispatched with the specific slot index that changed.
    /// </summary>
    public event Action<int> OnSlotChanged;

    void Awake()
    {
        InitializeSlots();
    }

    void Start()
    {
        if (grantStartingTools && IsEntireInventoryEmpty())
        {
            EquipInitialTestingTools();
        }
    }

    /// <summary>
    /// Ensures the slots array is properly allocated and initialized.
    /// </summary>
    public void InitializeSlots()
    {
        if (slots == null || slots.Length != totalSlots)
        {
            slots = new InventorySlot[totalSlots];
            for (int i = 0; i < totalSlots; i++)
            {
                slots[i] = new InventorySlot();
            }
        }
        else
        {
            for (int i = 0; i < totalSlots; i++)
            {
                if (slots[i] == null)
                {
                    slots[i] = new InventorySlot();
                }
            }
        }
    }

    /// <summary>
    /// Grants primitive stone tools into the first 4 hotbar slots if empty.
    /// </summary>
    public void EquipInitialTestingTools()
    {
        ItemDatabase.EnsureInitialized();
        ItemData knife = ItemDatabase.GetToolItem(ToolType.StoneKnife);
        ItemData axe = ItemDatabase.GetToolItem(ToolType.StoneAxe);
        ItemData pick = ItemDatabase.GetToolItem(ToolType.StonePickaxe);
        ItemData rod = ItemDatabase.GetToolItem(ToolType.FishingRod);

        if (knife != null && slots[0].IsEmpty) slots[0].Set(knife, 1);
        if (axe != null && slots[1].IsEmpty) slots[1].Set(axe, 1);
        if (pick != null && slots[2].IsEmpty) slots[2].Set(pick, 1);
        if (rod != null && slots[3].IsEmpty) slots[3].Set(rod, 1);

        NotifyChanged();
    }

    public bool IsEntireInventoryEmpty()
    {
        if (slots == null) return true;
        for (int i = 0; i < slots.Length; i++)
        {
            if (slots[i] != null && !slots[i].IsEmpty) return false;
        }
        return true;
    }

    public InventorySlot GetSlot(int index)
    {
        if (index < 0 || index >= slots.Length) return null;
        return slots[index];
    }

    /// <summary>
    /// Calculates how many units of the specified item could currently be accepted by the inventory.
    /// </summary>
    public int CheckAvailableSpace(ItemData item)
    {
        if (item == null) return 0;
        int totalSpace = 0;

        for (int i = 0; i < slots.Length; i++)
        {
            var slot = slots[i];
            if (slot.IsEmpty)
            {
                totalSpace += item.MaxStackSize;
            }
            else if (slot.Item.ItemId == item.ItemId && item.IsStackable)
            {
                totalSpace += Mathf.Max(0, item.MaxStackSize - slot.Quantity);
            }
        }

        return totalSpace;
    }

    /// <summary>
    /// Checks whether the inventory can accept the entire specified amount of an item.
    /// Prevents partial loss and guarantees atomic operations.
    /// </summary>
    public bool CanAddItem(ItemData item, int amount = 1)
    {
        if (item == null || amount <= 0) return false;
        return CheckAvailableSpace(item) >= amount;
    }

    /// <summary>
    /// Adds an item to the inventory, prioritizing existing non-full stacks,
    /// then filling empty slots. Returns leftover quantity (0 on complete success).
    /// </summary>
    public int AddItem(ItemData item, int amount = 1)
    {
        if (item == null || amount <= 0) return amount;

        int remaining = amount;

        // Pass 1: Fill existing non-full stacks if stackable
        if (item.IsStackable)
        {
            for (int i = 0; i < slots.Length; i++)
            {
                var slot = slots[i];
                if (!slot.IsEmpty && slot.Item.ItemId == item.ItemId && !slot.IsFull)
                {
                    remaining = slot.AddQuantity(remaining);
                    OnSlotChanged?.Invoke(i);
                    if (remaining <= 0) break;
                }
            }
        }

        // Pass 2: Place remaining into empty slots
        if (remaining > 0)
        {
            for (int i = 0; i < slots.Length; i++)
            {
                var slot = slots[i];
                if (slot.IsEmpty)
                {
                    int toPut = Mathf.Min(remaining, item.MaxStackSize);
                    slot.Set(item, toPut);
                    remaining -= toPut;
                    OnSlotChanged?.Invoke(i);
                    if (remaining <= 0) break;
                }
            }
        }

        NotifyChanged();
        return remaining;
    }

    /// <summary>
    /// Removes up to the specified amount of an item from the inventory.
    /// Returns true if the full amount was removed, false otherwise.
    /// </summary>
    public bool RemoveItem(ItemData item, int amount = 1)
    {
        if (item == null || amount <= 0 || GetItemCount(item) < amount)
        {
            return false;
        }

        int remainingToRemove = amount;

        // Remove from stacks until exhausted
        for (int i = slots.Length - 1; i >= 0; i--)
        {
            var slot = slots[i];
            if (!slot.IsEmpty && slot.Item.ItemId == item.ItemId)
            {
                int removed = slot.RemoveQuantity(remainingToRemove);
                remainingToRemove -= removed;
                OnSlotChanged?.Invoke(i);
                if (remainingToRemove <= 0) break;
            }
        }

        NotifyChanged();
        return true;
    }

    /// <summary>
    /// Checks whether the inventory has at least the required amount of an item.
    /// </summary>
    public bool HasItem(ItemData item, int amount = 1)
    {
        if (item == null) return false;
        return GetItemCount(item) >= amount;
    }

    /// <summary>
    /// Gets total count of an item currently in inventory across all slots.
    /// </summary>
    public int GetItemCount(ItemData item)
    {
        if (item == null) return 0;
        int count = 0;
        for (int i = 0; i < slots.Length; i++)
        {
            var slot = slots[i];
            if (!slot.IsEmpty && slot.Item.ItemId == item.ItemId)
            {
                count += slot.Quantity;
            }
        }
        return count;
    }

    /// <summary>
    /// Gets total count of a resource type currently in inventory.
    /// </summary>
    public int GetItemCount(ResourceType resourceType)
    {
        ItemData item = ItemDatabase.GetResourceItem(resourceType);
        return GetItemCount(item);
    }

    /// <summary>
    /// Swaps or merges the contents of two slots.
    /// Supports combining identical stackable items up to max stack limit.
    /// </summary>
    public void SwapSlots(int indexA, int indexB)
    {
        if (indexA < 0 || indexA >= slots.Length || indexB < 0 || indexB >= slots.Length || indexA == indexB)
        {
            return;
        }

        var slotA = slots[indexA];
        var slotB = slots[indexB];

        // Case 1: Both have the same stackable item -> Merge into B
        if (!slotA.IsEmpty && !slotB.IsEmpty && slotA.Item.ItemId == slotB.Item.ItemId && slotA.Item.IsStackable)
        {
            int spaceInB = slotB.Item.MaxStackSize - slotB.Quantity;
            if (spaceInB > 0)
            {
                int transfer = Mathf.Min(spaceInB, slotA.Quantity);
                slotB.AddQuantity(transfer);
                slotA.RemoveQuantity(transfer);
                OnSlotChanged?.Invoke(indexA);
                OnSlotChanged?.Invoke(indexB);
                NotifyChanged();
                return;
            }
        }

        // Case 2: Normal swap between A and B
        ItemData itemA = slotA.Item;
        int qtyA = slotA.Quantity;

        slotA.Set(slotB.Item, slotB.Quantity);
        slotB.Set(itemA, qtyA);

        OnSlotChanged?.Invoke(indexA);
        OnSlotChanged?.Invoke(indexB);
        NotifyChanged();
    }

    /// <summary>
    /// Clears a single slot at the specified index.
    /// </summary>
    public void ClearSlot(int index)
    {
        if (index < 0 || index >= slots.Length) return;
        slots[index]?.Clear();
        OnSlotChanged?.Invoke(index);
        NotifyChanged();
    }

    /// <summary>
    /// Clears all slots in the inventory.
    /// </summary>
    public void Clear()
    {
        for (int i = 0; i < slots.Length; i++)
        {
            slots[i]?.Clear();
            OnSlotChanged?.Invoke(i);
        }
        NotifyChanged();
    }

    private void NotifyChanged()
    {
        OnInventoryChanged?.Invoke();
    }
}
