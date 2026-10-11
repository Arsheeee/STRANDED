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

        // 1. Primitive Resources (Stackable to 99)
        RegisterResource(ResourceType.Wood, "wood", "Wood", "Sturdy timber chopped from island trees and driftwood.", "item_wood.png");
        RegisterResource(ResourceType.Stone, "stone", "Stone", "Dense raw stones gathered from island rocks and boulders.", "item_stone.png");
        RegisterResource(ResourceType.Fiber, "fiber", "Fiber", "Pliable plant fibers and ferns cut from island foliage.", "item_fiber.png");
        RegisterResource(ResourceType.Berries, "berries", "Berries", "Sweet wild island berries gathered from bushes.", "item_berry.png");
        RegisterResource(ResourceType.Coconut, "coconut", "Coconut", "Hard tropical coconut gathered from beach palms.", "item_coconut.png");
        RegisterResource(ResourceType.Fish, "fish", "Fish", "Raw coastal fish caught with a fishing rod.", "item_fish.png");

        // 2. Primitive Tools (Non-stackable, MaxStack = 1)
        RegisterTool(ToolType.StoneKnife, "tool_stone_knife", "Stone Knife", "Sharp carved stone knife tied to a wood handle. Cuts fibers.", "tool_stone_knife.png");
        RegisterTool(ToolType.StoneAxe, "tool_stone_axe", "Stone Axe", "Chipped flint axe lashed to a sturdy wooden shaft. Fells trees.", "tool_stone_axe.png");
        RegisterTool(ToolType.StonePickaxe, "tool_stone_pickaxe", "Stone Pickaxe", "Pointed rock pick bound with fiber rope. Breaks boulders.", "tool_stone_pickaxe.png");
        RegisterTool(ToolType.FishingRod, "tool_fishing_rod", "Fishing Rod", "Flexible pole with vine cord and bone hook.", "tool_fishing_rod.png");
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
