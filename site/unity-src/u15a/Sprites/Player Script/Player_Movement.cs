using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Player_Movement : MonoBehaviour
{
    [Header("Movement")]
    private PlayerStats stats;

    private float speedX;
    private float speedY;

    private Rigidbody2D rb;
    private Camera mainCamera;

    [Header("Animation")]
    public Animator animator;

    void Start()
    {
        rb = GetComponent<Rigidbody2D>();
        mainCamera = Camera.main;
        stats = GetComponent<PlayerStats>();
    }

    void Update()
    {
        // WASD input
        speedX = Input.GetAxisRaw("Horizontal");
        speedY = Input.GetAxisRaw("Vertical");

        // Animation
        bool isMoving = (speedX != 0 || speedY != 0);
        animator.SetBool("isRunning", isMoving);

        // Get mouse position in world space
        Vector3 mousePos3D = mainCamera.ScreenToWorldPoint(Input.mousePosition);

        // Convert to Vector2
        Vector2 mousePos = new Vector2(mousePos3D.x, mousePos3D.y);

        // Direction from player to mouse
        Vector2 direction = mousePos - (Vector2)transform.position;

        // Calculate angle
        float angle = Mathf.Atan2(direction.y, direction.x) * Mathf.Rad2Deg;

        // Rotate player to face mouse
        transform.rotation = Quaternion.Euler(0f, 0f, angle);
    }

    void FixedUpdate()
    {
        if (stats == null) return;

        // Zelda-style movement (WASD always stays the same relative to screen)
        rb.linearVelocity = new Vector2(speedX * stats.moveSpeed, speedY * stats.moveSpeed);
    }
}