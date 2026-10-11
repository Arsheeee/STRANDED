using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Temporary collection and harvest feedback system for Batch 2.
/// Verifies resource interactions with visual screen notifications,
/// contextual interaction prompts, and a debug harvest tracker.
/// Easily replaced when the full inventory system is implemented in later batches.
/// </summary>
public class TemporaryResourceHUD : MonoBehaviour
{
    private static TemporaryResourceHUD instance;
    public static TemporaryResourceHUD Instance => instance;

    // Track total collected amounts per resource type
    private static readonly Dictionary<ResourceType, int> collectedCounts = new Dictionary<ResourceType, int>()
    {
        { ResourceType.Wood, 0 },
        { ResourceType.Stone, 0 },
        { ResourceType.Fiber, 0 },
        { ResourceType.Berries, 0 },
        { ResourceType.Coconut, 0 },
        { ResourceType.Vines, 0 }
    };

    // Notification toast data
    private class ToastMessage
    {
        public string text;
        public float timer;
        public float duration;
        public Color color;
    }

    private readonly List<ToastMessage> activeToasts = new List<ToastMessage>();
    private string currentPrompt = "";
    private GUIStyle toastStyle;
    private GUIStyle promptStyle;
    private GUIStyle trackerStyle;
    private GUIStyle trackerHeaderStyle;
    private GUIStyle trackerToolStyle;
    private Texture2D boxTexture;
    private Texture2D promptTexture;
    private PlayerInteraction cachedPlayer;

    void Awake()
    {
        if (instance != null && instance != this)
        {
            Destroy(gameObject);
            return;
        }
        instance = this;
    }

    void Update()
    {
        // Update toast timers
        for (int i = activeToasts.Count - 1; i >= 0; i--)
        {
            activeToasts[i].timer -= Time.deltaTime;
            if (activeToasts[i].timer <= 0f)
            {
                activeToasts.RemoveAt(i);
            }
        }
    }

    /// <summary>
    /// Records a resource collection event, updating totals and displaying feedback.
    /// </summary>
    public static void RecordCollection(ResourceType type, int amount, string nodeName)
    {
        if (!collectedCounts.ContainsKey(type))
        {
            collectedCounts[type] = 0;
        }
        collectedCounts[type] += amount;
        int total = collectedCounts[type];

        string message = $"Collected {type} +{amount} (Total: {total})";
        Debug.Log($"[STRANDED Harvest] {message} from '{nodeName}'");

        if (instance != null)
        {
            Color toastColor = GetResourceColor(type);
            instance.AddToast(message, toastColor);
        }
    }

    /// <summary>
    /// Displays a requirement warning notification (e.g. 'Requires Stone Axe').
    /// </summary>
    public static void ShowRequirementFeedback(string feedback)
    {
        Debug.LogWarning($"[STRANDED Tool Requirement] {feedback}");
        if (instance != null)
        {
            instance.AddToast(feedback, new Color(1.0f, 0.42f, 0.38f)); // Warning coral-red
        }
    }

    /// <summary>
    /// Displays an equipment notification when the player switches or unequips tools.
    /// </summary>
    public static void ShowEquipmentNotification(string notification)
    {
        Debug.Log($"[STRANDED Equipment] {notification}");
        if (instance != null)
        {
            instance.AddToast(notification, new Color(0.40f, 0.85f, 1.0f)); // Equipment cyan
        }
    }

    /// <summary>
    /// Sets or clears the current interaction prompt displayed on screen.
    /// </summary>
    public void SetInteractionPrompt(string prompt)
    {
        currentPrompt = prompt;
    }

    public static int GetCollectedCount(ResourceType type)
    {
        if (instance != null && instance.cachedPlayer != null && instance.cachedPlayer.Inventory != null)
        {
            return instance.cachedPlayer.Inventory.GetItemCount(type);
        }
        return collectedCounts.ContainsKey(type) ? collectedCounts[type] : 0;
    }

    public void ShowNotification(string message, Color color)
    {
        AddToast(message, color);
    }

    public void AddToast(string message, Color color)
    {
        activeToasts.Add(new ToastMessage()
        {
            text = message,
            timer = 2.8f,
            duration = 2.8f,
            color = color
        });

        // Limit visible notifications
        if (activeToasts.Count > 4)
        {
            activeToasts.RemoveAt(0);
        }
    }

    private static Color GetResourceColor(ResourceType type)
    {
        switch (type)
        {
            case ResourceType.Wood: return new Color(0.95f, 0.72f, 0.45f); // Warm wood
            case ResourceType.Stone: return new Color(0.82f, 0.85f, 0.90f); // Slate grey
            case ResourceType.Fiber: return new Color(0.55f, 0.90f, 0.55f); // Fresh green
            case ResourceType.Berries: return new Color(1.0f, 0.45f, 0.55f); // Berry red/pink
            case ResourceType.Coconut: return new Color(0.95f, 0.85f, 0.60f); // Coconut tan
            case ResourceType.Vines: return new Color(0.35f, 0.80f, 0.35f); // Jungle vine green
            default: return Color.white;
        }
    }

