using UnityEngine;

public class Enemy : MonoBehaviour
{
    public float moveSpeed = 2f;
    
    private Rigidbody2D rb;
    private Transform target;
    private Vector2 moveDirection;
    private Animator animator;

    private void Awake()
    {
        rb = GetComponent<Rigidbody2D>();
        animator = GetComponent<Animator>();
    }

    void Start()
    {
        GameObject player = GameObject.FindGameObjectWithTag("Player");
        if (player != null)
        {
            target = player.transform;
        }
    }

    void Update()
    {
        if (target != null)
        {
            Vector3 direction = (target.position - transform.position).normalized;
            moveDirection = direction;
        }
        
        UpdateAnimation();
    }

    private void FixedUpdate()
    {
        if (target == null)
        {
            rb.linearVelocity = Vector2.zero;
            return;
        }

        // Instantly moves the physics body toward the player target coordinates
        rb.linearVelocity = moveDirection * moveSpeed;
    }

    private void UpdateAnimation()
    {
        if (animator == null) return;

        bool isMoving = moveDirection.sqrMagnitude > 0.01f;
        animator.SetBool("isMoving", isMoving);

        if (isMoving)
        {
            // Sends values straight to your 2D Blend Tree
            animator.SetFloat("moveX", moveDirection.x);
            animator.SetFloat("moveY", moveDirection.y);

            // Sprite flipping configuration for left/right mapping
            if (moveDirection.x > 0.1f) transform.localScale = new Vector3(1f, 1f, 1f);
            else if (moveDirection.x < -0.1f) transform.localScale = new Vector3(-1f, 1f, 1f);
        }
    }
}