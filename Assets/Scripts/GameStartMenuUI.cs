using System;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.SceneManagement;

/// <summary>
/// Pre-game start and loading menu for STRANDED.
/// Appears before the game starts, presenting Resume and Restart (New Game) options.
/// </summary>
public class GameStartMenuUI : MonoBehaviour
{
    private static GameStartMenuUI instance;
    public static GameStartMenuUI Instance => instance;

    private static bool hasDismissedInitialMenu = false;
    private bool isOpen = false;
    public static bool IsOpen => instance != null && instance.isOpen;

    // Textures & Styles
    private Texture2D panelTex;
    private Texture2D darkBackdropTex;

    private GUIStyle titleStyle;
    private GUIStyle subtitleStyle;
    private GUIStyle loreStyle;
    private GUIStyle statusStyle;
    private GUIStyle buttonStyle;
    private GUIStyle startButtonStyle;

    void Awake()
    {
        if (instance != null && instance != this)
        {
            Destroy(gameObject);
            return;
        }
        instance = this;
    }

    void Start()
    {
        LoadTextures();

        // If this is the initial game launch and not a mid-game scene reload
        if (!hasDismissedInitialMenu && Application.isPlaying)
        {
            ShowStartMenu();
        }
    }

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    public static GameStartMenuUI EnsureExists()
    {
        if (instance != null) return instance;

        var existing = FindAnyObjectByType<GameStartMenuUI>();
        if (existing != null)
        {
            instance = existing;
            return existing;
        }

        GameObject go = new GameObject("GameStartMenuUI");
        instance = go.AddComponent<GameStartMenuUI>();
        if (Application.isPlaying) DontDestroyOnLoad(go);
        return instance;
    }

    public void ShowStartMenu()
    {
        isOpen = true;
        Time.timeScale = 0f;
        Cursor.visible = true;
        Cursor.lockState = CursorLockMode.None;

        var playerMovement = FindAnyObjectByType<PlayerMovement>();
        playerMovement?.SetMovementEnabled(false);
    }

    public void DismissStartMenu()
    {
        isOpen = false;
        hasDismissedInitialMenu = true;
        Time.timeScale = 1f;
        Cursor.visible = true;

        var playerMovement = FindAnyObjectByType<PlayerMovement>();
        playerMovement?.SetMovementEnabled(true);

        AudioManager.Instance?.PlayInventoryOpen();
    }

    private void LoadTextures()
    {
        panelTex = LoadTexture("Assets/Art/UI/ui_menu_panel.png");
        if (panelTex == null) panelTex = LoadTexture("Assets/Art/UI/ui_inventory_panel.png");

        darkBackdropTex = new Texture2D(1, 1);
        darkBackdropTex.SetPixel(0, 0, new Color(0.04f, 0.08f, 0.06f, 0.85f));
        darkBackdropTex.Apply();
    }

    private Texture2D LoadTexture(string path)
    {
#if UNITY_EDITOR
        Sprite sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(path);
        if (sp != null) return sp.texture;
#endif
        if (System.IO.File.Exists(path))
        {
            byte[] bytes = System.IO.File.ReadAllBytes(path);
            Texture2D tex = new Texture2D(16, 16, TextureFormat.RGBA32, false);
            tex.filterMode = FilterMode.Point;
            if (tex.LoadImage(bytes)) return tex;
        }
        return null;
    }

    private void InitStyles()
    {
        Font titleFont = PixelArtFontManager.Title;
        Font regularFont = PixelArtFontManager.Regular;
        Font boldFont = PixelArtFontManager.Bold;

        if (titleStyle == null)
        {
            titleStyle = new GUIStyle();
            titleStyle.font = titleFont;
            titleStyle.fontSize = 20;
            titleStyle.alignment = TextAnchor.MiddleCenter;
            titleStyle.normal.textColor = new Color(1.0f, 0.88f, 0.45f);
        }
        else if (titleStyle.font == null && titleFont != null) titleStyle.font = titleFont;

        if (subtitleStyle == null)
        {
            subtitleStyle = new GUIStyle();
            subtitleStyle.font = boldFont;
            subtitleStyle.fontSize = 12;
            subtitleStyle.alignment = TextAnchor.MiddleCenter;
            subtitleStyle.normal.textColor = new Color(0.38f, 0.24f, 0.12f);
        }
        else if (subtitleStyle.font == null && boldFont != null) subtitleStyle.font = boldFont;

        if (loreStyle == null)
        {
            loreStyle = new GUIStyle();
            loreStyle.font = regularFont;
            loreStyle.fontSize = 12;
            loreStyle.alignment = TextAnchor.MiddleCenter;
            loreStyle.wordWrap = true;
            loreStyle.normal.textColor = new Color(0.32f, 0.18f, 0.08f);
        }
        else if (loreStyle.font == null && regularFont != null) loreStyle.font = regularFont;

        if (statusStyle == null)
        {
            statusStyle = new GUIStyle();
            statusStyle.font = regularFont;
            statusStyle.fontSize = 11;
            statusStyle.alignment = TextAnchor.MiddleCenter;
            statusStyle.normal.textColor = new Color(0.42f, 0.28f, 0.16f);
        }
        else if (statusStyle.font == null && regularFont != null) statusStyle.font = regularFont;

        if (buttonStyle == null)
        {
            buttonStyle = new GUIStyle(GUI.skin.button);
            buttonStyle.font = boldFont;
            buttonStyle.fontSize = 13;
            buttonStyle.alignment = TextAnchor.MiddleCenter;
            buttonStyle.normal.textColor = new Color(1.0f, 0.95f, 0.85f);
        }
        else if (buttonStyle.font == null && boldFont != null) buttonStyle.font = boldFont;

        if (startButtonStyle == null)
        {
            startButtonStyle = new GUIStyle(GUI.skin.button);
            startButtonStyle.font = boldFont;
            startButtonStyle.fontSize = 13;
            startButtonStyle.alignment = TextAnchor.MiddleCenter;
            startButtonStyle.normal.textColor = new Color(0.95f, 1.0f, 0.85f);
        }
        else if (startButtonStyle.font == null && boldFont != null) startButtonStyle.font = boldFont;
    }

