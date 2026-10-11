using System;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Central registry and catalog of all crafting recipes in STRANDED.
/// Initializes the 4 primitive tool recipes and provides recipe lookups.
/// Configurable and easily extensible for future survival recipes.
/// </summary>
public static class RecipeDatabase
{
    private static readonly Dictionary<string, CraftingRecipe> recipesById = new Dictionary<string, CraftingRecipe>(StringComparer.OrdinalIgnoreCase);
    private static readonly List<CraftingRecipe> allRecipes = new List<CraftingRecipe>();
    private static bool isInitialized = false;

    public static void EnsureInitialized()
    {
        if (isInitialized) return;
        isInitialized = true;

        ItemDatabase.EnsureInitialized();

        recipesById.Clear();
        allRecipes.Clear();

        ItemData wood = ItemDatabase.GetResourceItem(ResourceType.Wood);
        ItemData stone = ItemDatabase.GetResourceItem(ResourceType.Stone);
        ItemData fiber = ItemDatabase.GetResourceItem(ResourceType.Fiber);

        ItemData knife = ItemDatabase.GetToolItem(ToolType.StoneKnife);
        ItemData axe = ItemDatabase.GetToolItem(ToolType.StoneAxe);
        ItemData pickaxe = ItemDatabase.GetToolItem(ToolType.StonePickaxe);
        ItemData rod = ItemDatabase.GetToolItem(ToolType.FishingRod);

        // RECIPE 1 — STONE KNIFE (Stone x 2, Fiber x 1 -> Stone Knife x 1)
        RegisterRecipe(new CraftingRecipe(
            "recipe_stone_knife",
            "Stone Knife",
            "Sharp carved flint blade lashed with plant fiber. Essential for cutting wild fibers and foliage.",
            knife, 1,
            new List<CraftingIngredient>
            {
                new CraftingIngredient(stone, 2),
                new CraftingIngredient(fiber, 1)
            },
            "Tools"
        ));

        // RECIPE 2 — STONE AXE (Stone x 3, Wood x 2, Fiber x 1 -> Stone Axe x 1)
        RegisterRecipe(new CraftingRecipe(
            "recipe_stone_axe",
            "Stone Axe",
            "Chipped stone wedge tied to a sturdy timber haft. Capable of felling island trees for wood.",
            axe, 1,
            new List<CraftingIngredient>
            {
                new CraftingIngredient(stone, 3),
                new CraftingIngredient(wood, 2),
                new CraftingIngredient(fiber, 1)
            },
            "Tools"
        ));

        // RECIPE 3 — STONE PICKAXE (Stone x 3, Wood x 2, Fiber x 2 -> Stone Pickaxe x 1)
        RegisterRecipe(new CraftingRecipe(
            "recipe_stone_pickaxe",
            "Stone Pickaxe",
            "Heavy sharpened rock bound firmly with double fiber cords. Breaks coastal rocks and boulders.",
            pickaxe, 1,
            new List<CraftingIngredient>
            {
                new CraftingIngredient(stone, 3),
                new CraftingIngredient(wood, 2),
                new CraftingIngredient(fiber, 2)
            },
            "Tools"
        ));

        // RECIPE 4 — FISHING ROD (Wood x 3, Fiber x 2 -> Fishing Rod x 1)
        RegisterRecipe(new CraftingRecipe(
            "recipe_fishing_rod",
            "Fishing Rod",
            "Flexible springy wood pole strung with twisted vine cord. Used for coastal fishing.",
            rod, 1,
            new List<CraftingIngredient>
            {
                new CraftingIngredient(wood, 3),
                new CraftingIngredient(fiber, 2)
            },
            "Tools"
        ));
    }

    private static void RegisterRecipe(CraftingRecipe recipe)
    {
        if (recipe == null || string.IsNullOrEmpty(recipe.RecipeId)) return;
        recipesById[recipe.RecipeId] = recipe;
        allRecipes.Add(recipe);
    }

    public static IReadOnlyList<CraftingRecipe> GetAllRecipes()
    {
        EnsureInitialized();
        return allRecipes;
    }

    public static CraftingRecipe GetRecipeById(string recipeId)
    {
        EnsureInitialized();
        if (string.IsNullOrEmpty(recipeId)) return null;
        recipesById.TryGetValue(recipeId, out CraftingRecipe recipe);
        return recipe;
    }
}
