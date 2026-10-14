using System;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.SceneManagement;

/// <summary>
/// Stardew Valley-styled in-game pause and escape menu for STRANDED.
/// Pops up when Escape is pressed during gameplay, offering immediate Resume,
/// Save/Load access, and Restart Game confirmation.
/// </summary>
public class EscapeMenuUI : MonoBehaviour
{
    private static EscapeMenuUI instance;
    public static EscapeMenuUI Instance => instance;

    private bool isOpen = false;
    public static bool IsOpen => instance != null && instance.isOpen;

    private bool isConfirmingRestart = false;

    // Textures & Styles
    private Texture2D panelTex;
    private Texture2D buttonTex;
    private Texture2D darkBackdropTex;

    private GUIStyle headerStyle;
    private GUIStyle subHeaderStyle;
    private GUIStyle buttonStyle;
    private GUIStyle dangerButtonStyle;
    private GUIStyle warningTextStyle;

    void Awake()
    {
        if (instance != null && instance != this)
        {
            Destroy(gameObject);
            return;
        }
        instance = this;
    }

    void OnEnable()
    {
        SceneManager.sceneLoaded += OnSceneLoaded;
    }

    void OnDisable()
    {
        SceneManager.sceneLoaded -= OnSceneLoaded;
    }

    private void OnSceneLoaded(Scene scene, LoadSceneMode mode)
    {
        isOpen = false;
        isConfirmingRestart = false;
        Time.timeScale = 1f;
    }

    void Start()
    {
        LoadTextures();
    }

    void OnDestroy()
    {
        if (instance == this)
        {
            if (isOpen) Time.timeScale = 1f;
            instance = null;
        }
    }

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    public static EscapeMenuUI EnsureExists()
    {
        if (instance != null) return instance;

        var existing = FindAnyObjectByType<EscapeMenuUI>();
        if (existing != null)
        {
            instance = existing;
            return existing;
        }

        GameObject go = new GameObject("EscapeMenuUI");
        instance = go.AddComponent<EscapeMenuUI>();
        if (Application.isPlaying) DontDestroyOnLoad(go);
        return instance;
    }

    void Update()
    {
        // Don't intercept Escape if victory ending sequence is active
        if (EscapeEndingController.Instance != null && EscapeEndingController.Instance.IsEndingActive)
        {
            if (isOpen) SetMenuOpen(false);
            return;
        }

        bool escPressed = false;
        if (Keyboard.current != null)
        {
            if (Keyboard.current.escapeKey.wasPressedThisFrame)
            {
                escPressed = true;
            }
        }
#if ENABLE_LEGACY_INPUT_MANAGER
        if (!escPressed && Input.GetKeyDown(KeyCode.Escape))
        {
            escPressed = true;
        }
#endif

        if (escPressed)
        {
            // If another modal menu is currently open, it takes priority and closes itself first
            if (InventoryUI.IsOpen || CraftingUI.IsOpen || BoatConstructionUI.IsOpen)
            {
                return;
            }

            // If another modal was closed on this exact frame, do not immediately open pause menu
            if (InventoryUI.LastClosedFrame == Time.frameCount ||
                CraftingUI.LastClosedFrame == Time.frameCount ||
                BoatConstructionUI.LastClosedFrame == Time.frameCount)
            {
                return;
            }

            if (isOpen)
            {
                if (isConfirmingRestart)
                {
                    isConfirmingRestart = false; // Escape cancels restart confirmation dialog
                }
                else
                {
                    SetMenuOpen(false); // Escape resumes game
                }
            }
            else
            {
                SetMenuOpen(true);
            }
        }
    }

    public void SetMenuOpen(bool open)
    {
        isOpen = open;
        isConfirmingRestart = false;

        if (isOpen)
        {
            Time.timeScale = 0f;
            Cursor.visible = true;
            Cursor.lockState = CursorLockMode.None;
            AudioManager.Instance?.PlayInventoryOpen();
        }
        else
        {
            Time.timeScale = 1f;
            AudioManager.Instance?.PlayInventoryClose();
        }
    }

