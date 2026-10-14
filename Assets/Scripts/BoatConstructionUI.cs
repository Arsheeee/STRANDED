using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;

/// <summary>
/// Full interactive Boat Construction UI for STRANDED.
/// Displays overall boat construction progress, component checklist,
/// inventory validation for the next required part, and executes atomic installation.
/// Uses warm Stardew Valley parchment aesthetics consistent with inventory and crafting menus.
/// </summary>
public class BoatConstructionUI : MonoBehaviour
{
    private static bool isOpen = false;
    public static bool IsOpen => isOpen;
    public static int LastClosedFrame { get; private set; } = -1;

    private BoatConstructionSite currentSite;
    private Inventory inventory;
    private PlayerMovement playerMovement;

    private Texture2D panelTex;
    private Texture2D slotBgTex;
    private Texture2D slotSelectedTex;
    private Texture2D closeBtnTex;

    private GUIStyle titleStyle;
    private GUIStyle subtitleStyle;
    private GUIStyle sectionStyle;
    private GUIStyle itemTitleStyle;
    private GUIStyle itemDescStyle;
    private GUIStyle statusStyle;
    private GUIStyle bannerReadyStyle;
    private GUIStyle bannerPendingStyle;
    private GUIStyle actionBtnStyle;
    private GUIStyle actionBtnDisabledStyle;

    void Awake()
    {
        inventory = GetComponentInParent<Inventory>();
        playerMovement = GetComponentInParent<PlayerMovement>();
        LoadTextures();
    }

    void Start()
    {
        if (inventory == null) inventory = FindAnyObjectByType<Inventory>();
        if (playerMovement == null) playerMovement = FindAnyObjectByType<PlayerMovement>();
    }

    void Update()
    {
        if (!isOpen) return;

        bool closeRequested = false;

        if (Keyboard.current != null)
        {
            if (Keyboard.current.escapeKey.wasPressedThisFrame ||
                Keyboard.current.eKey.wasPressedThisFrame ||
                Keyboard.current.cKey.wasPressedThisFrame)
            {
                closeRequested = true;
            }
        }

#if ENABLE_LEGACY_INPUT_MANAGER
        if (!closeRequested && (Input.GetKeyDown(KeyCode.Escape) || Input.GetKeyDown(KeyCode.E) || Input.GetKeyDown(KeyCode.C)))
        {
            closeRequested = true;
        }
#endif

        // Auto-close if player moves too far
        if (currentSite != null && playerMovement != null)
        {
            float distSq = ((Vector2)playerMovement.transform.position - (Vector2)currentSite.transform.position).sqrMagnitude;
            float maxDist = currentSite.InteractionRadius + 1.5f;
            if (distSq > maxDist * maxDist)
            {
                closeRequested = true;
            }
        }

        if (closeRequested)
        {
            CloseUI();
        }
    }

    public void OpenUI(BoatConstructionSite site)
    {
        currentSite = site;
        isOpen = true;

        // Close conflicting windows
        var craftUI = FindAnyObjectByType<CraftingUI>();
        craftUI?.SetCraftingOpen(false);

        var invUI = FindAnyObjectByType<InventoryUI>();
        invUI?.SetInventoryOpen(false);

        if (playerMovement != null)
        {
            playerMovement.SetMovementEnabled(false);
        }

        Cursor.visible = true;
        Cursor.lockState = CursorLockMode.None;
        AudioManager.Instance?.PlayInventoryOpen();
    }

    public void CloseUI()
    {
        isOpen = false;
        currentSite = null;
        LastClosedFrame = Time.frameCount;
        AudioManager.Instance?.PlayInventoryClose();

        if (playerMovement != null)
        {
            playerMovement.SetMovementEnabled(true);
        }
    }

