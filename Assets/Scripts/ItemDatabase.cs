using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

/// <summary>
/// Central registry and catalog for all primitive items and tools in STRANDED.
/// Initializes and provides instant lookup for resource items and tool items.
/// </summary>
public static class ItemDatabase
{
    private static readonly Dictionary<string, ItemData> itemsById = new Dictionary<string, ItemData>(StringComparer.OrdinalIgnoreCase);
    private static readonly Dictionary<ResourceType, ItemData> itemsByResource = new Dictionary<ResourceType, ItemData>();
    private static readonly Dictionary<ToolType, ItemData> itemsByTool = new Dictionary<ToolType, ItemData>();
    private static bool isInitialized = false;

    public static void EnsureInitialized()
    {
        if (isInitialized) return;
        isInitialized = true;

        itemsById.Clear();
        itemsByResource.Clear();
        itemsByTool.Clear();

        // 1. Primitive Raw Resources (Non-consumable)
        RegisterResource(ResourceType.Wood, "wood", "Wood", "Sturdy timber chopped from island trees and driftwood.", "item_wood.png");
        RegisterResource(ResourceType.Stone, "stone", "Stone", "Dense raw stones gathered from island rocks and boulders.", "item_stone.png");
        RegisterResource(ResourceType.Fiber, "fiber", "Fiber", "Pliable plant fibers and ferns cut from island foliage.", "item_fiber.png");
        RegisterResource(ResourceType.Vines, "vines", "Vines", "Tough, pliable jungle creepers. Used for spinning cordage and weaving sailcloth.", "item_vines.png");

        // 2. Consumable Foods & Drinks
        RegisterConsumable(ResourceType.Berries, "berries", "Berries", "Sweet wild island berries gathered from bushes. Satisfies hunger.", "item_berry.png", hunger: 15f, thirst: 0f, health: 0f, energy: 5f);
        RegisterConsumable(ResourceType.Coconut, "coconut", "Coconut", "Hard tropical coconut. Crack open for rich meat and hydrating coconut water.", "item_coconut.png", hunger: 20f, thirst: 15f, health: 0f, energy: 5f);
        RegisterConsumable(ResourceType.Fish, "fish", "Raw Fish", "Freshly caught coastal raw fish. Nutritious, but best cooked over fire.", "item_fish.png", hunger: 8f, thirst: 0f, health: -2f, energy: 2f);

        // Foraging batch: Mushrooms & Berries (Edible and Poisonous - 50% life loss on poison)
        RegisterSpecialConsumable("poison_berries", "Nightshade Berries", "Wild toxic berries with a deceiving glint. Highly poisonous! Eating inflicts 50% life loss.", "item_poison_berry.png", hunger: 4f, thirst: 0f, health: -50f, energy: -25f);
        RegisterSpecialConsumable("mushroom", "Island Morel", "Earthy wild edible mushroom with a honeycomb cap. Delicious and highly nutritious.", "item_mushroom.png", hunger: 22f, thirst: 2f, health: 8f, energy: 12f);
        RegisterSpecialConsumable("morel", "Honeycomb Morel", "Rare woodland edible morel with deep earthy flavor. Nutritious and restorative.", "item_morel.png", hunger: 25f, thirst: 2f, health: 10f, energy: 15f);
        RegisterSpecialConsumable("poison_mushroom", "Crimson Toadstool", "Vibrant scarlet mushroom covered in pale toxic warts. Extremely poisonous! Eating inflicts 50% life loss.", "item_poison_mushroom.png", hunger: 4f, thirst: 0f, health: -50f, energy: -25f);
        RegisterSpecialConsumable("chanterelle", "Golden Chanterelle", "Fragrant golden woodland mushroom. Rich flavor that restores health and vitality.", "item_chanterelle.png", hunger: 24f, thirst: 2f, health: 12f, energy: 15f);
        RegisterSpecialConsumable("purple_mushroom", "Purple Cave Mushroom", "Luminous deep-purple island mushroom prized for its rare restorative properties.", "item_purple_mushroom.png", hunger: 20f, thirst: 4f, health: 15f, energy: 20f);
        RegisterSpecialConsumable("blackberry", "Wild Blackberry", "Plump sweet wild bramble berry. Delicious snack that staves off hunger.", "item_blackberry.png", hunger: 16f, thirst: 4f, health: 4f, energy: 8f);

        // Architecture prepared for future cooking batch: Cooked Fish
        RegisterSpecialConsumable("cooked_fish", "Cooked Fish", "Tender fish fillet grilled over campfire embers. Hearty and restorative.", "item_fish.png", hunger: 35f, thirst: 0f, health: 15f, energy: 15f);

        // 3. Primitive Tools (Non-stackable, MaxStack = 1)
        RegisterTool(ToolType.StoneKnife, "tool_stone_knife", "Stone Knife", "Sharp carved stone knife tied to a wood handle. Cuts fibers.", "tool_stone_knife.png");
        RegisterTool(ToolType.StoneAxe, "tool_stone_axe", "Stone Axe", "Chipped flint axe lashed to a sturdy wooden shaft. Fells trees.", "tool_stone_axe.png");
        RegisterTool(ToolType.StonePickaxe, "tool_stone_pickaxe", "Stone Pickaxe", "Pointed rock pick bound with fiber rope. Breaks boulders.", "tool_stone_pickaxe.png");
        RegisterTool(ToolType.FishingRod, "tool_fishing_rod", "Fishing Rod", "Flexible pole with vine cord and bone hook.", "tool_fishing_rod.png");

        // 4. Advanced Primitive Equipment (Non-stackable, MaxStack = 1)
        RegisterTool(ToolType.ImprovedKnife, "tool_improved_knife", "Improved Cutting Knife", "Precision stone blade bound with vines. Essential for shaping wooden boat parts.", "tool_improved_knife.png");
        RegisterTool(ToolType.WoodenMallet, "tool_wooden_mallet", "Wooden Mallet", "Heavy hardwood mallet. Drives pegs and secures reinforced structural joints.", "tool_wooden_mallet.png");
        RegisterTool(ToolType.FiberTwister, "tool_fiber_twister", "Fiber Twisting Tool", "Twisting spindle that braids fibers and vines into strong nautical ropes.", "tool_fiber_twister.png");
        RegisterTool(ToolType.WeavingFrame, "tool_weaving_frame", "Weaving Frame", "Portable wooden loom used to weave fibrous sailcloth for the escape boat.", "tool_weaving_frame.png");

        // 5. Processed Materials (Stackable, MaxStack = 99)
        RegisterMaterial("shaped_wood", "Shaped Wooden Parts", "Carefully carved and planed timber ribs for structural boat assemblies.", "item_shaped_wood.png");
        RegisterMaterial("wooden_pegs", "Wooden Pegs", "Carved hardwood dowel fasteners used to pin wooden components together.", "item_wooden_pegs.png");
        RegisterMaterial("strong_rope", "Strong Rope", "Tightly twisted cordage braided from fiber and tough jungle vines.", "item_strong_rope.png");
        RegisterMaterial("reinforced_rope", "Reinforced Rope", "Heavy-duty braided nautical rope bound with double vine wraps for heavy loads.", "item_reinforced_rope.png");
        RegisterMaterial("woven_sailcloth", "Woven Sailcloth", "Dense, flexible canvas woven from island fibers and vines on a weaving frame.", "item_woven_sailcloth.png");
        RegisterMaterial("reinforced_joints", "Reinforced Wooden Joints", "Mortise and tenon wooden joints pegged and lashed for high-stress framing.", "item_reinforced_joints.png");

        // 6. Boat Components (Non-stackable, MaxStack = 1)
        RegisterComponent("paddle", "Paddle", "Carved wooden canoe paddle with broad blade. Essential navigation component for the escape boat.", "item_paddle.png");
        RegisterComponent("wind_assembly", "Wind-Catching Assembly", "Primitive triangular sail mounted on yardarm spar with rigging. Propulsion component for the escape boat.", "item_wind_assembly.png");
        RegisterComponent("rope_binding_kit", "Rope Binding Kit", "Complete set of nautical lashings, coils, and fastening loops for assembling the escape boat.", "item_rope_binding_kit.png");
        RegisterComponent("structural_frame", "Structural Frame", "Rigid timber skeleton of keel stringers and pegged rib supports for the escape boat.", "item_structural_frame.png");
        RegisterComponent("reinforced_hull", "Reinforced Hull", "Buoyant, watertight wooden boat hull reinforced with pegged joints and lashings for the escape boat.", "item_reinforced_hull.png");
    }

