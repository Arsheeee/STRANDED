using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.Tilemaps;

public class PlayerMovement : MonoBehaviour
{
    private Rigidbody2D rb;
    private Vector2 movement;
    private Animator animator;
    private InputAction moveAction;

    [Header("Movement Settings")]
    [SerializeField] private float moveSpeed = 2.5f;

    [Header("Shoreline Water & Wading Settings")]
    [Tooltip("Speed multiplier applied when wading in shallow shoreline water.")]
    [SerializeField] private float wadeSpeedMultiplier = 0.32f;

    [Tooltip("Maximum movement speed allowed while wading in shallow shoreline water.")]
    [SerializeField] private float maxWadeSpeed = 0.85f;

    [Tooltip("Animator speed while wading in shallow water (slow-motion wading gait).")]
    [SerializeField] private float wadeAnimationSpeed = 0.55f;

    [Header("Tilemap References (Auto-Located if unassigned)")]
    [SerializeField] private Tilemap shallowWaterTilemap;
    [SerializeField] private Tilemap deepOceanTilemap;
    [SerializeField] private Tilemap riverTilemap;

    private readonly Vector2 feetOffset = new Vector2(0f, -0.35f);
    private bool isWading = false;
    public bool IsWading => isWading;

    private bool canMove = true;

    void Start()
    {
        rb = GetComponent<Rigidbody2D>();
        animator = GetComponent<Animator>();

        // Ensure AudioManager exists
        AudioManager.EnsureExists();

        // Locate water tilemaps and ensure river colliders exist
        LocateTilemaps();
        EnsureRiverCollider();

        // Default to facing forward/down upon spawn
        if (animator != null)
        {
            animator.SetFloat("MoveX", 0f);
            animator.SetFloat("MoveY", -1f);
            animator.SetBool("IsMoving", false);
        }

        // Inline InputAction ensures WASD/Arrows work immediately with New Input System
        moveAction = new InputAction("Move", binding: "<Gamepad>/leftStick");
        moveAction.AddCompositeBinding("Dpad")
            .With("Up", "<Keyboard>/w")
            .With("Down", "<Keyboard>/s")
            .With("Left", "<Keyboard>/a")
            .With("Right", "<Keyboard>/d")
            .With("Up", "<Keyboard>/upArrow")
            .With("Down", "<Keyboard>/downArrow")
            .With("Left", "<Keyboard>/leftArrow")
            .With("Right", "<Keyboard>/rightArrow");
        moveAction.Enable();
    }

    private void LocateTilemaps()
    {
        if (shallowWaterTilemap == null)
        {
            var go = GameObject.Find("Tilemap_ShallowWater");
            if (go != null) shallowWaterTilemap = go.GetComponent<Tilemap>();
        }
        if (deepOceanTilemap == null)
        {
            var go = GameObject.Find("Tilemap_DeepOcean");
            if (go != null) deepOceanTilemap = go.GetComponent<Tilemap>();
        }
        if (riverTilemap == null)
        {
            var go = GameObject.Find("Tilemap_River");
            if (go != null) riverTilemap = go.GetComponent<Tilemap>();
        }
    }

    private void EnsureRiverCollider()
    {
        if (riverTilemap == null) return;

        var tc = riverTilemap.GetComponent<TilemapCollider2D>();
        if (tc == null)
        {
            tc = riverTilemap.gameObject.AddComponent<TilemapCollider2D>();
            tc.compositeOperation = Collider2D.CompositeOperation.Merge;
        }

        var cc = riverTilemap.GetComponent<CompositeCollider2D>();
        if (cc == null)
        {
            cc = riverTilemap.gameObject.AddComponent<CompositeCollider2D>();
            cc.geometryType = CompositeCollider2D.GeometryType.Polygons;
        }

        var rbTilemap = riverTilemap.GetComponent<Rigidbody2D>();
        if (rbTilemap != null)
        {
            rbTilemap.bodyType = RigidbodyType2D.Static;
        }
    }

    void OnDestroy()
    {
        moveAction?.Disable();
    }

    public void SetMovementEnabled(bool enabled)
    {
        canMove = enabled;
        if (!canMove)
        {
            movement = Vector2.zero;
            if (rb != null) rb.linearVelocity = Vector2.zero;
            if (animator != null)
            {
                animator.SetBool("IsMoving", false);
                animator.speed = 1.0f;
            }
        }
    }

