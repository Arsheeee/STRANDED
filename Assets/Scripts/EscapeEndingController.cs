using System;
using System.Collections;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.SceneManagement;

/// <summary>
/// State of the boat launch and escape ending progression.
/// </summary>
public enum EscapeState
{
    NotStarted = 0,
    Departing = 1,
    Victory = 2
}

/// <summary>
/// Authoritative controller for the Boat Launch and Escape Victory Ending in STRANDED (Batch 10).
/// Coordinates pre-launch validation, atomic departure sequence, camera follow, screen fade,
/// and the warm Stardew-style Victory Screen with Restart and Main Menu navigation.
/// </summary>
public class EscapeEndingController : MonoBehaviour
{
    private static EscapeEndingController instance;
    public static EscapeEndingController Instance => instance;

    [Header("Ending State")]
    [SerializeField] private EscapeState currentState = EscapeState.NotStarted;
    [SerializeField] private bool hasLaunched = false;
    [SerializeField] private float departureDuration = 2.8f;

    [Header("Visual Transition")]
    [SerializeField] private float fadeAlpha = 0f;
    [SerializeField] private Vector3 sailDirection = new Vector3(1.2f, 0.6f, 0f);
    [SerializeField] private float sailSpeed = 1.8f;

    // References
    private BoatConstructionSite activeSite;
    private PlayerInteraction activePlayer;
    private Transform playerTransform;
    private ExplorationCamera sceneCamera;

    // UI Textures and Styles
    private Texture2D whiteTex;
    private Texture2D panelTex;
    private Texture2D slotBgTex;
    private GUIStyle victoryTitleStyle;
    private GUIStyle victorySubStyle;
    private GUIStyle statLabelStyle;
    private GUIStyle narrativeStyle;
    private GUIStyle restartBtnStyle;
    private GUIStyle menuBtnStyle;

    // Public Properties
    public EscapeState CurrentState => currentState;
    public bool IsEndingActive => currentState != EscapeState.NotStarted;
    public bool HasLaunched => hasLaunched;
    public float DepartureDuration => departureDuration;
    public float FadeAlpha => fadeAlpha;

    // Public Events
    public event Action OnDepartureStarted;
    public event Action OnVictoryReached;

    void Awake()
    {
        if (instance != null && instance != this)
        {
            Destroy(gameObject);
            return;
        }
        instance = this;

        CreateFallbackTextures();
        LoadPanelTextures();
    }

    void Start()
    {
        LocateReferences();
    }

    void OnDestroy()
    {
        if (instance == this) instance = null;
    }

    private void LocateReferences()
    {
        if (sceneCamera == null) sceneCamera = FindAnyObjectByType<ExplorationCamera>();
        if (activeSite == null) activeSite = BoatConstructionSite.Instance;
        if (activePlayer == null) activePlayer = FindAnyObjectByType<PlayerInteraction>();
        if (playerTransform == null && activePlayer != null) playerTransform = activePlayer.transform;
    }

    void Update()
    {
#if UNITY_EDITOR || DEVELOPMENT_BUILD
        UpdateDeveloperShortcuts();
#endif
    }

#if UNITY_EDITOR || DEVELOPMENT_BUILD
    /// <summary>
    /// Checks for F8 shortcut in editor/development builds to test the escape ending.
    /// Fast-completes all boat components and initiates the launch sequence.
    /// </summary>
    private void UpdateDeveloperShortcuts()
    {
        if (hasLaunched) return;

        bool f8Pressed = false;
        if (Keyboard.current != null && Keyboard.current.f8Key.wasPressedThisFrame)
        {
            f8Pressed = true;
        }
#if ENABLE_LEGACY_INPUT_MANAGER
        if (!f8Pressed && Input.GetKeyDown(KeyCode.F8))
        {
            f8Pressed = true;
        }
#endif

        if (f8Pressed)
        {
            TriggerDeveloperEndingShortcut();
        }
    }

    /// <summary>
    /// Developer testing helper: Fast-completes the boat site and triggers the escape launch.
    /// </summary>
    public void TriggerDeveloperEndingShortcut()
    {
        Debug.Log("[STRANDED Dev] F8 Shortcut triggered: Fast-completing boat site and launching escape ending.");

        var site = BoatConstructionSite.EnsureDefaultSiteExists();
        if (site != null)
        {
            site.DeveloperCompleteBoat();
        }

        var player = FindAnyObjectByType<PlayerInteraction>();
        TriggerLaunchSequence(site, player);
    }
#endif

