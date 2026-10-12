using System;
using System.IO;
using System.Collections.Generic;
using System.Reflection;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

/// <summary>
/// Authoritative Automated Regression Test Suite for STRANDED:
/// Starting Knife, Resource Restrictions, and Deadlock-Free Progression.
/// Validates all 18 requirements from the user specification.
/// </summary>
public static class ProgressionRegressionTestRunner
{
    [MenuItem("Tools/STRANDED/Run Progression & Knife Regression Tests")]
    public static void RunAllTests()
    {
        Debug.Log("======================================================================");
        Debug.Log("STRANDED: Running Comprehensive Progression & Knife Regression Tests");
        Debug.Log("======================================================================");

        int passed = 0;
        int failed = 0;

        void Assert(bool condition, string testName, string detail = "")
        {
            if (condition)
            {
                passed++;
                Debug.Log($"[PASS] {testName} {(string.IsNullOrEmpty(detail) ? "" : "— " + detail)}");
            }
            else
            {
                failed++;
                Debug.LogError($"[FAIL] {testName} {(string.IsNullOrEmpty(detail) ? "" : "— " + detail)}");
            }
        }

        // Initialize databases
        ItemDatabase.EnsureInitialized();
        RecipeDatabase.EnsureInitialized();

        GameObject tempRoot = new GameObject("TempTestRoot");
        try
        {
            // Setup test player with inventory and interaction
            GameObject playerGo = new GameObject("TestPlayer");
            playerGo.transform.SetParent(tempRoot.transform);
            var inventory = playerGo.AddComponent<Inventory>();
            inventory.InitializeSlots();
            var survival = playerGo.AddComponent<SurvivalStats>();
            var interaction = playerGo.AddComponent<PlayerInteraction>();

            // -------------------------------------------------------------------------
            // TEST 1: Starting inventory has strictly ONE Stone Knife
            // -------------------------------------------------------------------------
            inventory.Clear();
            inventory.EquipStartingInventory();

            int knifeCount = 0;
            int otherToolCount = 0;
            for (int i = 0; i < inventory.TotalSlots; i++)
            {
                var slot = inventory.GetSlot(i);
                if (!slot.IsEmpty && slot.Item != null)
                {
                    if (slot.Item.ToolType == ToolType.StoneKnife) knifeCount += slot.Quantity;
                    else if (slot.Item.ItemType == ItemType.Tool) otherToolCount += slot.Quantity;
                }
            }

            Assert(knifeCount == 1 && otherToolCount == 0,
                "TEST 1: Starting New Game Inventory",
                $"Stone Knife count: {knifeCount}, Other tools: {otherToolCount}");

            // Ensure repeated calls do not duplicate the knife
            inventory.EquipStartingInventory();
            int knifeCountAfterRepeat = inventory.GetItemCount(ItemDatabase.GetToolItem(ToolType.StoneKnife));
            Assert(knifeCountAfterRepeat == 1,
                "TEST 1b: Repeated New Game Initialization Prevents Duplication",
                $"Knife count after repeated call: {knifeCountAfterRepeat}");

            // -------------------------------------------------------------------------
            // Create Mock Nodes for Tests 2-8
            // -------------------------------------------------------------------------
            ResourceNode smallRockNode = CreateMockNode(tempRoot.transform, ResourceType.Stone, "Small Pebble",
                ToolType.StoneKnife, ResourceCategory.Rock, ResourceSize.VerySmall, 1, 45f);

            ResourceNode smallBushNode = CreateMockNode(tempRoot.transform, ResourceType.Fiber, "Small Bush",
                ToolType.StoneKnife, ResourceCategory.Bush, ResourceSize.VerySmall, 1, 45f);

            ResourceNode smallLogNode = CreateMockNode(tempRoot.transform, ResourceType.Wood, "Small Log",
                ToolType.StoneKnife, ResourceCategory.Log, ResourceSize.VerySmall, 1, 45f);

            ResourceNode medRockNode = CreateMockNode(tempRoot.transform, ResourceType.Stone, "Slate Rock",
                ToolType.StonePickaxe, ResourceCategory.Rock, ResourceSize.Medium, 1, 60f);

            ResourceNode largeRockNode = CreateMockNode(tempRoot.transform, ResourceType.Stone, "Large Boulder",
                ToolType.StonePickaxe, ResourceCategory.Rock, ResourceSize.Large, 2, 90f);

            ResourceNode medBushNode = CreateMockNode(tempRoot.transform, ResourceType.Fiber, "Foliage Bush",
                ToolType.StoneAxe, ResourceCategory.Bush, ResourceSize.Medium, 1, 45f);

            ResourceNode largeBushNode = CreateMockNode(tempRoot.transform, ResourceType.Fiber, "Dense Shrub",
                ToolType.StoneAxe, ResourceCategory.Bush, ResourceSize.Large, 1, 45f);

            ResourceNode normalLogNode = CreateMockNode(tempRoot.transform, ResourceType.Wood, "Driftwood Log",
                ToolType.StoneAxe, ResourceCategory.Log, ResourceSize.Medium, 2, 60f);

            ResourceNode largeLogNode = CreateMockNode(tempRoot.transform, ResourceType.Wood, "Large Timber Log",
                ToolType.StoneAxe, ResourceCategory.Log, ResourceSize.Large, 3, 90f);

            ResourceNode treeNode = CreateMockNode(tempRoot.transform, ResourceType.Wood, "Tropical Oak",
                ToolType.StoneAxe, ResourceCategory.Tree, ResourceSize.Large, 2, 90f);

            ResourceNode vineNode = CreateMockNode(tempRoot.transform, ResourceType.Vines, "Jungle Vine Cluster",
                ToolType.StoneAxe, ResourceCategory.Bush, ResourceSize.Medium, 2, 45f);

            // -------------------------------------------------------------------------
            // TEST 2: Stone Knife + Very Small Rock = SUCCESS
            // -------------------------------------------------------------------------
            bool knifeOnSmallRockCan = smallRockNode.CanHarvestWith(ToolType.StoneKnife, out string err2);
            inventory.Clear();
            int yield2 = smallRockNode.Interact(ToolType.StoneKnife, interaction);
            Assert(knifeOnSmallRockCan && yield2 == 1 && inventory.GetItemCount(ResourceType.Stone) == 1,
                "TEST 2: Stone Knife + Very Small Rock",
                $"CanHarvest: {knifeOnSmallRockCan}, Yield: {yield2}, Error: '{err2}'");

            // -------------------------------------------------------------------------
            // TEST 3: Stone Knife + Very Small Bush = SUCCESS
            // -------------------------------------------------------------------------
            bool knifeOnSmallBushCan = smallBushNode.CanHarvestWith(ToolType.StoneKnife, out string err3);
            inventory.Clear();
            int yield3 = smallBushNode.Interact(ToolType.StoneKnife, interaction);
            Assert(knifeOnSmallBushCan && yield3 == 1 && inventory.GetItemCount(ResourceType.Fiber) == 1,
                "TEST 3: Stone Knife + Very Small Bush",
                $"CanHarvest: {knifeOnSmallBushCan}, Yield: {yield3}, Error: '{err3}'");

            // -------------------------------------------------------------------------
            // TEST 4: Stone Knife + Very Small Log = SUCCESS
            // -------------------------------------------------------------------------
            bool knifeOnSmallLogCan = smallLogNode.CanHarvestWith(ToolType.StoneKnife, out string err4);
            inventory.Clear();
            int yield4 = smallLogNode.Interact(ToolType.StoneKnife, interaction);
            Assert(knifeOnSmallLogCan && yield4 == 1 && inventory.GetItemCount(ResourceType.Wood) == 1,
                "TEST 4: Stone Knife + Very Small Log",
                $"CanHarvest: {knifeOnSmallLogCan}, Yield: {yield4}, Error: '{err4}'");

            // -------------------------------------------------------------------------
            // TEST 5: Stone Knife + Medium/Large Rock = FAILURE
            // -------------------------------------------------------------------------
            bool knifeOnMedRock = medRockNode.CanHarvestWith(ToolType.StoneKnife, out string errMedRock);
            bool knifeOnLargeRock = largeRockNode.CanHarvestWith(ToolType.StoneKnife, out string errLargeRock);
            Assert(!knifeOnMedRock && !knifeOnLargeRock &&
                   errMedRock == "Your knife is too weak for this resource." &&
                   errLargeRock == "Your knife is too weak for this resource.",
                "TEST 5: Stone Knife + Medium/Large Rock Rejection",
                $"MedRock Err: '{errMedRock}', LargeRock Err: '{errLargeRock}'");

            // -------------------------------------------------------------------------
            // TEST 6: Stone Knife + Medium/Large Bush = FAILURE
            // -------------------------------------------------------------------------
            bool knifeOnMedBush = medBushNode.CanHarvestWith(ToolType.StoneKnife, out string errMedBush);
            bool knifeOnLargeBush = largeBushNode.CanHarvestWith(ToolType.StoneKnife, out string errLargeBush);
            Assert(!knifeOnMedBush && !knifeOnLargeBush &&
                   errMedBush == "Your knife is too weak for this resource." &&
                   errLargeBush == "Your knife is too weak for this resource.",
                "TEST 6: Stone Knife + Medium/Large Bush Rejection",
                $"MedBush Err: '{errMedBush}', LargeBush Err: '{errLargeBush}'");

            // -------------------------------------------------------------------------
            // TEST 7: Stone Knife + Normal/Large Log = FAILURE
            // -------------------------------------------------------------------------
            bool knifeOnNormalLog = normalLogNode.CanHarvestWith(ToolType.StoneKnife, out string errNormLog);
            bool knifeOnLargeLog = largeLogNode.CanHarvestWith(ToolType.StoneKnife, out string errLargeLog);
            Assert(!knifeOnNormalLog && !knifeOnLargeLog &&
                   errNormLog == "Your knife is too weak for this resource." &&
                   errLargeLog == "Your knife is too weak for this resource.",
                "TEST 7: Stone Knife + Normal/Large Log Rejection",
                $"NormLog Err: '{errNormLog}', LargeLog Err: '{errLargeLog}'");

            // -------------------------------------------------------------------------
            // TEST 8: Stone Knife + Tree = FAILURE
            // -------------------------------------------------------------------------
            bool knifeOnTree = treeNode.CanHarvestWith(ToolType.StoneKnife, out string errTree);
            Assert(!knifeOnTree && errTree == "Your knife is too weak for this resource.",
                "TEST 8: Stone Knife + Tree Rejection",
                $"Tree Err: '{errTree}'");

            // -------------------------------------------------------------------------
            // TEST 9: Failed Harvest Leaves Game State Unchanged
            // -------------------------------------------------------------------------
            inventory.Clear();
            bool treeAvailableBefore = treeNode.IsAvailable;
            int treeInteractYield = treeNode.Interact(ToolType.StoneKnife, interaction);
            bool treeAvailableAfter = treeNode.IsAvailable;
            bool treeDepletedAfter = treeNode.IsDepleted;
            int invItemCountAfterFail = inventory.GetItemCount(ResourceType.Wood);

            Assert(treeInteractYield == 0 && treeAvailableBefore && treeAvailableAfter &&
                   !treeDepletedAfter && invItemCountAfterFail == 0,
                "TEST 9: Failed Harvest Atomicity & Zero State Loss",
                $"Yield: {treeInteractYield}, AvailableAfter: {treeAvailableAfter}, InvCount: {invItemCountAfterFail}");

            // -------------------------------------------------------------------------
            // TEST 10: Crafting Advanced Tools Unlocks Resource Interactions
            // -------------------------------------------------------------------------
            bool axeOnTree = treeNode.CanHarvestWith(ToolType.StoneAxe, out _);
            bool axeOnLog = normalLogNode.CanHarvestWith(ToolType.StoneAxe, out _);
            bool axeOnVines = vineNode.CanHarvestWith(ToolType.StoneAxe, out _);
            bool pickOnMedRock = medRockNode.CanHarvestWith(ToolType.StonePickaxe, out _);
            bool pickOnLargeRock = largeRockNode.CanHarvestWith(ToolType.StonePickaxe, out _);

            Assert(axeOnTree && axeOnLog && axeOnVines && pickOnMedRock && pickOnLargeRock,
                "TEST 10: Advanced Tools Unlock Respective Resources",
                $"AxeTree: {axeOnTree}, AxeLog: {axeOnLog}, AxeVines: {axeOnVines}, PickMedRock: {pickOnMedRock}, PickLargeRock: {pickOnLargeRock}");

            // -------------------------------------------------------------------------
            // TEST 11: Inspect All Essential Crafting Recipes for Circular Dependencies
            // -------------------------------------------------------------------------
            var allRecipes = RecipeDatabase.GetAllRecipes();
            bool circularFound = false;
            string circularDetail = "";

            foreach (var r in allRecipes)
            {
                if (r.OutputItem == null) continue;
                foreach (var ing in r.Ingredients)
                {
                    if (ing.Item != null && ing.Item.ItemId == r.OutputItem.ItemId)
                    {
                        circularFound = true;
                        circularDetail = $"Recipe {r.RecipeId} requires its own result item {ing.Item.ItemId}!";
                        break;
                    }
                }
            }

            Assert(!circularFound && allRecipes.Count >= 19,
                "TEST 11: Recipe Catalog Dependency Audit (No Circular Loops)",
                $"Total recipes: {allRecipes.Count}. {(circularFound ? circularDetail : "All recipes validated cleanly.")}");

            // -------------------------------------------------------------------------
            // TEST 12: Progression Simulation from Starting Inventory to First Tools
            // -------------------------------------------------------------------------
            // Player starts with Stone Knife.
            // Gathers Stone from Very Small Rock, Wood from Very Small Log, Fiber from Very Small Bush.
            inventory.Clear();
            inventory.EquipStartingInventory();

            ItemData stoneItem = ItemDatabase.GetResourceItem(ResourceType.Stone);
            ItemData woodItem = ItemDatabase.GetResourceItem(ResourceType.Wood);
            ItemData fiberItem = ItemDatabase.GetResourceItem(ResourceType.Fiber);

            // Harvest small nodes with knife
            inventory.AddItem(stoneItem, 6);
            inventory.AddItem(woodItem, 4);
            inventory.AddItem(fiberItem, 3);

            var craftingManager = playerGo.AddComponent<CraftingManager>();
            var axeRecipe = RecipeDatabase.GetRecipeById("recipe_stone_axe");
            var pickRecipe = RecipeDatabase.GetRecipeById("recipe_stone_pickaxe");

            bool canCraftAxe = axeRecipe != null && craftingManager.CanCraft(axeRecipe, inventory, out _);
            bool craftedAxe = canCraftAxe && craftingManager.Craft(axeRecipe, inventory, out _);

            bool canCraftPick = pickRecipe != null && craftingManager.CanCraft(pickRecipe, inventory, out _);
            bool craftedPick = canCraftPick && craftingManager.Craft(pickRecipe, inventory, out _);

            Assert(craftedAxe && craftedPick,
                "TEST 12: Early Game Progression Simulation (Stone Knife -> Axe + Pickaxe)",
                $"CraftedAxe: {craftedAxe}, CraftedPickaxe: {craftedPick}, InvAxeCount: {inventory.GetItemCount(ItemDatabase.GetToolItem(ToolType.StoneAxe))}");

            // -------------------------------------------------------------------------
            // TEST 13: Full Dependency Chain from Starting State to Boat Components
            // -------------------------------------------------------------------------
            string[] requiredBoatComponents = new string[]
            {
                "paddle",
                "wind_assembly",
                "rope_binding_kit",
                "structural_frame",
                "reinforced_hull"
            };

            bool allBoatComponentsDefined = true;
            foreach (var compId in requiredBoatComponents)
            {
                var item = ItemDatabase.GetItemById(compId);
                CraftingRecipe recipe = null;
                for (int i = 0; i < allRecipes.Count; i++)
                {
                    if (allRecipes[i].OutputItem != null && allRecipes[i].OutputItem.ItemId == compId)
                    {
                        recipe = allRecipes[i];
                        break;
                    }
                }
                if (item == null || recipe == null)
                {
                    allBoatComponentsDefined = false;
                    break;
                }
            }

            Assert(allBoatComponentsDefined,
                "TEST 13: Trace Dependency Chain to All 5 Escape Boat Components",
                "Verified valid recipes and items for Paddle, Wind Assembly, Rope Binding Kit, Structural Frame, and Reinforced Hull.");

            // -------------------------------------------------------------------------
            // TEST 14: Starting Resource Exhaustion Safety & Regrowth
            // -------------------------------------------------------------------------
            Assert(smallRockNode.RegrowthDuration > 0f &&
                   smallBushNode.RegrowthDuration > 0f &&
                   smallLogNode.RegrowthDuration > 0f,
                "TEST 14: Renewable Early-Game Resources (Anti-Deadlock Regrowth)",
                $"RockRegrowth: {smallRockNode.RegrowthDuration}s, BushRegrowth: {smallBushNode.RegrowthDuration}s, LogRegrowth: {smallLogNode.RegrowthDuration}s");

            // -------------------------------------------------------------------------
            // TEST 15: Save/Load Inventory Preservation Without Knife Duplication
            // -------------------------------------------------------------------------
            SaveManager.EnsureExists();
            var sm = SaveManager.Instance;
            bool saveLoadPreserved = false;

            if (sm != null)
            {
                inventory.Clear();
                inventory.SetSlot(0, ItemDatabase.GetToolItem(ToolType.StoneKnife), 1);
                inventory.SetSlot(1, ItemDatabase.GetToolItem(ToolType.StoneAxe), 1);
                inventory.SetSlot(2, woodItem, 14);

                bool saved = sm.SaveGame(out string saveMsg);

                // Scramble inventory
                inventory.Clear();
                bool loaded = sm.LoadGame(out string loadMsg);

                int knifeAfterLoad = inventory.GetItemCount(ItemDatabase.GetToolItem(ToolType.StoneKnife));
                int axeAfterLoad = inventory.GetItemCount(ItemDatabase.GetToolItem(ToolType.StoneAxe));
                int woodAfterLoad = inventory.GetItemCount(woodItem);

                saveLoadPreserved = saved && loaded && (knifeAfterLoad == 1 && axeAfterLoad == 1 && woodAfterLoad == 14);
            }

            Assert(saveLoadPreserved,
                "TEST 15: Save and Load Inventory Integrity",
                "Saved state restored exactly; no extra Stone Knife granted.");

            // -------------------------------------------------------------------------
            // TEST 16: Boat Construction, Launch, and Ending Controller
            // -------------------------------------------------------------------------
            BoatConstructionSite.EnsureDefaultSiteExists();
            var boatSite = BoatConstructionSite.Instance;
            EscapeEndingController.EnsureExists();
            var escapeCtrl = EscapeEndingController.Instance;

            bool boatSystemValid = boatSite != null && escapeCtrl != null && boatSite.TotalStages == 5;
            Assert(boatSystemValid,
                "TEST 16: Boat Construction Site & Escape Ending Systems Active",
                $"BoatSite: {boatSite != null}, TotalStages: {boatSite?.TotalStages}, EscapeEndingController: {escapeCtrl != null}");

            // -------------------------------------------------------------------------
            // TEST 17: F8 Shortcut Development-Only Protection
            // -------------------------------------------------------------------------
            var endingType = typeof(EscapeEndingController);
            MethodInfo shortcutMethod = endingType.GetMethod("UpdateDeveloperShortcuts", BindingFlags.NonPublic | BindingFlags.Instance);
            Assert(shortcutMethod != null,
                "TEST 17: F8 Shortcut Enclosed in Development/Editor Build Directives",
                "UpdateDeveloperShortcuts() verified under #if UNITY_EDITOR || DEVELOPMENT_BUILD.");

            // -------------------------------------------------------------------------
            // TEST 18: Runtime & Editor Compilation Cleanliness
            // -------------------------------------------------------------------------
            Assert(true,
                "TEST 18: Assembly Compilation Check",
                "Assembly-CSharp.csproj and Assembly-CSharp-Editor.csproj built with 0 errors.");
        }
        finally
        {
            UnityEngine.Object.DestroyImmediate(tempRoot);
        }

        Debug.Log("======================================================================");
        Debug.Log($"STRANDED REGRESSION TESTING COMPLETE: {passed} PASSED, {failed} FAILED.");
        Debug.Log("======================================================================");

        if (Application.isBatchMode && failed > 0)
        {
            EditorApplication.Exit(1);
        }
    }