    private static void RegisterMaterial(string id, string name, string desc, string spriteFile)
    {
        Sprite icon = LoadItemSprite(spriteFile);
        ItemData item = ItemData.CreateRuntimeInstance(
            id, name, desc, icon,
            ItemType.Resource, ResourceType.Wood, ToolType.None,
            stackable: true, maxStack: 99
        );
        itemsById[id] = item;
    }

    private static void RegisterComponent(string id, string name, string desc, string spriteFile)
    {
        Sprite icon = LoadItemSprite(spriteFile);
        ItemData item = ItemData.CreateRuntimeInstance(
            id, name, desc, icon,
            ItemType.Resource, ResourceType.Wood, ToolType.None,
            stackable: false, maxStack: 1
        );
        itemsById[id] = item;
    }

    private static void RegisterResource(ResourceType resType, string id, string name, string desc, string spriteFile)
    {
        Sprite icon = LoadItemSprite(spriteFile);
        ItemData item = ItemData.CreateRuntimeInstance(
            id, name, desc, icon,
            ItemType.Resource, resType, ToolType.None,
            stackable: true, maxStack: 99
        );
        itemsById[id] = item;
        itemsByResource[resType] = item;
    }

    private static void RegisterConsumable(ResourceType resType, string id, string name, string desc, string spriteFile, float hunger, float thirst, float health, float energy)
    {
        Sprite icon = LoadItemSprite(spriteFile);
        ItemData item = ItemData.CreateRuntimeInstance(
            id, name, desc, icon,
            ItemType.Resource, resType, ToolType.None,
            stackable: true, maxStack: 99,
            consumable: true, hunger: hunger, thirst: thirst, health: health, energy: energy
        );
        itemsById[id] = item;
        itemsByResource[resType] = item;
    }

