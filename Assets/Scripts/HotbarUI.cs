using UnityEngine;
using UnityEngine.InputSystem;

/// <summary>
/// Hotbar UI for STRANDED.
/// Displays the 12 active hotbar slots (slots 0..11 of Inventory) at the bottom center of the screen.
/// Supports slot selection via keyboard (Keys 1-9, 0, -, =) and mouse clicks.
/// Synchronizes the equipped tool state directly with PlayerInteraction.
/// </summary>
public class HotbarUI : MonoBehaviour
{
    [Header("Hotbar Configuration")]
    [Tooltip("Size in screen pixels of each square hotbar slot.")]
    [SerializeField] private float slotSize = 80f;

    [Tooltip("Spacing between adjacent slots.")]
    [SerializeField] private float slotSpacing = 8f;

    [Tooltip("Vertical padding from the bottom edge of the screen.")]
    [SerializeField] private float bottomPadding = 24f;

    private Inventory inventory;
    private PlayerInteraction playerInteraction;
    private int selectedSlotIndex = 0;

    private Texture2D slotBgTex;
    private Texture2D slotSelectedTex;
    private GUIStyle slotNumberStyle;
    private GUIStyle quantityStyle;
    private GUIStyle containerStyle;

    public int SelectedSlotIndex => selectedSlotIndex;

    void Awake()
    {
        inventory = GetComponentInParent<Inventory>();
        playerInteraction = GetComponentInParent<PlayerInteraction>();

        LoadTextures();
    }

    void Start()
    {
        if (inventory == null) inventory = FindAnyObjectByType<Inventory>();
        if (playerInteraction == null) playerInteraction = FindAnyObjectByType<PlayerInteraction>();

        if (inventory != null)
        {
            inventory.OnInventoryChanged += OnInventoryContentsChanged;
        }

        // Initialize tool sync with currently selected slot
        SyncEquippedTool();
    }

    void OnDestroy()
    {
        if (inventory != null)
        {
            inventory.OnInventoryChanged -= OnInventoryContentsChanged;
        }
    }

    void Update()
    {
        // Only handle hotbar input if full inventory and crafting UI are NOT currently open
        if (InventoryUI.IsOpen || CraftingUI.IsOpen) return;

        HandleHotbarKeys();
    }

    private void HandleHotbarKeys()
    {
        if (Keyboard.current == null) return;

        int targetIndex = -1;

        if (Keyboard.current.digit1Key.wasPressedThisFrame || Keyboard.current.numpad1Key.wasPressedThisFrame) targetIndex = 0;
        else if (Keyboard.current.digit2Key.wasPressedThisFrame || Keyboard.current.numpad2Key.wasPressedThisFrame) targetIndex = 1;
        else if (Keyboard.current.digit3Key.wasPressedThisFrame || Keyboard.current.numpad3Key.wasPressedThisFrame) targetIndex = 2;
        else if (Keyboard.current.digit4Key.wasPressedThisFrame || Keyboard.current.numpad4Key.wasPressedThisFrame) targetIndex = 3;
        else if (Keyboard.current.digit5Key.wasPressedThisFrame || Keyboard.current.numpad5Key.wasPressedThisFrame) targetIndex = 4;
        else if (Keyboard.current.digit6Key.wasPressedThisFrame || Keyboard.current.numpad6Key.wasPressedThisFrame) targetIndex = 5;
        else if (Keyboard.current.digit7Key.wasPressedThisFrame || Keyboard.current.numpad7Key.wasPressedThisFrame) targetIndex = 6;
        else if (Keyboard.current.digit8Key.wasPressedThisFrame || Keyboard.current.numpad8Key.wasPressedThisFrame) targetIndex = 7;
        else if (Keyboard.current.digit9Key.wasPressedThisFrame || Keyboard.current.numpad9Key.wasPressedThisFrame) targetIndex = 8;
        else if (Keyboard.current.digit0Key.wasPressedThisFrame || Keyboard.current.numpad0Key.wasPressedThisFrame) targetIndex = 9;
        else if (Keyboard.current.minusKey.wasPressedThisFrame) targetIndex = 10;
        else if (Keyboard.current.equalsKey.wasPressedThisFrame) targetIndex = 11;

        if (targetIndex >= 0 && targetIndex < 12)
        {
            SelectSlot(targetIndex);
        }
    }