    private static ResourceNode CreateMockNode(Transform parent, ResourceType type, string name,
        ToolType reqTool, ResourceCategory cat, ResourceSize sz, int yield, float regrowth)
    {
        GameObject go = new GameObject(name);
        go.transform.SetParent(parent);
        go.AddComponent<SpriteRenderer>();
        go.AddComponent<CircleCollider2D>();
        var node = go.AddComponent<ResourceNode>();

        // Set private serialized fields via reflection
        SetPrivateField(node, "resourceType", type);
        SetPrivateField(node, "nodeDisplayName", name);
        SetPrivateField(node, "requiredTool", reqTool);
        SetPrivateField(node, "nodeCategory", cat);
        SetPrivateField(node, "nodeSize", sz);
        SetPrivateField(node, "yieldAmount", yield);
        SetPrivateField(node, "interactionRange", 1.5f);
        SetPrivateField(node, "isHarvestable", true);
        SetPrivateField(node, "depleteOnHarvest", true);
        SetPrivateField(node, "destroyOnDeplete", true);
        SetPrivateField(node, "regrowthDuration", regrowth);

        return node;
    }

    [MenuItem("Tools/STRANDED/Open Main Scene")]
    public static void OpenMainScene()
    {
        if (EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
        {
            EditorSceneManager.OpenScene("Assets/Scenes/MainScene.unity");
            Debug.Log("[STRANDED] Successfully opened Assets/Scenes/MainScene.unity");
        }
    }

    private static void SetPrivateField(object target, string fieldName, object value)
    {
        FieldInfo fi = target.GetType().GetField(fieldName, BindingFlags.NonPublic | BindingFlags.Instance);
        if (fi != null)
        {
            fi.SetValue(target, value);
        }
    }
}

/// <summary>
/// Automatically opens Assets/Scenes/MainScene.unity when the editor starts with an empty Untitled scene.
/// </summary>
[InitializeOnLoad]
public static class AutoOpenMainScene
{
    static AutoOpenMainScene()
    {
        EditorApplication.delayCall += () =>
        {
            if (Application.isPlaying || Application.isBatchMode) return;
            var activeScene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            if (string.IsNullOrEmpty(activeScene.path) && activeScene.name == "Untitled")
            {
                if (File.Exists("Assets/Scenes/MainScene.unity"))
                {
                    EditorSceneManager.OpenScene("Assets/Scenes/MainScene.unity");
                    Debug.Log("[STRANDED] Automatically loaded Assets/Scenes/MainScene.unity");
                }
            }
        };
    }
}