    /// <summary>
    /// Initiates the boat launch and escape departure sequence.
    /// Rejects if the boat is incomplete, or if launch has already been triggered.
    /// </summary>
    public bool TriggerLaunchSequence(BoatConstructionSite site, PlayerInteraction player)
    {
        if (hasLaunched || currentState != EscapeState.NotStarted)
        {
            Debug.LogWarning("[STRANDED Escape] Launch rejected: Ending sequence is already active or completed.");
            return false;
        }

        if (site == null)
        {
            site = BoatConstructionSite.Instance ?? BoatConstructionSite.EnsureDefaultSiteExists();
        }

        if (site == null || !site.IsComplete)
        {
            string failMsg = "Cannot launch: Boat construction is incomplete! Complete all 5 stages before launching.";
            TemporaryResourceHUD.Instance?.ShowNotification(failMsg, new Color(1.0f, 0.35f, 0.35f));
            Debug.LogWarning($"[STRANDED Escape] Launch prevented: {failMsg}");
            return false;
        }

        hasLaunched = true;
        currentState = EscapeState.Departing;
        activeSite = site;
        activePlayer = player != null ? player : FindAnyObjectByType<PlayerInteraction>();
        if (activePlayer != null) playerTransform = activePlayer.transform;

        // 1. Close open conflicting menus
        var boatUI = FindAnyObjectByType<BoatConstructionUI>();
        boatUI?.CloseUI();

        var craftUI = FindAnyObjectByType<CraftingUI>();
        craftUI?.SetCraftingOpen(false);

        var invUI = FindAnyObjectByType<InventoryUI>();
        invUI?.SetInventoryOpen(false);

        // 2. Clear HUD prompts and announce departure
        TemporaryResourceHUD.Instance?.SetInteractionPrompt("");
        TemporaryResourceHUD.Instance?.ShowNotification("Setting sail! Launching escape boat...", new Color(0.35f, 1.0f, 0.55f));
        AudioManager.Instance?.PlayBoatLaunch();

        // 3. Disable player movement and interactions during ending
        if (activePlayer != null)
        {
            var move = activePlayer.GetComponent<PlayerMovement>();
            if (move != null) move.SetMovementEnabled(false);
            activePlayer.enabled = false;
        }
        else
        {
            var move = FindAnyObjectByType<PlayerMovement>();
            if (move != null) move.SetMovementEnabled(false);
            var interact = FindAnyObjectByType<PlayerInteraction>();
            if (interact != null) interact.enabled = false;
        }

        // 4. Update Objective narrative
        ObjectiveManager.Instance?.MarkEscaped();

        Debug.Log("[STRANDED Escape] Escape boat launch initiated! Beginning departure sequence.");
        OnDepartureStarted?.Invoke();

        // 5. Start Departure Coroutine
        StartCoroutine(DepartureSequenceRoutine());
        return true;
    }

    private IEnumerator DepartureSequenceRoutine()
    {
        LocateReferences();

        // Switch camera to follow the departing boat
        if (sceneCamera != null && activeSite != null)
        {
            sceneCamera.SetTarget(activeSite.transform);
        }

        // Board player on boat (align position and ensure correct sorting)
        if (playerTransform != null && activeSite != null)
        {
            playerTransform.position = activeSite.transform.position + new Vector3(-0.35f, 0.25f, 0f);
            var playerSr = playerTransform.GetComponent<SpriteRenderer>();
            var boatSr = activeSite.GetComponent<SpriteRenderer>();
            if (playerSr != null && boatSr != null)
            {
                playerSr.sortingOrder = boatSr.sortingOrder + 1;
            }
        }

        Vector3 moveDir = sailDirection.normalized;
        float elapsed = 0f;

        while (elapsed < departureDuration)
        {
            elapsed += Time.deltaTime;
            float t = Mathf.Clamp01(elapsed / departureDuration);

            // Gently sail boat out into open ocean waters
            if (activeSite != null)
            {
                Vector3 boatDelta = moveDir * (sailSpeed * Time.deltaTime);
                activeSite.transform.position += boatDelta;
                if (playerTransform != null)
                {
                    playerTransform.position += boatDelta;
                }
            }

            // Smooth fade to deep oceanic blue
            fadeAlpha = Mathf.SmoothStep(0f, 1f, t);

            yield return null;
        }

        fadeAlpha = 1f;
        currentState = EscapeState.Victory;

        Cursor.visible = true;
        Cursor.lockState = CursorLockMode.None;

        AudioManager.Instance?.PlayVictory();

        Debug.Log("[STRANDED Escape] Departure sequence complete! Presenting Victory Screen.");
        OnVictoryReached?.Invoke();
    }

