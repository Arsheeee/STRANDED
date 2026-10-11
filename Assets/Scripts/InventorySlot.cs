using System;
using UnityEngine;

/// <summary>
/// Represents a single slot in an Inventory, holding an ItemData reference and quantity.
/// </summary>
[Serializable]
public class InventorySlot
{
    [SerializeField] private ItemData item;
    [SerializeField] private int quantity;

    public ItemData Item => item;
    public int Quantity => quantity;
    public bool IsEmpty => item == null || quantity <= 0;
    public bool IsFull => !IsEmpty && (!item.IsStackable || quantity >= item.MaxStackSize);
    public int AvailableSpace => IsEmpty ? 99 : (item.IsStackable ? item.MaxStackSize - quantity : 0);

    public InventorySlot()
    {
        item = null;
        quantity = 0;
    }

    public InventorySlot(ItemData item, int quantity)
    {
        Set(item, quantity);
    }

    /// <summary>
    /// Sets this slot's contents.
    /// </summary>
    public void Set(ItemData newItem, int newQuantity)
    {
        item = newItem;
        quantity = newItem != null ? Mathf.Max(0, newQuantity) : 0;
        if (quantity == 0)
        {
            item = null;
        }
    }

    /// <summary>
    /// Adds quantity up to the item's max stack limit.
    /// Returns the leftover amount that could not fit (0 if all was added).
    /// </summary>
    public int AddQuantity(int amount)
    {
        if (IsEmpty || !item.IsStackable)
        {
            return amount;
        }

        int space = item.MaxStackSize - quantity;
        int toAdd = Mathf.Min(space, amount);
        quantity += toAdd;
        return amount - toAdd;
    }

    /// <summary>
    /// Removes up to the specified amount from this slot.
    /// Returns the amount actually removed.
    /// </summary>
    public int RemoveQuantity(int amount)
    {
        if (IsEmpty)
        {
            return 0;
        }

        int toRemove = Mathf.Min(quantity, amount);
        quantity -= toRemove;
        if (quantity <= 0)
        {
            Clear();
        }
        return toRemove;
    }

    /// <summary>
    /// Clears the slot completely.
    /// </summary>
    public void Clear()
    {
        item = null;
        quantity = 0;
    }
}
