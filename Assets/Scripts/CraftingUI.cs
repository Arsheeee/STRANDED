using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;

/// <summary>
/// Full Crafting UI window for STRANDED.
/// Displays available primitive tool recipes, material requirements vs current player counts,
/// and executes crafting transactions.
/// Modeled after Stardew Valley warm parchment aesthetic and sized VERY VERY BIG for clear visibility.
/// </summary>
public class CraftingUI : MonoBehaviour
{
    private static bool isOpen = false;
    public static bool IsOpen => isOpen;

    private Inventory inventory;
    private PlayerMovement playerMovement;
    private CraftingManager craftingManager;

    private int selectedRecipeIndex = 0;
    private int selectedCategoryIndex = 0;
    private Vector2 recipeScrollPosition = Vector2.zero;
    private static readonly string[] CategoryLabels = new string[] { "ALL", "TOOLS", "MATERIALS", "BOAT" };
    private static readonly string[] CategoryFilters = new string[] { "All", "Tools", "Materials", "Boat Components" };

    private Texture2D panelTex;
    private Texture2D slotBgTex;
    private Texture2D slotSelectedTex;
    private Texture2D closeBtnTex;
    private Texture2D buttonNormalTex;
    private Texture2D buttonDisabledTex;
    private Texture2D buttonActiveTex;

    private GUIStyle titleStyle;
    private GUIStyle sectionStyle;
    private GUIStyle activeTabStyle;
    private GUIStyle inactiveTabStyle;
    private GUIStyle recipeTitleStyle;
    private GUIStyle recipeDescStyle;
    private GUIStyle ingredientStyle;
    private GUIStyle craftBtnStyle;
    private GUIStyle craftBtnDisabledStyle;
    private GUIStyle statusStyle;
    private GUIStyle cardStyle;
    private GUIStyle cardSelectedStyle;

    void Awake()
    {
        inventory = GetComponentInParent<Inventory>();
        playerMovement = GetComponentInParent<PlayerMovement>();
        craftingManager = GetComponentInParent<CraftingManager>();
        if (craftingManager == null)
        {
            craftingManager = gameObject.AddComponent<CraftingManager>();
        }

        RecipeDatabase.EnsureInitialized();
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

        if (Keyboard.current != null)
        {
            if (Keyboard.current.cKey.wasPressedThisFrame)
            {
                toggleRequested = true;
            }
            if (Keyboard.current.escapeKey.wasPressedThisFrame)
            {
                closeRequested = true;
            }
        }

#if ENABLE_LEGACY_INPUT_MANAGER
        if (!toggleRequested && Input.GetKeyDown(KeyCode.C))
        {
            toggleRequested = true;
        }
        if (!closeRequested && Input.GetKeyDown(KeyCode.Escape))
        {
            closeRequested = true;
        }
#endif

        if (toggleRequested)
        {
            SetCraftingOpen(!isOpen);
        }
        else if (isOpen && closeRequested)
        {
            SetCraftingOpen(false);
        }
    }

    public void SetCraftingOpen(bool open)
    {
        isOpen = open;

        // If opening crafting, close inventory window if it was open
        if (isOpen && InventoryUI.IsOpen)
        {
            var invUI = FindAnyObjectByType<InventoryUI>();
            invUI?.SetInventoryOpen(false);
        }

        if (playerMovement != null)
        {
            playerMovement.SetMovementEnabled(!isOpen);
        }

        if (isOpen)
        {
            Cursor.visible = true;
            Cursor.lockState = CursorLockMode.None;
            AudioManager.Instance?.PlayInventoryOpen();
        }
        else
        {
            AudioManager.Instance?.PlayInventoryClose();
        }
    }

