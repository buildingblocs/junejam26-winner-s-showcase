using UnityEngine;

public class Player_Combat : MonoBehaviour
{
    private Animator animator;
    private PlayerStats stats;

    private float attackCooldown = 0f;

    void Start()
    {
        animator = GetComponent<Animator>();
        stats = GetComponent<PlayerStats>();
    }

    void Update()
    {
        attackCooldown -= Time.deltaTime;
        Attack();
    }

    void Attack()
    {
        if (attackCooldown > 0)
            return;

        if (Input.GetMouseButtonDown(0))
        {
            animator.SetTrigger("attack");

            attackCooldown = 1f / stats.attackSpeed;

            // DEBUG: Prints the calculation to the console
            Debug.Log($"[Combat] Attacked! Calculated Cooldown: {attackCooldown} seconds (Base Speed: {stats.attackSpeed})");
        }

        if (Input.GetMouseButtonDown(1))
        {
            animator.SetTrigger("attack2");

            attackCooldown = 1f / stats.attackSpeed;
            
            // DEBUG: Prints the calculation to the console
            Debug.Log($"[Combat] Attacked Alt! Calculated Cooldown: {attackCooldown} seconds (Base Speed: {stats.attackSpeed})");
        }
    }
}