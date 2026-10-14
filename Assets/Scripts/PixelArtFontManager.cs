using UnityEngine;

/// <summary>
/// Provides centralized access to authentic pixel art fonts for STRANDED UI.
/// Supports both runtime (Resources.Load) and Unity Editor asset loading.
/// </summary>
public static class PixelArtFontManager
{
    private static Font regularFont;
    private static Font boldFont;
    private static Font titleFont;

    public static Font Regular
    {
        get
        {
            if (regularFont == null) regularFont = LoadFont("PixelArtFont");
            return regularFont;
        }
    }

    public static Font Bold
    {
        get
        {
            if (boldFont == null) boldFont = LoadFont("PixelArtFont-Bold") ?? Regular;
            return boldFont;
        }
    }

    public static Font Title
    {
        get
        {
            if (titleFont == null) titleFont = LoadFont("PixelArtFont-Title") ?? Bold;
            return titleFont;
        }
    }

    private static Font LoadFont(string name)
    {
        // 1. Runtime Resources folder
        Font font = Resources.Load<Font>("Fonts/" + name);
        if (font != null) return font;

#if UNITY_EDITOR
        // 2. AssetDatabase editor lookup
        font = UnityEditor.AssetDatabase.LoadAssetAtPath<Font>("Assets/Art/Fonts/" + name + ".ttf");
        if (font != null) return font;

        font = UnityEditor.AssetDatabase.LoadAssetAtPath<Font>("Assets/Resources/Fonts/" + name + ".ttf");
        if (font != null) return font;
#endif

        return null;
    }
}
