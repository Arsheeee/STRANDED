using UnityEngine;
using UnityEngine.InputSystem;

/// <summary>
/// Full Inventory Window UI for STRANDED.
/// Displays a 36-slot grid (3 rows of 12 slots) using authentic Stardew-inspired pixel art styling.
/// Toggles with key 'I' or closes with 'Escape' / close button.
/// Supports clicking to select and swap/merge items between any slots (Hotbar and Backpack).
/// </summary>
public class InventoryUI : MonoBehaviour
{
    private static bool isOpen = false;
    public static bool IsOpen => isOpen;

    [Header("UI Grid Configuration")]
    [Tooltip("Slot size in screen pixels.")]
    [SerializeField] private float slotSize = 80f;

    [Tooltip("Spacing between slots.")]
    [SerializeField] private float slotSpacing = 8f;

    private Inventory inventory;
    private PlayerMovement playerMovement;

    private Texture2D panelTex;
    private Texture2D slotBgTex;
    private Texture2D slotSelectedTex;
    private Texture2D closeBtnTex;

    private GUIStyle titleStyle;
    private GUIStyle sectionStyle;
    private GUIStyle quantityStyle;
    private GUIStyle tooltipStyle;

    private int heldSlotIndex = -1;
    private string hoveredTooltip = "";
    private Vector2 hoveredMousePos;

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
        bool toggleRequested = false;
        bool closeRequested = false;

        // Check New Input System Keyboard
        if (Keyboard.current != null)
        {
            if (Keyboard.current.iKey.wasPressedThisFrame ||
                Keyboard.current.tabKey.wasPressedThisFrame ||
                Keyboard.current.bKey.wasPressedThisFrame)
            {
                toggleRequested = true;
            }

            if (Keyboard.current.escapeKey.wasPressedThisFrame)
            {
                closeRequested = true;
            }
        }

        // Legacy input fallback if active in Project Settings
#if ENABLE_LEGACY_INPUT_MANAGER
        if (!toggleRequested)
        {
            if (Input.GetKeyDown(KeyCode.I) || Input.GetKeyDown(KeyCode.Tab) || Input.GetKeyDown(KeyCode.B))
            {
                toggleRequested = true;
            }
        }
        if (!closeRequested && Input.GetKeyDown(KeyCode.Escape))
        {
            closeRequested = true;
        }
#endif