    void OnGUI()
    {
        if (!isOpen || currentSite == null || inventory == null) return;

        InitStyles();

        // 980 x 640 px window
        float panelWidth = Mathf.Min(Screen.width - 40f, 980f);
        float panelHeight = Mathf.Min(Screen.height - 40f, 640f);

        float panelX = (Screen.width - panelWidth) * 0.5f;
        float panelY = (Screen.height - panelHeight) * 0.5f;

        Rect panelRect = new Rect(panelX, panelY, panelWidth, panelHeight);

        // Background
        if (panelTex != null)
        {
            GUI.DrawTexture(panelRect, panelTex, ScaleMode.StretchToFill);
        }
        else
        {
            GUI.Box(panelRect, GUIContent.none);
        }

        // Close button 'X'
        Rect closeRect = new Rect(panelX + panelWidth - 46, panelY + 16, 32, 32);
        if (closeBtnTex != null)
        {
            if (GUI.Button(closeRect, GUIContent.none, GUIStyle.none))
            {
                CloseUI();
                return;
            }
            GUI.DrawTexture(closeRect, closeBtnTex, ScaleMode.StretchToFill);
        }
        else
        {
            if (GUI.Button(closeRect, "X"))
            {
                CloseUI();
                return;
            }
        }

        // Header Titles
        Rect titleRect = new Rect(panelX + 32, panelY + 18, 600, 32);
        GUI.Label(titleRect, "ESCAPE BOAT CONSTRUCTION", titleStyle);

        Rect subRect = new Rect(panelX + 32, panelY + 48, 600, 24);
        GUI.Label(subRect, "Northeastern Escape Cove Shipyard", subtitleStyle);

        // Overall Progress Bar Banner
        float progY = panelY + 76f;
        Rect progRect = new Rect(panelX + 32, progY, panelWidth - 64, 38);
        string progText = currentSite.IsComplete
            ? "CONSTRUCTION 100% COMPLETE — VESSEL IS SEAWORTHY & READY FOR VOYAGE"
            : $"CONSTRUCTION PROGRESS: {currentSite.CurrentStageIndex} / {currentSite.TotalStages} STAGES COMPLETED ({Mathf.RoundToInt(currentSite.ProgressNormalized * 100f)}%)";

        GUI.Box(progRect, progText, currentSite.IsComplete ? bannerReadyStyle : bannerPendingStyle);

        // =====================================================================
        // LEFT COLUMN: 5-STAGE CHECKLIST (410px wide)
        // =====================================================================
        float colX = panelX + 32f;
        float colY = progY + 50f;
        float colW = 410f;

        Rect leftHeaderRect = new Rect(colX, colY, colW, 24);
        GUI.Label(leftHeaderRect, "CONSTRUCTION BLUEPRINT & CHECKLIST", sectionStyle);

        float cardStartY = colY + 28f;
        float cardH = 72f;
        float cardSpacing = 8f;

        IReadOnlyList<BoatComponentRequirement> reqs = currentSite.Requirements;
        for (int i = 0; i < reqs.Count; i++)
        {
            var req = reqs[i];
            bool isInstalled = (i < currentSite.CurrentStageIndex);
            bool isCurrent = (i == currentSite.CurrentStageIndex && !currentSite.IsComplete);

            Rect cardRect = new Rect(colX, cardStartY + i * (cardH + cardSpacing), colW, cardH);

            if (slotBgTex != null) GUI.DrawTexture(cardRect, slotBgTex, ScaleMode.StretchToFill);
            else GUI.Box(cardRect, GUIContent.none);

            if (isCurrent && slotSelectedTex != null)
            {
                Rect selRect = new Rect(cardRect.x - 2, cardRect.y - 2, cardRect.width + 4, cardRect.height + 4);
                GUI.DrawTexture(selRect, slotSelectedTex, ScaleMode.StretchToFill);
            }

            // Component Icon
            ItemData item = ItemDatabase.GetItemById(req.ComponentItemId);
            if (item != null && item.Icon != null)
            {
                Rect iconRect = new Rect(cardRect.x + 8, cardRect.y + 12, 48, 48);
                DrawSprite(iconRect, item.Icon);
            }

            // Name
            Rect nameRect = new Rect(cardRect.x + 64, cardRect.y + 8, cardRect.width - 70, 22);
            GUI.Label(nameRect, $"Stage {i + 1}: <b>{req.DisplayName}</b>", itemTitleStyle);

            // Status Badge
            Rect badgeRect = new Rect(cardRect.x + 64, cardRect.y + 36, cardRect.width - 70, 24);
            if (isInstalled)
            {
                GUI.Label(badgeRect, "<color=#1e7b24><b>[INSTALLED]</b></color>", statusStyle);
            }
            else if (isCurrent)
            {
                int invCount = inventory.GetItemCount(item);
                string cntColor = invCount >= req.RequiredQuantity ? "#1e7b24" : "#b82a20";
                GUI.Label(badgeRect, $"<color=#b87a18><b>[NEXT]</b></color> In Bag: <color={cntColor}><b>{invCount}</b></color> / {req.RequiredQuantity}", statusStyle);
            }
            else
            {
                GUI.Label(badgeRect, "<color=#756250><b>[LOCKED]</b> (Requires previous stages)</color>", statusStyle);
            }
        }

        // =====================================================================
        // RIGHT COLUMN: NEXT STAGE DETAILS & INSTALL BUTTON
        // =====================================================================
        float rightX = colX + colW + 24f;
        float rightY = colY;
        float rightW = panelWidth - (colW + 88f);
        float rightH = panelHeight - (rightY - panelY) - 24f;

        Rect rightBoxRect = new Rect(rightX, rightY, rightW, rightH);
        if (slotBgTex != null) GUI.DrawTexture(rightBoxRect, slotBgTex, ScaleMode.StretchToFill);
        else GUI.Box(rightBoxRect, GUIContent.none);

        if (currentSite.IsComplete)
        {
            // Fully completed state display
            DrawCompletedDetails(rightX, rightY, rightW, rightH);
        }
        else
        {
            // Active installation details
            DrawActiveStageDetails(rightX, rightY, rightW, rightH);
        }
    }

