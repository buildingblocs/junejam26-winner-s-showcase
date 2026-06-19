using UnityEngine;

public class PlayerMovement : MonoBehaviour
{
    public enum PlayerState { Free, Talking, Menu }
    [Header("Current Status")]
    public PlayerState currentState = PlayerState.Free;

    public float moveSpeed = 5f;
    
    private Rigidbody2D rb;
    private Vector2 inputDirection;
    private Vector2 lookDirection = Vector2.down;

    void Start()
    {
        rb = GetComponent<Rigidbody2D>();
        if (rb == null)
        {
            Debug.LogError("[PlayerMovement] CRITICAL: Rigidbody2D missing from Player GameObject!");
        }
    }

    void Update()
    {
        if (currentState != PlayerState.Free)
        {
            inputDirection = Vector2.zero;
            return;
        }

        float moveX = Input.GetAxisRaw("Horizontal");
        float moveY = Input.GetAxisRaw("Vertical");
        inputDirection = new Vector2(moveX, moveY).normalized;

        if (inputDirection != Vector2.zero)
        {
            lookDirection = inputDirection;
        }
    }

    void FixedUpdate()
    {
        if (currentState != PlayerState.Free)
        {
            rb.linearVelocity = Vector2.zero; 
            return;
        }

        rb.MovePosition(rb.position + inputDirection * moveSpeed * Time.fixedDeltaTime);
    }

    public Vector2 GetLookDirection()
    {
        return lookDirection;
    }
}