        if (toggleRequested)
        {
            SetInventoryOpen(!isOpen);
        }
        else if (isOpen && closeRequested)
        {
            if (heldSlotIndex != -1)
            {
                heldSlotIndex = -1; // Drop held cursor item first
            }
            else
            {
                SetInventoryOpen(false);
            }
        }
    }

    public void SetInventoryOpen(bool open)
    {
        isOpen = open;
        heldSlotIndex = -1;

        if (isOpen && CraftingUI.IsOpen)
        {
            var craftUI = FindAnyObjectByType<CraftingUI>();
            craftUI?.SetCraftingOpen(false);
        }

        if (playerMovement != null)
        {
            playerMovement.SetMovementEnabled(!isOpen);
        }

        if (isOpen)
        {
            Cursor.visible = true;
            Cursor.lockState = CursorLockMode.None;
        }
        else
        {
            Cursor.visible = true;
        }
    }

    void OnGUI()
    {
        if (!isOpen || inventory == null) return;

        InitStyles();

        int cols = 12;
        int rows = 3;
        float gridWidth = cols * slotSize + (cols - 1) * slotSpacing;
        float gridHeight = rows * slotSize + (rows - 1) * slotSpacing;

        // VERY VERY BIG Window (1120x720 px)
        float panelWidth = Mathf.Min(Screen.width - 40f, gridWidth + 72f);
        float panelHeight = Mathf.Min(Screen.height - 40f, 720f);

        float panelX = (Screen.width - panelWidth) * 0.5f;
        float panelY = (Screen.height - panelHeight) * 0.5f;

        Rect panelRect = new Rect(panelX, panelY, panelWidth, panelHeight);

        // Draw Panel Background
        if (panelTex != null)
        {
            GUI.DrawTexture(panelRect, panelTex, ScaleMode.StretchToFill);
        }
        else
        {
            GUI.Box(panelRect, GUIContent.none);
        }

        // Draw Decorative Header Tabs along Top
        float tabW = 150f;
        float tabH = 34f;
        Rect tab1 = new Rect(panelX + 36, panelY - tabH + 6, tabW, tabH);
        GUI.Box(tab1, "INVENTORY", activeTabStyle);

        Rect tab2 = new Rect(panelX + 36 + tabW + 8, panelY - tabH + 6, tabW, tabH);
        if (GUI.Button(tab2, "CRAFTING", inactiveTabStyle))
        {
            SetInventoryOpen(false);
            var craftUI = FindAnyObjectByType<CraftingUI>();
            craftUI?.SetCraftingOpen(true);
            return;
        }

        Rect tab3 = new Rect(panelX + 36 + (tabW + 8) * 2, panelY - tabH + 6, tabW, tabH);
        GUI.Box(tab3, "ISLAND MAP", inactiveTabStyle);

        // Draw Close Button 'X'
        Rect closeRect = new Rect(panelX + panelWidth - 48, panelY + 14, 36, 36);
        if (closeBtnTex != null)
        {
            if (GUI.Button(closeRect, GUIContent.none, GUIStyle.none))
            {
                SetInventoryOpen(false);
                return;
            }
            GUI.DrawTexture(closeRect, closeBtnTex, ScaleMode.StretchToFill);
        }
        else
        {
            if (GUI.Button(closeRect, "X"))
            {
                SetInventoryOpen(false);
                return;
            }
        }

        // Section Label: Hotbar vs Backpack
        Rect hotbarLabelRect = new Rect(panelX + 32, panelY + 16, 300, 22);
        GUI.Label(hotbarLabelRect, "HOTBAR (ROW 1) & BACKPACK (ROWS 2-3)", sectionStyle);

        Event e = Event.current;
        hoveredTooltip = "";

        float startGridX = panelX + 28;
        float startGridY = panelY + 44;

        for (int r = 0; r < rows; r++)
        {
            for (int c = 0; c < cols; c++)
            {
                int slotIndex = r * cols + c;
                if (slotIndex >= inventory.TotalSlots) break;

                Rect slotRect = new Rect(startGridX + c * (slotSize + slotSpacing), startGridY + r * (slotSize + slotSpacing), slotSize, slotSize);

                // Draw Slot Background
                if (slotBgTex != null)
                {
                    GUI.DrawTexture(slotRect, slotBgTex, ScaleMode.StretchToFill);
                }
                else
                {
                    GUI.Box(slotRect, GUIContent.none);
                }

                // Row 1 (Hotbar): Draw Red Hotkey Numbers matching Stardew Valley
                if (r == 0)
                {
                    string keyLabel = GetSlotKey(c);
                    Rect keyRect = new Rect(slotRect.x + 5, slotRect.y + 3, 20, 20);
                    GUI.Label(keyRect, keyLabel, slotNumberStyle);
                }

                // Highlight if currently held item slot
                if (heldSlotIndex == slotIndex && slotSelectedTex != null)
                {
                    Rect selRect = new Rect(slotRect.x - 3, slotRect.y - 3, slotSize + 6, slotSize + 6);
                    GUI.DrawTexture(selRect, slotSelectedTex, ScaleMode.StretchToFill);
                }

                var slot = inventory.GetSlot(slotIndex);
                if (slot != null && !slot.IsEmpty && slot.Item != null)
                {
                    // Draw Item Icon (Large 48x48)
                    if (slot.Item.Icon != null)
                    {
                        Rect iconRect = new Rect(slotRect.x + 8, slotRect.y + 8, slotSize - 16, slotSize - 16);
                        DrawSprite(iconRect, slot.Item.Icon);
                    }

                    // Draw Quantity
                    if (slot.Quantity > 1)
                    {
                        Rect qtyShadowRect = new Rect(slotRect.x + slotSize - 35, slotRect.y + slotSize - 25, 32, 22);
                        GUI.Label(qtyShadowRect, slot.Quantity.ToString(), quantityShadowStyle);
                        Rect qtyRect = new Rect(slotRect.x + slotSize - 36, slotRect.y + slotSize - 26, 32, 22);
                        GUI.Label(qtyRect, slot.Quantity.ToString(), quantityStyle);
                    }

                    // Hover tooltip
                    if (slotRect.Contains(e.mousePosition) && heldSlotIndex == -1)
                    {
                        hoveredTooltip = $"<b>{slot.Item.DisplayName}</b>\n<size=13>{slot.Item.Description}</size>";
                        hoveredMousePos = e.mousePosition;
                    }
                }

                // Click Handling: Pick up, Swap, or Merge
                if (e.type == EventType.MouseDown && e.button == 0 && slotRect.Contains(e.mousePosition))
                {
                    if (heldSlotIndex == -1)
                    {
                        // Pick up item if slot not empty
                        if (slot != null && !slot.IsEmpty)
                        {
                            heldSlotIndex = slotIndex;
                        }
                    }
                    else
                    {
                        // Place / Swap with target slot
                        inventory.SwapSlots(heldSlotIndex, slotIndex);
                        heldSlotIndex = -1;
                    }
                    e.Use();
                }
            }
        }

        // Draw Wood Divider Bar separating slot grid from bottom survivor card
        float dividerY = startGridY + gridHeight + 14f;
        Rect dividerRect = new Rect(panelX + 28, dividerY, panelWidth - 56, 4);
        if (dividerTex != null)
        {
            GUI.DrawTexture(dividerRect, dividerTex);
        }
        else
        {
            GUI.Box(dividerRect, GUIContent.none);
        }

        // Draw Bottom Survivor Card (matching Stardew Valley's Vinland Farm character card)
        float cardY = dividerY + 14f;

        // 1. Portrait Box on the Left
        Rect portraitFrame = new Rect(panelX + 36, cardY, 110, 130);
        if (slotBgTex != null) GUI.DrawTexture(portraitFrame, slotBgTex, ScaleMode.StretchToFill);
        else GUI.Box(portraitFrame, GUIContent.none);

        // Portrait inner artwork
        Rect portraitInner = new Rect(portraitFrame.x + 8, portraitFrame.y + 8, portraitFrame.width - 16, portraitFrame.height - 36);
        GUI.Box(portraitInner, GUIContent.none, portraitBoxStyle);
        Rect portraitLabelRect = new Rect(portraitFrame.x, portraitFrame.y + portraitFrame.height - 24, portraitFrame.width, 20);
        GUI.Label(portraitLabelRect, "SURVIVOR", cardSubStyle);

        // 2. Survivor & Island Details on the Right
        float infoX = panelX + 165f;
        Rect titleCardRect = new Rect(infoX, cardY + 2, 450, 30);
        GUI.Label(titleCardRect, "STRANDED ISLAND", cardTitleStyle);

        Rect campStatusRect = new Rect(infoX, cardY + 36, 450, 22);
        GUI.Label(campStatusRect, "Camp: Tropical Coastline Sanctuary", cardInfoStyle);

        Rect storageStatusRect = new Rect(infoX, cardY + 60, 450, 22);
        GUI.Label(storageStatusRect, "Storage: 36 Total Slots (12 Hotbar, 24 Backpack)", cardInfoStyle);

        string equippedName = "Bare Hands";
        var activeHotbar = inventory.GetSlot(0);
        var pInteraction = FindAnyObjectByType<PlayerInteraction>();
        if (pInteraction != null && pInteraction.CurrentTool != ToolType.None)
        {
            equippedName = pInteraction.CurrentTool.ToDisplayName();
        }
        Rect toolStatusRect = new Rect(infoX, cardY + 84, 450, 22);
        GUI.Label(toolStatusRect, $"Equipped Tool: <color=#206020><b>{equippedName}</b></color>", cardInfoStyle);

        Rect seasonRect = new Rect(infoX, cardY + 108, 450, 22);
        GUI.Label(seasonRect, "Day 1 - Spring, Year 1", cardSubStyle);

        // 3. Trash Can / Discard Box on far right
        Rect trashRect = new Rect(panelX + panelWidth - 95, cardY + 24, 60, 70);
        if (slotBgTex != null) GUI.DrawTexture(trashRect, slotBgTex, ScaleMode.StretchToFill);
        else GUI.Box(trashRect, GUIContent.none);
        GUI.Label(new Rect(trashRect.x, trashRect.y + 12, trashRect.width, 20), "TRASH", cardSubStyle);
        GUI.Label(new Rect(trashRect.x, trashRect.y + 36, trashRect.width, 20), "[Drop]", sectionStyle);

        if (e.type == EventType.MouseDown && e.button == 0 && trashRect.Contains(e.mousePosition))
        {
            if (heldSlotIndex != -1)
            {
                inventory.ClearSlot(heldSlotIndex);
                heldSlotIndex = -1;
            }
            e.Use();
        }

        // Draw Floating Held Cursor Item
        if (heldSlotIndex != -1)
        {
            var heldSlot = inventory.GetSlot(heldSlotIndex);
            if (heldSlot != null && !heldSlot.IsEmpty && heldSlot.Item != null && heldSlot.Item.Icon != null)
            {
                Rect heldRect = new Rect(e.mousePosition.x - 24, e.mousePosition.y - 24, 48, 48);
                DrawSprite(heldRect, heldSlot.Item.Icon);
                if (heldSlot.Quantity > 1)
                {
                    Rect heldQtyRect = new Rect(heldRect.x + 22, heldRect.y + 22, 28, 18);
                    GUI.Label(heldQtyRect, heldSlot.Quantity.ToString(), quantityStyle);
                }
            }
        }

        // Draw Hover Tooltip
        if (!string.IsNullOrEmpty(hoveredTooltip))
        {
            Vector2 tooltipSize = tooltipStyle.CalcSize(new GUIContent(hoveredTooltip));
            float tipW = Mathf.Max(160, tooltipSize.x + 24);
            float tipH = tooltipSize.y + 18;
            Rect tipRect = new Rect(hoveredMousePos.x + 16, hoveredMousePos.y + 16, tipW, tipH);
            GUI.Box(tipRect, GUIContent.none, tooltipStyle);
            GUI.Label(new Rect(tipRect.x + 10, tipRect.y + 8, tipRect.width - 20, tipRect.height - 16), hoveredTooltip, tooltipStyle);
        }
    }

    private string GetSlotKey(int col)
    {
        switch (col)
        {
            case 0: return "1";
            case 1: return "2";
            case 2: return "3";
            case 3: return "4";
            case 4: return "5";
            case 5: return "6";
            case 6: return "7";
            case 7: return "8";
            case 8: return "9";
            case 9: return "0";
            case 10: return "-";
            case 11: return "=";
            default: return "";
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

        dividerTex = new Texture2D(1, 1);
        dividerTex.SetPixel(0, 0, new Color(0.48f, 0.28f, 0.14f, 1f));
        dividerTex.Apply();
    }

    private Texture2D dividerTex;
    private GUIStyle activeTabStyle;
    private GUIStyle inactiveTabStyle;
    private GUIStyle cardTitleStyle;
    private GUIStyle cardInfoStyle;
    private GUIStyle cardSubStyle;
    private GUIStyle portraitBoxStyle;
    private GUIStyle quantityShadowStyle;
    private GUIStyle slotNumberStyle;

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
            titleStyle.fontSize = 20;
            titleStyle.fontStyle = FontStyle.Bold;
            titleStyle.normal.textColor = new Color(0.35f, 0.20f, 0.08f, 1f);
        }

        if (sectionStyle == null)
        {
            sectionStyle = new GUIStyle();
            sectionStyle.fontSize = 13;
            sectionStyle.fontStyle = FontStyle.Bold;
            sectionStyle.normal.textColor = new Color(0.45f, 0.28f, 0.14f, 1f);
        }

        if (slotNumberStyle == null)
        {
            slotNumberStyle = new GUIStyle();
            slotNumberStyle.fontSize = 15;
            slotNumberStyle.fontStyle = FontStyle.Bold;
            slotNumberStyle.normal.textColor = new Color(0.82f, 0.16f, 0.12f, 1f);
        }

        if (quantityStyle == null)
        {
            quantityStyle = new GUIStyle();
            quantityStyle.fontSize = 15;
            quantityStyle.fontStyle = FontStyle.Bold;
            quantityStyle.alignment = TextAnchor.LowerRight;
            quantityStyle.normal.textColor = Color.white;
        }

        if (quantityShadowStyle == null)
        {
            quantityShadowStyle = new GUIStyle(quantityStyle);
            quantityShadowStyle.normal.textColor = new Color(0.1f, 0.1f, 0.1f, 0.85f);
        }

        if (activeTabStyle == null)
        {
            activeTabStyle = new GUIStyle(GUI.skin.box);
            Texture2D aTex = new Texture2D(1, 1);
            aTex.SetPixel(0, 0, new Color(0.88f, 0.72f, 0.48f, 1f));
            aTex.Apply();
            activeTabStyle.normal.background = aTex;
            activeTabStyle.fontSize = 13;
            activeTabStyle.fontStyle = FontStyle.Bold;
            activeTabStyle.alignment = TextAnchor.MiddleCenter;
            activeTabStyle.normal.textColor = new Color(0.30f, 0.16f, 0.06f, 1f);
        }

        if (inactiveTabStyle == null)
        {
            inactiveTabStyle = new GUIStyle(GUI.skin.box);
            Texture2D inTex = new Texture2D(1, 1);
            inTex.SetPixel(0, 0, new Color(0.55f, 0.38f, 0.22f, 0.85f));
            inTex.Apply();
            inactiveTabStyle.normal.background = inTex;
            inactiveTabStyle.fontSize = 12;
            inactiveTabStyle.alignment = TextAnchor.MiddleCenter;
            inactiveTabStyle.normal.textColor = new Color(0.85f, 0.78f, 0.68f, 1f);
        }

        if (cardTitleStyle == null)
        {
            cardTitleStyle = new GUIStyle();
            cardTitleStyle.fontSize = 24;
            cardTitleStyle.fontStyle = FontStyle.Bold;
            cardTitleStyle.normal.textColor = new Color(0.32f, 0.18f, 0.08f, 1f);
        }

        if (cardInfoStyle == null)
        {
            cardInfoStyle = new GUIStyle();
            cardInfoStyle.fontSize = 15;
            cardInfoStyle.fontStyle = FontStyle.Normal;
            cardInfoStyle.normal.textColor = new Color(0.40f, 0.25f, 0.12f, 1f);
            cardInfoStyle.richText = true;
        }

        if (cardSubStyle == null)
        {
            cardSubStyle = new GUIStyle();
            cardSubStyle.fontSize = 14;
            cardSubStyle.fontStyle = FontStyle.Bold;
            cardSubStyle.alignment = TextAnchor.MiddleCenter;
            cardSubStyle.normal.textColor = new Color(0.45f, 0.28f, 0.14f, 1f);
        }

        if (portraitBoxStyle == null)
        {
            portraitBoxStyle = new GUIStyle(GUI.skin.box);
            Texture2D pTex = new Texture2D(1, 1);
            pTex.SetPixel(0, 0, new Color(0.32f, 0.48f, 0.30f, 0.90f));
            pTex.Apply();
            portraitBoxStyle.normal.background = pTex;
        }

        if (tooltipStyle == null)
        {
            tooltipStyle = new GUIStyle(GUI.skin.box);
            Texture2D tTex = new Texture2D(1, 1);
            tTex.SetPixel(0, 0, new Color(0.12f, 0.08f, 0.04f, 0.95f));
            tTex.Apply();
            tooltipStyle.normal.background = tTex;
            tooltipStyle.normal.textColor = new Color(0.95f, 0.90f, 0.80f, 1f);
            tooltipStyle.fontSize = 14;
            tooltipStyle.richText = true;
            tooltipStyle.wordWrap = true;
            tooltipStyle.padding = new RectOffset(12, 12, 10, 10);
        }
    }
}