    private void DrawActiveStageDetails(float rx, float ry, float rw, float rh)
    {
        var req = currentSite.GetCurrentRequirement();
        if (req == null) return;

        ItemData item = ItemDatabase.GetItemById(req.ComponentItemId);
        bool canInstall = currentSite.CanInstallNext(inventory, out string failReason);
        int hasCount = item != null ? inventory.GetItemCount(item) : 0;

        // Big Icon
        if (item != null && item.Icon != null)
        {
            Rect bigIconRect = new Rect(rx + 24, ry + 24, 72, 72);
            DrawSprite(bigIconRect, item.Icon);
        }

        // Stage & Component Name
        Rect nameRect = new Rect(rx + 108, ry + 20, rw - 128, 28);
        GUI.Label(nameRect, $"NEXT REQUIREMENT: {req.DisplayName.ToUpper()}", itemTitleStyle);

        Rect subReqRect = new Rect(rx + 108, ry + 48, rw - 128, 22);
        GUI.Label(subReqRect, $"Stage {currentSite.CurrentStageIndex + 1} of {currentSite.TotalStages}", subtitleStyle);

        // Description
        Rect descRect = new Rect(rx + 24, ry + 110, rw - 48, 60);
        GUI.Label(descRect, req.Description, itemDescStyle);

        // Requirements Box
        Rect reqBoxRect = new Rect(rx + 24, ry + 180, rw - 48, 86);
        if (slotBgTex != null) GUI.DrawTexture(reqBoxRect, slotBgTex, ScaleMode.StretchToFill);
        else GUI.Box(reqBoxRect, GUIContent.none);

        string countTag = hasCount >= req.RequiredQuantity ? "#1e7b24" : "#b82a20";
        Rect reqQtyRect = new Rect(reqBoxRect.x + 16, reqBoxRect.y + 12, reqBoxRect.width - 32, 26);
        GUI.Label(reqQtyRect, $"Required Quantity: <b>{req.RequiredQuantity}x</b>", itemDescStyle);

        Rect invQtyRect = new Rect(reqBoxRect.x + 16, reqBoxRect.y + 42, reqBoxRect.width - 32, 26);
        GUI.Label(invQtyRect, $"Available in Inventory: <color={countTag}><b>{hasCount}x</b></color>", itemDescStyle);

        // Status Feedback Banner
        Rect statusBannerRect = new Rect(rx + 24, ry + rh - 130, rw - 48, 40);
        if (canInstall)
        {
            GUI.Box(statusBannerRect, "READY TO INSTALL COMPONENT", bannerReadyStyle);
        }
        else
        {
            GUI.Box(statusBannerRect, $"CANNOT INSTALL: {failReason.ToUpper()}", bannerPendingStyle);
        }

        // Big INSTALL Button
        Rect btnRect = new Rect(rx + 24, ry + rh - 80, rw - 48, 56);
        if (canInstall)
        {
            if (GUI.Button(btnRect, $"INSTALL {req.DisplayName.ToUpper()}", actionBtnStyle))
            {
                AudioManager.Instance?.PlayButtonClick();
                currentSite.InstallNext(inventory, out _);
            }
        }
        else
        {
            GUI.Box(btnRect, $"INSTALL {req.DisplayName.ToUpper()}", actionBtnDisabledStyle);
        }
    }

