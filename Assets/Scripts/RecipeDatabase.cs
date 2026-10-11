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
        ItemData vines = ItemDatabase.GetResourceItem(ResourceType.Vines);

        // Primitive Tools
        ItemData knife = ItemDatabase.GetToolItem(ToolType.StoneKnife);
        ItemData axe = ItemDatabase.GetToolItem(ToolType.StoneAxe);
        ItemData pickaxe = ItemDatabase.GetToolItem(ToolType.StonePickaxe);
        ItemData rod = ItemDatabase.GetToolItem(ToolType.FishingRod);

        // Advanced Primitive Equipment
        ItemData improvedKnife = ItemDatabase.GetToolItem(ToolType.ImprovedKnife);
        ItemData woodenMallet = ItemDatabase.GetToolItem(ToolType.WoodenMallet);
        ItemData fiberTwister = ItemDatabase.GetToolItem(ToolType.FiberTwister);
        ItemData weavingFrame = ItemDatabase.GetToolItem(ToolType.WeavingFrame);

        // Processed Materials
        ItemData shapedWood = ItemDatabase.GetItemById("shaped_wood");
        ItemData woodenPegs = ItemDatabase.GetItemById("wooden_pegs");
        ItemData strongRope = ItemDatabase.GetItemById("strong_rope");
        ItemData reinforcedRope = ItemDatabase.GetItemById("reinforced_rope");
        ItemData wovenSailcloth = ItemDatabase.GetItemById("woven_sailcloth");
        ItemData reinforcedJoints = ItemDatabase.GetItemById("reinforced_joints");

        // Boat Components
        ItemData paddle = ItemDatabase.GetItemById("paddle");
        ItemData windAssembly = ItemDatabase.GetItemById("wind_assembly");
        ItemData ropeBindingKit = ItemDatabase.GetItemById("rope_binding_kit");
        ItemData structuralFrame = ItemDatabase.GetItemById("structural_frame");
        ItemData reinforcedHull = ItemDatabase.GetItemById("reinforced_hull");

        // =====================================================================
        // TIER 1: PRIMITIVE TOOLS
        // =====================================================================

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

        // =====================================================================
        // TIER 2: ADVANCED PRIMITIVE EQUIPMENT
        // =====================================================================

        // RECIPE 5 — IMPROVED CUTTING KNIFE (Wood x 2, Stone x 3, Vines x 2 -> Improved Knife x 1)
        RegisterRecipe(new CraftingRecipe(
            "recipe_improved_knife",
            "Improved Cutting Knife",
            "Precision stone blade bound with tough vines. Used to shape and carve wooden boat parts.",
            improvedKnife, 1,
            new List<CraftingIngredient>
            {
                new CraftingIngredient(wood, 2),
                new CraftingIngredient(stone, 3),
                new CraftingIngredient(vines, 2)
            },
            "Tools"
        ));

        // RECIPE 6 — WOODEN MALLET (Wood x 4, Vines x 2 -> Wooden Mallet x 1)
        RegisterRecipe(new CraftingRecipe(
            "recipe_wooden_mallet",
            "Wooden Mallet",
            "Heavy hardwood mallet. Drives pegs and secures reinforced structural boat joints.",
            woodenMallet, 1,
            new List<CraftingIngredient>
            {
                new CraftingIngredient(wood, 4),
                new CraftingIngredient(vines, 2)
            },
            "Tools"
        ));

        // RECIPE 7 — FIBER TWISTING TOOL (Wood x 3, Fiber x 2, Vines x 1 -> Fiber Twisting Tool x 1)
        RegisterRecipe(new CraftingRecipe(
            "recipe_fiber_twister",
            "Fiber Twisting Tool",
            "Twisting spindle used to process fiber and vines into durable cordage and nautical rope.",
            fiberTwister, 1,
            new List<CraftingIngredient>
            {
                new CraftingIngredient(wood, 3),
                new CraftingIngredient(fiber, 2),
                new CraftingIngredient(vines, 1)
            },
            "Tools"
        ));

        // RECIPE 8 — WEAVING FRAME (Wood x 6, Vines x 4, Fiber x 2 -> Weaving Frame x 1)
        RegisterRecipe(new CraftingRecipe(
            "recipe_weaving_frame",
            "Weaving Frame",
            "Sturdy four-post timber loom frame. Required for weaving fibrous sailcloth for the escape boat.",
            weavingFrame, 1,
            new List<CraftingIngredient>
            {
                new CraftingIngredient(wood, 6),
                new CraftingIngredient(vines, 4),
                new CraftingIngredient(fiber, 2)
            },
            "Tools"
        ));

        // =====================================================================
        // TIER 3: PROCESSED MATERIALS
        // =====================================================================

        // RECIPE 9 — SHAPED WOODEN PARTS (Wood x 2 + Improved Knife -> Shaped Wooden Parts x 2)
        RegisterRecipe(new CraftingRecipe(
            "recipe_shaped_wood",
            "Shaped Wooden Parts",
            "Carefully planed curved wooden timbers. Required for paddles and boat structures.",
            shapedWood, 2,
            new List<CraftingIngredient>
            {
                new CraftingIngredient(wood, 2)
            },
            "Materials",
            requiredTool: improvedKnife,
            requiredToolType: ToolType.ImprovedKnife
        ));

        // RECIPE 10 — WOODEN PEGS (Wood x 1 + Improved Knife -> Wooden Pegs x 4)
        RegisterRecipe(new CraftingRecipe(
            "recipe_wooden_pegs",
            "Wooden Pegs",
            "Hand-carved wooden dowels used to join and pin structural timber components.",
            woodenPegs, 4,
            new List<CraftingIngredient>
            {
                new CraftingIngredient(wood, 1)
            },
            "Materials",
            requiredTool: improvedKnife,
            requiredToolType: ToolType.ImprovedKnife
        ));

        // RECIPE 11 — STRONG ROPE (Fiber x 3, Vines x 2 + Fiber Twister -> Strong Rope x 1)
        RegisterRecipe(new CraftingRecipe(
            "recipe_strong_rope",
            "Strong Rope",
            "Heavy-duty cordage braided from wild fiber and flexible jungle vines.",
            strongRope, 1,
            new List<CraftingIngredient>
            {
                new CraftingIngredient(fiber, 3),
                new CraftingIngredient(vines, 2)
            },
            "Materials",
            requiredTool: fiberTwister,
            requiredToolType: ToolType.FiberTwister
        ));

        // RECIPE 12 — REINFORCED ROPE (Strong Rope x 1, Vines x 2, Fiber x 1 + Fiber Twister -> Reinforced Rope x 1)
        RegisterRecipe(new CraftingRecipe(
            "recipe_reinforced_rope",
            "Reinforced Rope",
            "Nautical-grade multi-ply cordage bound with extra vine windings for heavy rigging.",
            reinforcedRope, 1,
            new List<CraftingIngredient>
            {
                new CraftingIngredient(strongRope, 1),
                new CraftingIngredient(vines, 2),
                new CraftingIngredient(fiber, 1)
            },
            "Materials",
            requiredTool: fiberTwister,
            requiredToolType: ToolType.FiberTwister
        ));

        // RECIPE 13 — WOVEN SAILCLOTH (Fiber x 4, Vines x 4 + Weaving Frame -> Woven Sailcloth x 1)
        RegisterRecipe(new CraftingRecipe(
            "recipe_woven_sailcloth",
            "Woven Sailcloth",
            "Dense, flexible canvas woven from island fibers and vines on the Weaving Frame.",
            wovenSailcloth, 1,
            new List<CraftingIngredient>
            {
                new CraftingIngredient(fiber, 4),
                new CraftingIngredient(vines, 4)
            },
            "Materials",
            requiredTool: weavingFrame,
            requiredToolType: ToolType.WeavingFrame,
            requiredStation: "Weaving Frame"
        ));

        // RECIPE 14 — REINFORCED WOODEN JOINTS (Shaped Wood x 2, Wooden Pegs x 2, Strong Rope x 1 + Mallet -> Joints x 1)
        RegisterRecipe(new CraftingRecipe(
            "recipe_reinforced_joints",
            "Reinforced Wooden Joints",
            "Pinned and rope-lashed timber joints engineered to brace the escape boat frame and hull.",
            reinforcedJoints, 1,
            new List<CraftingIngredient>
            {
                new CraftingIngredient(shapedWood, 2),
                new CraftingIngredient(woodenPegs, 2),
                new CraftingIngredient(strongRope, 1)
            },
            "Materials",
            requiredTool: woodenMallet,
            requiredToolType: ToolType.WoodenMallet
        ));

        // =====================================================================
        // TIER 4: BOAT COMPONENTS
        // =====================================================================

        // RECIPE 15 — PADDLE (Shaped Wood x 2, Wooden Pegs x 2, Strong Rope x 1 + Improved Knife -> Paddle x 1)
        RegisterRecipe(new CraftingRecipe(
            "recipe_paddle",
            "Paddle",
            "Carved wooden canoe paddle with broad blade. Navigation component for the escape boat.",
            paddle, 1,
            new List<CraftingIngredient>
            {
                new CraftingIngredient(shapedWood, 2),
                new CraftingIngredient(woodenPegs, 2),
                new CraftingIngredient(strongRope, 1)
            },
            "Boat Components",
            requiredTool: improvedKnife,
            requiredToolType: ToolType.ImprovedKnife
        ));

        // RECIPE 16 — WIND-CATCHING ASSEMBLY (Sailcloth x 2, Shaped Wood x 3, Reinforced Rope x 2, Pegs x 4 + Mallet + Frame)
        RegisterRecipe(new CraftingRecipe(
            "recipe_wind_assembly",
            "Wind-Catching Assembly",
            "Primitive triangular sail rigged to shaped spars with heavy ropes. Propulsion component for the escape boat.",
            windAssembly, 1,
            new List<CraftingIngredient>
            {
                new CraftingIngredient(wovenSailcloth, 2),
                new CraftingIngredient(shapedWood, 3),
                new CraftingIngredient(reinforcedRope, 2),
                new CraftingIngredient(woodenPegs, 4)
            },
            "Boat Components",
            requiredTool: woodenMallet,
            requiredToolType: ToolType.WoodenMallet,
            requiredStation: "Weaving Frame"
        ));

        // RECIPE 17 — ROPE BINDING KIT (Strong Rope x 2, Reinforced Rope x 2, Vines x 3 + Fiber Twister -> Kit x 1)
        RegisterRecipe(new CraftingRecipe(
            "recipe_rope_binding_kit",
            "Rope Binding Kit",
            "Prepared bundle of lashing cordage, loops, and nautical knots for assembling the escape boat.",
            ropeBindingKit, 1,
            new List<CraftingIngredient>
            {
                new CraftingIngredient(strongRope, 2),
                new CraftingIngredient(reinforcedRope, 2),
                new CraftingIngredient(vines, 3)
            },
            "Boat Components",
            requiredTool: fiberTwister,
            requiredToolType: ToolType.FiberTwister
        ));

        // RECIPE 18 — STRUCTURAL FRAME (Shaped Wood x 4, Wooden Pegs x 6, Reinforced Joints x 2, Binding Kit x 1 + Mallet)
        RegisterRecipe(new CraftingRecipe(
            "recipe_structural_frame",
            "Structural Frame",
            "Internal skeletal framework of keel stringers and pegged rib supports for the escape boat.",
            structuralFrame, 1,
            new List<CraftingIngredient>
            {
                new CraftingIngredient(shapedWood, 4),
                new CraftingIngredient(woodenPegs, 6),
                new CraftingIngredient(reinforcedJoints, 2),
                new CraftingIngredient(ropeBindingKit, 1)
            },
            "Boat Components",
            requiredTool: woodenMallet,
            requiredToolType: ToolType.WoodenMallet
        ));

        // RECIPE 19 — REINFORCED HULL (Shaped Wood x 6, Reinforced Joints x 4, Binding Kit x 1, Strong Rope x 3 + Mallet)
        RegisterRecipe(new CraftingRecipe(
            "recipe_reinforced_hull",
            "Reinforced Hull",
            "Primary floating body of the boat, braced with reinforced joints and watertight lashings for the escape boat.",
            reinforcedHull, 1,
            new List<CraftingIngredient>
            {
                new CraftingIngredient(shapedWood, 6),
                new CraftingIngredient(reinforcedJoints, 4),
                new CraftingIngredient(ropeBindingKit, 1),
                new CraftingIngredient(strongRope, 3)
            },
            "Boat Components",
            requiredTool: woodenMallet,
            requiredToolType: ToolType.WoodenMallet
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

    public static List<CraftingRecipe> GetRecipesByCategory(string category)
    {
        EnsureInitialized();
        if (string.IsNullOrEmpty(category) || category.Equals("All", StringComparison.OrdinalIgnoreCase))
        {
            return new List<CraftingRecipe>(allRecipes);
        }

        List<CraftingRecipe> list = new List<CraftingRecipe>();
        for (int i = 0; i < allRecipes.Count; i++)
        {
            if (allRecipes[i].Category.Equals(category, StringComparison.OrdinalIgnoreCase))
            {
                list.Add(allRecipes[i]);
            }
        }
        return list;
    }

    public static CraftingRecipe GetRecipeById(string recipeId)
    {
        EnsureInitialized();
        if (string.IsNullOrEmpty(recipeId)) return null;
        recipesById.TryGetValue(recipeId, out CraftingRecipe recipe);
        return recipe;
    }
}
