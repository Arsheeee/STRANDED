using UnityEngine;

/// <summary>
/// ScriptableObject definition for all collectible items, resources, and tools in STRANDED.
/// </summary>
[CreateAssetMenu(fileName = "NewItem", menuName = "STRANDED/Item Data")]
public class ItemData : ScriptableObject
{
    [Header("Identity")]
    [Tooltip("Unique, stable string identifier (e.g. 'wood', 'stone_axe').")]
    [SerializeField] private string itemId = "";

    [Tooltip("Friendly display name shown in inventory and HUD.")]
    [SerializeField] private string displayName = "";

    [Tooltip("Short descriptive text for tooltips.")]
    [TextArea(2, 4)]
    [SerializeField] private string description = "";

    [Tooltip("Sprite icon used in UI slots.")]
    [SerializeField] private Sprite icon;

    [Header("Item Properties")]
    [Tooltip("Whether this is a stackable raw resource or an equipped tool.")]
    [SerializeField] private ItemType itemType = ItemType.Resource;

    [Tooltip("Mapped resource type if ItemType is Resource.")]
    [SerializeField] private ResourceType resourceType = ResourceType.Wood;

    [Tooltip("Mapped tool type if ItemType is Tool.")]
    [SerializeField] private ToolType toolType = ToolType.None;

    [Tooltip("Whether multiple items can occupy the same slot.")]
    [SerializeField] private bool isStackable = true;

    [Tooltip("Maximum stack size (tools default to 1, resources to 99).")]
    [SerializeField] private int maxStackSize = 99;

    [Header("Consumable / Food Properties")]
    [Tooltip("Whether this item can be directly eaten or drunk by the player.")]
    [SerializeField] private bool isConsumable = false;

    [Tooltip("Amount of hunger restored when consumed.")]
    [SerializeField] private float hungerRestored = 0f;

    [Tooltip("Amount of thirst restored when consumed.")]
    [SerializeField] private float thirstRestored = 0f;

    [Tooltip("Amount of health restored when consumed.")]
    [SerializeField] private float healthRestored = 0f;

    [Tooltip("Amount of energy restored when consumed.")]
    [SerializeField] private float energyRestored = 0f;

    public string ItemId => itemId;
    public string DisplayName => string.IsNullOrEmpty(displayName) ? name : displayName;
    public string Description => description;
    public Sprite Icon => icon;
    public ItemType ItemType => itemType;
    public ResourceType ResourceType => resourceType;
    public ToolType ToolType => toolType;
    public bool IsStackable => isStackable;
    public int MaxStackSize => isStackable ? maxStackSize : 1;
    public bool IsConsumable => isConsumable;
    public float HungerRestored => hungerRestored;
    public float ThirstRestored => thirstRestored;
    public float HealthRestored => healthRestored;
    public float EnergyRestored => energyRestored;

    /// <summary>
    /// Runtime factory method to instantiate or initialize item data dynamically.
    /// </summary>
    public static ItemData CreateRuntimeInstance(
        string id,
        string name,
        string desc,
        Sprite iconSprite,
        ItemType type,
        ResourceType resType,
        ToolType tool,
        bool stackable,
        int maxStack,
        bool consumable = false,
        float hunger = 0f,
        float thirst = 0f,
        float health = 0f,
        float energy = 0f)
    {
        ItemData item = ScriptableObject.CreateInstance<ItemData>();
        item.itemId = id;
        item.displayName = name;
        item.description = desc;
        item.icon = iconSprite;
        item.itemType = type;
        item.resourceType = resType;
        item.toolType = tool;
        item.isStackable = stackable;
        item.maxStackSize = stackable ? maxStack : 1;
        item.isConsumable = consumable;
        item.hungerRestored = hunger;
        item.thirstRestored = thirst;
        item.healthRestored = health;
        item.energyRestored = energy;
        return item;
    }
}
