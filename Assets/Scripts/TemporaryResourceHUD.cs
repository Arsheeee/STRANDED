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
        { ResourceType.Coconut, 0 }
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

    private void AddToast(string message, Color color)
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
            toastStyle.fontSize = 15;
            toastStyle.fontStyle = FontStyle.Bold;
            toastStyle.alignment = TextAnchor.MiddleCenter;
            toastStyle.normal.textColor = Color.white;
        }

        if (promptStyle == null)
        {
            promptStyle = new GUIStyle(GUI.skin.box);
            promptStyle.normal.background = promptTexture;
            promptStyle.fontSize = 16;
            promptStyle.fontStyle = FontStyle.Bold;
            promptStyle.alignment = TextAnchor.MiddleCenter;
            promptStyle.normal.textColor = new Color(0.40f, 1.0f, 0.60f);
        }

        if (trackerStyle == null)
        {
            trackerStyle = new GUIStyle(GUI.skin.box);
            trackerStyle.normal.background = boxTexture;
            trackerStyle.fontSize = 13;
            trackerStyle.alignment = TextAnchor.MiddleLeft;
            trackerStyle.normal.textColor = new Color(0.90f, 0.92f, 0.95f);
            trackerStyle.padding = new RectOffset(10, 10, 6, 6);
        }

        if (trackerHeaderStyle == null)
        {
            trackerHeaderStyle = new GUIStyle(GUI.skin.label);
            trackerHeaderStyle.fontSize = 12;
            trackerHeaderStyle.fontStyle = FontStyle.Bold;
            trackerHeaderStyle.normal.textColor = new Color(0.65f, 0.80f, 0.95f);
        }

        if (trackerToolStyle == null)
        {
            trackerToolStyle = new GUIStyle(trackerStyle);
            trackerToolStyle.fontSize = 12;
            trackerToolStyle.fontStyle = FontStyle.Bold;
            trackerToolStyle.normal.textColor = new Color(0.40f, 0.88f, 1.0f);
        }
    }

    void OnGUI()
    {
        EnsureStyles();

        if (cachedPlayer == null)
        {
            cachedPlayer = Object.FindAnyObjectByType<PlayerInteraction>();
        }

        // 1. Session Harvest & Tool Equipment Tracker in Top-Left Corner
        float trackerWidth = 390f;
        float trackerHeight = 90f;
        Rect trackerRect = new Rect(16f, 16f, trackerWidth, trackerHeight);
        GUI.Box(trackerRect, GUIContent.none, trackerStyle);

        GUILayout.BeginArea(trackerRect);
        GUILayout.Space(3);
        GUILayout.Label("  [STRANDED BATCH 4: INVENTORY & TOOL SYSTEM]", trackerHeaderStyle);
        GUILayout.Space(1);
        string summaryLine = $"   Wood: {GetCollectedCount(ResourceType.Wood)}  |  " +
                             $"Stone: {GetCollectedCount(ResourceType.Stone)}  |  " +
                             $"Fiber: {GetCollectedCount(ResourceType.Fiber)}  |  " +
                             $"Berries: {GetCollectedCount(ResourceType.Berries)}  |  " +
                             $"Coconut: {GetCollectedCount(ResourceType.Coconut)}";
        GUILayout.Label(summaryLine, trackerStyle);
        GUILayout.Space(1);

        string toolName = cachedPlayer != null ? cachedPlayer.CurrentTool.ToDisplayName() : "None";
        string toolLine = $"   Equipped: [{toolName}]  (Hotbar: 1-9,0,-,= | Bag: 'I')";
        GUILayout.Label(toolLine, trackerToolStyle);
        GUILayout.EndArea();

        // 2. Contextual Interaction Prompt (e.g. "[E] Harvest Berry Bush")
        if (!string.IsNullOrEmpty(currentPrompt))
        {
            float promptWidth = 340f;
            float promptHeight = 38f;
            float promptX = (Screen.width - promptWidth) * 0.5f;
            float promptY = Screen.height - 110f;
            GUI.Box(new Rect(promptX, promptY, promptWidth, promptHeight), currentPrompt, promptStyle);
        }

        // 3. Collection Toast Notifications (Top-Right stacked)
        float startY = 16f;
        float toastWidth = 280f;
        float toastHeight = 32f;
        float toastX = Screen.width - toastWidth - 16f;

        for (int i = 0; i < activeToasts.Count; i++)
        {
            var toast = activeToasts[i];
            float alpha = Mathf.Clamp01(toast.timer / 0.5f); // Fade out in last 0.5 sec
            Color prevColor = GUI.color;
            GUI.color = new Color(toast.color.r, toast.color.g, toast.color.b, alpha);

            Rect toastRect = new Rect(toastX, startY + (i * (toastHeight + 6f)), toastWidth, toastHeight);
            GUI.Box(toastRect, toast.text, toastStyle);

            GUI.color = prevColor;
        }
    }
}