    private void EnsureStyles()
    {
        if (boxTexture == null)
        {
            boxTexture = new Texture2D(1, 1);
            boxTexture.SetPixel(0, 0, new Color(0.10f, 0.12f, 0.15f, 0.85f));
            boxTexture.Apply();
        }

        if (promptTexture == null)
        {
            promptTexture = new Texture2D(1, 1);
            promptTexture.SetPixel(0, 0, new Color(0.08f, 0.18f, 0.12f, 0.90f));
            promptTexture.Apply();
        }

        if (toastStyle == null)
        {
            toastStyle = new GUIStyle(GUI.skin.box);
            toastStyle.normal.background = boxTexture;
            toastStyle.fontSize = 22;
            toastStyle.fontStyle = FontStyle.Bold;
            toastStyle.alignment = TextAnchor.MiddleCenter;
            toastStyle.normal.textColor = Color.white;
        }

        if (promptStyle == null)
        {
            promptStyle = new GUIStyle(GUI.skin.box);
            promptStyle.normal.background = promptTexture;
            promptStyle.fontSize = 22;
            promptStyle.fontStyle = FontStyle.Bold;
            promptStyle.alignment = TextAnchor.MiddleCenter;
            promptStyle.normal.textColor = new Color(0.40f, 1.0f, 0.65f);
        }

        if (trackerStyle == null)
        {
            trackerStyle = new GUIStyle(GUI.skin.box);
            trackerStyle.normal.background = boxTexture;
            trackerStyle.fontSize = 16;
            trackerStyle.alignment = TextAnchor.MiddleLeft;
            trackerStyle.normal.textColor = new Color(0.92f, 0.94f, 0.96f);
            trackerStyle.padding = new RectOffset(14, 14, 8, 8);
        }

        if (trackerHeaderStyle == null)
        {
            trackerHeaderStyle = new GUIStyle(GUI.skin.label);
            trackerHeaderStyle.fontSize = 18;
            trackerHeaderStyle.fontStyle = FontStyle.Bold;
            trackerHeaderStyle.normal.textColor = new Color(0.70f, 0.85f, 1.0f);
        }

        if (trackerToolStyle == null)
        {
            trackerToolStyle = new GUIStyle(trackerStyle);
            trackerToolStyle.fontSize = 17;
            trackerToolStyle.fontStyle = FontStyle.Bold;
            trackerToolStyle.normal.textColor = new Color(0.45f, 0.90f, 1.0f);
        }
    }

    void OnGUI()
    {
        EnsureStyles();

        if (cachedPlayer == null)
        {
            cachedPlayer = Object.FindAnyObjectByType<PlayerInteraction>();
        }

        // 1. Session Harvest & Tool Equipment Tracker in Top-Left Corner (VERY VERY BIG)
        float trackerWidth = 640f;
        float trackerHeight = 135f;
        Rect trackerRect = new Rect(20f, 20f, trackerWidth, trackerHeight);
        GUI.Box(trackerRect, GUIContent.none, trackerStyle);

        GUILayout.BeginArea(trackerRect);
        GUILayout.Space(8);
        GUILayout.Label("  [STRANDED: INVENTORY, HOTBAR & CRAFTING]", trackerHeaderStyle);
        GUILayout.Space(4);
        string summaryLine = $"   Wood: {GetCollectedCount(ResourceType.Wood)}  |  " +
                             $"Stone: {GetCollectedCount(ResourceType.Stone)}  |  " +
                             $"Fiber: {GetCollectedCount(ResourceType.Fiber)}  |  " +
                             $"Vines: {GetCollectedCount(ResourceType.Vines)}  |  " +
                             $"Berries: {GetCollectedCount(ResourceType.Berries)}  |  " +
                             $"Coconut: {GetCollectedCount(ResourceType.Coconut)}";
        GUILayout.Label(summaryLine, trackerStyle);
        GUILayout.Space(4);

        string toolName = cachedPlayer != null ? cachedPlayer.CurrentTool.ToDisplayName() : "None";
        string toolLine = $"   Equipped: [{toolName}]  (Hotbar: 1-9,0,-,= | Bag: 'I' | Craft: 'C')";
        GUILayout.Label(toolLine, trackerToolStyle);
        GUILayout.EndArea();

        // 2. Contextual Interaction Prompt (Positioned cleanly above the 80px enlarged hotbar)
        if (!string.IsNullOrEmpty(currentPrompt))
        {
            float promptWidth = 620f;
            float promptHeight = 56f;
            float promptX = (Screen.width - promptWidth) * 0.5f;
            float promptY = Screen.height - 172f;
            GUI.Box(new Rect(promptX, promptY, promptWidth, promptHeight), currentPrompt, promptStyle);
        }

        // 3. Collection Toast Notifications (Top-Right stacked, VERY VERY BIG)
        float startY = 20f;
        float toastWidth = 440f;
        float toastHeight = 52f;
        float toastX = Screen.width - toastWidth - 20f;

        for (int i = 0; i < activeToasts.Count; i++)
        {
            var toast = activeToasts[i];
            float alpha = Mathf.Clamp01(toast.timer / 0.5f); // Fade out in last 0.5 sec
            Color prevColor = GUI.color;
            GUI.color = new Color(toast.color.r, toast.color.g, toast.color.b, alpha);

            Rect toastRect = new Rect(toastX, startY + (i * (toastHeight + 10f)), toastWidth, toastHeight);
            GUI.Box(toastRect, toast.text, toastStyle);

            GUI.color = prevColor;
        }
    }
}
