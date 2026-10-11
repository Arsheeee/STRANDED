using UnityEngine;

/// <summary>
/// Survival HUD for STRANDED (Batch 6).
/// Displays real-time Health, Hunger, Thirst, and Energy status bars.
/// Positioned in the bottom-right corner to complement the hotbar and avoid screen clutter.
/// Also displays resting state and the Game Over death/respawn modal.
/// </summary>
public class SurvivalHUD : MonoBehaviour
{
    private SurvivalStats survivalStats;

    private Texture2D panelTex;
    private Texture2D barBgTex;
    private Texture2D whiteTex;

    private GUIStyle labelStyle;
    private GUIStyle headerStyle;
    private GUIStyle gameOverTitleStyle;
    private GUIStyle gameOverSubStyle;
    private GUIStyle respawnBtnStyle;

    void Awake()
    {
        survivalStats = GetComponent<SurvivalStats>();
        CreateTextures();
    }

    void Start()
    {
        if (survivalStats == null) survivalStats = FindAnyObjectByType<SurvivalStats>();
    }

    private void CreateTextures()
    {
        whiteTex = new Texture2D(1, 1);
        whiteTex.SetPixel(0, 0, Color.white);
        whiteTex.Apply();

        barBgTex = new Texture2D(1, 1);
        barBgTex.SetPixel(0, 0, new Color(0.12f, 0.08f, 0.05f, 0.85f));
        barBgTex.Apply();

        panelTex = new Texture2D(1, 1);
        panelTex.SetPixel(0, 0, new Color(0.18f, 0.12f, 0.08f, 0.90f));
        panelTex.Apply();
    }

    private void InitStyles()
    {
        if (labelStyle == null)
        {
            labelStyle = new GUIStyle(GUI.skin.label);
            labelStyle.fontSize = 13;
            labelStyle.fontStyle = FontStyle.Bold;
            labelStyle.alignment = TextAnchor.MiddleLeft;
            labelStyle.normal.textColor = Color.white;
        }

        if (headerStyle == null)
        {
            headerStyle = new GUIStyle(GUI.skin.label);
            headerStyle.fontSize = 14;
            headerStyle.fontStyle = FontStyle.Bold;
            headerStyle.alignment = TextAnchor.MiddleCenter;
            headerStyle.normal.textColor = new Color(1.0f, 0.88f, 0.45f);
        }

        if (gameOverTitleStyle == null)
        {
            gameOverTitleStyle = new GUIStyle(GUI.skin.label);
            gameOverTitleStyle.fontSize = 32;
            gameOverTitleStyle.fontStyle = FontStyle.Bold;
            gameOverTitleStyle.alignment = TextAnchor.MiddleCenter;
            gameOverTitleStyle.normal.textColor = new Color(0.95f, 0.20f, 0.20f);
        }

        if (gameOverSubStyle == null)
        {
            gameOverSubStyle = new GUIStyle(GUI.skin.label);
            gameOverSubStyle.fontSize = 16;
            gameOverSubStyle.fontStyle = FontStyle.Bold;
            gameOverSubStyle.alignment = TextAnchor.MiddleCenter;
            gameOverSubStyle.normal.textColor = new Color(0.90f, 0.85f, 0.80f);
        }

        if (respawnBtnStyle == null)
        {
            respawnBtnStyle = new GUIStyle(GUI.skin.button);
            respawnBtnStyle.fontSize = 18;
            respawnBtnStyle.fontStyle = FontStyle.Bold;
            respawnBtnStyle.alignment = TextAnchor.MiddleCenter;
            respawnBtnStyle.normal.textColor = Color.white;
        }
    }

    void OnGUI()
    {
        if (survivalStats == null)
        {
            survivalStats = FindAnyObjectByType<SurvivalStats>();
            if (survivalStats == null) return;
        }

        InitStyles();

        // 1. Draw In-Game Survival HUD (Bottom-Right Corner)
        DrawSurvivalBars();

        // 2. Draw Game Over Overlay if dead
        if (survivalStats.IsDead)
        {
            DrawGameOverModal();
        }
    }