    void OnGUI()
    {
        if (currentState == EscapeState.NotStarted) return;

        InitStyles();

        if (currentState == EscapeState.Departing)
        {
            // Oceanic fade overlay during departure
            if (fadeAlpha > 0f)
            {
                DrawRect(new Rect(0, 0, Screen.width, Screen.height), new Color(0.06f, 0.12f, 0.22f, fadeAlpha));

                // Bottom subtitle during sailing
                if (fadeAlpha > 0.35f)
                {
                    GUI.Label(new Rect(0, Screen.height - 80, Screen.width, 40), "Setting sail for freedom...", narrativeStyle);
                }
            }
        }
        else if (currentState == EscapeState.Victory)
        {
            DrawVictoryScreen();
        }
    }

    private void DrawVictoryScreen()
    {
        // 1. Deep ocean dark backdrop overlay
        DrawRect(new Rect(0, 0, Screen.width, Screen.height), new Color(0.05f, 0.09f, 0.16f, 0.95f));

        // 2. Centered Stardew-style parchment modal dialog (640 x 450 px)
        float modalW = Mathf.Min(640f, Screen.width - 40f);
        float modalH = Mathf.Min(450f, Screen.height - 40f);
        float modalX = (Screen.width - modalW) * 0.5f;
        float modalY = (Screen.height - modalH) * 0.5f;

        Rect modalRect = new Rect(modalX, modalY, modalW, modalH);

        // Dark wood border trim
        DrawRect(new Rect(modalX - 4, modalY - 4, modalW + 8, modalH + 8), new Color(0.35f, 0.20f, 0.10f, 1f));

        // Warm parchment interior
        if (panelTex != null)
        {
            GUI.DrawTexture(modalRect, panelTex, ScaleMode.StretchToFill);
        }
        else
        {
            DrawRect(modalRect, new Color(0.18f, 0.13f, 0.09f, 0.98f));
        }

        // 3. Victory Header Title
        Rect titleRect = new Rect(modalX + 20, modalY + 28, modalW - 40, 48);
        GUI.Label(titleRect, "YOU ESCAPED!", victoryTitleStyle);

        // 4. Subtitle
        Rect subRect = new Rect(modalX + 20, modalY + 80, modalW - 40, 28);
        GUI.Label(subRect, "You survived the island and built your way to freedom.", victorySubStyle);

        // 5. Narrative & Stats Parchment Box
        float boxX = modalX + 32;
        float boxY = modalY + 120;
        float boxW = modalW - 64;
        float boxH = 190;
        Rect boxRect = new Rect(boxX, boxY, boxW, boxH);

        if (slotBgTex != null)
        {
            GUI.DrawTexture(boxRect, slotBgTex, ScaleMode.StretchToFill);
        }
        else
        {
            DrawRect(boxRect, new Color(0.12f, 0.08f, 0.05f, 0.85f));
        }

        // Inner stats
        float lineY = boxY + 16;
        float lineHeight = 28;

        string timeStr = FormatSurvivalTime(Time.timeSinceLevelLoad);
        GUI.Label(new Rect(boxX + 20, lineY, boxW - 40, lineHeight), $"• Time Survived: <b>{timeStr}</b>", statLabelStyle);
        lineY += lineHeight;

        GUI.Label(new Rect(boxX + 20, lineY, boxW - 40, lineHeight), "• Escape Vessel: <b>5 / 5 Stages Assembled (Fully Seaworthy)</b>", statLabelStyle);
        lineY += lineHeight;

        GUI.Label(new Rect(boxX + 20, lineY, boxW - 40, lineHeight), "• Voyage Status: <b>Cleared Coral Reef & Open Sea Navigated</b>", statLabelStyle);
        lineY += lineHeight + 8;

        string flavorText = "With hand-crafted timber, woven cordage, and a stitched canvas sail, you overcame the wilderness. The open ocean carries you onward to safety.";
        GUI.Label(new Rect(boxX + 20, lineY, boxW - 40, 60), flavorText, narrativeStyle);

        // 6. Navigation Buttons
        float btnW = (modalW - 88) * 0.5f;
        float btnH = 52f;
        float btnY = modalY + modalH - 74f;

        // Button: RESTART GAME
        Rect restartRect = new Rect(modalX + 32, btnY, btnW, btnH);
        if (GUI.Button(restartRect, "RESTART GAME", restartBtnStyle))
        {
            AudioManager.Instance?.PlayButtonClick();
            RestartGame();
        }

        // Button: RETURN TO MAIN MENU
        Rect menuRect = new Rect(modalX + 32 + btnW + 24, btnY, btnW, btnH);
        if (GUI.Button(menuRect, "RETURN TO MAIN MENU", menuBtnStyle))
        {
            ReturnToMainMenu();
        }
    }