    void Update()
    {
        if (!canMove)
        {
            movement = Vector2.zero;
            return;
        }

        movement = moveAction.ReadValue<Vector2>();

        if (animator != null)
        {
            if (movement.sqrMagnitude > 0.01f)
            {
                // Snap to dominant cardinal axis to prevent awkward 50-50 blending between perpendicular clips
                float faceX = 0f;
                float faceY = 0f;
                if (Mathf.Abs(movement.x) > Mathf.Abs(movement.y))
                {
                    faceX = Mathf.Sign(movement.x);
                }
                else
                {
                    faceY = Mathf.Sign(movement.y);
                }

                animator.SetFloat("MoveX", faceX);
                animator.SetFloat("MoveY", faceY);
                animator.SetBool("IsMoving", true);

                // Slow motion wading gait animation while wading in water
                animator.speed = isWading ? wadeAnimationSpeed : 1.0f;

                // Play footsteps while moving (rate-limited inside AudioManager; switches to splash when wading)
                AudioManager.Instance?.PlayFootstep(isWading);
            }
            else
            {
                animator.SetBool("IsMoving", false);
                animator.speed = 1.0f;
            }
        }
    }

    void FixedUpdate()
    {
        if (!canMove)
        {
            rb.linearVelocity = Vector2.zero;
            return;
        }

        LocateTilemaps();

        Vector2 feetPos = (Vector2)transform.position + feetOffset;

        // 1. Detect if player is wading in shallow shoreline water (or crossing ford)
        isWading = IsPositionInShallowWater(feetPos);

        // Wading in shoreline water moves "very very slowly" (~0.80f vs normal 2.5f)
        float currentSpeed = isWading ? Mathf.Min(moveSpeed * wadeSpeedMultiplier, maxWadeSpeed) : moveSpeed;

        Vector2 desiredVelocity = movement.normalized * currentSpeed;

        // 2. Authoritative impassable water boundary blocking with cardinal axis sliding
        if (desiredVelocity.sqrMagnitude > 0.001f)
        {
            float dt = Time.fixedDeltaTime;
            float stepDistance = Mathf.Max(currentSpeed * dt, 0.05f);

            // Test X component
            if (Mathf.Abs(desiredVelocity.x) > 0.001f)
            {
                Vector2 targetX = feetPos + new Vector2(Mathf.Sign(desiredVelocity.x) * (0.22f + stepDistance), 0f);
                if (IsImpassableWater(targetX) || IsImpassableWater(targetX + new Vector2(0f, 0.1f)) || IsImpassableWater(targetX - new Vector2(0f, 0.1f)))
                {
                    desiredVelocity.x = 0f;
                }
            }

            // Test Y component
            if (Mathf.Abs(desiredVelocity.y) > 0.001f)
            {
                Vector2 targetY = feetPos + new Vector2(0f, Mathf.Sign(desiredVelocity.y) * (0.12f + stepDistance));
                if (IsImpassableWater(targetY) || IsImpassableWater(targetY + new Vector2(0.2f, 0f)) || IsImpassableWater(targetY - new Vector2(0.2f, 0f)))
                {
                    desiredVelocity.y = 0f;
                }
            }
        }

        rb.linearVelocity = desiredVelocity;
    }

    /// <summary>
    /// Designated shallow river crossing along dirt path at X=174, Y=151..156.
    /// Player can wade through this narrow ford between the island halves.
    /// </summary>
    private bool IsCrossingFord(Vector3Int cell)
    {
        return cell.x == 174 && cell.y >= 151 && cell.y <= 156;
    }

    /// <summary>
    /// Checks if a world position falls inside shallow shoreline water (or the river crossing ford).
    /// </summary>
    private bool IsPositionInShallowWater(Vector2 pos)
    {
        if (shallowWaterTilemap != null)
        {
            Vector3Int cell = shallowWaterTilemap.WorldToCell(pos);
            if (shallowWaterTilemap.HasTile(cell) || IsCrossingFord(cell))
            {
                return true;
            }
        }
        else if (IsCrossingFord(new Vector3Int(Mathf.FloorToInt(pos.x), Mathf.FloorToInt(pos.y), 0)))
        {
            return true;
        }

        return false;
    }

    /// <summary>
    /// Checks if a world position is in deep ocean or river water (strictly impassable).
    /// </summary>
    private bool IsImpassableWater(Vector2 pos)
    {
        // Deep Ocean is strictly impassable everywhere
        if (deepOceanTilemap != null)
        {
            Vector3Int cell = deepOceanTilemap.WorldToCell(pos);
            if (deepOceanTilemap.HasTile(cell))
            {
                return true;
            }
        }

        // River water is impassable everywhere EXCEPT the designated crossing ford
        if (riverTilemap != null)
        {
            Vector3Int cell = riverTilemap.WorldToCell(pos);
            if (riverTilemap.HasTile(cell) && !IsCrossingFord(cell))
            {
                return true;
            }
        }

        return false;
    }
}
