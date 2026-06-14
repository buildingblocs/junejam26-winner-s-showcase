using UnityEngine;
using UnityEngine.InputSystem;
public class PlayerController : MonoBehaviour
{
    InputAction moveAction;
    public float moveSpeed = 8f;
    public float jumpForce = 300f;
    public int maxJumpCount = 2;
    private int jumpCount = 0;
    private Animator animator;
    public int health = 3;

    Rigidbody2D rb;
    InputAction jumpAction;

    
    void Start()
    {
        moveAction = InputSystem.actions.FindAction("Move");
        rb = GetComponent<Rigidbody2D>();
        jumpAction = InputSystem.actions.FindAction("Jump");

        moveAction = InputSystem.actions.FindAction("Move");
        rb = GetComponent<Rigidbody2D>();
        jumpAction = InputSystem.actions.FindAction("Jump");
        animator = GetComponent<Animator>();
    }
    void Update()
    {
        Vector2 moveValue = moveAction.ReadValue<Vector2>();
        transform.Translate(Vector2.right * moveValue.x * Time.deltaTime * moveSpeed);
        if (jumpAction.WasPressedThisFrame() && jumpCount < maxJumpCount)
        {
            rb.AddForce(Vector2.up * jumpForce);
            jumpCount++;
            animator.SetInteger("jumpCount", jumpCount);
        }
        animator.SetFloat("runSpeed", Mathf.Abs(moveValue.x));

        if (moveValue.x > 0)
        {
            transform.localScale = new Vector3(6, 6, 1);
        }
        if (moveValue.x < 0)
        {
            transform.localScale = new Vector3(-6, 6, 1);
        }
    }

    private void OnCollisionEnter2D(Collision2D collision)
    {
        if (collision.gameObject.CompareTag("Ground"))
        {
            jumpCount = 0;
            animator.SetInteger("jumpCount", jumpCount);
        }
    }

}