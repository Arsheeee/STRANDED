using System;
using UnityEngine;

/// <summary>
/// Represents a single ingredient requirement in a crafting recipe.
/// </summary>
[Serializable]
public class CraftingIngredient
{
    [SerializeField] private ItemData item;
    [SerializeField] private int requiredQuantity;

    public ItemData Item => item;
    public int RequiredQuantity => requiredQuantity;

    public CraftingIngredient(ItemData item, int requiredQuantity)
    {
        this.item = item;
        this.requiredQuantity = requiredQuantity;
    }
}
