using UnityEngine;

/// <summary>
/// Exploration camera for STRANDED.
/// Smoothly follows the player character while strictly clamping within the world boundaries
/// so the camera never reveals void or space outside the playable island world.
/// </summary>
[RequireComponent(typeof(Camera))]
public class ExplorationCamera : MonoBehaviour
{
    [Header("Target Tracking")]
    [Tooltip("Target transform to follow (typically Player)")]
    [SerializeField] private Transform target;

    [Tooltip("Smoothing time for camera movement (lower is snappier, higher is floatier)")]
    [Range(0.01f, 0.5f)]
    [SerializeField] private float smoothTime = 0.18f;

    [Tooltip("Offset relative to the target")]
    [SerializeField] private Vector3 targetOffset = Vector3.zero;

    [Header("World Boundaries (in world units)")]
    [Tooltip("Minimum X and Y boundaries of the world")]
    [SerializeField] private Vector2 worldMin = Vector2.zero;

    [Tooltip("Maximum X and Y boundaries of the world (e.g. 350x350 tiles)")]
    [SerializeField] private Vector2 worldMax = new Vector2(350f, 350f);

    [Tooltip("Whether to clamp camera viewport strictly within world boundaries")]
    [SerializeField] private bool clampToBounds = true;

    private Camera cam;
    private Vector3 currentVelocity = Vector3.zero;

    void Awake()
    {
        cam = GetComponent<Camera>();
        if (cam == null)
        {
            cam = Camera.main;
        }

        // Ensure camera is orthographic for 2D pixel-art exploration
        cam.orthographic = true;
    }

    void Start()
    {
        // Automatically find Player if not assigned
        if (target == null)
        {
            GameObject playerObj = GameObject.FindGameObjectWithTag("Player");
            if (playerObj == null)
            {
                playerObj = GameObject.Find("Player");
            }
            if (playerObj != null)
            {
                target = playerObj.transform;
            }
        }

        // Snap camera immediately to target on start to avoid opening pan jitter
        if (target != null)
        {
            Vector3 initialPos = CalculateClampedPosition(target.position + targetOffset);
            initialPos.z = transform.position.z;
            transform.position = initialPos;
        }
    }

    void LateUpdate()
    {
        if (target == null) return;

        Vector3 targetPos = target.position + targetOffset;
        Vector3 targetClamped = CalculateClampedPosition(targetPos);
        targetClamped.z = transform.position.z; // Maintain orthographic camera Z

        // Smooth follow without jitter or snapping
        transform.position = Vector3.SmoothDamp(transform.position, targetClamped, ref currentVelocity, smoothTime);
    }

    /// <summary>
    /// Calculates the camera center position clamped so the visible frustum stays within world bounds.
    /// </summary>
    public Vector3 CalculateClampedPosition(Vector3 desiredPos)
    {
        if (cam == null)
        {
            cam = GetComponent<Camera>();
            if (cam == null) cam = Camera.main;
        }

        if (!clampToBounds || cam == null)
        {
            return desiredPos;
        }

        float vertExtent = cam.orthographicSize;
        float aspect = (cam.targetTexture != null && cam.targetTexture.height > 0)
            ? (float)cam.targetTexture.width / cam.targetTexture.height
            : cam.aspect;
        float horizExtent = vertExtent * aspect;

        float minX = worldMin.x + horizExtent;
        float maxX = worldMax.x - horizExtent;
        float minY = worldMin.y + vertExtent;
        float maxY = worldMax.y - vertExtent;

        float clampedX;
        if (minX > maxX)
        {
            // Viewport is wider than world bounds: center horizontally
            clampedX = (worldMin.x + worldMax.x) * 0.5f;
        }
        else
        {
            clampedX = Mathf.Clamp(desiredPos.x, minX, maxX);
        }

        float clampedY;
        if (minY > maxY)
        {
            // Viewport is taller than world bounds: center vertically
            clampedY = (worldMin.y + worldMax.y) * 0.5f;
        }
        else
        {
            clampedY = Mathf.Clamp(desiredPos.y, minY, maxY);
        }

        return new Vector3(clampedX, clampedY, desiredPos.z);
    }

    /// <summary>
    /// Updates world boundary limits at runtime.
    /// </summary>
    public void SetWorldBounds(Vector2 min, Vector2 max)
    {
        worldMin = min;
        worldMax = max;
    }

    /// <summary>
    /// Assigns a new target for the camera to follow.
    /// </summary>
    public void SetTarget(Transform newTarget)
    {
        target = newTarget;
    }

#if UNITY_EDITOR
    private void OnDrawGizmosSelected()
    {
        // Visualize world boundary gizmo in scene view
        Gizmos.color = Color.cyan;
        Vector3 center = new Vector3((worldMin.x + worldMax.x) * 0.5f, (worldMin.y + worldMax.y) * 0.5f, 0f);
        Vector3 size = new Vector3(worldMax.x - worldMin.x, worldMax.y - worldMin.y, 0.1f);
        Gizmos.DrawWireCube(center, size);
    }
#endif
}
