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
    FishingRod = 4
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
            case ToolType.None:
            default: return "None";
        }
    }
}