    void OnGUI()
    {
        if (!isOpen) return;

        InitStyles();

        // 1. Full-screen backdrop
        if (darkBackdropTex != null)
        {
            GUI.DrawTexture(new Rect(0, 0, Screen.width, Screen.height), darkBackdropTex);
        }

        // 2. Central wooden notice board modal
        float panelW = 440f;
        float panelH = 370f;
        float panelX = (Screen.width - panelW) * 0.5f;
        float panelY = (Screen.height - panelH) * 0.5f;
        Rect modalRect = new Rect(panelX, panelY, panelW, panelH);

        if (panelTex != null)
        {
            GUI.DrawTexture(modalRect, panelTex, ScaleMode.StretchToFill);
        }
        else
        {
            GUI.Box(modalRect, GUIContent.none);
        }

        // Header Title
        DrawTextWithShadow(new Rect(panelX, panelY + 28, panelW, 32), "* STRANDED *", titleStyle, new Color(1.0f, 0.88f, 0.45f), new Color(0.2f, 0.1f, 0.05f));
        GUI.Label(new Rect(panelX, panelY + 62, panelW, 20), "A Tropical Survival Odyssey", subtitleStyle);

        // Lore summary
        string lore = "Survive the remote island wreckage.\nGather coastal resources, craft survival tools,\nand construct an escape boat.";
        GUI.Label(new Rect(panelX + 24, panelY + 92, panelW - 48, 60), lore, loreStyle);

        // Check if save exists
        var saveMgr = SaveManager.Instance ?? FindAnyObjectByType<SaveManager>();
        bool hasSave = saveMgr != null && saveMgr.SaveExists();

        string statusMsg = hasSave ? "Saved game detected on island" : "No previous save found (New Run)";
        GUI.Label(new Rect(panelX + 24, panelY + 160, panelW - 48, 20), statusMsg, statusStyle);

        float btnW = panelW - 80f;
        float btnH = 40f;
        float btnX = panelX + 40f;
        float startBtnY = panelY + 195f;
        float spacing = 12f;

        // Button 1: RESUME GAME (loads save file if one exists)
        bool prevEnabled = GUI.enabled;
        GUI.enabled = hasSave;
        Rect resumeRect = new Rect(btnX, startBtnY, btnW, btnH);
        if (GUI.Button(resumeRect, "RESUME GAME", buttonStyle))
        {
            AudioManager.Instance?.PlayButtonClick();
            saveMgr?.LoadGame(out _);
            DismissStartMenu();
            return;
        }
        GUI.enabled = prevEnabled;

        // Button 2: START NEW GAME / RESTART (wakes at helicopter crash site)
        Rect restartRect = new Rect(btnX, startBtnY + btnH + spacing, btnW, btnH);
        if (GUI.Button(restartRect, "RESTART / NEW GAME", startButtonStyle))
        {
            AudioManager.Instance?.PlayButtonClick();
            SaveManager.IsLoadedSession = false;
            DismissStartMenu();
            return;
        }

        // Hint at bottom
        GUI.Label(new Rect(panelX, panelY + panelH - 32, panelW, 20), "[ESC] in-game to pause or save anytime", statusStyle);
    }

    private void DrawTextWithShadow(Rect rect, string text, GUIStyle style, Color frontColor, Color shadowColor)
    {
        style.normal.textColor = shadowColor;
        GUI.Label(new Rect(rect.x + 2, rect.y + 2, rect.width, rect.height), text, style);
        style.normal.textColor = frontColor;
        GUI.Label(rect, text, style);
    }
}