    private void LoadTextures()
    {
        panelTex = LoadTexture("Assets/Art/UI/ui_menu_panel.png");
        if (panelTex == null) panelTex = LoadTexture("Assets/Art/UI/ui_inventory_panel.png");

        darkBackdropTex = new Texture2D(1, 1);
        darkBackdropTex.SetPixel(0, 0, new Color(0f, 0f, 0f, 0.65f));
        darkBackdropTex.Apply();

        buttonTex = LoadTexture("Assets/Art/UI/ui_slot_background.png");
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

        if (headerStyle == null)
        {
            headerStyle = new GUIStyle();
            headerStyle.font = titleFont;
            headerStyle.fontSize = 16;
            headerStyle.alignment = TextAnchor.MiddleCenter;
            headerStyle.normal.textColor = new Color(1.0f, 0.88f, 0.45f);
        }
        else if (headerStyle.font == null && titleFont != null)
        {
            headerStyle.font = titleFont;
        }

        if (subHeaderStyle == null)
        {
            subHeaderStyle = new GUIStyle();
            subHeaderStyle.font = regularFont;
            subHeaderStyle.fontSize = 12;
            subHeaderStyle.alignment = TextAnchor.MiddleCenter;
            subHeaderStyle.normal.textColor = new Color(0.38f, 0.24f, 0.12f);
        }
        else if (subHeaderStyle.font == null && regularFont != null)
        {
            subHeaderStyle.font = regularFont;
        }

        if (buttonStyle == null)
        {
            buttonStyle = new GUIStyle(GUI.skin.button);
            buttonStyle.font = boldFont;
            buttonStyle.fontSize = 13;
            buttonStyle.alignment = TextAnchor.MiddleCenter;
            buttonStyle.normal.textColor = new Color(1.0f, 0.95f, 0.85f);
        }
        else if (buttonStyle.font == null && boldFont != null)
        {
            buttonStyle.font = boldFont;
        }

        if (dangerButtonStyle == null)
        {
            dangerButtonStyle = new GUIStyle(GUI.skin.button);
            dangerButtonStyle.font = boldFont;
            dangerButtonStyle.fontSize = 13;
            dangerButtonStyle.alignment = TextAnchor.MiddleCenter;
            dangerButtonStyle.normal.textColor = new Color(1.0f, 0.45f, 0.35f);
        }
        else if (dangerButtonStyle.font == null && boldFont != null)
        {
            dangerButtonStyle.font = boldFont;
        }

        if (warningTextStyle == null)
        {
            warningTextStyle = new GUIStyle();
            warningTextStyle.font = regularFont;
            warningTextStyle.fontSize = 12;
            warningTextStyle.alignment = TextAnchor.MiddleCenter;
            warningTextStyle.wordWrap = true;
            warningTextStyle.normal.textColor = new Color(0.32f, 0.16f, 0.08f);
        }
        else if (warningTextStyle.font == null && regularFont != null)
        {
            warningTextStyle.font = regularFont;
        }
    }

