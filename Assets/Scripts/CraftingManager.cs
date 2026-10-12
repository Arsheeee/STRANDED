using System;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Core crafting logic manager for STRANDED.
/// Validates recipe ingredients against the player's authoritative Inventory,
/// ensures atomic transactions, handles inventory capacity safeguards,
/// and produces crafted tools.
/// </summary>
public class CraftingManager : MonoBehaviour
{
    private static CraftingManager instance;
    public static CraftingManager Instance => instance;

    public event Action<CraftingRecipe> OnRecipeCrafted;

    void Awake()
    {
        if (instance != null && instance != this)
        {
            Destroy(gameObject);
            return;
        }
        instance = this;

        RecipeDatabase.EnsureInitialized();
    }

    /// <summary>
    /// Validates whether a recipe can be crafted with the current inventory contents.
    /// Returns true if all ingredient quantities are satisfied AND the output item can fit.
    /// </summary>
    public bool CanCraft(CraftingRecipe recipe, Inventory inventory, out string failReason)
    {
        failReason = string.Empty;

        if (recipe == null)
        {
            failReason = "Invalid recipe.";
            return false;
        }

        if (inventory == null)
        {
            failReason = "No inventory available.";
            return false;
        }

        // 1. Check required tool
        if (recipe.HasToolRequirement && !HasRequiredTool(recipe, inventory))
        {
            string toolName = recipe.RequiredTool != null ? recipe.RequiredTool.DisplayName : recipe.RequiredToolType.GetDisplayName();
            failReason = $"Requires tool: {toolName}.";
            return false;
        }

        // 2. Check required station
        if (recipe.HasStationRequirement && !HasRequiredStation(recipe, inventory))
        {
            failReason = $"Requires station: {recipe.RequiredStation}.";
            return false;
        }

        // 3. Check all required ingredients
        for (int i = 0; i < recipe.Ingredients.Count; i++)
        {
            var ingredient = recipe.Ingredients[i];
            if (ingredient == null || ingredient.Item == null) continue;

            int currentCount = inventory.GetItemCount(ingredient.Item);
            if (currentCount < ingredient.RequiredQuantity)
            {
                failReason = $"Not enough {ingredient.Item.DisplayName} ({currentCount}/{ingredient.RequiredQuantity}).";
                return false;
            }
        }

        // 4. Check if output can fit into inventory
        if (!CanFitOutput(recipe, inventory))
        {
            failReason = "Not enough inventory space.";
            return false;
        }

        return true;
    }

    /// <summary>
    /// Checks whether the player possesses the required tool in their inventory or hotbar.
    /// </summary>
    public bool HasRequiredTool(CraftingRecipe recipe, Inventory inventory)
    {
        if (recipe == null || !recipe.HasToolRequirement || inventory == null) return true;

        if (recipe.RequiredTool != null && inventory.GetItemCount(recipe.RequiredTool) > 0)
        {
            return true;
        }

        if (recipe.RequiredToolType != ToolType.None)
        {
            for (int i = 0; i < inventory.TotalSlots; i++)
            {
                var slot = inventory.GetSlot(i);
                if (slot != null && !slot.IsEmpty && slot.Item != null && slot.Item.ToolType == recipe.RequiredToolType)
                {
                    return true;
                }
            }
        }

        return false;
    }

    /// <summary>
    /// Checks whether the required crafting station is available.
    /// For portable stations like Weaving Frame, having the station item in inventory satisfies it.
    /// </summary>
    public bool HasRequiredStation(CraftingRecipe recipe, Inventory inventory)
    {
        if (recipe == null || !recipe.HasStationRequirement || inventory == null) return true;

        if (recipe.RequiredStation.IndexOf("Weaving", StringComparison.OrdinalIgnoreCase) >= 0)
        {
            for (int i = 0; i < inventory.TotalSlots; i++)
            {
                var slot = inventory.GetSlot(i);
                if (slot != null && !slot.IsEmpty && slot.Item != null)
                {
                    if (slot.Item.ToolType == ToolType.WeavingFrame || slot.Item.ItemId.Equals("tool_weaving_frame", StringComparison.OrdinalIgnoreCase))
                    {
                        return true;
                    }
                }
            }
            return false;
        }

        return true;
    }

    /// <summary>
    /// Checks whether the output item can fit into the inventory,
    /// taking into account whether consuming the ingredients will completely free up any slots.
    /// </summary>
    public bool CanFitOutput(CraftingRecipe recipe, Inventory inventory)
    {
        if (recipe == null || recipe.OutputItem == null || inventory == null) return false;

        // If inventory already has space, output fits immediately
        if (inventory.CanAddItem(recipe.OutputItem, recipe.OutputQuantity))
        {
            return true;
        }

        // If inventory is currently full of occupied slots, check if consuming the ingredients
        // will completely deplete and free at least one occupied slot.
        // For non-stackable tools, exactly 1 empty slot is needed.
        int freedSlots = 0;
        for (int i = 0; i < recipe.Ingredients.Count; i++)
        {
            var ing = recipe.Ingredients[i];
            if (ing == null || ing.Item == null) continue;

            int neededToRemove = ing.RequiredQuantity;
            for (int s = 0; s < inventory.TotalSlots; s++)
            {
                var slot = inventory.GetSlot(s);
                if (slot != null && !slot.IsEmpty && slot.Item.ItemId == ing.Item.ItemId)
                {
                    if (slot.Quantity <= neededToRemove)
                    {
                        neededToRemove -= slot.Quantity;
                        freedSlots++;
                        if (freedSlots >= 1) return true; // Output is a tool (requires 1 slot)
                    }
                    else
                    {
                        break;
                    }
                }
            }
        }

        return freedSlots >= 1;
    }

    /// <summary>
    /// Executes an atomic crafting transaction:
    /// Validates requirements -> removes ingredients -> awards output -> triggers feedback.
    /// If validation fails, zero items are consumed and the inventory remains completely untouched.
    /// </summary>
    public bool Craft(CraftingRecipe recipe, Inventory inventory, out string message)
    {
        if (!CanCraft(recipe, inventory, out string failReason))
        {
            message = failReason;
            TemporaryResourceHUD.Instance?.ShowNotification(failReason, new Color(1.0f, 0.35f, 0.35f));
            AudioManager.Instance?.PlayCraftFail();
            return false;
        }

        // Deduct ingredients
        for (int i = 0; i < recipe.Ingredients.Count; i++)
        {
            var ing = recipe.Ingredients[i];
            inventory.RemoveItem(ing.Item, ing.RequiredQuantity);
        }

        // Add crafted output
        inventory.AddItem(recipe.OutputItem, recipe.OutputQuantity);

        message = $"{recipe.DisplayName} crafted!";
        TemporaryResourceHUD.Instance?.ShowNotification(message, new Color(0.40f, 1.0f, 0.60f));
        AudioManager.Instance?.PlayCraftSuccess();

        OnRecipeCrafted?.Invoke(recipe);
        return true;
    }
}
