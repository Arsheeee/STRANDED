using System;

/// <summary>
/// Primitive tool types for STRANDED survival game.
/// All tools are primitive stone/wood tier; no modern metals, iron, steel, or ores exist.
/// </summary>
public enum ToolType
{
    None = 0,
    StoneKnife = 1,
    StoneAxe = 2,
    StonePickaxe = 3,
    FishingRod = 4,
    ImprovedKnife = 5,
    WoodenMallet = 6,
    FiberTwister = 7,
    WeavingFrame = 8
}

/// <summary>
/// Extension methods for ToolType providing user-friendly display names.
/// </summary>
public static class ToolExtensions
{
    public static string ToDisplayName(this ToolType tool)
    {
        switch (tool)
        {
            case ToolType.StoneKnife: return "Stone Knife";
            case ToolType.StoneAxe: return "Stone Axe";
            case ToolType.StonePickaxe: return "Stone Pickaxe";
            case ToolType.FishingRod: return "Fishing Rod";
            case ToolType.ImprovedKnife: return "Improved Cutting Knife";
            case ToolType.WoodenMallet: return "Wooden Mallet";
            case ToolType.FiberTwister: return "Fiber Twisting Tool";
            case ToolType.WeavingFrame: return "Weaving Frame";
            case ToolType.None:
            default: return "None";
        }
    }

    public static string GetDisplayName(this ToolType tool)
    {
        return tool.ToDisplayName();
    }
}