    public void SelectSlot(int index)
    {
        if (index < 0 || index >= 12) return;
        selectedSlotIndex = index;
        SyncEquippedTool();
    }

    private void OnInventoryContentsChanged()
    {
        // Re-sync equipped tool whenever inventory changes in case selected slot item changed
        SyncEquippedTool();
    }

    /// <summary>
    /// Synchronizes PlayerInteraction with whatever item is in the currently selected hotbar slot.
    /// Single source of truth.
    /// </summary>
    public void SyncEquippedTool()
    {
        if (inventory == null || playerInteraction == null) return;

        InventorySlot activeSlot = inventory.GetSlot(selectedSlotIndex);
        if (activeSlot != null && !activeSlot.IsEmpty && activeSlot.Item.ItemType == ItemType.Tool)
        {
            playerInteraction.EquipTool(activeSlot.Item.ToolType);
        }
        else
        {
            playerInteraction.EquipTool(ToolType.None);
        }
    }

    void OnGUI()
    {
        if (inventory == null) return;

        InitStyles();

        int count = Mathf.Min(12, inventory.HotbarSlotsCount);
        float totalWidth = count * slotSize + (count - 1) * slotSpacing;
        float startX = (Screen.width - (totalWidth + (slotSize + slotSpacing) * 2)) * 0.5f;
        float startY = Screen.height - slotSize - bottomPadding;

        // Draw hotbar outer container (includes 12 slots + BAG button + CRAFT button)
        float sideButtonsWidth = (slotSize + slotSpacing) * 2;
        float fullBarWidth = totalWidth + sideButtonsWidth;
        Rect containerRect = new Rect(startX - 10, startY - 10, fullBarWidth + 20, slotSize + 20);
        GUI.Box(containerRect, GUIContent.none, containerStyle);

        Event e = Event.current;

        for (int i = 0; i < count; i++)
        {
            Rect slotRect = new Rect(startX + i * (slotSize + slotSpacing), startY, slotSize, slotSize);

            // Draw Slot Background
            if (slotBgTex != null)
            {
                GUI.DrawTexture(slotRect, slotBgTex, ScaleMode.StretchToFill);
            }
            else
            {
                GUI.Box(slotRect, GUIContent.none);
            }

            // Draw Slot Item Icon & Quantity
            var slot = inventory.GetSlot(i);
            if (slot != null && !slot.IsEmpty && slot.Item != null)
            {
                if (slot.Item.Icon != null)
                {
                    // Large icon inside 80x80 slot
                    Rect iconRect = new Rect(slotRect.x + 10, slotRect.y + 10, slotSize - 20, slotSize - 20);
                    DrawSprite(iconRect, slot.Item.Icon);
                }

                if (slot.Quantity > 1)
                {
                    Rect qtyShadowRect = new Rect(slotRect.x + slotSize - 42, slotRect.y + slotSize - 30, 38, 26);
                    GUI.Label(qtyShadowRect, slot.Quantity.ToString(), quantityShadowStyle);
                    Rect qtyRect = new Rect(slotRect.x + slotSize - 43, slotRect.y + slotSize - 31, 38, 26);
                    GUI.Label(qtyRect, slot.Quantity.ToString(), quantityStyle);
                }
            }

            // Draw Slot Index Label (1, 2, ... 9, 0, -, =) in Stardew-style red
            string labelKey = GetSlotLabel(i);
            Rect labelRect = new Rect(slotRect.x + 6, slotRect.y + 4, 24, 24);
            GUI.Label(labelRect, labelKey, slotNumberStyle);

            // Draw Selected Highlight (prominent border)
            if (i == selectedSlotIndex && slotSelectedTex != null)
            {
                Rect selRect = new Rect(slotRect.x - 4, slotRect.y - 4, slotSize + 8, slotSize + 8);
                GUI.DrawTexture(selRect, slotSelectedTex, ScaleMode.StretchToFill);
            }

            // Mouse Click to select slot
            if (e.type == EventType.MouseDown && e.button == 0 && slotRect.Contains(e.mousePosition))
            {
                SelectSlot(i);
                e.Use();
            }
        }

        // Draw Clickable Bag Toggle Button on right of hotbar
        Rect bagBtnRect = new Rect(startX + count * (slotSize + slotSpacing) + 6, startY, slotSize, slotSize);
        if (slotBgTex != null) GUI.DrawTexture(bagBtnRect, slotBgTex, ScaleMode.StretchToFill);
        else GUI.Box(bagBtnRect, GUIContent.none);

        GUI.Label(new Rect(bagBtnRect.x, bagBtnRect.y + 14, slotSize, 22), "BAG", bagLabelStyle);
        GUI.Label(new Rect(bagBtnRect.x, bagBtnRect.y + 40, slotSize, 22), "[ I ]", bagSubStyle);

        if (e.type == EventType.MouseDown && e.button == 0 && bagBtnRect.Contains(e.mousePosition))
        {
            var invUI = Object.FindAnyObjectByType<InventoryUI>();
            invUI?.SetInventoryOpen(!InventoryUI.IsOpen);
            e.Use();
        }

        // Draw Clickable Craft Toggle Button right next to Bag button
        Rect craftBtnRect = new Rect(bagBtnRect.x + slotSize + slotSpacing, startY, slotSize, slotSize);
        if (slotBgTex != null) GUI.DrawTexture(craftBtnRect, slotBgTex, ScaleMode.StretchToFill);
        else GUI.Box(craftBtnRect, GUIContent.none);

        GUI.Label(new Rect(craftBtnRect.x, craftBtnRect.y + 14, slotSize, 22), "CRAFT", bagLabelStyle);
        GUI.Label(new Rect(craftBtnRect.x, craftBtnRect.y + 40, slotSize, 22), "[ C ]", bagSubStyle);

        if (e.type == EventType.MouseDown && e.button == 0 && craftBtnRect.Contains(e.mousePosition))
        {
            var craftUI = Object.FindAnyObjectByType<CraftingUI>();
            craftUI?.SetCraftingOpen(!CraftingUI.IsOpen);
            e.Use();
        }
    }

