using UnityEngine;
using UnityEngine.InputSystem;

public class PlayerMovement : MonoBehaviour
{
    private Rigidbody2D rb;
    private Vector2 movement;
    [SerializeField] private float moveSpeed = 2.5f;
    private Animator animator;
    private InputAction moveAction;

    void Start()
    {
        rb = GetComponent<Rigidbody2D>();
        animator = GetComponent<Animator>();

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

    void OnDestroy()
    {
        moveAction?.Disable();
    }

    void Update()
    {
        movement = moveAction.ReadValue<Vector2>();

        if (animator != null)
        {
            if (movement.sqrMagnitude > 0)
            {
                animator.SetFloat("MoveX", movement.x);
                animator.SetFloat("MoveY", movement.y);
                animator.SetBool("IsMoving", true);
            }
            else
            {
                animator.SetBool("IsMoving", false);
            }
        }
    }

    void FixedUpdate()
    {
        // Normalize to prevent faster diagonal movement
        rb.linearVelocity = movement.normalized * moveSpeed;
    }
}