    void OnGUI()
    {
        if (!isOpen || inventory == null) return;

        InitStyles();

        string activeFilter = CategoryFilters[selectedCategoryIndex];
        List<CraftingRecipe> recipes = RecipeDatabase.GetRecipesByCategory(activeFilter);
        if (recipes == null) recipes = new List<CraftingRecipe>();
        if (selectedRecipeIndex >= recipes.Count) selectedRecipeIndex = Mathf.Max(0, recipes.Count - 1);

        // VERY VERY BIG Window (1120 x 720 px)
        float panelWidth = Mathf.Min(Screen.width - 40f, 1120f);
        float panelHeight = Mathf.Min(Screen.height - 40f, 720f);

        float panelX = (Screen.width - panelWidth) * 0.5f;
        float panelY = (Screen.height - panelHeight) * 0.5f;

        Rect panelRect = new Rect(panelX, panelY, panelWidth, panelHeight);

        // Draw Parchment Panel Background
        if (panelTex != null)
        {
            GUI.DrawTexture(panelRect, panelTex, ScaleMode.StretchToFill);
        }
        else
        {
            GUI.Box(panelRect, GUIContent.none);
        }

        // Draw Top Tabs
        float tabW = 150f;
        float tabH = 34f;
        Rect tab1 = new Rect(panelX + 36, panelY - tabH + 6, tabW, tabH);
        if (GUI.Button(tab1, "INVENTORY", inactiveTabStyle))
        {
            SetCraftingOpen(false);
            var invUI = FindAnyObjectByType<InventoryUI>();
            invUI?.SetInventoryOpen(true);
            return;
        }

        Rect tab2 = new Rect(panelX + 36 + tabW + 8, panelY - tabH + 6, tabW, tabH);
        GUI.Box(tab2, "CRAFTING", activeTabStyle);

        // Red Close Button 'X'
        Rect closeRect = new Rect(panelX + panelWidth - 48, panelY + 14, 36, 36);
        if (closeBtnTex != null)
        {
            if (GUI.Button(closeRect, GUIContent.none, GUIStyle.none))
            {
                SetCraftingOpen(false);
                return;
            }
            GUI.DrawTexture(closeRect, closeBtnTex, ScaleMode.StretchToFill);
        }
        else
        {
            if (GUI.Button(closeRect, "X"))
            {
                SetCraftingOpen(false);
                return;
            }
        }

        // Title
        Rect titleRect = new Rect(panelX + 36, panelY + 16, 500, 32);
        GUI.Label(titleRect, "PRIMITIVE CRAFTING BENCH", titleStyle);

        Event e = Event.current;

        // =====================================================================
        // LEFT COLUMN: RECIPES & CATEGORY FILTER
        // =====================================================================
        float listX = panelX + 36f;
        float listY = panelY + 54f;
        float listW = 390f;

        // Category Filter Buttons
        float catBtnW = (listW - 12f) / 4f;
        float catBtnH = 28f;
        for (int c = 0; c < CategoryLabels.Length; c++)
        {
            Rect catRect = new Rect(listX + c * (catBtnW + 4f), listY, catBtnW, catBtnH);
            bool isCatActive = (c == selectedCategoryIndex);
            if (GUI.Button(catRect, CategoryLabels[c], isCatActive ? activeTabStyle : inactiveTabStyle))
            {
                if (selectedCategoryIndex != c)
                {
                    selectedCategoryIndex = c;
                    selectedRecipeIndex = 0;
                    recipeScrollPosition = Vector2.zero;
                }
            }
        }

        float cardStartY = listY + 36f;
        float cardH = 104f;
        float cardSpacing = 8f;
        float scrollOuterH = panelHeight - (cardStartY - panelY) - 24f;

        Rect scrollOuterRect = new Rect(listX, cardStartY, listW, scrollOuterH);
        float totalInnerH = recipes.Count * (cardH + cardSpacing);
        Rect scrollInnerRect = new Rect(0, 0, listW - 18f, Mathf.Max(scrollOuterH, totalInnerH));

        recipeScrollPosition = GUI.BeginScrollView(scrollOuterRect, recipeScrollPosition, scrollInnerRect, false, true);

        for (int i = 0; i < recipes.Count; i++)
        {
            var recipe = recipes[i];
            bool isSelected = (i == selectedRecipeIndex);
            bool canCraftThis = craftingManager.CanCraft(recipe, inventory, out string failReason);

            Rect cardRect = new Rect(0, i * (cardH + cardSpacing), listW - 20f, cardH);

            // Card background
            if (slotBgTex != null)
            {
                GUI.DrawTexture(cardRect, slotBgTex, ScaleMode.StretchToFill);
            }
            else
            {
                GUI.Box(cardRect, GUIContent.none);
            }

            // Selection border
            if (isSelected && slotSelectedTex != null)
            {
                Rect selRect = new Rect(cardRect.x - 2, cardRect.y - 2, cardRect.width + 4, cardRect.height + 4);
                GUI.DrawTexture(selRect, slotSelectedTex, ScaleMode.StretchToFill);
            }

            // Icon on the left
            if (recipe.Icon != null)
            {
                Rect iconRect = new Rect(cardRect.x + 10, cardRect.y + 14, 68, 68);
                DrawSprite(iconRect, recipe.Icon);
            }

            // Recipe Name
            Rect nameRect = new Rect(cardRect.x + 84, cardRect.y + 8, cardRect.width - 90, 22);
            GUI.Label(nameRect, recipe.DisplayName, recipeTitleStyle);

            float curCardY = cardRect.y + 30;

            // Prerequisite Badge
            if (recipe.HasToolRequirement || recipe.HasStationRequirement)
            {
                string reqBadge = "";
                if (recipe.HasToolRequirement)
                {
                    string tName = recipe.RequiredTool != null ? recipe.RequiredTool.DisplayName : recipe.RequiredToolType.GetDisplayName();
                    bool hasT = craftingManager.HasRequiredTool(recipe, inventory);
                    reqBadge += hasT ? $"<color=#1e7b24>[Tool: {tName}]</color> " : $"<color=#b82a20>[Need: {tName}]</color> ";
                }
                if (recipe.HasStationRequirement)
                {
                    bool hasS = craftingManager.HasRequiredStation(recipe, inventory);
                    reqBadge += hasS ? $"<color=#1e7b24>[{recipe.RequiredStation}]</color>" : $"<color=#b82a20>[Need: {recipe.RequiredStation}]</color>";
                }
                Rect badgeReqRect = new Rect(cardRect.x + 84, curCardY, cardRect.width - 90, 18);
                GUI.Label(badgeReqRect, reqBadge, statusStyle);
                curCardY += 18;
            }

            // Ingredients summary line
            string ingSummary = "";
            for (int k = 0; k < recipe.Ingredients.Count; k++)
            {
                var ing = recipe.Ingredients[k];
                if (k > 0) ingSummary += ", ";
                ingSummary += $"{ing.Item.DisplayName} x{ing.RequiredQuantity}";
            }
            Rect summaryRect = new Rect(cardRect.x + 84, curCardY, cardRect.width - 90, 18);
            GUI.Label(summaryRect, ingSummary, ingredientStyle);
            curCardY += 20;

            // Status Badge
            Rect badgeRect = new Rect(cardRect.x + 84, curCardY, cardRect.width - 90, 20);
            if (canCraftThis)
            {
                GUI.Label(badgeRect, "<color=#1e7b24><b>[READY TO CRAFT]</b></color>", statusStyle);
            }
            else
            {
                string shortFail = failReason.Contains("Requires tool") ? "[TOOL REQUIRED]" :
                                   (failReason.Contains("Requires station") ? "[STATION REQUIRED]" :
                                   (failReason.Contains("space") ? "[BAG FULL]" : "[MISSING INGREDIENTS]"));
                GUI.Label(badgeRect, $"<color=#a83228><b>{shortFail}</b></color>", statusStyle);
            }

            // Click card to select
            if (e.type == EventType.MouseDown && e.button == 0 && cardRect.Contains(e.mousePosition))
            {
                selectedRecipeIndex = i;
                e.Use();
            }
        }

        GUI.EndScrollView();

        // =====================================================================
        // RIGHT COLUMN: RECIPE DETAILS & CRAFT BUTTON
        // =====================================================================
        float detailsX = listX + listW + 24f;
        float detailsY = listY;
        float detailsW = panelWidth - (listW + 96f);
        float detailsH = panelHeight - 90f;

        Rect detailsBoxRect = new Rect(detailsX, detailsY, detailsW, detailsH);
        if (slotBgTex != null)
        {
            GUI.DrawTexture(detailsBoxRect, slotBgTex, ScaleMode.StretchToFill);
        }
        else
        {
            GUI.Box(detailsBoxRect, GUIContent.none);
        }

        if (selectedRecipeIndex >= 0 && selectedRecipeIndex < recipes.Count)
        {
            var selectedRecipe = recipes[selectedRecipeIndex];
            bool canCraftSelected = craftingManager.CanCraft(selectedRecipe, inventory, out string failReason);

            // Header Icon and Name
            if (selectedRecipe.Icon != null)
            {
                Rect bigIconRect = new Rect(detailsX + 24, detailsY + 20, 80, 80);
                DrawSprite(bigIconRect, selectedRecipe.Icon);
            }

            Rect selTitleRect = new Rect(detailsX + 116, detailsY + 16, detailsW - 136, 32);
            GUI.Label(selTitleRect, $"{selectedRecipe.DisplayName.ToUpper()} <size=15><color=#7a4b18>[{selectedRecipe.Category.ToUpper()}]</color></size>", titleStyle);

            Rect selYieldRect = new Rect(detailsX + 116, detailsY + 46, detailsW - 136, 22);
            GUI.Label(selYieldRect, $"Yields: <b>{selectedRecipe.OutputQuantity}x {selectedRecipe.OutputItem.DisplayName}</b>", ingredientStyle);

            Rect selDescRect = new Rect(detailsX + 116, detailsY + 68, detailsW - 136, 44);
            GUI.Label(selDescRect, selectedRecipe.Description, recipeDescStyle);

            // Dividing line
            float lineY = detailsY + 118f;
            Rect divRect = new Rect(detailsX + 20, lineY, detailsW - 40, 2);
            GUI.Box(divRect, GUIContent.none);

            float curDetailY = lineY + 10f;

            // Optional Prerequisites Section
            if (selectedRecipe.HasToolRequirement || selectedRecipe.HasStationRequirement)
            {
                Rect prereqHeaderRect = new Rect(detailsX + 24, curDetailY, detailsW - 48, 22);
                GUI.Label(prereqHeaderRect, "REQUIRED EQUIPMENT / STATION", sectionStyle);
                curDetailY += 24f;

                if (selectedRecipe.HasToolRequirement)
                {
                    string tName = selectedRecipe.RequiredTool != null ? selectedRecipe.RequiredTool.DisplayName : selectedRecipe.RequiredToolType.GetDisplayName();
                    bool hasT = craftingManager.HasRequiredTool(selectedRecipe, inventory);
                    string tStatus = hasT ? "<color=#1e7b24><b>[OWNED IN INVENTORY]</b></color>" : "<color=#b82a20><b>[MISSING - REQUIRED TO CRAFT]</b></color>";
                    Rect tRect = new Rect(detailsX + 32, curDetailY, detailsW - 64, 22);
                    GUI.Label(tRect, $"Required Tool: <b>{tName}</b> — {tStatus}", ingredientStyle);
                    curDetailY += 22f;
                }

                if (selectedRecipe.HasStationRequirement)
                {
                    bool hasS = craftingManager.HasRequiredStation(selectedRecipe, inventory);
                    string sStatus = hasS ? "<color=#1e7b24><b>[AVAILABLE]</b></color>" : "<color=#b82a20><b>[MISSING - CRAFT WEAVING FRAME FIRST]</b></color>";
                    Rect sRect = new Rect(detailsX + 32, curDetailY, detailsW - 64, 22);
                    GUI.Label(sRect, $"Required Station: <b>{selectedRecipe.RequiredStation}</b> — {sStatus}", ingredientStyle);
                    curDetailY += 22f;
                }

                curDetailY += 6f;
            }

            // Required Materials Section Header
            Rect reqHeaderRect = new Rect(detailsX + 24, curDetailY, detailsW - 48, 22);
            GUI.Label(reqHeaderRect, "REQUIRED INGREDIENTS", sectionStyle);
            curDetailY += 26f;

            // Ingredient list
            for (int j = 0; j < selectedRecipe.Ingredients.Count; j++)
            {
                var ing = selectedRecipe.Ingredients[j];
                int hasCount = inventory.GetItemCount(ing.Item);
                bool hasEnough = hasCount >= ing.RequiredQuantity;

                Rect ingRowRect = new Rect(detailsX + 24, curDetailY + j * 44f, detailsW - 48, 40);

                // Mini slot background for ingredient icon
                Rect ingSlotRect = new Rect(ingRowRect.x, ingRowRect.y, 40, 40);
                if (slotBgTex != null) GUI.DrawTexture(ingSlotRect, slotBgTex, ScaleMode.StretchToFill);
                if (ing.Item.Icon != null)
                {
                    DrawSprite(new Rect(ingSlotRect.x + 4, ingSlotRect.y + 4, 32, 32), ing.Item.Icon);
                }

                // Name and Quantity Ratio
                string colorTag = hasEnough ? "#1e7b24" : "#b82a20";
                string ingText = $"<b>{ing.Item.DisplayName}</b>: <color={colorTag}><b>{hasCount}</b></color> / {ing.RequiredQuantity}";

                Rect ingTextRect = new Rect(ingRowRect.x + 50, ingRowRect.y + 8, 280, 26);
                GUI.Label(ingTextRect, ingText, ingredientStyle);

                // Status text
                string statusText = hasEnough
                    ? "<color=#1e7b24><b>[SATISFIED]</b></color>"
                    : $"<color=#b82a20><b>[NEED {ing.RequiredQuantity - hasCount} MORE]</b></color>";
                Rect ingStatusRect = new Rect(ingRowRect.x + 340, ingRowRect.y + 8, 220, 26);
                GUI.Label(ingStatusRect, statusText, ingredientStyle);
            }

            // Craftability Banner
            float bannerY = detailsY + detailsH - 128f;
            Rect bannerRect = new Rect(detailsX + 24, bannerY, detailsW - 48, 38);
            if (canCraftSelected)
            {
                GUI.Box(bannerRect, "CRAFTABLE: ALL PREREQUISITES AND MATERIALS READY", activeTabStyle);
            }
            else
            {
                GUI.Box(bannerRect, $"CANNOT CRAFT: {failReason.ToUpper()}", inactiveTabStyle);
            }

            // Big CRAFT Button
            float btnY = detailsY + detailsH - 80f;
            Rect craftBtnRect = new Rect(detailsX + 24, btnY, detailsW - 48, 60);

            if (canCraftSelected)
            {
                if (GUI.Button(craftBtnRect, $"CRAFT {selectedRecipe.DisplayName.ToUpper()}", craftBtnStyle))
                {
                    AudioManager.Instance?.PlayButtonClick();
                    craftingManager.Craft(selectedRecipe, inventory, out _);
                }
            }
            else
            {
                GUI.Box(craftBtnRect, $"CRAFT {selectedRecipe.DisplayName.ToUpper()}", craftBtnDisabledStyle);
            }
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
            titleStyle.fontSize = 26;
            titleStyle.fontStyle = FontStyle.Bold;
            titleStyle.normal.textColor = new Color(0.32f, 0.18f, 0.08f, 1f);
        }

        if (sectionStyle == null)
        {
            sectionStyle = new GUIStyle();
            sectionStyle.fontSize = 17;
            sectionStyle.fontStyle = FontStyle.Bold;
            sectionStyle.normal.textColor = new Color(0.45f, 0.28f, 0.14f, 1f);
        }

        if (recipeTitleStyle == null)
        {
            recipeTitleStyle = new GUIStyle();
            recipeTitleStyle.fontSize = 20;
            recipeTitleStyle.fontStyle = FontStyle.Bold;
            recipeTitleStyle.normal.textColor = new Color(0.32f, 0.18f, 0.08f, 1f);
        }

        if (recipeDescStyle == null)
        {
            recipeDescStyle = new GUIStyle();
            recipeDescStyle.fontSize = 15;
            recipeDescStyle.normal.textColor = new Color(0.42f, 0.28f, 0.16f, 1f);
            recipeDescStyle.wordWrap = true;
        }

        if (ingredientStyle == null)
        {
            ingredientStyle = new GUIStyle();
            ingredientStyle.fontSize = 18;
            ingredientStyle.richText = true;
            ingredientStyle.normal.textColor = new Color(0.35f, 0.22f, 0.12f, 1f);
        }

        if (statusStyle == null)
        {
            statusStyle = new GUIStyle();
            statusStyle.fontSize = 14;
            statusStyle.fontStyle = FontStyle.Bold;
            statusStyle.richText = true;
        }

        if (activeTabStyle == null)
        {
            activeTabStyle = new GUIStyle(GUI.skin.box);
            Texture2D aTex = new Texture2D(1, 1);
            aTex.SetPixel(0, 0, new Color(0.88f, 0.72f, 0.48f, 1f));
            aTex.Apply();
            activeTabStyle.normal.background = aTex;
            activeTabStyle.fontSize = 16;
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
            inactiveTabStyle.fontSize = 15;
            inactiveTabStyle.alignment = TextAnchor.MiddleCenter;
            inactiveTabStyle.normal.textColor = new Color(0.88f, 0.82f, 0.72f, 1f);
        }

        if (craftBtnStyle == null)
        {
            craftBtnStyle = new GUIStyle(GUI.skin.button);
            Texture2D btnTex = new Texture2D(1, 1);
            btnTex.SetPixel(0, 0, new Color(0.24f, 0.58f, 0.22f, 1f)); // Stardew vibrant green
            btnTex.Apply();
            craftBtnStyle.normal.background = btnTex;
            craftBtnStyle.fontSize = 22;
            craftBtnStyle.fontStyle = FontStyle.Bold;
            craftBtnStyle.alignment = TextAnchor.MiddleCenter;
            craftBtnStyle.normal.textColor = Color.white;
        }

        if (craftBtnDisabledStyle == null)
        {
            craftBtnDisabledStyle = new GUIStyle(GUI.skin.box);
            Texture2D disTex = new Texture2D(1, 1);
            disTex.SetPixel(0, 0, new Color(0.48f, 0.42f, 0.38f, 0.85f));
            disTex.Apply();
            craftBtnDisabledStyle.normal.background = disTex;
            craftBtnDisabledStyle.fontSize = 20;
            craftBtnDisabledStyle.fontStyle = FontStyle.Bold;
            craftBtnDisabledStyle.alignment = TextAnchor.MiddleCenter;
            craftBtnDisabledStyle.normal.textColor = new Color(0.75f, 0.72f, 0.70f, 1f);
        }
    }
}