    private string GetSlotLabel(int index)
    {
        switch (index)
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
        slotBgTex = LoadTexture("Assets/Art/UI/ui_slot_background.png");
        slotSelectedTex = LoadTexture("Assets/Art/UI/ui_slot_selected.png");
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

    private GUIStyle quantityShadowStyle;
    private GUIStyle bagLabelStyle;
    private GUIStyle bagSubStyle;

    private void InitStyles()
    {
        if (slotNumberStyle == null)
        {
            slotNumberStyle = new GUIStyle();
            slotNumberStyle.fontSize = 18;
            slotNumberStyle.fontStyle = FontStyle.Bold;
            // Authentic Stardew Valley red slot numbers
            slotNumberStyle.normal.textColor = new Color(0.85f, 0.16f, 0.12f, 1f);
        }

        if (quantityStyle == null)
        {
            quantityStyle = new GUIStyle();
            quantityStyle.fontSize = 18;
            quantityStyle.fontStyle = FontStyle.Bold;
            quantityStyle.alignment = TextAnchor.LowerRight;
            quantityStyle.normal.textColor = Color.white;
        }

        if (quantityShadowStyle == null)
        {
            quantityShadowStyle = new GUIStyle(quantityStyle);
            quantityShadowStyle.normal.textColor = new Color(0.1f, 0.1f, 0.1f, 0.85f);
        }

        if (bagLabelStyle == null)
        {
            bagLabelStyle = new GUIStyle();
            bagLabelStyle.fontSize = 16;
            bagLabelStyle.fontStyle = FontStyle.Bold;
            bagLabelStyle.alignment = TextAnchor.MiddleCenter;
            bagLabelStyle.normal.textColor = new Color(0.38f, 0.22f, 0.10f, 1f);
        }

        if (bagSubStyle == null)
        {
            bagSubStyle = new GUIStyle();
            bagSubStyle.fontSize = 15;
            bagSubStyle.fontStyle = FontStyle.Bold;
            bagSubStyle.alignment = TextAnchor.MiddleCenter;
            bagSubStyle.normal.textColor = new Color(0.85f, 0.16f, 0.12f, 1f);
        }

        if (containerStyle == null)
        {
            containerStyle = new GUIStyle(GUI.skin.box);
            Texture2D cTex = new Texture2D(1, 1);
            cTex.SetPixel(0, 0, new Color(0.18f, 0.11f, 0.05f, 0.88f));
            cTex.Apply();
            containerStyle.normal.background = cTex;
        }
    }
}
