using UnityEngine;

public class PlayerStats : MonoBehaviour
{
    [Header("Health")]
    public float maxHealth = 100f;
    public float currentHealth = 100f;

    [Header("Combat")]
    public float attackDamage = 10f;
    public float attackSpeed = 1f;

    [Header("Defense")]
    public float damageReduction = 0f; // percentage (e.g., 0.10 = 10% reduction)

    [Header("Movement")]
    public float moveSpeed = 5f;

    [Header("Regeneration")]
    public float regenPerSecond = 0f;

    // Visuals variables
    private SpriteRenderer playerSprite;
    private Color fullHealthColor;

    private void Start()
    {
        // Grab the player's SpriteRenderer and save its native colors
        playerSprite = GetComponent<SpriteRenderer>();
        if (playerSprite != null)
        {
            fullHealthColor = playerSprite.color;
        }
    }

    private void Update()
    {
        // Passive Regeneration
        if (currentHealth < maxHealth)
        {
            currentHealth += regenPerSecond * Time.deltaTime;
            currentHealth = Mathf.Min(currentHealth, maxHealth);
        }
        
        // Dynamically update the player's color based on health percentage
        UpdatePlayerColor();

        // DEBUG: Test damage mechanic in editor
        if (Input.GetKeyDown(KeyCode.K)) 
        {
            TakeDamage(10f);
        }

        // Add this inside the Update() method of PlayerStats
        Debug.Log($"[Stats Frame Log] HP: {currentHealth}/{maxHealth} | DMG: {attackDamage} | ATK SPD: {attackSpeed} | MOV: {moveSpeed} | REG: {regenPerSecond}/s");
    }

    private void UpdatePlayerColor()
    {
        if (playerSprite == null || maxHealth <= 0) return;

        // Calculate health ratio (Value between 0.0 and 1.0)
        float healthPercent = currentHealth / maxHealth;

        // Smoothly blend between full original colors and solid black
        playerSprite.color = Color.Lerp(Color.black, fullHealthColor, healthPercent);
    }

    // Centralized Damage Method to account for stats like Damage Reduction
    public void TakeDamage(float amount)
    {
        // Apply damage reduction percentage (e.g., if damageReduction is 0.1, take 10% less damage)
        float finalDamage = amount * (1f - damageReduction);
        
        currentHealth -= finalDamage;
        currentHealth = Mathf.Max(currentHealth, 0f); // Prevents health from dropping below 0

        Debug.Log($"[Player] Took {finalDamage} damage (Reduced from {amount}). HP remaining: {currentHealth}");

        if (currentHealth <= 0f)
        {
            Die();
        }
    }

    public void Heal(float amount)
    {
        currentHealth += amount;
        currentHealth = Mathf.Min(currentHealth, maxHealth);
    }

    public void IncreaseMaxHealth(float amount)
    {
        maxHealth += amount;
        currentHealth += amount; // Heals the player by the amount increased
    }

    public void IncreaseDamage(float amount)
    {
        attackDamage += amount;
    }

    public void IncreaseAttackSpeed(float amount)
    {
        attackSpeed += amount;
    }

    public void IncreaseMoveSpeed(float amount)
    {
        moveSpeed += amount;
    }

    public void IncreaseRegen(float amount)
    {
        regenPerSecond += amount;
    }

    public void IncreaseDamageReduction(float amount)
    {
        // E.g., adding 0.05 adds 5% damage reduction
        damageReduction += amount;
        damageReduction = Mathf.Clamp(damageReduction, 0f, 0.95f); // Cap reduction at 95% so player isn't completely invincible
    }

    private void Die()
    {
        Debug.Log("[Player] Game Over! Health reached 0.");
        // Add your game over screen triggers or scene reloads here
    }
}