    private void DrawCompletedDetails(float rx, float ry, float rw, float rh)
    {
        Rect hRect = new Rect(rx + 24, ry + 24, rw - 48, 32);
        GUI.Label(hRect, "VESSEL FULLY CONSTRUCTED!", titleStyle);

        Rect subHRect = new Rect(rx + 24, ry + 64, rw - 48, 60);
        GUI.Label(subHRect, "All 5 boat components have been securely installed:\n" +
            "• Reinforced Hull\n• Structural Frame\n• Rope Binding Kit\n• Navigation Paddle\n• Wind-Catching Sail Assembly", itemDescStyle);

        Rect infoBox = new Rect(rx + 24, ry + 160, rw - 48, 100);
        if (slotBgTex != null) GUI.DrawTexture(infoBox, slotBgTex, ScaleMode.StretchToFill);
        else GUI.Box(infoBox, GUIContent.none);

        Rect infoTextRect = new Rect(infoBox.x + 16, infoBox.y + 16, infoBox.width - 32, 68);
        GUI.Label(infoTextRect, "The boat is perched at the cove shoreline and ready for ocean navigation.\n" +
            "Prepare your survival supplies (food, fresh water) before launching the final escape voyage.", itemDescStyle);

        // Launch Button
        Rect launchBtnRect = new Rect(rx + 24, ry + rh - 126, rw - 48, 52);
        if (GUI.Button(launchBtnRect, "LAUNCH ESCAPE BOAT (SET SAIL)", actionBtnStyle))
        {
            AudioManager.Instance?.PlayButtonClick();
            var p = FindAnyObjectByType<PlayerInteraction>();
            CloseUI();
            currentSite.TryLaunch(p, out _);
            return;
        }

        // Close Inspection Button
        Rect btnRect = new Rect(rx + 24, ry + rh - 64, rw - 48, 44);
        if (GUI.Button(btnRect, "CLOSE SHIPYARD INSPECTION", actionBtnStyle))
        {
            AudioManager.Instance?.PlayButtonClick();
            CloseUI();
        }
    }

    private void DrawSprite(Rect rect, Sprite sprite)
    {
        if (sprite == null || sprite.texture == null) return;
        Rect texRect = sprite.rect;
        Rect uvRect = new Rect(
            texRect.x / sprite.texture.width,
            texRect.y / sprite.texture.height,
            texRect.width / sprite.texture.width,
            texRect.height / sprite.texture.height
        );
        GUI.DrawTextureWithTexCoords(rect, sprite.texture, uvRect);
    }