    /// <summary>
    /// Cleanly reloads the active scene, restoring fresh playable game state.
    /// </summary>
    public void RestartGame()
    {
        Debug.Log("[STRANDED Escape] Restarting game — reloading active scene.");
        Time.timeScale = 1f;
        SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
    }

    /// <summary>
    /// Navigates to the main menu or reloads active scene if STRANDED is running single-scene.
    /// </summary>
    public void ReturnToMainMenu()
    {
        Debug.Log("[STRANDED Escape] Returning to main menu.");
        Time.timeScale = 1f;
        if (SceneManager.sceneCountInBuildSettings > 1)
        {
            SceneManager.LoadScene(0);
        }
        else
        {
            SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
        }
    }

    private string FormatSurvivalTime(float seconds)
    {
        int totalSec = Mathf.FloorToInt(seconds);
        int mins = totalSec / 60;
        int secs = totalSec % 60;
        return $"{mins:D2}:{secs:D2}";
    }

    private void DrawRect(Rect rect, Color color)
    {
        if (whiteTex == null) CreateFallbackTextures();
        Color prev = GUI.color;
        GUI.color = color;
        GUI.DrawTexture(rect, whiteTex);
        GUI.color = prev;
    }

    private void CreateFallbackTextures()
    {
        if (whiteTex != null) return;
        whiteTex = new Texture2D(1, 1, TextureFormat.RGBA32, false);
        whiteTex.SetPixel(0, 0, Color.white);
        whiteTex.Apply();
    }

    private void LoadPanelTextures()
    {
        panelTex = LoadTexture("Assets/Art/UI/ui_inventory_panel.png");
        slotBgTex = LoadTexture("Assets/Art/UI/ui_slot_background.png");
    }

    private Texture2D LoadTexture(string path)
    {
#if UNITY_EDITOR
        Texture2D t = UnityEditor.AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        if (t != null) return t;
#endif
        if (System.IO.File.Exists(path))
        {
            try
            {
                byte[] bytes = System.IO.File.ReadAllBytes(path);
                Texture2D tex = new Texture2D(32, 32, TextureFormat.RGBA32, false);
                tex.filterMode = FilterMode.Point;
                if (tex.LoadImage(bytes)) return tex;
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[EscapeEndingController] Failed to load UI texture {path}: {ex.Message}");
            }
        }
        return null;
    }

    private void InitStyles()
    {
        if (victoryTitleStyle != null) return;

        victoryTitleStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = 32,
            fontStyle = FontStyle.Bold,
            alignment = TextAnchor.MiddleCenter
        };
        victoryTitleStyle.normal.textColor = new Color(1.0f, 0.88f, 0.45f); // Rich warm gold

        victorySubStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = 16,
            fontStyle = FontStyle.Normal,
            alignment = TextAnchor.MiddleCenter
        };
        victorySubStyle.normal.textColor = new Color(0.92f, 0.88f, 0.80f);

        statLabelStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = 14,
            fontStyle = FontStyle.Normal,
            alignment = TextAnchor.MiddleLeft,
            richText = true
        };
        statLabelStyle.normal.textColor = new Color(0.90f, 0.85f, 0.75f);

        narrativeStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = 13,
            fontStyle = FontStyle.Italic,
            alignment = TextAnchor.UpperLeft,
            wordWrap = true
        };
        narrativeStyle.normal.textColor = new Color(0.78f, 0.74f, 0.65f);

        restartBtnStyle = new GUIStyle(GUI.skin.button)
        {
            fontSize = 16,
            fontStyle = FontStyle.Bold,
            alignment = TextAnchor.MiddleCenter
        };
        restartBtnStyle.normal.textColor = Color.white;

        menuBtnStyle = new GUIStyle(GUI.skin.button)
        {
            fontSize = 15,
            fontStyle = FontStyle.Bold,
            alignment = TextAnchor.MiddleCenter
        };
        menuBtnStyle.normal.textColor = new Color(0.95f, 0.90f, 0.80f);
    }

    /// <summary>
    /// Ensures a singleton instance of EscapeEndingController exists in the scene.
    /// </summary>
    public static EscapeEndingController EnsureExists()
    {
        if (instance != null) return instance;

        var existing = FindAnyObjectByType<EscapeEndingController>();
        if (existing != null)
        {
            instance = existing;
            return existing;
        }

        GameObject go = new GameObject("EscapeEndingController");
        instance = go.AddComponent<EscapeEndingController>();
        Debug.Log("[STRANDED Escape] Initialized EscapeEndingController singleton in scene.");
        return instance;
    }
}