    private void DrawSurvivalBars()
    {
        float hudWidth = 250f;
        float hudHeight = 148f;
        float hudX = Screen.width - hudWidth - 20f;
        float hudY = Screen.height - hudHeight - 20f;

        Rect hudRect = new Rect(hudX, hudY, hudWidth, hudHeight);

        // Outer Dark Wood Border
        DrawRect(new Rect(hudX - 3, hudY - 3, hudWidth + 6, hudHeight + 6), new Color(0.42f, 0.24f, 0.10f, 1f));
        // Inner Container
        GUI.DrawTexture(hudRect, panelTex);

        // Header Title
        string headerText = survivalStats.IsResting ? "<color=#ffd700>★ RESTING [R] ★</color>" : "SURVIVAL VITALS";
        GUI.Label(new Rect(hudX, hudY + 4, hudWidth, 20), headerText, headerStyle);

        // Bar Metrics
        float startBarY = hudY + 28f;
        float barH = 22f;
        float barSpacing = 6f;
        float barW = hudWidth - 28f;
        float barX = hudX + 14f;

        // 1. HEALTH (Red)
        DrawStatBar(barX, startBarY, barW, barH, "HP", survivalStats.CurrentHealth, survivalStats.MaxHealth, new Color(0.85f, 0.20f, 0.20f), new Color(0.50f, 0.10f, 0.10f));

        // 2. HUNGER (Orange)
        DrawStatBar(barX, startBarY + (barH + barSpacing), barW, barH, "HUNGER", survivalStats.CurrentHunger, survivalStats.MaxHunger, new Color(0.92f, 0.45f, 0.05f), new Color(0.55f, 0.25f, 0.02f));

        // 3. THIRST (Cyan/Blue)
        DrawStatBar(barX, startBarY + (barH + barSpacing) * 2, barW, barH, "THIRST", survivalStats.CurrentThirst, survivalStats.MaxThirst, new Color(0.10f, 0.65f, 0.90f), new Color(0.05f, 0.35f, 0.50f));

        // 4. ENERGY (Yellow/Gold)
        DrawStatBar(barX, startBarY + (barH + barSpacing) * 3, barW, barH, "ENERGY", survivalStats.CurrentEnergy, survivalStats.MaxEnergy, new Color(0.95f, 0.78f, 0.15f), new Color(0.55f, 0.42f, 0.05f));
    }

    private void DrawStatBar(float x, float y, float w, float h, string statName, float current, float max, Color fillColor, Color borderColor)
    {
        Rect barRect = new Rect(x, y, w, h);

        // Border
        DrawRect(new Rect(x - 1, y - 1, w + 2, h + 2), borderColor);
        // Background
        GUI.DrawTexture(barRect, barBgTex);

        // Fill Proportion
        float ratio = Mathf.Clamp01(current / Mathf.Max(1f, max));
        if (ratio > 0f)
        {
            Rect fillRect = new Rect(x, y, w * ratio, h);
            DrawRect(fillRect, fillColor);
        }

        // Text Overlay: e.g. "HP: 100/100"
        string statText = $"{statName}: {Mathf.CeilToInt(current)}/{Mathf.CeilToInt(max)}";
        GUI.Label(new Rect(x + 8, y, w - 16, h), statText, labelStyle);
    }

    private void DrawGameOverModal()
    {
        // Dark crimson wash overlay
        DrawRect(new Rect(0, 0, Screen.width, Screen.height), new Color(0.15f, 0.02f, 0.02f, 0.85f));

        float modalW = 540f;
        float modalH = 340f;
        float modalX = (Screen.width - modalW) * 0.5f;
        float modalY = (Screen.height - modalH) * 0.5f;

        Rect modalRect = new Rect(modalX, modalY, modalW, modalH);

        // Warm parchment dialog box with dark wood trim
        DrawRect(new Rect(modalX - 4, modalY - 4, modalW + 8, modalH + 8), new Color(0.35f, 0.18f, 0.08f, 1f));
        DrawRect(modalRect, new Color(0.20f, 0.14f, 0.10f, 0.98f));

        // Header Title
        GUI.Label(new Rect(modalX, modalY + 30, modalW, 40), "YOU DID NOT SURVIVE", gameOverTitleStyle);

        // Cause of Death
        string causeText = $"Succumbed to: {survivalStats.DeathCause}";
        GUI.Label(new Rect(modalX, modalY + 80, modalW, 28), causeText, gameOverSubStyle);

        // Narrative details
        string flavorText = "The harsh island elements have claimed you.\nYour vitals have depleted.\nAwaken once more at your camp sanctuary.";
        GUI.Label(new Rect(modalX + 30, modalY + 120, modalW - 60, 65), flavorText, gameOverSubStyle);

        // Prominent Respawn Button
        Rect btnRect = new Rect(modalX + 70, modalY + 220, modalW - 140, 56);
        if (GUI.Button(btnRect, "RESPAWN AT CAMP", respawnBtnStyle))
        {
            survivalStats.Respawn();
        }
    }

    private void DrawRect(Rect rect, Color color)
    {
        Color prev = GUI.color;
        GUI.color = color;
        GUI.DrawTexture(rect, whiteTex);
        GUI.color = prev;
    }
}