    private void LoadTextures()
    {
        panelTex = LoadTexture("Assets/Art/UI/ui_inventory_panel.png");
        slotBgTex = LoadTexture("Assets/Art/UI/ui_slot_background.png");
        slotSelectedTex = LoadTexture("Assets/Art/UI/ui_slot_selected.png");
        closeBtnTex = LoadTexture("Assets/Art/UI/ui_close_button.png");
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
        if (titleStyle == null)
        {
            titleStyle = new GUIStyle();
            titleStyle.fontSize = 24;
            titleStyle.fontStyle = FontStyle.Bold;
            titleStyle.normal.textColor = new Color(0.32f, 0.18f, 0.08f, 1f);
        }

        if (subtitleStyle == null)
        {
            subtitleStyle = new GUIStyle();
            subtitleStyle.fontSize = 15;
            subtitleStyle.fontStyle = FontStyle.Italic;
            subtitleStyle.normal.textColor = new Color(0.50f, 0.32f, 0.18f, 1f);
        }

        if (sectionStyle == null)
        {
            sectionStyle = new GUIStyle();
            sectionStyle.fontSize = 16;
            sectionStyle.fontStyle = FontStyle.Bold;
            sectionStyle.normal.textColor = new Color(0.40f, 0.24f, 0.12f, 1f);
        }

        if (itemTitleStyle == null)
        {
            itemTitleStyle = new GUIStyle();
            itemTitleStyle.fontSize = 17;
            itemTitleStyle.fontStyle = FontStyle.Bold;
            itemTitleStyle.normal.textColor = new Color(0.30f, 0.18f, 0.08f, 1f);
        }

        if (itemDescStyle == null)
        {
            itemDescStyle = new GUIStyle();
            itemDescStyle.fontSize = 15;
            itemDescStyle.richText = true;
            itemDescStyle.wordWrap = true;
            itemDescStyle.normal.textColor = new Color(0.36f, 0.22f, 0.12f, 1f);
        }

        if (statusStyle == null)
        {
            statusStyle = new GUIStyle();
            statusStyle.fontSize = 14;
            statusStyle.fontStyle = FontStyle.Bold;
            statusStyle.richText = true;
        }

        if (bannerReadyStyle == null)
        {
            bannerReadyStyle = new GUIStyle(GUI.skin.box);
            Texture2D bTex = new Texture2D(1, 1);
            bTex.SetPixel(0, 0, new Color(0.24f, 0.58f, 0.22f, 0.90f));
            bTex.Apply();
            bannerReadyStyle.normal.background = bTex;
            bannerReadyStyle.fontSize = 15;
            bannerReadyStyle.fontStyle = FontStyle.Bold;
            bannerReadyStyle.alignment = TextAnchor.MiddleCenter;
            bannerReadyStyle.normal.textColor = Color.white;
        }

        if (bannerPendingStyle == null)
        {
            bannerPendingStyle = new GUIStyle(GUI.skin.box);
            Texture2D pTex = new Texture2D(1, 1);
            pTex.SetPixel(0, 0, new Color(0.55f, 0.38f, 0.22f, 0.85f));
            pTex.Apply();
            bannerPendingStyle.normal.background = pTex;
            bannerPendingStyle.fontSize = 15;
            bannerPendingStyle.fontStyle = FontStyle.Bold;
            bannerPendingStyle.alignment = TextAnchor.MiddleCenter;
            bannerPendingStyle.normal.textColor = new Color(0.92f, 0.86f, 0.76f, 1f);
        }

        if (actionBtnStyle == null)
        {
            actionBtnStyle = new GUIStyle(GUI.skin.button);
            Texture2D btnTex = new Texture2D(1, 1);
            btnTex.SetPixel(0, 0, new Color(0.22f, 0.55f, 0.20f, 1f));
            btnTex.Apply();
            actionBtnStyle.normal.background = btnTex;
            actionBtnStyle.fontSize = 18;
            actionBtnStyle.fontStyle = FontStyle.Bold;
            actionBtnStyle.alignment = TextAnchor.MiddleCenter;
            actionBtnStyle.normal.textColor = Color.white;
        }

        if (actionBtnDisabledStyle == null)
        {
            actionBtnDisabledStyle = new GUIStyle(GUI.skin.box);
            Texture2D disTex = new Texture2D(1, 1);
            disTex.SetPixel(0, 0, new Color(0.48f, 0.42f, 0.38f, 0.85f));
            disTex.Apply();
            actionBtnDisabledStyle.normal.background = disTex;
            actionBtnDisabledStyle.fontSize = 17;
            actionBtnDisabledStyle.fontStyle = FontStyle.Bold;
            actionBtnDisabledStyle.alignment = TextAnchor.MiddleCenter;
            actionBtnDisabledStyle.normal.textColor = new Color(0.75f, 0.72f, 0.70f, 1f);
        }
    }
}
