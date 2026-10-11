using System;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Data-driven definition for a primitive crafting recipe in STRANDED.
/// Contains the output item, yield quantity, required ingredients, description, and category.
/// </summary>
[Serializable]
public class CraftingRecipe
{
    [SerializeField] private string recipeId;
    [SerializeField] private string displayName;
    [SerializeField] private string description;
    [SerializeField] private ItemData outputItem;
    [SerializeField] private int outputQuantity = 1;
    [SerializeField] private List<CraftingIngredient> ingredients = new List<CraftingIngredient>();
    [SerializeField] private string category = "Tools";
    [SerializeField] private ItemData requiredTool;
    [SerializeField] private ToolType requiredToolType = ToolType.None;
    [SerializeField] private string requiredStation = "";

    public string RecipeId => recipeId;
    public string DisplayName => displayName;
    public string Description => description;
    public ItemData OutputItem => outputItem;
    public int OutputQuantity => outputQuantity;
    public IReadOnlyList<CraftingIngredient> Ingredients => ingredients;
    public string Category => category;
    public Sprite Icon => outputItem != null ? outputItem.Icon : null;
    public ItemData RequiredTool => requiredTool;
    public ToolType RequiredToolType => requiredToolType;
    public string RequiredStation => requiredStation;
    public bool HasToolRequirement => requiredTool != null || requiredToolType != ToolType.None;
    public bool HasStationRequirement => !string.IsNullOrEmpty(requiredStation);

    public CraftingRecipe(
        string recipeId,
        string displayName,
        string description,
        ItemData outputItem,
        int outputQuantity,
        List<CraftingIngredient> ingredients,
        string category = "Tools",
        ItemData requiredTool = null,
        ToolType requiredToolType = ToolType.None,
        string requiredStation = "")
    {
        this.recipeId = recipeId;
        this.displayName = displayName;
        this.description = description;
        this.outputItem = outputItem;
        this.outputQuantity = outputQuantity;
        this.ingredients = ingredients ?? new List<CraftingIngredient>();
        this.category = category;
        this.requiredTool = requiredTool;
        this.requiredToolType = requiredToolType;
        this.requiredStation = requiredStation ?? "";
    }
}
