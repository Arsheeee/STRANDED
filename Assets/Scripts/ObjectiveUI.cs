using UnityEngine;
using UnityEngine.InputSystem;

/// <summary>
/// Unobtrusive, Stardew Valley-styled HUD banner for displaying the current objective in STRANDED.
/// Positioned at (20, 165) directly below the top-left inventory tracker.
/// Shows objective title, active step instruction, and a mini progress bar.
/// Suppressed during full modal windows (Inventory, Crafting, Boat UI) to prevent visual clutter.
/// </summary>
public class ObjectiveUI : MonoBehaviour
{
    private static bool isVisible = true;
    public static bool IsVisible => isVisible;

    private ObjectiveManager manager;

    private Texture2D panelTex;
    private Texture2D barBgTex;
    private Texture2D barFillTex;
    private Texture2D goldBorderTex;

    private GUIStyle headerStyle;
    private GUIStyle stepStyle;
    private GUIStyle badgeStyle;
    private GUIStyle progressTextStyle;

    void Awake()
    {
        CreateTextures();
    }

    void Start()
    {
        manager = ObjectiveManager.Instance;
        if (manager == null) manager = ObjectiveManager.EnsureExists();
    }

    void Update()
    {
        // Optional toggle with 'O' key
        if (Keyboard.current != null && Keyboard.current.oKey.wasPressedThisFrame)
        {
            isVisible = !isVisible;
            string stateStr = isVisible ? "Visible" : "Hidden";
            TemporaryResourceHUD.Instance?.ShowNotification($"Objectives HUD: {stateStr} (Press 'O' to toggle)", Color.gray);
        }
    }

    private void CreateTextures()
    {
        panelTex = new Texture2D(1, 1);
        panelTex.SetPixel(0, 0, new Color(0.12f, 0.14f, 0.18f, 0.88f));
        panelTex.Apply();

        goldBorderTex = new Texture2D(1, 1);
        goldBorderTex.SetPixel(0, 0, new Color(0.85f, 0.65f, 0.28f, 0.95f));
        goldBorderTex.Apply();

        barBgTex = new Texture2D(1, 1);
        barBgTex.SetPixel(0, 0, new Color(0.08f, 0.09f, 0.11f, 0.90f));
        barBgTex.Apply();

        barFillTex = new Texture2D(1, 1);
        barFillTex.SetPixel(0, 0, new Color(0.35f, 0.85f, 0.45f, 0.95f));
        barFillTex.Apply();
    }

    private void InitStyles()
    {
        if (headerStyle == null)
        {
            headerStyle = new GUIStyle(GUI.skin.label);
            headerStyle.fontSize = 15;
            headerStyle.fontStyle = FontStyle.Bold;
            headerStyle.normal.textColor = new Color(1.0f, 0.86f, 0.45f); // Warm gold
        }

        if (stepStyle == null)
        {
            stepStyle = new GUIStyle(GUI.skin.label);
            stepStyle.fontSize = 14;
            stepStyle.wordWrap = true;
            stepStyle.normal.textColor = new Color(0.92f, 0.94f, 0.96f);
        }

        if (badgeStyle == null)
        {
            badgeStyle = new GUIStyle(GUI.skin.label);
            badgeStyle.fontSize = 13;
            badgeStyle.fontStyle = FontStyle.Bold;
            badgeStyle.alignment = TextAnchor.MiddleCenter;
            badgeStyle.normal.textColor = new Color(0.55f, 0.85f, 1.0f);
        }

        if (progressTextStyle == null)
        {
            progressTextStyle = new GUIStyle(GUI.skin.label);
            progressTextStyle.fontSize = 12;
            progressTextStyle.fontStyle = FontStyle.Bold;
            progressTextStyle.alignment = TextAnchor.MiddleRight;
            progressTextStyle.normal.textColor = new Color(0.75f, 0.82f, 0.90f);
        }
    }

    void OnGUI()
    {
        if (!isVisible) return;

        // Hide when fullscreen / modal menus are open
        if (BoatConstructionUI.IsOpen || InventoryUI.IsOpen || CraftingUI.IsOpen) return;

        if (manager == null) manager = ObjectiveManager.Instance;
        if (manager == null) return;

        InitStyles();

        float x = 20f;
        float y = 165f;
        float width = 640f;
        float height = 76f;

        Rect outerRect = new Rect(x, y, width, height);

        // Gold border outline
        GUI.DrawTexture(outerRect, goldBorderTex);

        // Dark inner panel
        Rect innerRect = new Rect(x + 2f, y + 2f, width - 4f, height - 4f);
        GUI.DrawTexture(innerRect, panelTex);

        // Content layout
        GUILayout.BeginArea(innerRect);
        GUILayout.Space(4);

        // Header line: ★ CURRENT OBJECTIVE: {Title}
        GUILayout.BeginHorizontal();
        GUILayout.Space(8);
        string headerText = $"★ OBJECTIVE:  {manager.Title.ToUpper()}";
        GUILayout.Label(headerText, headerStyle, GUILayout.Width(440));

        // Right side: Progress label
        string progText = manager.ProgressText;
        GUILayout.Label(progText, progressTextStyle, GUILayout.Width(170));
        GUILayout.EndHorizontal();

        GUILayout.Space(2);

        // Description line
        GUILayout.BeginHorizontal();
        GUILayout.Space(10);
        GUILayout.Label(manager.Description, stepStyle, GUILayout.Width(600), GUILayout.Height(22));
        GUILayout.EndHorizontal();

        GUILayout.Space(2);

        // Progress mini-bar at bottom
        float barWidth = 612f;
        float barHeight = 8f;
        Rect barRect = new Rect(10f, height - 16f, barWidth, barHeight);
        GUI.DrawTexture(barRect, barBgTex);

        float fillRatio = Mathf.Clamp01(manager.ProgressNormalized);
        if (fillRatio > 0f)
        {
            Rect fillRect = new Rect(10f, height - 16f, barWidth * fillRatio, barHeight);
            GUI.DrawTexture(fillRect, barFillTex);
        }

        GUILayout.EndArea();
    }
}
