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
    [SerializeField] private float slotSize = 44f;

    [Tooltip("Spacing between slots.")]
    [SerializeField] private float slotSpacing = 4f;

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

        float panelWidth = gridWidth + 48f;
        float panelHeight = gridHeight + 96f;

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

        // Draw Title
        Rect titleRect = new Rect(panelX + 24, panelY + 14, 200, 24);
        GUI.Label(titleRect, "INVENTORY", titleStyle);

        // Draw Close Button 'X'
        Rect closeRect = new Rect(panelX + panelWidth - 38, panelY + 12, 24, 24);
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
        Rect hotbarLabelRect = new Rect(panelX + 24, panelY + 38, 200, 16);
        GUI.Label(hotbarLabelRect, "Hotbar (Row 1) & Backpack", sectionStyle);

        Event e = Event.current;
        hoveredTooltip = "";

        float startGridX = panelX + 24;
        float startGridY = panelY + 60;

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

                // Highlight if currently held item slot
                if (heldSlotIndex == slotIndex && slotSelectedTex != null)
                {
                    Rect selRect = new Rect(slotRect.x - 2, slotRect.y - 2, slotSize + 4, slotSize + 4);
                    GUI.DrawTexture(selRect, slotSelectedTex, ScaleMode.StretchToFill);
                }

                var slot = inventory.GetSlot(slotIndex);
                if (slot != null && !slot.IsEmpty && slot.Item != null)
                {
                    // Draw Item Icon
                    if (slot.Item.Icon != null)
                    {
                        Rect iconRect = new Rect(slotRect.x + 6, slotRect.y + 6, slotSize - 12, slotSize - 12);
                        DrawSprite(iconRect, slot.Item.Icon);
                    }

                    // Draw Quantity
                    if (slot.Quantity > 1)
                    {
                        Rect qtyRect = new Rect(slotRect.x + slotSize - 26, slotRect.y + slotSize - 18, 24, 16);
                        GUI.Label(qtyRect, slot.Quantity.ToString(), quantityStyle);
                    }

                    // Hover tooltip
                    if (slotRect.Contains(e.mousePosition) && heldSlotIndex == -1)
                    {
                        hoveredTooltip = $"{slot.Item.DisplayName}\n<size=10>{slot.Item.Description}</size>";
                        hoveredMousePos = e.mousePosition;
                    }
                }

                // Click Handling: Pick up, Swap, or Move
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

        // Draw Floating Held Cursor Item
        if (heldSlotIndex != -1)
        {
            var heldSlot = inventory.GetSlot(heldSlotIndex);
            if (heldSlot != null && !heldSlot.IsEmpty && heldSlot.Item != null && heldSlot.Item.Icon != null)
            {
                Rect heldRect = new Rect(e.mousePosition.x - 18, e.mousePosition.y - 18, 36, 36);
                DrawSprite(heldRect, heldSlot.Item.Icon);
                if (heldSlot.Quantity > 1)
                {
                    Rect heldQtyRect = new Rect(heldRect.x + 16, heldRect.y + 16, 20, 16);
                    GUI.Label(heldQtyRect, heldSlot.Quantity.ToString(), quantityStyle);
                }
            }
        }

        // Draw Hover Tooltip
        if (!string.IsNullOrEmpty(hoveredTooltip))
        {
            Vector2 tooltipSize = tooltipStyle.CalcSize(new GUIContent(hoveredTooltip));
            Rect tipRect = new Rect(hoveredMousePos.x + 14, hoveredMousePos.y + 14, Mathf.Max(120, tooltipSize.x + 16), tooltipSize.y + 12);
            GUI.Box(tipRect, GUIContent.none, tooltipStyle);
            GUI.Label(new Rect(tipRect.x + 8, tipRect.y + 6, tipRect.width - 16, tipRect.height - 12), hoveredTooltip, tooltipStyle);
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
            titleStyle.fontSize = 16;
            titleStyle.fontStyle = FontStyle.Bold;
            titleStyle.normal.textColor = new Color(0.35f, 0.20f, 0.08f, 1f);
        }

        if (sectionStyle == null)
        {
            sectionStyle = new GUIStyle();
            sectionStyle.fontSize = 11;
            sectionStyle.fontStyle = FontStyle.Italic;
            sectionStyle.normal.textColor = new Color(0.50f, 0.35f, 0.20f, 1f);
        }

        if (quantityStyle == null)
        {
            quantityStyle = new GUIStyle();
            quantityStyle.fontSize = 11;
            quantityStyle.fontStyle = FontStyle.Bold;
            quantityStyle.alignment = TextAnchor.LowerRight;
            quantityStyle.normal.textColor = Color.white;
        }

        if (tooltipStyle == null)
        {
            tooltipStyle = new GUIStyle(GUI.skin.box);
            Texture2D tTex = new Texture2D(1, 1);
            tTex.SetPixel(0, 0, new Color(0.12f, 0.08f, 0.04f, 0.92f));
            tTex.Apply();
            tooltipStyle.normal.background = tTex;
            tooltipStyle.normal.textColor = new Color(0.95f, 0.90f, 0.80f, 1f);
            tooltipStyle.fontSize = 12;
            tooltipStyle.wordWrap = true;
        }
    }
}