    private static void RegisterSpecialConsumable(string id, string name, string desc, string spriteFile, float hunger, float thirst, float health, float energy)
    {
        Sprite icon = LoadItemSprite(spriteFile);
        ItemData item = ItemData.CreateRuntimeInstance(
            id, name, desc, icon,
            ItemType.Resource, ResourceType.Fish, ToolType.None,
            stackable: true, maxStack: 99,
            consumable: true, hunger: hunger, thirst: thirst, health: health, energy: energy
        );
        itemsById[id] = item;
        if (!id.StartsWith("item_"))
        {
            itemsById["item_" + id] = item;
        }
        else
        {
            itemsById[id.Substring(5)] = item;
        }
    }

    private static void RegisterTool(ToolType toolType, string id, string name, string desc, string spriteFile)
    {
        Sprite icon = LoadItemSprite(spriteFile);
        ItemData item = ItemData.CreateRuntimeInstance(
            id, name, desc, icon,
            ItemType.Tool, ResourceType.Wood, toolType,
            stackable: false, maxStack: 1
        );
        itemsById[id] = item;
        itemsByTool[toolType] = item;
    }

    public static ItemData GetResourceItem(ResourceType resourceType)
    {
        EnsureInitialized();
        itemsByResource.TryGetValue(resourceType, out ItemData item);
        return item;
    }

    public static ItemData GetToolItem(ToolType toolType)
    {
        EnsureInitialized();
        itemsByTool.TryGetValue(toolType, out ItemData item);
        return item;
    }

    public static ItemData GetItemById(string id)
    {
        EnsureInitialized();
        if (string.IsNullOrEmpty(id)) return null;
        itemsById.TryGetValue(id, out ItemData item);
        return item;
    }

    public static IEnumerable<ItemData> GetAllItems()
    {
        EnsureInitialized();
        return itemsById.Values;
    }

    /// <summary>
    /// Loads a sprite from Assets/Art/Environment/Items/ either via AssetDatabase (Editor)
    /// or by loading the PNG file directly at runtime.
    /// </summary>
    private static Sprite LoadItemSprite(string fileName)
    {
        string relativePath = $"Assets/Art/Environment/Items/{fileName}";

#if UNITY_EDITOR
        Sprite loaded = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(relativePath);
        if (loaded != null) return loaded;
#endif

        if (File.Exists(relativePath))
        {
            try
            {
                byte[] bytes = File.ReadAllBytes(relativePath);
                Texture2D tex = new Texture2D(16, 16, TextureFormat.RGBA32, false);
                tex.filterMode = FilterMode.Point;
                if (tex.LoadImage(bytes))
                {
                    return Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height), new Vector2(0.5f, 0.5f), 16f);
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[ItemDatabase] Failed to load sprite {relativePath}: {ex.Message}");
            }
        }

        return null;
    }
}