    void OnGUI()
    {
        if (!isOpen) return;

        InitStyles();

        // 1. Semi-transparent backdrop overlay
        if (darkBackdropTex != null)
        {
            GUI.DrawTexture(new Rect(0, 0, Screen.width, Screen.height), darkBackdropTex);
        }

        // 2. Center Wooden Board Modal
        float panelW = 420f;
        float panelH = isConfirmingRestart ? 340f : 380f;
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

        if (!isConfirmingRestart)
        {
            // Title Header with shadow
            DrawTextWithShadow(new Rect(panelX, panelY + 24, panelW, 30), "* GAME PAUSED *", headerStyle, new Color(1.0f, 0.88f, 0.45f), new Color(0.2f, 0.1f, 0.05f));
            GUI.Label(new Rect(panelX, panelY + 56, panelW, 20), "STRANDED - Tropical Base Camp", subHeaderStyle);

            float btnW = panelW - 80f;
            float btnH = 38f;
            float btnX = panelX + 40f;
            float startBtnY = panelY + 86f;
            float spacing = 10f;

            // 1. Resume Game
            Rect resumeRect = new Rect(btnX, startBtnY, btnW, btnH);
            if (GUI.Button(resumeRect, "RESUME GAME", buttonStyle))
            {
                SetMenuOpen(false);
                return;
            }

            // 2. Restart Game (Opens confirmation dialog)
            Rect restartRect = new Rect(btnX, startBtnY + (btnH + spacing), btnW, btnH);
            if (GUI.Button(restartRect, "RESTART GAME", dangerButtonStyle))
            {
                AudioManager.Instance?.PlayButtonClick();
                isConfirmingRestart = true;
                return;
            }

            // 3. Save Game (F5)
            Rect saveRect = new Rect(btnX, startBtnY + (btnH + spacing) * 2, btnW, btnH);
            if (GUI.Button(saveRect, "SAVE GAME (F5)", buttonStyle))
            {
                AudioManager.Instance?.PlayButtonClick();
                var sm = SaveManager.Instance ?? FindAnyObjectByType<SaveManager>();
                sm?.SaveGame(out _);
                return;
            }

            // 4. Load Game (F9)
            Rect loadRect = new Rect(btnX, startBtnY + (btnH + spacing) * 3, btnW, btnH);
            var saveMgr = SaveManager.Instance ?? FindAnyObjectByType<SaveManager>();
            bool hasSave = saveMgr != null && saveMgr.SaveExists();
            bool prevEnabled = GUI.enabled;
            GUI.enabled = hasSave;
            if (GUI.Button(loadRect, "LOAD GAME (F9)", buttonStyle))
            {
                AudioManager.Instance?.PlayButtonClick();
                saveMgr?.LoadGame(out _);
                SetMenuOpen(false);
                return;
            }
            GUI.enabled = prevEnabled;

            // 5. Close Menu hint
            GUI.Label(new Rect(panelX, panelY + panelH - 30, panelW, 20), "[ESC] to Resume Game", subHeaderStyle);
        }
        else
        {
            // Confirmation Screen for Restarting Game
            DrawTextWithShadow(new Rect(panelX, panelY + 26, panelW, 30), "RESTART GAME?", headerStyle, new Color(1.0f, 0.45f, 0.35f), new Color(0.2f, 0.1f, 0.05f));

            string warningMsg = "Are you sure you want to restart?\n\nYou will wake up at the crashed helicopter\nwith fresh starting survival gear.\nAny unsaved progress will be lost.";
            GUI.Label(new Rect(panelX + 24, panelY + 74, panelW - 48, 120), warningMsg, warningTextStyle);

            float btnW = (panelW - 90f) * 0.5f;
            float btnH = 40f;
            float btnY = panelY + panelH - 68f;

            // Confirm Restart Button
            Rect confirmRect = new Rect(panelX + 38, btnY, btnW, btnH);
            if (GUI.Button(confirmRect, "YES, RESTART", dangerButtonStyle))
            {
                Debug.Log("[STRANDED Menu] Restart confirmed by player. Reloading scene at crash site.");
                SetMenuOpen(false);
                isConfirmingRestart = false;
                Time.timeScale = 1f;
                SaveManager.IsLoadedSession = false;
                SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
                return;
            }

            // Cancel Button
            Rect cancelRect = new Rect(panelX + 38 + btnW + 14, btnY, btnW, btnH);
            if (GUI.Button(cancelRect, "CANCEL", buttonStyle))
            {
                AudioManager.Instance?.PlayButtonClick();
                isConfirmingRestart = false;
                return;
            }
        }
    }

    private void DrawTextWithShadow(Rect rect, string text, GUIStyle style, Color frontColor, Color shadowColor)
    {
        style.normal.textColor = shadowColor;
        GUI.Label(new Rect(rect.x + 2, rect.y + 2, rect.width, rect.height), text, style);
        style.normal.textColor = frontColor;
        GUI.Label(rect, text, style);
    }
}
